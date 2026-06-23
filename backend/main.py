"""
FastAPI Backend — main application entry point.

Endpoints:
  GET  /                     → Serve frontend HTML
  GET  /static/*             → Serve CSS/JS
  POST /api/scout            → Start a scouting pipeline (SSE stream)
  GET  /api/download/{run_id} → Download the generated PDF
  GET  /api/health           → Health check
  GET  /api/agents           → List available agents & their prompts
"""
import asyncio
import json
import uuid
from pathlib import Path

import aiofiles
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from openai import AsyncAzureOpenAI

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

# Mount frontend static files
_frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if _frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(_frontend_dir)), name="static")


# ── OpenAI Client (shared) ────────────────────────────────────────────────────
def get_openai_client() -> AsyncAzureOpenAI:
    return make_azure_client()


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
    """Return all available agents and their system prompt summaries."""
    manifest = PromptLoader.manifest()
    agents = []
    for name, description in manifest.items():
        agents.append({
            "name": name,
            "description": description,
            "prompt_file": f"prompts/{name}.md",
        })
    return {"agents": agents}


@app.post("/api/scout")
async def scout_players(request: Request):
    """
    Start a full agentic scouting pipeline.
    Streams real-time SSE events as agents run.

    Body: {"query": "Find me a striker under £60K/week who scores 15+ goals"}
    """
    body = await request.json()
    query: str = body.get("query", "").strip()

    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    run_id = str(uuid.uuid4())
    client = get_openai_client()

    async def event_stream():
        queue: asyncio.Queue = asyncio.Queue()

        # Emit initial connection event
        yield f"data: {json.dumps({'type': 'connected', 'run_id': run_id, 'query': query})}\n\n"

        # Start the pipeline in a background task
        async def run_pipeline():
            try:
                planner = PlannerAgent(client=client, sse_queue=queue, run_id=run_id)
                result = await planner.run(query=query)
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
                await queue.put(None)  # Sentinel → close stream

        task = asyncio.create_task(run_pipeline())

        # Stream events from queue
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
    """Download the generated PDF scouting report for a given run ID."""
    # Sanitize run_id
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
    """Return the raw system prompt for a given agent (for debugging/inspection)."""
    try:
        content = PromptLoader.get(agent_name, use_cache=False)
        return {"agent": agent_name, "prompt": content}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"No prompt found for agent: {agent_name}")
