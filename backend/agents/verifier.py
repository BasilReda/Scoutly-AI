"""Verifier Agent — confirms scouted player names exist in the local database to catch hallucinations."""
import asyncio
import json
from typing import Any

from openai import AsyncOpenAI
from langchain_core.tools import tool

from .base import BaseAgent


class VerifierAgent(BaseAgent):
    AGENT_NAME = "verifier"

    def __init__(self, client: AsyncOpenAI, sse_queue: asyncio.Queue):
        super().__init__(client, sse_queue)

    async def run(self, players: list[dict], **kwargs) -> dict[str, Any]:
        names = [p.get("name", "") for p in players if p.get("name")]
        if not names:
            return {"all_valid": True, "verified": [], "invalid": [], "feedback": "No players to verify."}

        await self.emit_start(f"Verifying {len(names)} scouted player(s) against the database...")

        verifier = self

        @tool
        async def check_player_in_database(player_name: str) -> str:
            """Check whether a player with this exact name exists in the football database."""
            try:
                sql = f"SELECT id, name FROM players WHERE LOWER(name) = LOWER('{player_name.replace(chr(39), chr(39)*2)}')"
                result = await verifier._call_mcp_tool("query_players", {"sql": sql})
                if result and isinstance(result, list) and len(result) > 0:
                    return json.dumps({"exists": True, "db_name": result[0].get("name", player_name)})
                return json.dumps({"exists": False, "db_name": None})
            except Exception as exc:
                return json.dumps({"exists": False, "db_name": None, "error": str(exc)})

        task = (
            f"Verify whether each of the following player names exists in the football database. "
            f"Use check_player_in_database exactly once per name.\n\n"
            f"Players to verify: {names}\n\n"
            f"After checking all names, output a single JSON object:\n"
            f'{{"all_valid": true/false, "verified": ["name1", ...], "invalid": ["name2", ...], '
            f'"feedback": "brief description of what was found/missing"}}'
        )

        raw = await self._run_deep_agent(task_message=task, tools=[check_player_in_database])

        # Parse the result
        result = None
        cleaned = raw.replace("```json", "").replace("```", "").strip()
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
            await self.emit_progress("[verifier] Could not parse verification result — assuming all valid")
            return {"all_valid": True, "verified": names, "invalid": [], "feedback": "Verification parse error — assumed valid."}

        all_valid = result.get("all_valid", True)
        invalid = result.get("invalid", [])
        verified = result.get("verified", names)
        feedback = result.get("feedback", "")

        if all_valid:
            await self.emit_complete(f"All {len(verified)} player(s) confirmed in database.")
        else:
            await self.emit_progress(f"[verifier] {len(invalid)} hallucinated player(s) detected: {invalid}")

        return {
            "all_valid": all_valid,
            "verified": verified,
            "invalid": invalid,
            "feedback": feedback,
        }
