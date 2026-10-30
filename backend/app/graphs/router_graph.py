# Owner: Person 1
# Purpose: LangGraph workflow for intent classification and sub-agent dispatch
# TODO(person1): Compile into StateGraph when LangGraph runtime is fully loaded

from typing import Any, TypedDict

from backend.app.agents.router import RouterAgent
from backend.app.core.logging import logger
from backend.app.providers.base import ModelProvider


class RouterState(TypedDict, total=False):
    query: str
    target_agent: str
    confidence: float
    reason: str
    status: str
    approval_required: bool


# Agents that need user confirmation before executing (write/destructive operations)
_APPROVAL_REQUIRED_AGENTS = {"file_organiser", "inbox"}


def create_router_graph(provider: ModelProvider) -> dict[str, Any]:
    """Creates router state graph with approval-pause node when routing to sensitive agents.

    Node order: analyze → approval_check → dispatch
    All routing decisions go through RouterAgent which uses rule-first heuristics
    and falls back to the validated ModelProvider classification.
    """
    agent = RouterAgent(provider)

    async def analyze_node(state: RouterState) -> RouterState:
        """Uses RouterAgent (rules + model) to classify the user query."""
        query = state.get("query", "")
        logger.info("RouterGraph.analyze: query='%s'", query[:80])
        result = await agent.route(query)
        return {
            **state,
            "target_agent": result["target_agent"],
            "confidence": result["confidence"],
            "reason": result["reason"],
            "status": "analyzed",
        }

    def approval_check_node(state: RouterState) -> RouterState:
        """Pauses workflow for sensitive agent targets that require user confirmation."""
        target = state.get("target_agent", "")
        requires_approval = target in _APPROVAL_REQUIRED_AGENTS
        logger.info(
            "RouterGraph.approval_check: target=%s requires_approval=%s",
            target,
            requires_approval,
        )
        return {
            **state,
            "approval_required": requires_approval,
            "status": "paused_for_approval" if requires_approval else "ready",
        }

    def dispatch_node(state: RouterState) -> RouterState:
        """Marks the workflow as dispatched — the caller spawns the sub-agent."""
        logger.info(
            "RouterGraph.dispatch: → %s (confidence=%.2f, reason=%s)",
            state.get("target_agent"),
            state.get("confidence", 0.0),
            state.get("reason", "?"),
        )
        return {**state, "status": "dispatched"}

    # ── Graph definition ──────────────────────────────────────────────────────
    # When LangGraph StateGraph is available, replace this dict with a compiled graph.
    # The node dict and entry_point key are the stable interface teammates depend on.
    return {
        "nodes": {
            "analyze": analyze_node,
            "approval_check": approval_check_node,
            "dispatch": dispatch_node,
        },
        "entry_point": "analyze",
        "edges": [
            ("analyze", "approval_check"),
            ("approval_check", "dispatch"),  # edge only taken when approval_required=False
        ],
    }


async def run_router_graph(provider: ModelProvider, query: str) -> RouterState:
    """Convenience runner that executes the router graph end-to-end and returns final state.

    This is the stable integration point for the FastAPI endpoint and other agents.
    """
    graph = create_router_graph(provider)
    nodes = graph["nodes"]

    state: RouterState = {"query": query, "status": "init"}

    # analyze
    state = await nodes["analyze"](state)

    # approval_check
    state = nodes["approval_check"](state)

    # dispatch only if not waiting for approval
    if not state.get("approval_required"):
        state = nodes["dispatch"](state)

    return state
