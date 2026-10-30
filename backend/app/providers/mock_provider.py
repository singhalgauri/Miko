# Owner: Person 1
# Purpose: Mock model provider returning deterministic canned responses for offline development.
#          Teammates can develop and test with PROVIDER=mock without any model or GPU.

from typing import Any

from backend.app.providers.base import ChatResult, ModelProvider, ToolCall, Usage

_MOCK_MODEL = "mock-nemotron-3_5-lightning"

# ── Canned tool call responses ─────────────────────────────────────────────────
_CANNED_FILE_MOVE = ToolCall(
    id="tc-mock-001",
    name="file.move",
    args={
        "source": "Downloads/invoice_oct.pdf",
        "destination": "Documents/Invoices/invoice_oct.pdf",
    },
)

_CANNED_WEATHER_TOOL = ToolCall(
    id="tc-mock-002",
    name="get_weather",
    args={"city": "Mumbai"},
)

_CANNED_EMAIL_DRAFT = ToolCall(
    id="tc-mock-003",
    name="email.draft",
    args={
        "recipient": "sarah.lead@company.com",
        "subject": "Re: Q4 Product Roadmap Final Review",
        "body": "Hi Sarah, I have reviewed the milestone plan. Will share feedback by EOD. — Miko",
    },
)

# ── Canned structured text responses ──────────────────────────────────────────
_CANNED_TRIAGE = """\
{
  "category": "action_required",
  "importance": "high",
  "suggested_action": "reply",
  "draft_reply": "Hi Sarah, I have reviewed the Q4 roadmap milestone plan and will share detailed feedback before 4 PM today. — Miko"
}"""

_CANNED_BRIEFING = """\
{
  "sections": [
    {
      "title": "Urgent Emails",
      "items": [
        "sarah.lead@company.com — Q4 Product Roadmap Final Review (reply required by 4 PM)"
      ]
    },
    {
      "title": "Today's Calendar",
      "items": [
        "10:00 AM — Sprint Sync with Engineering",
        "12:30 PM — Team Lunch & Hackathon Prep",
        "03:00 PM — Nebius Demo Video Recording"
      ]
    },
    {
      "title": "New Files",
      "items": [
        "Documents/Invoices/invoice_oct.pdf — moved from Downloads"
      ]
    }
  ]
}"""

_CANNED_ROUTER = "inbox"

_MOCK_USAGE = Usage(prompt_tokens=15, completion_tokens=25, total_tokens=40)


class MockProvider(ModelProvider):
    """Deterministic mock LLM provider.

    Trigger keywords select specific canned responses:
      - "move" → file.move tool call
      - "weather" → get_weather tool call
      - "triage" / "email" / "classify" → JSON triage result
      - "briefing" / "morning" / "digest" → JSON briefing result
      - "route" / "intent" / "classify" → route target name
      - "draft" → email.draft tool call
      - anything else → generic mock response
    """

    @property
    def name(self) -> str:
        return "mock"

    async def chat(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
    ) -> ChatResult:
        """Returns deterministic canned response based on message content and tools."""
        last_msg = messages[-1].get("content", "").lower() if messages else ""
        all_content = " ".join(m.get("content", "").lower() for m in messages)

        # ── Tool-call canned responses (only when tools are provided) ──────────
        if tools:
            tool_names = [t.get("function", t).get("name", "") for t in tools]

            if "file.move" in tool_names or "move" in last_msg:
                return ChatResult(
                    content="I will move the invoice to Documents/Invoices.",
                    tool_calls=[_CANNED_FILE_MOVE],
                    model=_MOCK_MODEL,
                    finish_reason="tool_calls",
                    usage=_MOCK_USAGE,
                    provider=self.name,
                )

            if "get_weather" in tool_names or "weather" in last_msg:
                return ChatResult(
                    content="",
                    tool_calls=[_CANNED_WEATHER_TOOL],
                    model=_MOCK_MODEL,
                    finish_reason="tool_calls",
                    usage=_MOCK_USAGE,
                    provider=self.name,
                )

            if "email.draft" in tool_names or "draft" in last_msg:
                return ChatResult(
                    content="",
                    tool_calls=[_CANNED_EMAIL_DRAFT],
                    model=_MOCK_MODEL,
                    finish_reason="tool_calls",
                    usage=_MOCK_USAGE,
                    provider=self.name,
                )

        # ── Structured text canned responses ───────────────────────────────────
        if any(k in all_content for k in ["triage", "classify email", "inbox triage"]):
            return ChatResult(
                content=_CANNED_TRIAGE,
                model=_MOCK_MODEL,
                usage=_MOCK_USAGE,
                provider=self.name,
            )

        if any(k in all_content for k in ["briefing", "morning briefing", "daily digest", "catch-up", "catchup"]):
            return ChatResult(
                content=_CANNED_BRIEFING,
                model=_MOCK_MODEL,
                usage=_MOCK_USAGE,
                provider=self.name,
            )

        if any(k in all_content for k in ["route", "intent", "classify", "which agent"]):
            return ChatResult(
                content=_CANNED_ROUTER,
                model=_MOCK_MODEL,
                usage=_MOCK_USAGE,
                provider=self.name,
            )

        # ── Generic fallback ───────────────────────────────────────────────────
        preview = last_msg[:60] if last_msg else "(empty)"
        return ChatResult(
            content=f"[Mock Miko] Processed: '{preview}...' — mock mode active.",
            tool_calls=[],
            model=_MOCK_MODEL,
            usage=_MOCK_USAGE,
            provider=self.name,
        )

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Returns deterministic 768-dim mock embedding vectors (normalised)."""
        # Use text hash for slight variation between inputs while staying deterministic
        results = []
        for text in texts:
            seed = sum(ord(c) for c in text) % 100
            vec = [round(0.05 + (seed * 0.001), 4)] * 768
            results.append(vec)
        return results
