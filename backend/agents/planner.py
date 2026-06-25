"""
Planner Agent — top-level orchestrator that coordinates all sub-agents.

The Planner:
1. Reads its system prompt from prompts/planner.md (dynamically built with agent manifest)
2. Uses OpenAI function calling to decide which agents to invoke
3. Executes the chosen agents in the correct order
4. Triggers PDF report generation
5. Returns the final pipeline result
"""
import asyncio
import json
from typing import Any

from openai import AsyncAzureOpenAI

from .base import BaseAgent
from .financial import FinancialAgent
from .scouter import ScouterAgent
from .analysis import AnalysisAgent
from .tactical import TacticalAgent
from ..pdf.generator import PDFGenerator
from ..utils.prompt_loader import PromptLoader
from ..utils.config import settings


class PlannerAgent(BaseAgent):
    AGENT_NAME = "planner"

    def __init__(self, client: AsyncAzureOpenAI, sse_queue: asyncio.Queue, run_id: str):
        super().__init__(client, sse_queue)
        self.run_id = run_id

        # Instantiate all sub-agents (they share the same SSE queue)
        self.financial = FinancialAgent(client, sse_queue)
        self.scouter = ScouterAgent(client, sse_queue)
        self.analysis = AnalysisAgent(client, sse_queue)
        self.tactical = TacticalAgent(client, sse_queue)
        self.pdf_gen = PDFGenerator(sse_queue)

    @property
    def system_prompt(self) -> str:
        """
        Build the Planner's system prompt dynamically by injecting the agent manifest
        (list of available .md prompt files) into the base planner.md content.
        """
        base_prompt = PromptLoader.get("planner", use_cache=False)
        manifest = PromptLoader.manifest()
        manifest_text = "\n".join(
            f"- **{name}**: {desc}" for name, desc in manifest.items()
        )
        return (
            base_prompt
            + f"\n\n## Currently Available Agent Prompts (loaded at runtime)\n{manifest_text}"
        )

    # ── DeepAgents Implementation ────────────────────────────────────────────────

    async def run(self, query: str, **kwargs) -> dict[str, Any]:
        """
        Run the full agentic pipeline for a scouting query using a deep agent.
        """
        await self.emit_start(f"Planner received query: '{query}'")
        await self.emit_progress("Analysing query and planning agent pipeline...")

        from langchain_core.tools import tool
        from deepagents import create_deep_agent
        from ..utils.config import get_langchain_azure_llm

        pipeline_state = {}

        @tool
        async def run_financial_agent(query: str, position: str = None) -> dict:
            """Analyze the club's financial plan and determine salary thresholds for scouting. Call this first when scouting players."""
            res = await self.financial.run(query=query, position=position)
            pipeline_state["financial"] = res
            return res

        @tool
        async def run_scouter_agent(query: str, financial_decision: dict) -> dict:
            """Query the player database via MCP to find 3-5 matching candidates. Requires financial_decision."""
            res = await self.scouter.run(query=query, financial_decision=financial_decision)
            pipeline_state["scouter"] = res
            return res

        @tool
        async def run_analysis_agent(players: list[dict]) -> dict:
            """Perform deep statistical analysis and generate 6 visualizations for candidate players."""
            res = await self.analysis.run(players=players, run_id=self.run_id)
            pipeline_state["analysis"] = res
            return res

        @tool
        async def run_tactical_agent(players: list[dict], analysis_report: str, financial_decision: dict) -> dict:
            """Evaluate players against team tactics PDF and rank them by tactical fit."""
            res = await self.tactical.run(
                players=players, analysis_report=analysis_report, financial_decision=financial_decision
            )
            pipeline_state["tactical"] = res
            return res

        @tool
        async def generate_pdf_report(
            query: str = "", 
            ranked_players: list[dict] = None, 
            financial_decision: dict = None, 
            tactical_summary: str = "", 
            charts: list[str] = None, 
            unified_analysis: str = "",
            unified_report: str = ""
        ) -> dict:
            """Generate the final PDF scouting report with all data, charts, and narratives."""
            res = await self.pdf_gen.generate(
                run_id=self.run_id,
                query=query,
                ranked_players=ranked_players or [],
                financial_decision=financial_decision or {},
                tactical_summary=tactical_summary,
                charts=charts or [],
                unified_analysis=unified_analysis or unified_report
            )
            pipeline_state["pdf"] = res
            return res

        llm = get_langchain_azure_llm()
        agent = create_deep_agent(
            model=llm,
            tools=[run_financial_agent, run_scouter_agent, run_analysis_agent, run_tactical_agent, generate_pdf_report],
            instructions=self.system_prompt,
        )

        task_prompt = (
            f"Scouting request: {query}\n\n"
            f"Run ID: {self.run_id}\n\n"
            "Execute the appropriate agent pipeline to fulfill this request based on your Decision Logic. "
            "You do NOT need to run every agent if the user already provided the required information. "
            "If you skip an agent (e.g. financial_agent because the user gave a budget), you MUST manually construct its expected output JSON to pass into the subsequent agents. "
            "Always end with the generate_pdf_report tool once you have gathered everything.\n"
        )

        final_summary = ""
        try:
            async for event in agent.astream({"messages": task_prompt}, stream_mode="updates"):
                if not isinstance(event, dict): continue
                for node, state in event.items():
                    if not isinstance(state, dict): continue
                    for msg in (state.get("messages") or []):
                        if msg is None: continue
                        kind = type(msg).__name__
                        content = getattr(msg, "content", "") or ""
                        tool_calls = getattr(msg, "tool_calls", []) or []

                        if tool_calls:
                            for tc in tool_calls:
                                if not isinstance(tc, dict): continue
                                name = tc.get("name", "")
                                args = tc.get("args", {})
                                formatted_args = ", ".join(f"{k}={v}" for k, v in args.items())
                                await self.emit_progress(f"Delegating to: {name}({formatted_args})")
                        elif kind == "ToolMessage":
                            tool_name = getattr(msg, "name", "tool")
                            content_str = str(content)
                            try:
                                parsed = json.loads(content_str)
                                if isinstance(parsed, list):
                                    preview = f"Returned {len(parsed)} items."
                                    if parsed and isinstance(parsed[0], dict) and "name" in parsed[0]:
                                        names = [p.get('name', 'Unknown') for p in parsed[:3]]
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
                                preview = content_str[:100] + "..." if len(content_str) > 100 else content_str
                            await self.emit_progress(f"Tool finished [{tool_name}]: {preview}")
                        elif kind == "AIMessage" and content and isinstance(content, str):
                            if len(content) > 50:
                                final_summary = content
                                await self.emit_progress(f"Planner Reasoning: {content[:150]}...")
        except Exception as exc:
            await self.emit_error("Planner Deep agent error", str(exc))
            raise

        tactical_res = pipeline_state.get("tactical", {})
        scouter_res = pipeline_state.get("scouter", {})
        pdf_res = pipeline_state.get("pdf", {})

        final = {
            "run_id": self.run_id,
            "pdf_path": pdf_res.get("pdf_path", ""),
            "summary": final_summary,
            "ranked_players": tactical_res.get("ranked_players", scouter_res.get("players", [])),
        }

        await self.emit_complete("Pipeline complete — PDF report ready!")
        return final
