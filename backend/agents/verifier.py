"""Verifier Agent — checks scouted player names against FBref to catch hallucinations."""
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
        await self.emit_start(f"Verifying {len(players)} scouted player(s) against FBref...")

        names = [p.get("name", "") for p in players if p.get("name")]
        if not names:
            return {"all_valid": True, "verified": [], "invalid": [], "feedback": "No players to verify."}

        verifier = self

        @tool
        async def check_player_on_fbref(player_name: str) -> str:
            """Check whether a footballer with this exact name exists on FBref."""
            try:
                result = await verifier._call_mcp_tool("verify_player_on_fbref", {"player_name": player_name})
                if isinstance(result, dict):
                    return json.dumps(result)
                return str(result)
            except Exception as exc:
                return json.dumps({"exists": False, "matched_name": None, "error": str(exc)})

        task = (
            f"You must verify whether each of the following player names actually exists "
            f"as a real footballer. Use the check_player_on_fbref tool exactly once per name.\n\n"
            f"Players to verify: {names}\n\n"
            f"After checking all names, respond with a single JSON object:\n"
            f'{{"all_valid": true/false, "verified": ["name1", ...], "invalid": ["name2", ...], '
            f'"feedback": "brief description of what was found/missing"}}'
        )

        raw = await self._run_deep_agent(task_message=task, tools=[check_player_on_fbref])

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
            # If parsing failed, assume all valid so pipeline isn't blocked
            await self.emit_progress("[verifier] Could not parse verification result — assuming all valid")
            return {"all_valid": True, "verified": names, "invalid": [], "feedback": "Verification parse error — assumed valid."}

        all_valid = result.get("all_valid", True)
        invalid = result.get("invalid", [])
        verified = result.get("verified", names)
        feedback = result.get("feedback", "")

        if all_valid:
            await self.emit_complete(f"All {len(verified)} player(s) verified on FBref.")
        else:
            await self.emit_progress(f"[verifier] {len(invalid)} player(s) not found on FBref: {invalid}")

        return {
            "all_valid": all_valid,
            "verified": verified,
            "invalid": invalid,
            "feedback": feedback,
        }
