# Owner: Person 1
# Purpose: Nebius Token Factory model provider via OpenAI-compatible client
# Confirmed model: nvidia/Nemotron-3_5-Lightning (see docs/nebius-notes.md)

import asyncio
import os
import random
import time
from typing import Any

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.providers.base import ChatResult, ModelProvider, ToolCall, Usage
from openai import AsyncOpenAI, RateLimitError

# Retry config
_MAX_RETRIES = 3
_INITIAL_DELAY = 1.0  # seconds
_MAX_DELAY = 60.0
_JITTER = 0.5

# Default models (overridden by registry / env)
_DEFAULT_MODEL = "nvidia/Nemotron-3_5-Lightning"
_DEFAULT_EMBED_MODEL = "BAAI/bge-en-icl"


def _get_env_or_setting(env_var: str, setting_val: str, fallback: str) -> str:
    """Read env first, then settings, then hardcoded fallback."""
    return os.getenv(env_var) or setting_val or fallback


class NebiusProvider(ModelProvider):
    """Provider connecting to Nebius Token Factory serving NVIDIA Nemotron models.

    Confirmed working model: nvidia/Nemotron-3_5-Lightning
    Base URL: https://api.tokenfactory.nebius.com/v1
    The NEBIUS_API_KEY is never printed or included in log messages.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        embed_model: str | None = None,
    ):
        # Key is resolved but NEVER logged
        self._api_key = (
            api_key
            or os.getenv("NEBIUS_API_KEY")
            or getattr(settings, "nebius_api_key", "")
        )
        self.base_url = (
            base_url
            or os.getenv("NEBIUS_BASE_URL")
            or getattr(settings, "nebius_base_url", "https://api.tokenfactory.nebius.com/v1")
        )
        self.model = (
            model
            or os.getenv("NEBIUS_MODEL")
            or _DEFAULT_MODEL
        )
        self.embed_model = (
            embed_model
            or os.getenv("NEBIUS_EMBED_MODEL")
            or _DEFAULT_EMBED_MODEL
        )
        self._client: AsyncOpenAI | None = None

        if self._api_key:
            self._client = AsyncOpenAI(
                api_key=self._api_key,
                base_url=self.base_url,
                timeout=30.0,
            )
        else:
            logger.warning(
                "NebiusProvider: NEBIUS_API_KEY not set — provider will return stub responses."
            )

    @property
    def name(self) -> str:
        return "nebius"

    # ── Internal retry helper ────────────────────────────────────────────────

    async def _with_retry(self, coro_fn, *args, **kwargs):
        """Runs coro_fn with exponential backoff on 429 / 5xx errors."""
        delay = _INITIAL_DELAY
        last_exc: Exception | None = None
        for attempt in range(_MAX_RETRIES + 1):
            try:
                return await coro_fn(*args, **kwargs)
            except RateLimitError as exc:
                last_exc = exc
                jitter = random.uniform(-_JITTER, _JITTER)
                wait = min(delay + jitter, _MAX_DELAY)
                logger.warning(
                    "NebiusProvider: 429 rate limit (attempt %d/%d), retrying in %.1fs",
                    attempt + 1,
                    _MAX_RETRIES,
                    wait,
                )
                await asyncio.sleep(wait)
                delay = min(delay * 2, _MAX_DELAY)
            except Exception as exc:
                # Retry on 5xx-style errors (openai wraps them as APIStatusError)
                status = getattr(exc, "status_code", 0)
                if status and status >= 500 and attempt < _MAX_RETRIES:
                    last_exc = exc
                    jitter = random.uniform(-_JITTER, _JITTER)
                    wait = min(delay + jitter, _MAX_DELAY)
                    logger.warning(
                        "NebiusProvider: HTTP %d (attempt %d/%d), retrying in %.1fs",
                        status,
                        attempt + 1,
                        _MAX_RETRIES,
                        wait,
                    )
                    await asyncio.sleep(wait)
                    delay = min(delay * 2, _MAX_DELAY)
                else:
                    raise
        raise last_exc  # type: ignore[misc]

    # ── chat ─────────────────────────────────────────────────────────────────

    async def chat(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
    ) -> ChatResult:
        """Sends chat completion request to Nebius Token Factory with retry/backoff."""
        logger.info("NebiusProvider: dispatching chat to %s model=%s", self.base_url, self.model)

        if not self._client:
            logger.warning("NebiusProvider: no client (missing API key) — returning stub")
            return ChatResult(
                content="[Nebius Stub] Set NEBIUS_API_KEY to use cloud Nemotron.",
                model=self.model,
                provider=self.name,
            )

        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools

        t0 = time.perf_counter()
        try:
            response = await self._with_retry(
                self._client.chat.completions.create, **kwargs
            )
        except Exception as exc:
            # Key must never appear in logs — exc message is safe (no key in it)
            logger.error("NebiusProvider: chat failed after retries: %s", type(exc).__name__)
            return ChatResult(
                content=f"[Nebius Error] Inference failed: {type(exc).__name__}",
                model=self.model,
                provider=self.name,
            )
        latency_ms = (time.perf_counter() - t0) * 1000

        choice = response.choices[0]
        content = choice.message.content or ""

        tool_calls: list[ToolCall] = []
        if choice.message.tool_calls:
            import json as _json

            for tc in choice.message.tool_calls:
                try:
                    raw_args = _json.loads(tc.function.arguments or "{}")
                except Exception:
                    raw_args = {}
                tool_calls.append(
                    ToolCall(
                        id=tc.id or "",
                        name=tc.function.name,
                        args=raw_args,
                    )
                )

        usage = Usage()
        if response.usage:
            usage = Usage(
                prompt_tokens=response.usage.prompt_tokens or 0,
                completion_tokens=response.usage.completion_tokens or 0,
                total_tokens=response.usage.total_tokens or 0,
            )

        return ChatResult(
            content=content,
            tool_calls=tool_calls,
            model=response.model or self.model,
            finish_reason=choice.finish_reason or "stop",
            usage=usage,
            latency_ms=latency_ms,
            provider=self.name,
        )

    # ── embed ─────────────────────────────────────────────────────────────────

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Generates embeddings via Nebius API (BAAI/bge-en-icl) or fallback vectors.

        Note: No NVIDIA-branded embedding model exists in Token Factory catalogue.
        BAAI/bge-en-icl is the confirmed Nebius embedding model (see docs/nebius-notes.md).
        """
        if not self._client:
            logger.warning("NebiusProvider: no client for embed — returning zeros")
            return [[0.0] * 768 for _ in texts]

        try:
            t0 = time.perf_counter()
            response = await self._with_retry(
                self._client.embeddings.create,
                model=self.embed_model,
                input=texts,
                encoding_format="float",
            )
            latency_ms = (time.perf_counter() - t0) * 1000
            logger.info(
                "NebiusProvider: embed %d texts in %.0f ms (model=%s)",
                len(texts),
                latency_ms,
                self.embed_model,
            )
            return [item.embedding for item in response.data]
        except Exception as exc:
            logger.error("NebiusProvider: embed failed: %s", type(exc).__name__)
            return [[0.0] * 768 for _ in texts]
