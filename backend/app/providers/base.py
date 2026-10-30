# Owner: Person 1
# Purpose: Abstract ModelProvider interface for all LLM backends
# TODO(person1): Add streaming chat generator interface (stream_chat)

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    """A single tool/function call returned by the model."""

    id: str = ""
    name: str
    args: dict[str, Any] = Field(default_factory=dict)


class Usage(BaseModel):
    """Token usage statistics returned by the provider."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatResult(BaseModel):
    """Structured result returned by ModelProvider chat completions."""

    content: str = ""
    tool_calls: list[ToolCall] = Field(default_factory=list)
    model: str = "mock-model"
    finish_reason: str = "stop"
    usage: Usage = Field(default_factory=Usage)
    latency_ms: float = 0.0
    provider: str = ""


class ModelProvider(ABC):
    """Abstract base class that all LLM providers must implement."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Identifier for the provider ('local' | 'nebius' | 'mock')."""
        pass

    @abstractmethod
    async def chat(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
    ) -> ChatResult:
        """Sends chat messages and optional tools to the provider and returns structured result."""
        pass

    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Calculates embeddings for the given list of texts."""
        pass
