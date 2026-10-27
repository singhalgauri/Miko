# Owner: Person 2
# Purpose: 'While you were away' catch-up service aggregating missed events and updates
# TODO(person2): Add persistent timestamp checkpointing across system sleeps/reboots

from datetime import datetime
from typing import Any

from backend.app.core.logging import logger
from backend.app.providers.base import ModelProvider


class CatchupService:
    """Detects inactivity intervals and synthesizes high-priority updates for the user."""

    def __init__(self, provider: ModelProvider):
        self.provider = provider
        self.last_active_time = datetime.now()

    async def generate_catchup_summary(self) -> dict[str, Any]:
        """Summarizes events and communications received during the user's absence."""
        logger.info("Generating 'While You Were Away' catch-up summary with provider %s", self.provider.name)

        chat_res = await self.provider.chat(
            messages=[
                {
                    "role": "user",
                    "content": "Summarize what happened while the user was away: 2 new emails, 1 calendar shift.",
                }
            ]
        )

        return {
            "last_active": self.last_active_time.isoformat(),
            "summary": chat_res.content,
            "missed_events": [
                {"type": "email", "from": "alex@company.com", "subject": "Project review notes"},
                {"type": "calendar", "event": "Sync moved to 3:00 PM"},
            ],
        }
