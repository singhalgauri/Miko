# Owner: Person 1
# Purpose: Mock model provider returning deterministic canned responses for offline development
# TODO(person1): Add scenario-specific canned responses for inbox, briefing, and file organisation

from typing import Any

from backend.app.providers.base import ChatResult, ModelProvider


class MockProvider(ModelProvider):
    """Mock LLM provider returning canned responses without requiring models or GPUs."""

    @property
    def name(self) -> str:
        return "mock"

    async def chat(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
    ) -> ChatResult:
        """Returns canned chat response or simulated tool call based on input messages."""
        last_msg = messages[-1].get("content", "") if messages else ""

        # Check for simulated tool call trigger in testing
        if tools and "move" in last_msg.lower():
            return ChatResult(
                content="I will move the invoice file to the appropriate folder.",
                tool_calls=[
                    {
                        "name": "file.move",
                        "args": {
                            "source": "Downloads/invoice_oct.pdf",
                            "destination": "Documents/Invoices/invoice_oct.pdf",
                        },
                    }
                ],
                model="mock-nemotron-3-nano",
            )

        return ChatResult(
            content=f"[Mock Miko Response] Processed: '{last_msg[:60]}...' smoothly in mock mode.",
            tool_calls=[],
            model="mock-nemotron-3-nano",
            usage={"prompt_tokens": 15, "completion_tokens": 25, "total_tokens": 40},
        )

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Returns deterministic 384-dimensional mock embedding vectors."""
        # Fixed 384-dim dummy vector normalized
        dummy_vector = [0.05] * 384
        return [dummy_vector for _ in texts]
