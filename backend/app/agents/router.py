# Owner: Person 1
# Purpose: Intent routing agent using rule-first heuristics, invoking ModelProvider only when ambiguous
# TODO(person1): Integrate NeMo Switchyard pattern and multi-intent decomposition

from typing import Any

from backend.app.core.logging import logger
from backend.app.providers.base import ModelProvider


class RouterAgent:
    """Evaluates user requests and routes to the appropriate specialist agent."""

    def __init__(self, provider: ModelProvider):
        self.provider = provider

    async def route(self, user_query: str) -> dict[str, Any]:
        """Routes query using fast rule heuristics first; falls back to ModelProvider when unclear."""
        logger.info("Router evaluating query: '%s'", user_query)
        q = user_query.lower()

        # Rule-first routing heuristics
        if any(w in q for w in ["email", "inbox", "mail", "unread"]):
            return {"target_agent": "inbox", "confidence": 1.0, "reason": "rule_heuristic"}

        if any(w in q for w in ["file", "clean", "download", "folder", "organise", "organize"]):
            return {"target_agent": "file_organiser", "confidence": 1.0, "reason": "rule_heuristic"}

        if any(w in q for w in ["document", "pdf", "contract", "search", "find", "citation"]):
            return {"target_agent": "document", "confidence": 1.0, "reason": "rule_heuristic"}

        if any(w in q for w in ["briefing", "morning", "calendar", "agenda", "catchup", "schedule"]):
            return {"target_agent": "briefing", "confidence": 1.0, "reason": "rule_heuristic"}

        # Fallback to ModelProvider reasoning turn
        logger.info("Query ambiguous under rules; invoking ModelProvider '%s'", self.provider.name)
        prompt = (
            f"Classify the following user request into one of: inbox, file_organiser, document, briefing.\n"
            f"Request: {user_query}\nTarget:"
        )
        result = await self.provider.chat([{"role": "user", "content": prompt}])
        content = result.content.lower()

        for candidate in ["inbox", "file_organiser", "document", "briefing"]:
            if candidate in content:
                return {"target_agent": candidate, "confidence": 0.85, "reason": "model_classification"}

        return {"target_agent": "briefing", "confidence": 0.5, "reason": "default_fallback"}
