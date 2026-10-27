# Owner: Person 1
# Purpose: LangGraph workflow for daily briefing and catch-up synthesis
# TODO(person1): Integrate multi-modal TTS audio generation node

from typing import Any, TypedDict

from backend.app.core.logging import logger
from backend.app.providers.base import ModelProvider


class BriefingState(TypedDict, total=False):
    calendar_events: list[dict[str, Any]]
    unread_emails: list[dict[str, Any]]
    briefing_markdown: str
    status: str


def create_briefing_graph(provider: ModelProvider):
    """Creates LangGraph daily briefing generation workflow."""

    def gather_data_node(state: BriefingState) -> BriefingState:
        logger.info("BriefingGraph: Gathering calendar and notification data")
        return {**state, "status": "data_gathered"}

    def synthesize_node(state: BriefingState) -> BriefingState:
        logger.info("BriefingGraph: Synthesizing briefing with provider %s", provider.name)
        return {
            **state,
            "briefing_markdown": "### Good morning!\nYou have 3 events scheduled today.",
            "status": "synthesized",
        }

    return {
        "nodes": {
            "gather": gather_data_node,
            "synthesize": synthesize_node,
        },
        "entry_point": "gather",
    }
