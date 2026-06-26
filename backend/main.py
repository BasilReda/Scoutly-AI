"""
FastAPI Backend — main application entry point.

Endpoints:
  GET  /                               → Serve frontend HTML
  GET  /static/*                       → Serve CSS/JS
  POST /api/scout                      → Start a scouting pipeline (SSE stream)
  POST /api/scout/{run_id}/decision    → HITL: proceed / stop / adjust with comment
  POST /api/scout/{run_id}/select-player → User picks a player card
  POST /api/scout/{run_id}/send-email  → User confirms email and sends
  GET  /api/download/{run_id}          → Download the generated PDF
  GET  /api/health                     → Health check
  GET  /api/agents                     → List available agents & their prompts
"""
import asyncio
import json
import uuid
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from openai import AsyncAzureOpenAI
from pydantic import BaseModel

from .agents.planner import PlannerAgent
from .utils.config import settings, make_azure_client
from .utils.prompt_loader import PromptLoader

# ── App Setup ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Football AI Management System",
    description="Multi-agent AI scouting platform for professional football clubs",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if _frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(_frontend_dir)), name="static")


def get_openai_client() -> AsyncAzureOpenAI:
    return make_azure_client()


# ── HITL Coordination State ───────────────────────────────────────────────────
# Queue-based: avoids the asyncio.Event "already set" race condition.
# Each queue item is {"action": "proceed"|"stop"|"adjust", "comment": str}
run_hitl_queues: dict[str, asyncio.Queue] = {}

# Player selection: queue item is the selected player name (str)
run_player_selection_queues: dict[str, asyncio.Queue] = {}

# Email body: stored here so the planner can read the user-edited body on send
run_email_bodies: dict[str, str] = {}


# ── Request Models ────────────────────────────────────────────────────────────
class DecisionRequest(BaseModel):
    action: str   # "proceed" | "stop" | "adjust"
    comment: str = ""

class PlayerSelectionRequest(BaseModel):
    player_name: str

class SendEmailRequest(BaseModel):
    email_body: str


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
async def serve_frontend():
    index_path = _frontend_dir / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return JSONResponse({"status": "Football AI Management System API", "docs": "/docs"})


@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "model": settings.OPENAI_MODEL,
        "agents": PromptLoader.list_agents(),
    }


@app.get("/api/agents")
async def list_agents():
    manifest = PromptLoader.manifest()
    return {"agents": [
        {"name": n, "description": d, "prompt_file": f"prompts/{n}.md"}
        for n, d in manifest.items()
    ]}


@app.post("/api/scout/{run_id}/decision")
async def submit_decision(run_id: str, body: DecisionRequest):
    """
    HITL decision endpoint.
    action = "proceed"  → continue pipeline to next agent
    action = "stop"     → halt pipeline
    action = "adjust"   → re-run current agent with comment as extra context
    """
    if run_id not in run_hitl_queues:
        raise HTTPException(status_code=404, detail="Run not found or already completed.")
    if body.action not in ("proceed", "stop", "adjust"):
        raise HTTPException(status_code=400, detail="action must be 'proceed', 'stop', or 'adjust'.")
    await run_hitl_queues[run_id].put({"action": body.action, "comment": body.comment or ""})
    return {"status": "ok", "action": body.action}


@app.post("/api/scout/{run_id}/select-player")
async def select_player(run_id: str, body: PlayerSelectionRequest):
    if run_id not in run_player_selection_queues:
        raise HTTPException(status_code=404, detail="Run not found or player selection already received.")
    await run_player_selection_queues[run_id].put(body.player_name)
    return {"status": "ok", "player": body.player_name}


@app.post("/api/scout/{run_id}/send-email")
async def send_email_confirm(run_id: str, body: SendEmailRequest):
    if run_id not in run_hitl_queues:
        raise HTTPException(status_code=404, detail="Run not found or already completed.")
    run_email_bodies[run_id] = body.email_body
    await run_hitl_queues[run_id].put({"action": "send", "comment": ""})
    return {"status": "ok"}


@app.post("/api/scout")
async def scout_players(request: Request):
    """
    Start a full agentic scouting pipeline.
    Streams real-time SSE events as agents run.
    Body: {"query": "..."}
    """
    body = await request.json()
    query: str = body.get("query", "").strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    run_id = str(uuid.uuid4())
    client = get_openai_client()

    async def event_stream():
        queue: asyncio.Queue = asyncio.Queue()

        # Register coordination state for this run
        run_hitl_queues[run_id] = asyncio.Queue()
        run_player_selection_queues[run_id] = asyncio.Queue()

        yield f"data: {json.dumps({'type': 'connected', 'run_id': run_id, 'query': query})}\n\n"

        async def run_pipeline():
            try:
                planner = PlannerAgent(
                    client=client,
                    sse_queue=queue,
                    run_id=run_id,
                    hitl_queues=run_hitl_queues,
                    player_selection_queues=run_player_selection_queues,
                    email_bodies=run_email_bodies,
                )
                result = await planner.run(query=query)
                if not result.get("stopped"):
                    await queue.put({
                        "type": "pipeline_complete",
                        "run_id": run_id,
                        "pdf_filename": Path(result.get("pdf_path", "")).name,
                        "ranked_count": len(result.get("ranked_players", [])),
                    })
            except Exception as exc:
                await queue.put({
                    "type": "pipeline_error",
                    "run_id": run_id,
                    "error": str(exc),
                })
            finally:
                await queue.put(None)

        asyncio.create_task(run_pipeline())

        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=300.0)
                except asyncio.TimeoutError:
                    yield f"data: {json.dumps({'type': 'timeout', 'message': 'Pipeline timed out'})}\n\n"
                    break

                if event is None:
                    yield f"data: {json.dumps({'type': 'stream_end'})}\n\n"
                    break

                yield f"data: {json.dumps(event, default=str)}\n\n"
        finally:
            run_hitl_queues.pop(run_id, None)
            run_player_selection_queues.pop(run_id, None)
            run_email_bodies.pop(run_id, None)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@app.get("/api/download/{run_id}")
async def download_pdf(run_id: str):
    if not all(c in "0123456789abcdef-" for c in run_id):
        raise HTTPException(status_code=400, detail="Invalid run ID.")
    pdf_path = settings.REPORTS_DIR / f"{run_id}.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Report not found. The pipeline may still be running.")
    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=f"scouting_report_{run_id[:8]}.pdf",
    )


@app.get("/api/prompt/{agent_name}")
async def get_agent_prompt(agent_name: str):
    try:
        content = PromptLoader.get(agent_name, use_cache=False)
        return {"agent": agent_name, "prompt": content}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"No prompt found for agent: {agent_name}")
