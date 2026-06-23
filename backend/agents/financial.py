"""Financial Agent — reads YAML financial plan and determines player salary thresholds."""
import asyncio
import json
from typing import Any

import yaml
from openai import AsyncOpenAI

from .base import BaseAgent
from ..utils.config import settings


class FinancialAgent(BaseAgent):
    AGENT_NAME = "financial"

    def __init__(self, client: AsyncOpenAI, sse_queue: asyncio.Queue):
        super().__init__(client, sse_queue)
        self._plan_cache: dict | None = None

    def _load_financial_plan(self) -> dict:
        """Load and cache the financial plan YAML."""
        if self._plan_cache is None:
            with open(settings.FINANCIAL_PLAN_PATH, encoding="utf-8") as f:
                self._plan_cache = yaml.safe_load(f)
        return self._plan_cache

    async def run(self, query: str, position: str | None = None, **kwargs) -> dict[str, Any]:
        """
        Analyze the club's financial plan and return salary thresholds for scouting.

        Args:
            query:    The original scouting query from the Planner.
            position: Target position (e.g. 'ST', 'CM'). Derived from query if not given.

        Returns:
            {
                salary_min, salary_max, value_max,
                adjustment_up_pct, adjustment_down_pct,
                position_cap, remaining_wage_capacity,
                financial_notes, risk_flags
            }
        """
        await self.emit_start("Reading club financial plan and calculating salary thresholds...")

        plan = self._load_financial_plan()
        await self.emit_progress("Financial plan loaded", {"team": plan["team"]["name"]})

        # Build prompt with full financial context
        plan_json = json.dumps(plan, indent=2)

        result = await self.chat_json(
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Scouting query: {query}\n"
                        f"Target position: {position or 'to be determined from query'}\n\n"
                        f"Financial Plan:\n```json\n{plan_json}\n```\n\n"
                        "Based on the scouting query and the financial plan above, "
                        "determine the appropriate salary thresholds and financial parameters. "
                        "Return a JSON object with these exact keys: "
                        "salary_min (int, EUR/week), salary_max (int, EUR/week), "
                        "value_max (int, EUR transfer fee), "
                        "adjustment_up_pct (float, max % above market rate for top performers), "
                        "adjustment_down_pct (float, max % below market rate for underperformers), "
                        "position_cap (int, EUR/week cap for this position), "
                        "remaining_wage_capacity (int, EUR/week the club can still add), "
                        "financial_notes (str, plain English summary), "
                        "risk_flags (list of str, any financial risks to flag)."
                    ),
                }
            ]
        )

        await self.emit_complete(
            f"Financial analysis complete — salary range: €{result.get('salary_min', 0):,} – €{result.get('salary_max', 0):,}/week",
            result,
        )
        return result
