# Owner: Person 1
# Purpose: Inbox triage agent for email classification, summarization, and draft creation
# TODO(person1): Implement multi-email batching and priority ranking prompts

from typing import Any

from backend.app.core.logging import logger
from backend.app.gateway.permission_gateway import execute_tool
from backend.app.providers.base import ModelProvider
from backend.app.validation.tool_validation import TriageResult, validate_with_retry


class InboxAgent:
    """Classifies incoming messages and drafts appropriate responses.

    All tool calls go through the permission gateway (execute_tool).
    All model outputs are validated with TriageResult before being acted on.
    The agent pauses at an approval node before sending or saving drafts.
    """

    def __init__(self, provider: ModelProvider):
        self.provider = provider

    async def triage(self, emails: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        """Triages inbox emails and produces action recommendations.

        For each email:
        1. Ask model to classify and produce a TriageResult (JSON).
        2. Validate the structured output before using it.
        3. If suggested_action == 'reply', route draft through gateway (ask_first policy).
        4. Flag important emails (importance == 'high').

        Returns a summary dict with triaged items and pending_approvals.
        """
        logger.info("InboxAgent.triage(): provider='%s', emails=%d", self.provider.name, len(emails or []))

        # Use seed data if no emails passed
        if not emails:
            emails = _load_seed_emails()

        triaged_items: list[dict[str, Any]] = []
        pending_approvals: list[Any] = []
        flagged: list[str] = []

        for email in emails:
            subject = email.get("subject", "(no subject)")
            sender = email.get("from", "unknown")
            snippet = email.get("snippet", "")

            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an email triage assistant. Classify this email and produce a JSON response.\n"
                        "Respond ONLY with valid JSON in this exact format:\n"
                        '{"category":"<action_required|informational|newsletter|spam>",'
                        '"importance":"<high|medium|low>",'
                        '"suggested_action":"<reply|flag|archive|delete|none>",'
                        '"draft_reply":"<optional draft reply text>"}'
                    ),
                },
                {
                    "role": "user",
                    "content": f"From: {sender}\nSubject: {subject}\nSnippet: {snippet}",
                },
            ]

            triage_result, raw = await validate_with_retry(self.provider, messages, TriageResult)

            if triage_result is None:
                logger.error("InboxAgent: triage validation failed for email '%s' — skipping", subject)
                triaged_items.append({
                    "email_id": email.get("id", "?"),
                    "subject": subject,
                    "error": "triage_validation_failed",
                    "raw": raw,
                })
                continue

            # Flag high-importance items
            if triage_result.importance == "high":
                flagged.append(subject)

            item = {
                "email_id": email.get("id", "?"),
                "subject": subject,
                "from": sender,
                "triage": triage_result.model_dump(),
            }

            # Route draft through gateway — policy is 'ask_first', will return ApprovalRequired
            if triage_result.suggested_action == "reply" and triage_result.draft_reply:
                gw_result = execute_tool(
                    action_type="email.draft",
                    params={
                        "recipient": sender,
                        "subject": f"Re: {subject}",
                        "body": triage_result.draft_reply,
                    },
                    agent="inbox",
                    provider=self.provider.name,
                )
                item["gateway_result"] = gw_result.model_dump()
                pending_approvals.append(gw_result.model_dump())

            triaged_items.append(item)

        return {
            "agent": "inbox",
            "provider": self.provider.name,
            "triaged_count": len(triaged_items),
            "flagged_subjects": flagged,
            "triaged_items": triaged_items,
            "pending_approvals": pending_approvals,
        }


def _load_seed_emails() -> list[dict[str, Any]]:
    """Loads seed emails from synthetic_data or returns inline fixtures."""
    import json as _json
    from pathlib import Path

    seed_path = Path(__file__).resolve().parent.parent / "seed" / "synthetic_data" / "sample_emails.json"
    if seed_path.exists():
        try:
            return _json.loads(seed_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    # Inline fixture fallback
    return [
        {
            "id": "email-001",
            "from": "sarah.lead@company.com",
            "subject": "Urgent: Q4 Product Roadmap Final Review",
            "snippet": "Can you review the attached milestone plan before 4 PM today?",
            "unread": True,
            "priority": "high",
        },
        {
            "id": "email-002",
            "from": "newsletter@techinsights.io",
            "subject": "Weekly AI Dispatch #142",
            "snippet": "New breakthroughs in local inference and on-device quantization models...",
            "unread": False,
            "priority": "low",
        },
    ]
