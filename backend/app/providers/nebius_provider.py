# Owner: Person 1
# Purpose: Nebius Token Factory model provider via OpenAI-compatible client
# TODO(person1): Confirm Nemotron model IDs and support for streaming tool calls from docs/nebius-notes.md

import os
from typing import Any

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.providers.base import ChatResult, ModelProvider
from openai import AsyncOpenAI


class NebiusProvider(ModelProvider):
    """Provider connecting to Nebius Token Factory serving NVIDIA Nemotron models."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.api_key = api_key or os.getenv("NEBIUS_API_KEY") or settings.nebius_api_key
        self.base_url = base_url or os.getenv("NEBIUS_BASE_URL") or settings.nebius_base_url
        self._client: AsyncOpenAI | None = None

        if self.api_key:
            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            )

    @property
    def name(self) -> str:
        return "nebius"

    async def chat(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
    ) -> ChatResult:
        """Sends chat completion request to Nebius Token Factory."""
        logger.info("NebiusProvider dispatching chat completion to %s", self.base_url)

        if not self._client or not self.api_key:
            logger.warning("NEBIUS_API_KEY not configured. Returning fallback stub response.")
            return ChatResult(
                content="[Nebius Token Factory Stub] Connect NEBIUS_API_KEY to query cloud Nemotron.",
                model="nebius-nemotron-stub",
            )

        try:
            kwargs: dict[str, Any] = {
                "model": "nvidia/nemotron-3.5-lightning",  # TODO confirm exact ID
                "messages": messages,
            }
            if tools:
                kwargs["tools"] = tools

            response = await self._client.chat.completions.create(**kwargs)
            choice = response.choices[0]
            content = choice.message.content or ""
            tool_calls = []
            if choice.message.tool_calls:
                for tc in choice.message.tool_calls:
                    tool_calls.append(
                        {
                            "name": tc.function.name,
                            "args": tc.function.arguments,
                        }
                    )
            return ChatResult(
                content=content,
                tool_calls=tool_calls,
                model=response.model or "nebius-nemotron",
                finish_reason=choice.finish_reason or "stop",
            )
        except Exception as e:
            logger.error("Error invoking Nebius Token Factory: %s", e)
            return ChatResult(
                content=f"[Nebius Error Fallback] Inference failed: {e}",
                model="nebius-error-fallback",
            )

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Generates embeddings via Nebius API or fallback vectors."""
        # TODO(person1): Verify if Nebius Token Factory hosts an embedding endpoint
        return [[0.02] * 384 for _ in texts]
