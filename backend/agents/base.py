"""Base Agent — shared foundation for all sub-agents."""
import asyncio
import json
import time
from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator

from openai import AsyncAzureOpenAI

from ..utils.prompt_loader import PromptLoader
from ..utils.config import settings


class BaseAgent(ABC):
    """
    Abstract base class for all football management agents.

    Each agent:
    - Loads its own system prompt from prompts/<name>.md at runtime
    - Emits SSE events to a shared asyncio.Queue for real-time streaming
    - Communicates with OpenAI GPT-4o using function calling
    """

    #: Override in subclass — must match the .md filename in prompts/
    AGENT_NAME: str = "base"

    def __init__(self, client: AsyncAzureOpenAI, sse_queue: asyncio.Queue):
        self.client = client
        self.queue = sse_queue
        self._system_prompt: str | None = None

    # ─────────────────────────────────────────────────────────────────────────
    # Prompt Loading
    # ─────────────────────────────────────────────────────────────────────────

    @property
    def system_prompt(self) -> str:
        """
        Dynamically load the system prompt from prompts/<AGENT_NAME>.md.
        Reloaded fresh every invocation (no cache) for hot-reload support.
        """
        return PromptLoader.get(self.AGENT_NAME, use_cache=False)

    # ─────────────────────────────────────────────────────────────────────────
    # SSE Event Emission
    # ─────────────────────────────────────────────────────────────────────────

    async def emit(self, event: dict[str, Any]) -> None:
        """Push a structured event to the SSE queue."""
        event.setdefault("agent", self.AGENT_NAME)
        event.setdefault("timestamp", time.time())
        await self.queue.put(event)

    async def emit_start(self, message: str) -> None:
        await self.emit({"type": "agent_start", "message": message})

    async def emit_progress(self, message: str, data: Any = None) -> None:
        payload: dict[str, Any] = {"type": "progress", "message": message}
        if data is not None:
            payload["data"] = data
        await self.emit(payload)

    async def emit_complete(self, message: str, data: Any = None) -> None:
        payload: dict[str, Any] = {"type": "agent_complete", "message": message}
        if data is not None:
            payload["data"] = data
        await self.emit(payload)

    async def emit_error(self, message: str, error: str = "") -> None:
        await self.emit({"type": "error", "message": message, "error": error})

    # ─────────────────────────────────────────────────────────────────────────
    # LLM Helpers
    # ─────────────────────────────────────────────────────────────────────────

    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        response_format: dict | None = None,
        temperature: float = 0.3,
    ) -> Any:
        """
        Call OpenAI chat completions with the agent's system prompt.
        Returns the raw ChatCompletion response.
        """
        full_messages = [
            {"role": "system", "content": self.system_prompt},
            *messages,
        ]
        kwargs: dict[str, Any] = {
            "model": settings.OPENAI_MODEL,
            "messages": full_messages,
            "temperature": temperature,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        if response_format:
            kwargs["response_format"] = response_format

        return await self.client.chat.completions.create(**kwargs)

    async def chat_json(
        self,
        messages: list[dict],
        temperature: float = 0.2,
    ) -> dict:
        """
        Call OpenAI and parse the response as JSON.
        Uses response_format=json_object for reliability.
        """
        response = await self.chat(
            messages=messages,
            response_format={"type": "json_object"},
            temperature=temperature,
        )
        content = response.choices[0].message.content
        return json.loads(content)

    # ─────────────────────────────────────────────────────────────────────────
    # Abstract Interface
    # ─────────────────────────────────────────────────────────────────────────

    @abstractmethod
    async def run(self, **kwargs) -> dict[str, Any]:
        """
        Execute this agent's task.
        Must be implemented by each concrete agent.
        Returns a dict with the agent's output.
        """
        ...
