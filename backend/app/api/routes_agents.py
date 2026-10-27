# Owner: Person 1
# Purpose: Agent execution REST routes dispatching to specialist agents or LangGraph workflows
# TODO(person1): Connect LangGraph execution thread IDs and streaming SSE token response

from backend.app.agents.briefing import BriefingAgent
from backend.app.agents.document import DocumentAgent
from backend.app.agents.file_organiser import FileOrganiserAgent
from backend.app.agents.inbox import InboxAgent
from backend.app.agents.router import RouterAgent
from backend.app.api.schemas import AgentRunRequest, AgentRunResponse
from backend.app.core.logging import logger
from backend.app.providers.factory import get_provider
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.post("/{name}/run", response_model=AgentRunResponse)
async def run_agent(name: str, req: AgentRunRequest) -> AgentRunResponse:
    """Dispatches execution to the named specialist agent."""
    logger.info("POST /api/agents/%s/run: input='%s'", name, req.input_text)
    provider = get_provider()

    name_lower = name.lower()

    if name_lower == "router":
        agent = RouterAgent(provider)
        outcome = await agent.route(req.input_text or "Check my emails and schedule")
    elif name_lower == "inbox":
        agent = InboxAgent(provider)
        outcome = await agent.triage()
    elif name_lower == "file_organiser":
        agent = FileOrganiserAgent(provider)
        outcome = await agent.organise_directory(req.parameters.get("target_dir", "Downloads"))
    elif name_lower == "document":
        agent = DocumentAgent(provider)
        outcome = await agent.query(req.input_text or "termination terms")
    elif name_lower == "briefing":
        agent = BriefingAgent(provider)
        outcome = await agent.generate_briefing()
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{name}' not found. Available: router, inbox, file_organiser, document, briefing",
        )

    return AgentRunResponse(
        agent=name,
        provider=provider.name,
        status="completed",
        output=outcome,
    )
