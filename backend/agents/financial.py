"""Financial Agent — reads YAML financial plan and determines player salary thresholds."""
import asyncio
import json
from typing import Any

import yaml
from langchain_core.messages import HumanMessage, SystemMessage
from openai import AsyncOpenAI

from .base import BaseAgent
from ..utils.config import settings, get_langchain_azure_llm
from ..utils.prompt_loader import PromptLoader


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
        await self.emit_start("Reading club financial plan and calculating salary thresholds...")

        plan = self._load_financial_plan()
        await self.emit_progress(f"Financial plan loaded for {plan.get('team', {}).get('name', 'Unknown')}")

        plan_json = json.dumps(plan, indent=2)

        system_prompt = self.system_prompt or (
            "You are a football club financial analyst. "
            "Always respond with a single valid JSON object — no markdown, no explanation."
        )

        user_prompt = PromptLoader.get("financial_analyze").format(
            query=query,
            position=position or "to be determined from query",
            plan_json=plan_json,
        )

        await self.emit_progress("[financial] Analysing financial plan...")

        # Use JSON mode to guarantee valid JSON output
        llm = get_langchain_azure_llm().bind(response_format={"type": "json_object"})
        response = await llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ])
        raw = response.content if hasattr(response, "content") else str(response)

        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            # Fallback: extract first {...} block
            start, end = raw.find("{"), raw.rfind("}")
            if start != -1 and end != -1:
                try:
                    result = json.loads(raw[start:end + 1])
                except json.JSONDecodeError:
                    result = None
            else:
                result = None

        if not isinstance(result, dict):
            await self.emit_error("Failed to parse JSON from financial agent.", raw[:300])
            raise ValueError("No valid JSON found in financial agent response")

        await self.emit_complete(
            f"Financial analysis complete — salary range: "
            f"€{result.get('salary_min', 0):,} – €{result.get('salary_max', 0):,}/week"
        )
        return result
