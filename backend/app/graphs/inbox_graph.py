# Owner: Person 1
# Purpose: LangGraph workflow for inbox triage with approval-pause node for drafts and sending
# TODO(person1): Add LangGraph checkpointing and state persistence to SQLite

from typing import Any, TypedDict

from backend.app.agents.inbox import InboxAgent
from backend.app.core.logging import logger
from backend.app.providers.base import ModelProvider


class InboxState(TypedDict, total=False):
    emails: list[dict[str, Any]]
    triaged_items: list[dict[str, Any]]
    flagged_subjects: list[str]
    pending_approvals: list[dict[str, Any]]
    pending_approval: dict[str, Any] | None  # kept for backward compat
    status: str


def create_inbox_graph(provider: ModelProvider) -> dict[str, Any]:
    """Creates LangGraph inbox workflow with human-in-the-loop approval pause node.

    Node order: fetch → triage → approval_pause → finalize
    The approval_pause node blocks until user confirms any pending email actions.
    No email is sent or saved without gateway approval.
    """
    agent = InboxAgent(provider)

    async def fetch_emails_node(state: InboxState) -> InboxState:
        """Loads emails from seed data (real IMAP fetch is in tools/email_imap.py)."""
        logger.info("InboxGraph.fetch: loading emails")
        from backend.app.agents.inbox import _load_seed_emails
        emails = state.get("emails") or _load_seed_emails()
        return {**state, "emails": emails, "status": "fetched"}

    async def classify_and_triage_node(state: InboxState) -> InboxState:
        """Runs InboxAgent.triage() — validates all model output before using it."""
        logger.info(
            "InboxGraph.triage: %d emails, provider=%s",
            len(state.get("emails", [])),
            provider.name,
        )
        triage_result = await agent.triage(emails=state.get("emails"))
        return {
            **state,
            "triaged_items": triage_result["triaged_items"],
            "flagged_subjects": triage_result["flagged_subjects"],
            "pending_approvals": triage_result["pending_approvals"],
            # backward-compat: single pending_approval for existing gateway tests
            "pending_approval": triage_result["pending_approvals"][0] if triage_result["pending_approvals"] else None,
            "status": "triaged",
        }

    def approval_pause_node(state: InboxState) -> InboxState:
        """Pauses workflow — caller must resume after user grants approval for each action."""
        pending = state.get("pending_approvals", [])
        logger.info(
            "InboxGraph.approval_pause: %d draft(s) pending user approval",
            len(pending),
        )
        return {
            **state,
            "status": "paused_for_approval",
        }

    def finalize_node(state: InboxState) -> InboxState:
        """Marks workflow complete after all approvals resolved (or none pending)."""
        logger.info("InboxGraph.finalize: workflow completed")
        return {**state, "status": "completed"}

    return {
        "nodes": {
            "fetch": fetch_emails_node,
            "triage": classify_and_triage_node,
            "approval_pause": approval_pause_node,
            "finalize": finalize_node,
        },
        "entry_point": "fetch",
        "edges": [
            ("fetch", "triage"),
            ("triage", "approval_pause"),
            ("approval_pause", "finalize"),  # taken only after approvals resolved
        ],
    }


async def run_inbox_graph(
    provider: ModelProvider,
    emails: list[dict[str, Any]] | None = None,
) -> InboxState:
    """Convenience runner: execute the inbox graph and pause at approval node.

    Returns the state after triage (status='paused_for_approval') so the caller
    can present pending_approvals to the user before calling resume_inbox_graph().
    """
    graph = create_inbox_graph(provider)
    nodes = graph["nodes"]

    state: InboxState = {"emails": emails or [], "status": "init"}
    state = await nodes["fetch"](state)
    state = await nodes["triage"](state)
    state = nodes["approval_pause"](state)
    # Do NOT call finalize — caller must confirm approvals first
    return state


async def resume_inbox_graph(state: InboxState, approved: bool = True) -> InboxState:
    """Resumes workflow after user approval decision.

    approved=True → finalize; approved=False → cancel pending actions.
    """
    if not approved:
        logger.info("InboxGraph.resume: user rejected approvals — cancelling pending actions")
        return {**state, "pending_approvals": [], "pending_approval": None, "status": "cancelled"}

    # In real implementation, gateway.confirm_approval() would be called here.
    logger.info("InboxGraph.resume: approvals granted — finalizing")
    return {**state, "status": "completed"}
