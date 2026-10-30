# Owner: Person 1
# Purpose: Intent routing agent using rule-first heuristics, invoking ModelProvider only when ambiguous
# TODO(person1): Integrate NeMo Switchyard pattern and multi-intent decomposition

from typing import Any

from backend.app.core.logging import logger
from backend.app.providers.base import ModelProvider
from backend.app.validation.tool_validation import RouterOutput, validate_with_retry

_VALID_AGENTS = ["inbox", "file_organiser", "document", "briefing"]

# Keyword routing rules — deterministic, no model call needed
_RULES: list[tuple[list[str], str]] = [
    (["email", "inbox", "mail", "unread", "message", "reply", "sender"], "inbox"),
    (["file", "clean", "download", "folder", "organise", "organize", "move", "rename", "sort"], "file_organiser"),
    (["document", "pdf", "contract", "search", "find", "citation", "doc", "read", "summarize"], "document"),
    (["briefing", "morning", "calendar", "agenda", "catchup", "catch-up", "schedule", "digest", "summary", "today"], "briefing"),
]


class RouterAgent:
    """Evaluates user requests and routes to the appropriate specialist agent.

    Strategy:
    1. Fast keyword rules → deterministic, confidence=1.0
    2. ModelProvider turn → validated RouterOutput, confidence=0.85
    3. Default fallback → briefing, confidence=0.5
    """

    def __init__(self, provider: ModelProvider):
        self.provider = provider

    async def route(self, user_query: str) -> dict[str, Any]:
        """Routes query using fast rule heuristics first; falls back to ModelProvider when unclear."""
        logger.info("RouterAgent evaluating query: '%s'", user_query[:80])
        q = user_query.lower()

        # ── Rule-first routing ────────────────────────────────────────────────
        for keywords, target in _RULES:
            if any(w in q for w in keywords):
                logger.info("RouterAgent: rule-matched '%s'", target)
                return {"target_agent": target, "confidence": 1.0, "reason": "rule_heuristic"}

        # ── Model classification ──────────────────────────────────────────────
        logger.info("RouterAgent: ambiguous query — invoking ModelProvider '%s'", self.provider.name)
        prompt_messages = [
            {
                "role": "system",
                "content": (
                    "You are a routing agent. Classify the user request into exactly one category.\n"
                    "Valid categories: inbox, file_organiser, document, briefing\n"
                    "Respond ONLY with valid JSON in this format:\n"
                    '{"target_agent": "<category>", "confidence": 0.85, "reason": "model_classification"}'
                ),
            },
            {"role": "user", "content": f"Route this request: {user_query}"},
        ]

        validated, _ = await validate_with_retry(self.provider, prompt_messages, RouterOutput)
        if validated and validated.target_agent in _VALID_AGENTS:
            return {
                "target_agent": validated.target_agent,
                "confidence": validated.confidence,
                "reason": validated.reason,
            }

        # ── Default fallback ──────────────────────────────────────────────────
        logger.warning("RouterAgent: model classification failed — defaulting to 'briefing'")
        return {"target_agent": "briefing", "confidence": 0.5, "reason": "default_fallback"}
