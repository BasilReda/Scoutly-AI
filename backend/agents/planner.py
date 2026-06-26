"""
Planner Agent — top-level orchestrator that coordinates all sub-agents.

Human-in-the-Loop (HITL) is implemented using LangGraph's native interrupt()
mechanism (part of the deepagents framework). After each sub-agent runs, the
graph pauses via interrupt(), the outer astream loop emits an SSE event, and
resumes with Command(resume=user_decision) when the user responds.

Adjustment loop: if the user sends action="adjust" with a comment, the tool
re-runs the sub-agent with the adjusted query and calls interrupt() again to
show the updated output. This repeats until action="proceed" or "stop".
"""
import asyncio
import json
from typing import Any

from openai import AsyncAzureOpenAI
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver

from .base import BaseAgent
from .financial import FinancialAgent
from .scouter import ScouterAgent
from .verifier import VerifierAgent
from .analysis import AnalysisAgent
from .tactical import TacticalAgent
from .email_agent import EmailAgent
from ..pdf.generator import PDFGenerator
from ..utils.prompt_loader import PromptLoader


class PlannerAgent(BaseAgent):
    AGENT_NAME = "planner"

    def __init__(
        self,
        client: AsyncAzureOpenAI,
        sse_queue: asyncio.Queue,
        run_id: str,
        hitl_queues: dict | None = None,
        player_selection_queues: dict | None = None,
        email_bodies: dict | None = None,
    ):
        super().__init__(client, sse_queue)
        self.run_id = run_id

        # Coordination state bridges: HTTP endpoints put values here; the
        # outer astream loop reads them and resumes the graph via Command(resume=…)
        self._hitl_queues = hitl_queues or {}
        self._player_selection_queues = player_selection_queues or {}
        self._email_bodies = email_bodies or {}

        self._stopped = False

        self.financial = FinancialAgent(client, sse_queue)
        self.scouter = ScouterAgent(client, sse_queue)
        self.verifier = VerifierAgent(client, sse_queue)
        self.analysis = AnalysisAgent(client, sse_queue)
        self.tactical = TacticalAgent(client, sse_queue)
        self.email = EmailAgent(client, sse_queue)
        self.pdf_gen = PDFGenerator(sse_queue)

    @property
    def system_prompt(self) -> str:
        base_prompt = PromptLoader.get("planner", use_cache=False)
        manifest = PromptLoader.manifest()
        manifest_text = "\n".join(
            f"- **{name}**: {desc}" for name, desc in manifest.items()
        )
        return base_prompt + f"\n\n## Available Agent Prompts (runtime)\n{manifest_text}"

    async def run(self, query: str, **kwargs) -> dict[str, Any]:
        await self.emit_start(f"Planner received query: '{query}'")
        await self.emit_progress("Analysing query and planning agent pipeline...")

        from langchain_core.tools import tool
        from deepagents import create_deep_agent
        from ..utils.config import get_langchain_azure_llm

        pipeline_state: dict = {}
        planner = self  # captured by tool closures

        # ── Tool: Financial Agent ──────────────────────────────────────────────

        @tool
        async def run_financial_agent(query: str, position: str = None) -> dict:
            """Analyze the club financial plan and determine salary thresholds. Call FIRST when scouting."""
            if planner._stopped:
                return {"stopped": True}

            # Restore effective query from state (idempotency across re-executions)
            effective_query = pipeline_state.get("_fin_eff_query", query)
            cache = pipeline_state.get("_fin_cache", {})

            if cache.get("q") != effective_query or cache.get("pos") != position:
                res = await planner.financial.run(query=effective_query, position=position)
                pipeline_state["financial"] = res
                pipeline_state["_fin_cache"] = {"q": effective_query, "pos": position}
                pipeline_state["_fin_eff_query"] = effective_query
            else:
                res = pipeline_state["financial"]

            while True:
                # interrupt() pauses the graph; outer astream loop emits SSE and waits for user
                user_decision = interrupt({
                    "agent": "financial",
                    "action_type": "decision",
                    "emit_data": {
                        "salary_min": res.get("salary_min"),
                        "salary_max": res.get("salary_max"),
                        "value_max": res.get("value_max"),
                        "team_name": res.get("team_name"),
                        "financial_notes": str(res.get("financial_notes", ""))[:300],
                    },
                })

                action = user_decision.get("action", "stop") if isinstance(user_decision, dict) else "stop"
                comment = user_decision.get("comment", "") if isinstance(user_decision, dict) else ""

                if action == "stop":
                    planner._stopped = True
                    return {**res, "stopped": True}
                if action == "proceed":
                    break
                if action == "adjust":
                    prev = pipeline_state.get("financial", {})
                    adj_q = (
                        f"{effective_query}\n\n"
                        f"Current values: salary_min={prev.get('salary_min')}, "
                        f"salary_max={prev.get('salary_max')}, value_max={prev.get('value_max')}\n\n"
                        f"User adjustment: {comment}"
                    )
                    adj_cache = {"q": adj_q, "pos": position}
                    if pipeline_state.get("_fin_cache") != adj_cache:
                        res = await planner.financial.run(query=adj_q, position=position)
                        pipeline_state["financial"] = res
                        pipeline_state["_fin_cache"] = adj_cache
                        pipeline_state["_fin_eff_query"] = adj_q
                        effective_query = adj_q
            return res

        # ── Tool: Scouter Agent ────────────────────────────────────────────────

        @tool
        async def run_scouter_agent(query: str, financial_decision: dict) -> dict:
            """Query the player database via MCP to find 3-5 matching candidates. Requires financial_decision."""
            if planner._stopped:
                return {"stopped": True, "players": []}

            effective_query = pipeline_state.get("_scout_eff_query", query)
            cache = pipeline_state.get("_scout_cache", {})

            if cache.get("q") != effective_query:
                res = await planner.scouter.run(query=effective_query, financial_decision=financial_decision)
                pipeline_state["scouter"] = res
                pipeline_state["_scout_cache"] = {"q": effective_query}
                pipeline_state["_scout_eff_query"] = effective_query
            else:
                res = pipeline_state["scouter"]

            players = res.get("players", [])

            # ── Verification loop (automatic, no HITL) ────────────────────────
            _MAX_VERIFY = 3
            for _attempt in range(_MAX_VERIFY):
                ver = await planner.verifier.run(players=players)
                pipeline_state["verifier"] = ver
                if ver["all_valid"]:
                    break
                if _attempt < _MAX_VERIFY - 1 and ver["invalid"]:
                    _feedback_q = (
                        f"{effective_query}\n\n"
                        f"VERIFICATION FAILED — the following names do NOT exist on FBref "
                        f"and must not be returned: {ver['invalid']}\n\n"
                        f"{ver['feedback']}\n\n"
                        f"Re-query the database and return only real, verified players."
                    )
                    res = await planner.scouter.run(query=_feedback_q, financial_decision=financial_decision)
                    pipeline_state["scouter"] = res
                    pipeline_state["_scout_cache"] = {"q": _feedback_q}
                    pipeline_state["_scout_eff_query"] = _feedback_q
                    effective_query = _feedback_q
                    players = res.get("players", [])

            return res

        # ── Tool: Analysis Agent ───────────────────────────────────────────────

        @tool
        async def run_analysis_agent(players: list[dict]) -> dict:
            """Perform deep statistical analysis and generate visualizations for candidate players."""
            if planner._stopped:
                return {"stopped": True, "charts": [], "unified_report": "Pipeline stopped."}
            if not players:
                return {"unified_report": "No players to analyze — requirements not met."}

            extra = pipeline_state.get("_analysis_extra", "")
            cache = pipeline_state.get("_analysis_cache", {})

            if cache.get("count") != len(players) or cache.get("extra") != extra:
                res = await planner.analysis.run(
                    players=players, run_id=planner.run_id, extra_context=extra
                )
                pipeline_state["analysis"] = res
                pipeline_state["_analysis_cache"] = {"count": len(players), "extra": extra}
            else:
                res = pipeline_state["analysis"]

            return res

        # ── Tool: Tactical Agent ───────────────────────────────────────────────

        @tool
        async def run_tactical_agent(players: list[dict], analysis_report: str, financial_decision: dict) -> dict:
            """Evaluate players against team tactics PDF, rank by fit, then let user select one player."""
            if planner._stopped:
                return {"stopped": True, "ranked_players": []}
            if not players:
                return {"ranked_players": [], "tactical_summary": "No players to evaluate."}

            effective_report = pipeline_state.get("_tact_eff_report", analysis_report)
            cache = pipeline_state.get("_tact_cache", {})

            if cache.get("rlen") != len(effective_report) or cache.get("count") != len(players):
                res = await planner.tactical.run(
                    players=players, analysis_report=effective_report, financial_decision=financial_decision
                )
                pipeline_state["tactical"] = res
                pipeline_state["_tact_cache"] = {"rlen": len(effective_report), "count": len(players)}
                pipeline_state["_tact_eff_report"] = effective_report
            else:
                res = pipeline_state["tactical"]

            ranked = res.get("ranked_players", [])

            # Player selection interrupt — user picks from ranked cards
            top_3 = ranked[:3]
            card_data = [
                {
                    "name": p.get("name", ""),
                    "position": p.get("position", ""),
                    "age": p.get("age", ""),
                    "club": p.get("club", ""),
                    "wage_eur": p.get("wage_eur", 0),
                    "overall_rating": p.get("overall_rating", 0),
                    "tactical_fit_score": p.get("tactical_fit_score", 0),
                    "rank": p.get("rank", idx + 1),
                    "strengths": p.get("strengths", [])[:2],
                    "tactical_verdict": p.get("tactical_verdict", ""),
                }
                for idx, p in enumerate(top_3)
            ]

            selected_name = interrupt({
                "agent": "tactical",
                "action_type": "player_selection",
                "emit_data": {"players": card_data},
            })

            pipeline_state["selected_player"] = selected_name
            await planner.emit_progress(f"Player selected for recruitment: {selected_name}")
            return {**res, "selected_player": selected_name}

        # ── Tool: Email Agent ──────────────────────────────────────────────────

        @tool
        async def run_email_agent(player_name: str) -> dict:
            """Generate a recruitment email, show to user, allow adjustment or send."""
            if planner._stopped:
                return {"stopped": True, "sent": False}

            ranked = pipeline_state.get("tactical", {}).get("ranked_players", [])
            player_data = next((p for p in ranked if p.get("name") == player_name), {})
            financial_decision = pipeline_state.get("financial", {})

            previous_draft = ""

            while True:
                extra = ""
                if previous_draft and pipeline_state.get("_email_adj"):
                    extra = (
                        f"Previous draft for reference:\n{previous_draft}\n\n"
                        f"User requested this adjustment: {pipeline_state['_email_adj']}\n"
                        f"Revise the email incorporating this feedback. Keep the salary unchanged."
                    )

                res = await planner.email.run(
                    player_name=player_name,
                    player_data=player_data,
                    financial_decision=financial_decision,
                    run_id=planner.run_id,
                    extra_context=extra,
                )
                previous_draft = res["draft"]

                user_decision = interrupt({
                    "agent": "email",
                    "action_type": "email_decision",
                    "emit_data": {
                        "draft": res["draft"],
                        "subject": res["subject"],
                        "to": res["to"],
                        "from": res["from"],
                        "player_name": player_name,
                    },
                })

                action = user_decision.get("action", "send") if isinstance(user_decision, dict) else "send"
                comment = user_decision.get("comment", "") if isinstance(user_decision, dict) else ""

                if action == "stop":
                    planner._stopped = True
                    return {**res, "sent": False, "stopped": True}
                elif action == "adjust" and comment:
                    pipeline_state["_email_adj"] = comment
                    continue
                else:  # "send"
                    final_body = planner._email_bodies.get(planner.run_id, res["draft"])
                    sent = await planner.email.send(to=res["to"], subject=res["subject"], body=final_body)
                    result = {**res, "final_body": final_body, "sent": sent}
                    pipeline_state["email"] = result
                    return result

        # ── Tool: PDF Report ───────────────────────────────────────────────────

        @tool
        async def generate_pdf_report(
            query: str = "",
            ranked_players: list[dict] = None,
            financial_decision: dict = None,
            tactical_summary: str = "",
            charts: list[str] = None,
            unified_analysis: str = "",
            unified_report: str = "",
        ) -> dict:
            """Generate the final PDF scouting report with all data, charts, and narratives."""
            if planner._stopped:
                return {"stopped": True, "pdf_path": "", "filename": ""}
            res = await planner.pdf_gen.generate(
                run_id=planner.run_id,
                query=query,
                ranked_players=ranked_players or [],
                financial_decision=financial_decision or {},
                tactical_summary=tactical_summary,
                charts=charts or [],
                unified_analysis=unified_analysis or unified_report,
            )
            pipeline_state["pdf"] = res
            return res

        # ── Build Deep Agent with LangGraph checkpointer ──────────────────────

        llm = get_langchain_azure_llm()
        checkpointer = MemorySaver()  # Required for interrupt() support
        agent = create_deep_agent(
            model=llm,
            tools=[
                run_financial_agent,
                run_scouter_agent,
                run_analysis_agent,
                run_tactical_agent,
                run_email_agent,
                generate_pdf_report,
            ],
            system_prompt=self.system_prompt,
            checkpointer=checkpointer,
        )

        config = {"configurable": {"thread_id": self.run_id}}
        task_prompt = (
            f"Scouting request: {query}\n\n"
            f"Run ID: {self.run_id}\n\n"
            "Execute the agent pipeline for this request per your Decision Logic.\n"
            "After run_tactical_agent completes (its result includes selected_player), "
            "call run_email_agent(player_name=<selected_player>) BEFORE generate_pdf_report.\n"
            "If any tool returns {\"stopped\": true}, stop immediately — do NOT call generate_pdf_report.\n"
            "Always end with generate_pdf_report unless the pipeline was stopped.\n"
        )

        current_input: dict | Command = {"messages": task_prompt}
        final_summary = ""

        # ── Astream loop: handles interrupts and normal events ─────────────────

        try:
            while True:
                pending_interrupt = None

                async for event in agent.astream(current_input, config=config, stream_mode="updates"):
                    if not isinstance(event, dict):
                        continue

                    # LangGraph interrupt — graph is paused, needs human input
                    if "__interrupt__" in event:
                        interrupt_list = event["__interrupt__"]
                        if interrupt_list:
                            pending_interrupt = interrupt_list[0].value
                        break

                    # Normal event processing
                    for node, state in event.items():
                        if not isinstance(state, dict):
                            continue
                        for msg in (state.get("messages") or []):
                            if msg is None:
                                continue
                            kind = type(msg).__name__
                            content = getattr(msg, "content", "") or ""
                            tool_calls = getattr(msg, "tool_calls", []) or []

                            if tool_calls:
                                for tc in tool_calls:
                                    if not isinstance(tc, dict):
                                        continue
                                    name = tc.get("name", "")
                                    args = tc.get("args", {})
                                    formatted = ", ".join(f"{k}={v}" for k, v in args.items())
                                    await self.emit_progress(f"Delegating to: {name}({formatted})")
                            elif kind == "ToolMessage":
                                tool_name = getattr(msg, "name", "tool")
                                content_str = str(content)
                                try:
                                    parsed = json.loads(content_str)
                                    if isinstance(parsed, list):
                                        preview = f"Returned {len(parsed)} items."
                                        if parsed and isinstance(parsed[0], dict) and "name" in parsed[0]:
                                            names = [p.get("name", "Unknown") for p in parsed[:3]]
                                            preview += f" Top: {', '.join(names)}"
                                    elif isinstance(parsed, dict):
                                        if "players" in parsed:
                                            preview = f"Returned {len(parsed['players'])} players."
                                        elif "ranked_players" in parsed:
                                            preview = f"Ranked {len(parsed['ranked_players'])} players."
                                        else:
                                            preview = f"Returned keys: {', '.join(parsed.keys())}"
                                    else:
                                        preview = str(parsed)[:100]
                                except Exception:
                                    preview = content_str[:100] + ("..." if len(content_str) > 100 else "")
                                await self.emit_progress(f"Tool finished [{tool_name}]: {preview}")
                            elif kind == "AIMessage" and content and isinstance(content, str):
                                final_summary = content
                                if len(content) > 50:
                                    await self.emit_progress(f"Planner: {content[:150]}...")

                # Graph completed without interrupt → done
                if pending_interrupt is None:
                    break

                # Handle the interrupt
                action_type = pending_interrupt.get("action_type", "decision")
                agent_name = pending_interrupt.get("agent", "agent")
                emit_data = pending_interrupt.get("emit_data", {})

                if action_type == "player_selection":
                    # Emit player card SSE, wait for user to click a card
                    await self.emit({
                        "type": "player_selection_required",
                        "agent": "tactical",
                        "message": "Select a player to send a recruitment offer",
                        "data": emit_data,
                        "run_id": self.run_id,
                    })

                    sel_queue = self._player_selection_queues.get(self.run_id)
                    if sel_queue:
                        while not sel_queue.empty():
                            try:
                                sel_queue.get_nowait()
                            except asyncio.QueueEmpty:
                                break
                        try:
                            selected = await asyncio.wait_for(sel_queue.get(), timeout=300.0)
                        except asyncio.TimeoutError:
                            players_list = emit_data.get("players", [])
                            selected = players_list[0]["name"] if players_list else ""
                            await self.emit_progress("Player selection timed out — defaulting to rank-1")
                    else:
                        players_list = emit_data.get("players", [])
                        selected = players_list[0]["name"] if players_list else ""

                    current_input = Command(resume=selected)

                elif action_type == "email_decision":
                    # Emit email draft SSE, wait for send or adjustment
                    await self.emit({
                        "type": "email_draft_ready",
                        "agent": "email",
                        "message": "Recruitment email draft ready — send or request adjustments",
                        "data": emit_data,
                        "run_id": self.run_id,
                    })

                    hitl_queue = self._hitl_queues.get(self.run_id)
                    user_input = {"action": "send", "comment": ""}

                    if hitl_queue:
                        while not hitl_queue.empty():
                            try:
                                hitl_queue.get_nowait()
                            except asyncio.QueueEmpty:
                                break
                        try:
                            user_input = await asyncio.wait_for(hitl_queue.get(), timeout=600.0)
                        except asyncio.TimeoutError:
                            await self.emit_progress("Email confirmation timed out — sending as-is.")

                    current_input = Command(resume=user_input)

                else:  # HITL decision (financial only)
                    await self.emit({
                        "type": "human_decision_required",
                        "agent": agent_name,
                        "message": f"{agent_name.title()} agent output — review and decide",
                        "data": emit_data,
                        "run_id": self.run_id,
                    })

                    hitl_queue = self._hitl_queues.get(self.run_id)
                    user_input = {"action": "proceed", "comment": ""}

                    if hitl_queue:
                        while not hitl_queue.empty():
                            try:
                                hitl_queue.get_nowait()
                            except asyncio.QueueEmpty:
                                break
                        try:
                            user_input = await asyncio.wait_for(hitl_queue.get(), timeout=300.0)
                        except asyncio.TimeoutError:
                            user_input = {"action": "stop", "comment": ""}
                            self._stopped = True
                            await self.emit({
                                "type": "pipeline_stopped",
                                "agent": agent_name,
                                "message": "Auto-stopped: no response within 5 minutes.",
                                "run_id": self.run_id,
                            })

                    action = user_input.get("action", "stop")
                    if action == "stop" and not self._stopped:
                        self._stopped = True
                        await self.emit({
                            "type": "pipeline_stopped",
                            "agent": agent_name,
                            "message": "Pipeline stopped by user.",
                            "run_id": self.run_id,
                        })

                    current_input = Command(resume=user_input)

        except Exception as exc:
            await self.emit_error("Planner error", str(exc))
            raise

        # ── Collect final results ──────────────────────────────────────────────

        tactical_res = pipeline_state.get("tactical", {})
        scouter_res = pipeline_state.get("scouter", {})
        pdf_res = pipeline_state.get("pdf", {})

        final = {
            "run_id": self.run_id,
            "pdf_path": pdf_res.get("pdf_path", ""),
            "summary": final_summary,
            "ranked_players": tactical_res.get("ranked_players", scouter_res.get("players", [])),
            "stopped": self._stopped,
        }

        if self._stopped:
            await self.emit_complete("Pipeline was stopped by user — partial results available.")
        else:
            await self.emit_complete("Pipeline complete — PDF report ready!")

        return final
