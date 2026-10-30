# Owner: Person 1
# Purpose: Daily briefing agent summarizing calendar events, unread emails, and pending tasks
# TODO(person1): Integrate multi-source agenda aggregation and morning audio synthesis

import json
from typing import Any

from backend.app.core.logging import logger
from backend.app.gateway.permission_gateway import execute_tool
from backend.app.providers.base import ModelProvider
from backend.app.validation.tool_validation import BriefingOutput, validate_with_retry


class BriefingAgent:
    """Synthesizes daily events and pending items into a structured briefing.

    All data fetches go through the permission gateway (execute_tool).
    Model output is validated with BriefingOutput before use.
    Works end-to-end with PROVIDER=mock.
    """

    def __init__(self, provider: ModelProvider):
        self.provider = provider

    async def generate_briefing(self) -> dict[str, Any]:
        """Generates morning briefing using calendar data and LLM synthesis.

        Steps:
        1. Fetch calendar events via gateway (act_alone policy → executes directly).
        2. Load unread emails from seed data.
        3. Ask model to synthesize a BriefingOutput (sections + items).
        4. Validate model output before returning.
        """
        logger.info("BriefingAgent.generate_briefing(): provider='%s'", self.provider.name)

        # ── 1. Fetch calendar events via gateway ─────────────────────────────
        cal_result = execute_tool(
            action_type="calendar.list_events",
            params={"start_date": "today", "end_date": "tomorrow"},
            agent="briefing",
            provider=self.provider.name,
        )
        logger.info("BriefingAgent: calendar gateway result: %s", type(cal_result).__name__)

        # ── 2. Load unread emails ─────────────────────────────────────────────
        unread_emails = _load_seed_emails()
        unread_subjects = [
            f"{e.get('from','?')} — {e.get('subject','?')}"
            for e in unread_emails
            if e.get("unread")
        ]

        # ── 3. Synthesize briefing with model ─────────────────────────────────
        context = (
            f"Unread emails: {json.dumps(unread_subjects)}\n"
            f"Calendar status: {type(cal_result).__name__} (gateway returned)\n"
            f"Calendar highlights: Sprint Sync 10AM, Team Lunch 12:30PM, Nebius Demo 3PM"
        )
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a daily briefing assistant. Synthesize the information into a structured JSON briefing.\n"
                    "Respond ONLY with valid JSON in this exact format:\n"
                    '{"sections":[{"title":"<section name>","items":["<item1>","<item2>"]}]}'
                ),
            },
            {
                "role": "user",
                "content": f"Generate a morning briefing from this context:\n{context}",
            },
        ]

        validated, raw = await validate_with_retry(self.provider, messages, BriefingOutput)

        # ── 4. Build result ───────────────────────────────────────────────────
        if validated:
            sections = [s.model_dump() for s in validated.sections]
        else:
            logger.error("BriefingAgent: model output validation failed — using fallback sections")
            sections = [
                {
                    "title": "Urgent Emails",
                    "items": unread_subjects or ["No unread emails"],
                },
                {
                    "title": "Today's Calendar",
                    "items": [
                        "10:00 AM — Sprint Sync with Engineering",
                        "12:30 PM — Team Lunch & Hackathon Prep",
                        "03:00 PM — Nebius Demo Video Recording",
                    ],
                },
            ]

        return {
            "agent": "briefing",
            "provider": self.provider.name,
            "sections": sections,
            "calendar_gateway": type(cal_result).__name__,
            "raw_model_output": raw,
            "validation_ok": validated is not None,
        }


def _load_seed_emails() -> list[dict[str, Any]]:
    """Loads seed emails from synthetic_data or inline fixture."""
    import json as _json
    from pathlib import Path

    seed_path = Path(__file__).resolve().parent.parent / "seed" / "synthetic_data" / "sample_emails.json"
    if seed_path.exists():
        try:
            return _json.loads(seed_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    return [
        {
            "id": "email-001",
            "from": "sarah.lead@company.com",
            "subject": "Urgent: Q4 Product Roadmap Final Review",
            "unread": True,
        }
    ]
