"""Scouter Agent — queries player database via MCP server."""
import asyncio
import json
from typing import Any

from openai import AsyncOpenAI

from .base import BaseAgent
from ..utils.prompt_loader import PromptLoader


class ScouterAgent(BaseAgent):
    AGENT_NAME = "scouter"

    def __init__(self, client: AsyncOpenAI, sse_queue: asyncio.Queue):
        super().__init__(client, sse_queue)

    # _call_mcp_tool inherited from BaseAgent

    # ── Main Run ──────────────────────────────────────────────────────────────

    async def run(
        self,
        query: str,
        financial_decision: dict,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Scout players from the database using MCP tools via Deep Agent.
        """
        await self.emit_start("Connecting to player database via MCP server...")

        salary_max = financial_decision.get("salary_max", 100_000)
        salary_min = financial_decision.get("salary_min", 0)
        value_max = financial_decision.get("value_max", 100_000_000)

        from langchain_core.tools import tool

        @tool
        async def query_player_database(
            min_wage: int = 0,
            max_wage: int = 100000,
            position: str = None,
            min_rating: int = None,
            max_value: int = None,
            limit: int = 15,
        ) -> list[dict]:
            """
            Search the postgres player database. 
            Returns a list of player dicts matching the criteria.
            If no results are found, you should call this again with relaxed constraints (e.g. higher max_wage, lower min_rating).
            """
            params = {
                "min_wage": min_wage,
                "max_wage": max_wage,
                "limit": limit
            }
            if position: params["position"] = position
            if min_rating: params["min_rating"] = min_rating
            if max_value: params["max_value"] = max_value
            
            try:
                res = await self._call_mcp_tool("search_players", params)
                return res or []
            except Exception as e:
                return [{"error": str(e)}]

        task_template = PromptLoader.get("scouter_task")
        task_prompt = task_template.format(
            query=query,
            salary_min=salary_min,
            salary_max=salary_max,
            value_max=value_max
        )

        response_text = await self._run_deep_agent(task_prompt, tools=[query_player_database])

        cleaned = response_text.replace("```json", "").replace("```", "").strip()
        result = None
        start, end = cleaned.find("{"), cleaned.rfind("}")
        for candidate in ([cleaned, cleaned[start:end + 1]] if start != -1 and end != -1 else [cleaned]):
            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, dict):
                    result = parsed
                    break
            except json.JSONDecodeError:
                continue
        if result is None:
            await self.emit_error("Failed to parse JSON from scouter agent.", cleaned[:300])
            raise ValueError("No valid JSON found in scouter agent response")
        players = result.get("players", [])

        await self.emit_complete(
            f"Shortlisted {len(players)} verified players from database"
        )
        return {"players": players}
