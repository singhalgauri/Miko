# Owner: Person 1
# Purpose: Inbox triage agent for email classification, summarization, and draft creation
# TODO(person1): Implement multi-email batching and priority ranking prompts

from typing import Any

from backend.app.core.logging import logger
from backend.app.providers.base import ModelProvider
from backend.app.tools.email_imap import draft_email


class InboxAgent:
    """Classifies incoming messages and drafts appropriate responses."""

    def __init__(self, provider: ModelProvider):
        self.provider = provider

    async def triage(self, emails: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        """Triages inbox emails and produces action recommendations."""
        logger.info("InboxAgent running triage with provider='%s'", self.provider.name)

        # Provider chat turn for summarization/classification
        chat_res = await self.provider.chat(
            messages=[
                {
                    "role": "user",
                    "content": "Perform triage on recent inbox messages and highlight urgent action items.",
                }
            ]
        )

        # Example action routed strictly through gateway via tools/email_imap
        draft_outcome = draft_email(
            recipient="client@example.com",
            subject="Re: Quarterly Status Update",
            body="Thank you for your inquiry. Miko is drafting your requested project summary.",
            agent="inbox",
            provider=self.provider.name,
        )

        return {
            "agent": "inbox",
            "provider": self.provider.name,
            "summary": chat_res.content,
            "draft_action": draft_outcome.model_dump(),
            "triaged_count": len(emails) if emails else 3,
        }
