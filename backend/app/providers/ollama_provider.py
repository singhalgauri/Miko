# Owner: Person 1
# Purpose: Ollama local model provider (strictly bound to 127.0.0.1)

import json
import time
from typing import Any

import httpx
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.providers.base import ChatResult, ModelProvider, ToolCall, Usage
from backend.app.registry.loader import load_models_registry

_DEFAULT_CHAT_MODEL = "nemotron-mini:4b"
_DEFAULT_EMBED_MODEL = "nomic-embed-text:latest"
_TIMEOUT = 60.0  # seconds; local models can be slow on first load


def _get_ollama_model(role: str = "router") -> str:
    """Pick the ollama_tag for the given role from the model registry."""
    try:
        models = load_models_registry()
        for m in models:
            if m.get("provider") == "local" and m.get("role") == role:
                tag = m.get("ollama_tag", "")
                if tag and tag != "n/a":
                    return tag
    except Exception:
        pass
    return _DEFAULT_CHAT_MODEL


def _get_ollama_embed_model() -> str:
    """Pick the embed model tag from the registry."""
    try:
        models = load_models_registry()
        for m in models:
            if m.get("provider") == "local" and m.get("role") == "embeddings":
                tag = m.get("ollama_tag", "")
                if tag and tag != "n/a":
                    return tag
    except Exception:
        pass
    return _DEFAULT_EMBED_MODEL


class OllamaProvider(ModelProvider):
    """Local model provider connecting strictly to Ollama at 127.0.0.1.

    Tool calling is forwarded via the /api/chat endpoint using the standard
    Ollama tools payload (mirrors OpenAI schema).
    Embeddings use /api/embeddings with nomic-embed-text.
    """

    def __init__(self, host: str | None = None):
        self.host = host or settings.ollama_host
        # Enforce local-only binding for privacy/security
        if "127.0.0.1" not in self.host and "localhost" not in self.host:
            raise ValueError(
                f"Security violation: OllamaProvider must bind to 127.0.0.1 only. Got: {self.host}"
            )
        self._chat_model: str | None = None  # resolved lazily
        self._embed_model: str | None = None

    @property
    def name(self) -> str:
        return "local"

    def _resolve_chat_model(self) -> str:
        if self._chat_model is None:
            self._chat_model = _get_ollama_model(role="router")
        return self._chat_model

    def _resolve_embed_model(self) -> str:
        if self._embed_model is None:
            self._embed_model = _get_ollama_embed_model()
        return self._embed_model

    # ── chat ─────────────────────────────────────────────────────────────────

    async def chat(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
    ) -> ChatResult:
        """Sends chat request to local Ollama /api/chat endpoint."""
        model_tag = self._resolve_chat_model()
        logger.info("OllamaProvider: dispatching chat to %s model=%s", self.host, model_tag)

        payload: dict[str, Any] = {
            "model": model_tag,
            "messages": messages,
            "stream": False,
        }
        if tools:
            payload["tools"] = tools

        t0 = time.perf_counter()
        try:
            async with httpx.AsyncClient(base_url=self.host, timeout=_TIMEOUT) as client:
                resp = await client.post("/api/chat", json=payload)
            latency_ms = (time.perf_counter() - t0) * 1000

            if resp.status_code != 200:
                logger.warning(
                    "OllamaProvider: HTTP %d from /api/chat — returning stub",
                    resp.status_code,
                )
                return self._offline_stub(latency_ms)

            data = resp.json()
            msg = data.get("message", {})
            content = msg.get("content", "")

            # Parse Ollama tool_calls format → ToolCall objects
            raw_tool_calls = msg.get("tool_calls", [])
            tool_calls: list[ToolCall] = []
            for tc in raw_tool_calls:
                fn = tc.get("function", tc)
                name = fn.get("name", "")
                args = fn.get("arguments", {})
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except Exception:
                        args = {}
                tool_calls.append(ToolCall(name=name, args=args))

            # Ollama returns eval_count (completion tokens) and prompt_eval_count
            usage = Usage(
                prompt_tokens=data.get("prompt_eval_count", 0),
                completion_tokens=data.get("eval_count", 0),
                total_tokens=data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
            )

            return ChatResult(
                content=content,
                tool_calls=tool_calls,
                model=model_tag,
                finish_reason="stop",
                usage=usage,
                latency_ms=latency_ms,
                provider=self.name,
            )

        except httpx.ConnectError:
            logger.warning("OllamaProvider: Ollama daemon not reachable at %s — returning stub", self.host)
        except httpx.TimeoutException:
            logger.warning("OllamaProvider: request timed out after %.0fs — returning stub", _TIMEOUT)
        except Exception as exc:
            logger.warning("OllamaProvider: unexpected error (%s) — returning stub", exc)

        return self._offline_stub((time.perf_counter() - t0) * 1000)

    def _offline_stub(self, latency_ms: float = 0.0) -> ChatResult:
        return ChatResult(
            content="[Ollama Offline] Miko local model is not reachable. Start Ollama with `ollama serve`.",
            model="ollama-offline-stub",
            provider=self.name,
            latency_ms=latency_ms,
        )

    # ── embed ─────────────────────────────────────────────────────────────────

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Computes embeddings using local Ollama nomic-embed-text via /api/embeddings."""
        embed_model = self._resolve_embed_model()
        logger.info("OllamaProvider: embed %d texts with model=%s", len(texts), embed_model)

        results: list[list[float]] = []
        try:
            async with httpx.AsyncClient(base_url=self.host, timeout=_TIMEOUT) as client:
                for text in texts:
                    resp = await client.post(
                        "/api/embeddings",
                        json={"model": embed_model, "prompt": text},
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        results.append(data.get("embedding", [0.01] * 768))
                    else:
                        logger.warning(
                            "OllamaProvider: embed HTTP %d for text — using zero vector",
                            resp.status_code,
                        )
                        results.append([0.0] * 768)
        except Exception as exc:
            logger.warning("OllamaProvider: embed failed (%s) — returning zero vectors", exc)
            results = [[0.0] * 768 for _ in texts]

        return results
