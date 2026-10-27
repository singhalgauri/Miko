# Owner: Person 2
# Purpose: CalDAV calendar integration tools
# TODO(person2): Add iCalendar format parsing and recurring event support

from typing import Any

from backend.app.core.logging import logger
from backend.app.gateway.permission_gateway import ApprovalRequired, Result, execute_tool


def list_events(
    start_date: str,
    end_date: str,
    agent: str = "briefing",
    provider: str = "mock",
) -> Result | ApprovalRequired:
    """Lists calendar events between dates, routed through Permission Gateway."""
    logger.info("Tool calendar.read called: %s to %s", start_date, end_date)
    return execute_tool(
        action_type="calendar.read",
        params={"start_date": start_date, "end_date": end_date},
        agent=agent,
        provider=provider,
    )


def create_event(
    event_details: dict[str, Any],
    agent: str = "briefing",
    provider: str = "mock",
) -> Result | ApprovalRequired:
    """Creates a calendar event, routed through Permission Gateway."""
    logger.info("Tool calendar.create_event called")
    return execute_tool(
        action_type="calendar.create_event",
        params=event_details,
        agent=agent,
        provider=provider,
    )
