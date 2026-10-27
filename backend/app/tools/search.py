# Owner: Person 2
# Purpose: Local search and indexing tools
# TODO(person2): Connect with sqlite-vec storage backend

from backend.app.core.logging import logger
from backend.app.gateway.permission_gateway import ApprovalRequired, Result, execute_tool


def search_documents(
    query: str,
    top_k: int = 5,
    agent: str = "document",
    provider: str = "mock",
) -> Result | ApprovalRequired:
    """Executes semantic document search, routed through Permission Gateway."""
    logger.info("Tool document.search called: query='%s' top_k=%d", query, top_k)
    return execute_tool(
        action_type="document.search",
        params={"query": query, "top_k": top_k},
        agent=agent,
        provider=provider,
    )
