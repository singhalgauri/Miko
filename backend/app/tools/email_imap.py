# Owner: Person 2
# Purpose: Email IMAP / SMTP operations gated by permission gateway
# TODO(person2): Add secure TLS IMAP sync and encrypted local credential storage

from backend.app.core.logging import logger
from backend.app.gateway.permission_gateway import ApprovalRequired, Result, execute_tool


def draft_email(
    recipient: str,
    subject: str,
    body: str,
    agent: str = "inbox",
    provider: str = "mock",
) -> Result | ApprovalRequired:
    """Drafts an email, routed through the Permission Gateway."""
    logger.info("Tool email.draft called for: %s", recipient)
    return execute_tool(
        action_type="email.draft",
        params={"recipient": recipient, "subject": subject, "body": body},
        agent=agent,
        provider=provider,
    )


def send_email(
    recipient: str,
    subject: str,
    body: str,
    agent: str = "inbox",
    provider: str = "mock",
) -> Result | ApprovalRequired:
    """Sends an email, routed through the Permission Gateway."""
    logger.info("Tool email.send called for: %s", recipient)
    return execute_tool(
        action_type="email.send",
        params={"recipient": recipient, "subject": subject, "body": body},
        agent=agent,
        provider=provider,
    )
