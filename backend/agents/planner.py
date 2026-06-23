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


# ── OpenAI Tool Schemas ───────────────────────────────────────────────────────
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_financial_agent",
            "description": "Analyze the club's financial plan and determine salary thresholds for scouting. Call this first when scouting players.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The original scouting query"},
                    "position": {"type": "string", "description": "Target player position (e.g. ST, CM, CB)"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_scouter_agent",
            "description": "Query the player database via MCP to find 3-5 matching candidates. Requires financial_decision from financial agent.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The scouting query"},
                    "financial_decision": {"type": "object", "description": "Output from run_financial_agent"},
                },
                "required": ["query", "financial_decision"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_analysis_agent",
            "description": "Perform deep statistical analysis and generate 6 visualizations for candidate players.",
            "parameters": {
                "type": "object",
                "properties": {
                    "players": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "List of player dicts from scouter agent",
                    },
                    "run_id": {"type": "string", "description": "Unique run ID for chart output"},
                },
                "required": ["players", "run_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_tactical_agent",
            "description": "Evaluate players against team tactics PDF and rank them by tactical fit.",
            "parameters": {
                "type": "object",
                "properties": {
                    "players": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "List of player dicts",
                    },
                    "analysis_report": {"type": "string", "description": "Unified analysis report from analysis agent"},
                    "financial_decision": {"type": "object", "description": "Financial constraints"},
                },
                "required": ["players", "analysis_report", "financial_decision"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_pdf_report",
            "description": "Generate the final PDF scouting report with all data, charts, and narratives.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "ranked_players": {"type": "array", "items": {"type": "object"}},
                    "financial_decision": {"type": "object"},
                    "tactical_summary": {"type": "string"},
                    "charts": {"type": "array", "items": {"type": "string"}},
                    "unified_analysis": {"type": "string"},
                    "run_id": {"type": "string"},
                },
                "required": ["query", "ranked_players", "run_id"],
            },
        },
    },
]


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

    # ── Tool Dispatcher ───────────────────────────────────────────────────────

    async def _dispatch_tool(self, tool_name: str, args: dict) -> Any:
        """Route a tool call from GPT-4o to the correct agent."""

        if tool_name == "run_financial_agent":
            return await self.financial.run(**args)

        elif tool_name == "run_scouter_agent":
            return await self.scouter.run(**args)

        elif tool_name == "run_analysis_agent":
            return await self.analysis.run(run_id=self.run_id, **args)

        elif tool_name == "run_tactical_agent":
            return await self.tactical.run(**args)

        elif tool_name == "generate_pdf_report":
            return await self.pdf_gen.generate(run_id=self.run_id, **args)

        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    # ── Main Orchestration Loop ───────────────────────────────────────────────

    async def run(self, query: str, **kwargs) -> dict[str, Any]:
        """
        Run the full agentic pipeline for a scouting query.

        Args:
            query: Natural language scouting request.

        Returns:
            {"pdf_path": str, "summary": str, "ranked_players": list}
        """
        await self.emit_start(f"Planner received query: '{query}'")
        await self.emit_progress("Analysing query and planning agent pipeline...")

        messages: list[dict] = [
            {
                "role": "user",
                "content": (
                    f"Scouting request: {query}\n\n"
                    f"Run ID: {self.run_id}\n\n"
                    "Execute the appropriate agent pipeline to fulfill this request. "
                    "Start with the financial agent, then scouter, analysis, tactical, and finally generate the PDF report. "
                    "Pass outputs from each agent as inputs to the next."
                ),
            }
        ]

        # ── Agentic Loop: keep calling tools until GPT-4o stops ──────────
        pipeline_state: dict[str, Any] = {}
        max_iterations = 10

        for iteration in range(max_iterations):
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "system", "content": self.system_prompt}, *messages],
                tools=TOOLS,
                tool_choice="auto",
                temperature=0.2,
            )

            choice = response.choices[0]
            msg = choice.message

            # Append assistant message
            messages.append({"role": "assistant", "content": msg.content or "", "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in (msg.tool_calls or [])
            ] if msg.tool_calls else []})

            # If no tool calls → LLM is done
            if not msg.tool_calls:
                await self.emit_progress("Planner completed orchestration", {"summary": msg.content})
                break

            # Execute each requested tool call
            for tool_call in msg.tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)

                await self.emit_progress(f"Delegating to: {fn_name}", fn_args)

                try:
                    result = await self._dispatch_tool(fn_name, fn_args)
                except Exception as exc:
                    result = {"error": str(exc)}
                    await self.emit_error(f"Tool {fn_name} failed", str(exc))

                # Store results for final output
                pipeline_state[fn_name] = result

                # Feed tool result back to the conversation
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, default=str)[:8000],  # Truncate for context
                })

        # ── Extract final outputs ─────────────────────────────────────────
        pdf_result = pipeline_state.get("generate_pdf_report", {})
        scouter_result = pipeline_state.get("run_scouter_agent", {})
        tactical_result = pipeline_state.get("run_tactical_agent", {})

        final = {
            "run_id": self.run_id,
            "pdf_path": pdf_result.get("pdf_path", ""),
            "summary": messages[-1].get("content", "") if messages else "",
            "ranked_players": tactical_result.get("ranked_players", scouter_result.get("players", [])),
        }

        await self.emit_complete("Pipeline complete — PDF report ready!", final)
        return final
