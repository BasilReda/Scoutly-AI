"""Scouter Agent — queries player database via MCP server."""
import asyncio
import json
from typing import Any

from openai import AsyncOpenAI
from mcp import ClientSession
from mcp.client.sse import sse_client

from .base import BaseAgent
from ..utils.config import settings


class ScouterAgent(BaseAgent):
    AGENT_NAME = "scouter"

    def __init__(self, client: AsyncOpenAI, sse_queue: asyncio.Queue):
        super().__init__(client, sse_queue)

    # ── MCP Communication ─────────────────────────────────────────────────────

    async def _call_mcp_tool(self, tool_name: str, params: dict) -> Any:
        """Connect to the MCP server and call a single tool."""
        mcp_url = settings.MCP_SERVER_URL
        async with sse_client(mcp_url) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, params)
                # result.content is a list of TextContent objects
                if result.content:
                    raw = result.content[0].text
                    try:
                        return json.loads(raw)
                    except (json.JSONDecodeError, TypeError):
                        return raw
                return None

    # ── Main Run ──────────────────────────────────────────────────────────────

    async def run(
        self,
        query: str,
        financial_decision: dict,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Scout players from the database using MCP tools.

        Args:
            query:              Original scouting query.
            financial_decision: Output from FinancialAgent (salary thresholds).

        Returns:
            {"players": [list of 3–5 player dicts with scout_note added]}
        """
        await self.emit_start("Connecting to player database via MCP server...")

        salary_max = financial_decision.get("salary_max", 100_000)
        salary_min = financial_decision.get("salary_min", 0)
        value_max = financial_decision.get("value_max", 100_000_000)

        # Step 1 — Let the LLM parse the query and decide search parameters
        await self.emit_progress("Parsing scouting query to extract search filters...")

        search_params_raw = await self.chat_json(
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Scouting query: {query}\n"
                        f"Financial constraints: salary_min={salary_min}, salary_max={salary_max}, value_max={value_max}\n\n"
                        "Extract structured search parameters from this query. "
                        "Return a JSON object with these optional keys: "
                        "position (str, e.g. ST/CM/CB/LW/RW/CAM/CDM/LB/RB/GK), "
                        "max_age (int), min_age (int), nationality (str), "
                        "min_goals (float), min_rating (int, default 78), limit (int, default 10). "
                        "Always include salary constraints from the financial data."
                    ),
                }
            ]
        )

        search_params = {
            "max_wage": salary_max,
            "min_wage": salary_min,
            "limit": 15,
            **{k: v for k, v in search_params_raw.items() if v is not None},
        }

        # Step 2 — Query via MCP
        await self.emit_progress(f"Querying database with filters: {search_params}")
        try:
            raw_players: list[dict] = await self._call_mcp_tool("search_players", search_params)
        except Exception as exc:
            await self.emit_error("MCP query failed", str(exc))
            raise

        if not raw_players:
            # Fallback: relax salary by 15% and remove rating filter
            await self.emit_progress("No results found — relaxing filters and retrying...")
            search_params["max_wage"] = int(salary_max * 1.15)
            search_params.pop("min_rating", None)
            raw_players = await self._call_mcp_tool("search_players", search_params) or []

        await self.emit_progress(f"Database returned {len(raw_players)} candidates — shortlisting best 3–5...")

        # Step 3 — Let the LLM shortlist and add scout notes
        shortlist_result = await self.chat_json(
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Original scouting query: {query}\n"
                        f"Financial constraints: salary_max={salary_max}/week, value_max={value_max}\n\n"
                        f"Candidate players from database:\n"
                        f"{json.dumps(raw_players, indent=2)}\n\n"
                        "Shortlist the best 3 to 5 players that best match the query. "
                        "For each selected player, add a 'scout_note' field (1-2 sentences) "
                        "explaining why they match. Return JSON: "
                        '{"players": [<selected player dicts with scout_note added>]}'
                    ),
                }
            ]
        )

        players = shortlist_result.get("players", raw_players[:5])

        await self.emit_complete(
            f"Shortlisted {len(players)} candidate players",
            {"count": len(players), "names": [p.get("name") for p in players]},
        )
        return {"players": players}
