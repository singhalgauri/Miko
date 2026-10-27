# Owner: Person 2
# Purpose: Local filesystem tools with undo-able move and rename
# TODO(person2): Implement real path isolation, sandbox checks, and atomic file operations

from backend.app.core.logging import logger
from backend.app.gateway.permission_gateway import ApprovalRequired, Result, execute_tool


def move_file(
    source: str,
    destination: str,
    agent: str = "file_organiser",
    provider: str = "mock",
) -> Result | ApprovalRequired:
    """Moves a file, routed strictly through the Permission Gateway."""
    logger.info("Tool file.move called: %s -> %s", source, destination)
    return execute_tool(
        action_type="file.move",
        params={"source": source, "destination": destination},
        agent=agent,
        provider=provider,
    )


def rename_file(
    source: str,
    new_name: str,
    agent: str = "file_organiser",
    provider: str = "mock",
) -> Result | ApprovalRequired:
    """Renames a file, routed strictly through the Permission Gateway."""
    logger.info("Tool file.rename called: %s -> %s", source, new_name)
    return execute_tool(
        action_type="file.rename",
        params={"source": source, "new_name": new_name},
        agent=agent,
        provider=provider,
    )


def list_files(
    directory: str,
    agent: str = "file_organiser",
    provider: str = "mock",
) -> Result | ApprovalRequired:
    """Lists files in directory, routed strictly through the Permission Gateway."""
    logger.info("Tool file.list called for: %s", directory)
    return execute_tool(
        action_type="file.list",
        params={"directory": directory},
        agent=agent,
        provider=provider,
    )
