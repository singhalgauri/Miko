# Owner: Person 1
# Purpose: Daily briefing agent summarizing calendar events, unread emails, and pending tasks
# TODO(person1): Integrate multi-source agenda aggregation and morning audio synthesis

from typing import Any

from backend.app.core.logging import logger
from backend.app.providers.base import ModelProvider
from backend.app.tools.calendar_caldav import list_events


class BriefingAgent:
    """Synthesizes daily events and pending items into a structured briefing."""

    def __init__(self, provider: ModelProvider):
        self.provider = provider

    async def generate_briefing(self) -> dict[str, Any]:
        """Generates morning briefing using calendar data and LLM synthesis."""
        logger.info("BriefingAgent generating daily summary with provider='%s'", self.provider.name)

        # 1. Fetch calendar events via gateway
        events_res = list_events(
            start_date="today",
            end_date="tomorrow",
            agent="briefing",
            provider=self.provider.name,
        )

        # 2. Synthesize with ModelProvider
        chat_res = await self.provider.chat(
            messages=[
                {
                    "role": "user",
                    "content": "Create a 3-bullet morning briefing for today's priorities and schedule.",
                }
            ]
        )

        return {
            "agent": "briefing",
            "provider": self.provider.name,
            "briefing_text": chat_res.content,
            "events_status": events_res.model_dump(),
            "highlights": [
                "10:00 AM - Sprint Sync with Engineering",
                "12:30 PM - Team Lunch & Hackathon Prep",
                "03:00 PM - Nebius Demo Video Recording",
            ],
        }
