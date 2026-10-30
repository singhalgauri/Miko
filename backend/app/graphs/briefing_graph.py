# Owner: Person 1
# Purpose: LangGraph workflow for daily briefing and catch-up synthesis
# TODO(person1): Integrate multi-modal TTS audio generation node

from typing import Any, TypedDict

from backend.app.agents.briefing import BriefingAgent
from backend.app.core.logging import logger
from backend.app.providers.base import ModelProvider


class BriefingState(TypedDict, total=False):
    calendar_events: list[dict[str, Any]]
    unread_emails: list[dict[str, Any]]
    sections: list[dict[str, Any]]
    briefing_markdown: str  # kept for backward compat
    validation_ok: bool
    status: str


def create_briefing_graph(provider: ModelProvider) -> dict[str, Any]:
    """Creates LangGraph daily briefing generation workflow.

    Node order: gather_data → synthesize
    All data access goes through the permission gateway inside BriefingAgent.
    Model output is validated with BriefingOutput before use.
    """
    agent = BriefingAgent(provider)

    def gather_data_node(state: BriefingState) -> BriefingState:
        """Marks data-gathering intent; actual fetch happens inside BriefingAgent."""
        logger.info("BriefingGraph.gather: preparing briefing context")
        return {**state, "status": "data_gathered"}

    async def synthesize_node(state: BriefingState) -> BriefingState:
        """Calls BriefingAgent.generate_briefing() which validates model output."""
        logger.info("BriefingGraph.synthesize: calling BriefingAgent, provider=%s", provider.name)
        result = await agent.generate_briefing()

        # Build legacy briefing_markdown from sections for backward compat
        sections = result.get("sections", [])
        md_lines = ["### Good morning! Here's your Miko briefing.\n"]
        for section in sections:
            md_lines.append(f"\n#### {section.get('title', '')}")
            for item in section.get("items", []):
                md_lines.append(f"- {item}")
        briefing_markdown = "\n".join(md_lines)

        return {
            **state,
            "sections": sections,
            "briefing_markdown": briefing_markdown,
            "validation_ok": result.get("validation_ok", False),
            "status": "synthesized",
        }

    return {
        "nodes": {
            "gather": gather_data_node,
            "synthesize": synthesize_node,
        },
        "entry_point": "gather",
        "edges": [("gather", "synthesize")],
    }


async def run_briefing_graph(provider: ModelProvider) -> BriefingState:
    """Convenience runner: executes the briefing graph end-to-end and returns final state."""
    graph = create_briefing_graph(provider)
    nodes = graph["nodes"]

    state: BriefingState = {"status": "init"}
    state = nodes["gather"](state)
    state = await nodes["synthesize"](state)
    return state
