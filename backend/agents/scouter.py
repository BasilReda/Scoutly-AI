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
                        PromptLoader.get("scouter_search_params").format(
                            query=query,
                            salary_min=salary_min,
                            salary_max=salary_max,
                            value_max=value_max,
                        )
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

        # Step 3 — Pick top 5 from DB results (no LLM — avoids hallucination)
        # The MCP server already orders by performance DESC, so just take the best.
        shortlist = raw_players[:5]
        await self.emit_progress(
            f"Database returned {len(raw_players)} candidates — taking top {len(shortlist)}"
        )

        # Step 4 — LLM writes scout_note ONLY; player data is never modified
        await self.emit_progress("Generating scouting notes for each player...")
        players = []
        for player in shortlist:
            note_result = await self.chat_json(
                messages=[
                    {
                        "role": "user",
                        "content": (
                            PromptLoader.get("scouter_note").format(
                                query=query,
                                player_json=json.dumps(player, indent=2)
                            )
                        ),
                    }
                ]
            )
            # Keep the original DB record untouched; only append the note
            enriched = dict(player)
            enriched["scout_note"] = note_result.get("scout_note", "No note generated.")
            players.append(enriched)

        await self.emit_complete(
            f"Shortlisted {len(players)} verified players from database",
            {"count": len(players), "names": [p.get("name") for p in players]},
        )
        return {"players": players}
