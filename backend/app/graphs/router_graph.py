# Owner: Person 1
# Purpose: LangGraph workflow for intent classification and sub-agent dispatch
# TODO(person1): Compile into StateGraph when LangGraph runtime is fully loaded

from typing import TypedDict

from backend.app.core.logging import logger
from backend.app.providers.base import ModelProvider


class RouterState(TypedDict, total=False):
    query: str
    target_agent: str
    confidence: float
    status: str
    approval_required: bool


def create_router_graph(provider: ModelProvider):
    """Creates router state graph with approval-pause node when routing to sensitive agents."""

    def analyze_node(state: RouterState) -> RouterState:
        logger.info("RouterGraph: Analyzing query: %s", state.get("query"))
        # Heuristic / model turn
        return {**state, "target_agent": "inbox", "confidence": 0.95}

    def approval_check_node(state: RouterState) -> RouterState:
        # Check if routing requires user confirmation
        target = state.get("target_agent")
        requires_approval = target in ["file_organiser", "inbox"]
        logger.info("RouterGraph: approval_check for %s -> %s", target, requires_approval)
        return {**state, "approval_required": requires_approval, "status": "paused" if requires_approval else "active"}

    def dispatch_node(state: RouterState) -> RouterState:
        logger.info("RouterGraph: Dispatching to %s", state.get("target_agent"))
        return {**state, "status": "dispatched"}

    return {
        "nodes": {
            "analyze": analyze_node,
            "approval_check": approval_check_node,
            "dispatch": dispatch_node,
        },
        "entry_point": "analyze",
    }
