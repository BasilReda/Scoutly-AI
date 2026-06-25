"""Scouter Agent — queries player database via MCP server."""
import asyncio
import json
from typing import Any

from openai import AsyncOpenAI
from mcp import ClientSession
from mcp.client.sse import sse_client

from .base import BaseAgent
from ..utils.config import settings
from ..utils.prompt_loader import PromptLoader


class ScouterAgent(BaseAgent):
    AGENT_NAME = "scouter"

    def __init__(self, client: AsyncOpenAI, sse_queue: asyncio.Queue):
        super().__init__(client, sse_queue)

    # ── MCP Communication ─────────────────────────────────────────────────────

    async def _call_mcp_tool(self, tool_name: str, params: dict) -> Any:
        """Connect to the MCP server and call a single tool."""
        mcp_url = settings.MCP_SERVER_URL
        result_data: Any = None

        try:
            async with sse_client(mcp_url) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, params)
                    if result.content:
                        if len(result.content) == 1:
                            # Single-item result (dict, str, int, …)
                            raw = result.content[0].text
                            try:
                                result_data = json.loads(raw)
                            except (json.JSONDecodeError, TypeError):
                                try:
                                    import ast
                                    result_data = ast.literal_eval(raw)
                                except Exception:
                                    result_data = raw
                        else:
                            # mcp >= 1.10 serialises list results as one block per item
                            result_data = []
                            for block in result.content:
                                try:
                                    result_data.append(json.loads(block.text))
                                except (json.JSONDecodeError, TypeError):
                                    try:
                                        import ast
                                        result_data.append(ast.literal_eval(block.text))
                                    except Exception:
                                        result_data.append(block.text)
        except BaseException as exc:
            # mcp >= 1.10 raises an ExceptionGroup during SSE connection cleanup,
            # even when the tool call succeeded. If we already received data,
            # the error is a benign teardown race — ignore it.
            if result_data is not None:
                return result_data
            # Real failure: unwrap and surface the inner exception
            inner: BaseException = exc
            if hasattr(exc, "exceptions") and exc.exceptions:
                inner = exc.exceptions[0]
            raise RuntimeError(
                f"MCP call '{tool_name}' to {mcp_url} failed — "
                f"{type(inner).__name__}: {inner}"
            ) from inner

        return result_data

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

        task_prompt = (
            f"Original user query: {query}\n\n"
            f"Financial constraints to enforce:\n"
            f"- Min Wage: {salary_min}\n"
            f"- Max Wage: {salary_max}\n"
            f"- Max Value: {value_max}\n\n"
            f"Use the `query_player_database` tool to search for candidates. "
            f"If the tool returns empty, try again with slightly relaxed constraints (e.g. increase max_wage by 15%, drop rating). "
            f"Pick up to 5 candidates from the results. If you cannot find 5 candidates after a few tries, just return the ones you found. For each candidate, append a 'scout_note' field to their data dictionary with a brief justification of why they fit. "
            f"CRITICAL: Your final response MUST be ONLY valid JSON containing the final list of players in this exact format:\n"
            f'{{"players": [ {{ "id": 1, "name": "...", "scout_note": "..." }} ]}}\n'
            f"Do not output markdown codeblocks, just the raw JSON."
        )

        response_text = await self._run_deep_agent(task_prompt, tools=[query_player_database])
        
        cleaned_text = response_text.replace("```json", "").replace("```", "").strip()
        try:
            result = json.loads(cleaned_text)
            players = result.get("players", [])
        except json.JSONDecodeError:
            await self.emit_error("Failed to parse JSON from scouter agent.", cleaned_text)
            raise

        await self.emit_complete(
            f"Shortlisted {len(players)} verified players from database"
        )
        return {"players": players}
