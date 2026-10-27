# Owner: Person 1
# Purpose: LangGraph workflow for inbox triage with approval-pause node for drafts and sending
# TODO(person1): Add LangGraph checkpointing and state persistence to SQLite

from typing import Any, TypedDict

from backend.app.core.logging import logger
from backend.app.providers.base import ModelProvider


class InboxState(TypedDict, total=False):
    emails: list[dict[str, Any]]
    triaged_items: list[dict[str, Any]]
    pending_approval: dict[str, Any] | None
    status: str


def create_inbox_graph(provider: ModelProvider):
    """Creates LangGraph inbox workflow with human-in-the-loop approval pause node."""

    def fetch_emails_node(state: InboxState) -> InboxState:
        logger.info("InboxGraph: Fetching unread emails")
        return {**state, "status": "fetched"}

    def classify_and_triage_node(state: InboxState) -> InboxState:
        logger.info("InboxGraph: Classifying emails with provider %s", provider.name)
        return {**state, "status": "triaged"}

    def approval_pause_node(state: InboxState) -> InboxState:
        logger.info("InboxGraph: Pausing for user approval before sending reply")
        approval = {
            "action": "email.send",
            "recipient": "client@example.com",
            "summary": "Approval required before dispatching email.",
        }
        return {**state, "pending_approval": approval, "status": "paused_for_approval"}

    def finalize_node(state: InboxState) -> InboxState:
        logger.info("InboxGraph: Workflow completed")
        return {**state, "status": "completed"}

    return {
        "nodes": {
            "fetch": fetch_emails_node,
            "triage": classify_and_triage_node,
            "approval_pause": approval_pause_node,
            "finalize": finalize_node,
        },
        "entry_point": "fetch",
    }
