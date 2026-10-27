# Owner: Person 1
# Purpose: Ollama local model provider (strictly bound to 127.0.0.1)
# TODO(person1): Implement robust error handling when Ollama daemon is offline and streaming support

from typing import Any

import httpx
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.providers.base import ChatResult, ModelProvider


class OllamaProvider(ModelProvider):
    """Local model provider connecting strictly to Ollama at 127.0.0.1."""

    def __init__(self, host: str | None = None):
        self.host = host or settings.ollama_host
        # Enforce local binding
        if "127.0.0.1" not in self.host and "localhost" not in self.host:
            raise ValueError(f"Security violation: Local provider must bind to 127.0.0.1 only. Got: {self.host}")

    @property
    def name(self) -> str:
        return "local"

    async def chat(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
    ) -> ChatResult:
        """Sends chat request to local Ollama API."""
        logger.info("OllamaProvider dispatching chat turn to %s", self.host)
        # TODO(person1): Connect using official ollama client or httpx with selected model from registry
        try:
            async with httpx.AsyncClient(base_url=self.host, timeout=30.0) as client:
                payload = {
                    "model": "nemotron-3-nano:4b",  # Default local tag
                    "messages": messages,
                    "stream": False,
                }
                if tools:
                    payload["tools"] = tools
                # Stub execution fallback if server is unreachable
                resp = await client.post("/api/chat", json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    msg = data.get("message", {})
                    return ChatResult(
                        content=msg.get("content", ""),
                        tool_calls=msg.get("tool_calls", []),
                        model="ollama-local",
                    )
        except Exception as e:
            logger.warning("Ollama connection failed (%s), returning fallback stub", e)

        return ChatResult(
            content="[Ollama Local Stub Response] Model running locally on 127.0.0.1.",
            model="ollama-local-stub",
        )

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Computes embeddings using local Ollama nomic-embed-text."""
        # TODO(person1): Call /api/embeddings on Ollama
        return [[0.01] * 384 for _ in texts]
