# Owner: Person 2
# Purpose: The ONE central permission gateway every tool call must pass through
# TODO(person2): Add persistent storage of pending approval cards and dynamic UI webhooks

from pathlib import Path
from typing import Any

import yaml
from backend.app.core.activity_log import log_action
from backend.app.core.logging import logger
from backend.app.validation.tool_validation import validate_tool_call
from pydantic import BaseModel


class Result(BaseModel):
    """Result of an executed tool call."""

    success: bool
    data: Any = None
    error: str | None = None
    action_id: str | None = None


class ApprovalRequired(BaseModel):
    """Signal indicating user interaction and approval is required before execution."""

    approval_id: str
    action_type: str
    params: dict[str, Any]
    agent: str
    provider: str
    message: str = "User approval required before performing sensitive action"
    status: str = "pending"


def get_permissions_config() -> dict[str, str]:
    """Loads default permissions mapping from config/permissions.default.yaml."""
    current = Path(__file__).resolve().parent
    for _ in range(5):
        candidate = current / "config" / "permissions.default.yaml"
        if candidate.exists():
            with open(candidate, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data.get("permissions", {})
        current = current.parent
    return {
        "file.move": "ask_first",
        "file.rename": "ask_first",
        "file.delete": "never",
        "email.send": "never",
        "email.draft": "act_alone",
    }


def execute_tool(
    action_type: str,
    params: dict[str, Any],
    agent: str,
    provider: str,
) -> Result | ApprovalRequired:
    """The single gateway gatekeeper through which every tool call must pass.

    Checks permissions policy:
      - act_alone: executes tool, logs action with provider, returns Result
      - ask_first: intercepts execution, returns ApprovalRequired
      - never: blocks execution immediately
    """
    logger.info(
        "Permission Gateway: intercepting action='%s' agent='%s' provider='%s'",
        action_type,
        agent,
        provider,
    )

    # 1. Validate parameters
    validated_params = validate_tool_call(action_type, params)

    # 2. Check permission policy
    policy_map = get_permissions_config()
    policy = policy_map.get(action_type, "ask_first")

    if policy == "never":
        logger.warning("Permission Gateway: blocked action '%s' with policy 'never'", action_type)
        return Result(
            success=False,
            error=f"Permission denied: action '{action_type}' is set to 'never' in security policy.",
        )

    if policy == "ask_first":
        logger.info("Permission Gateway: pausing action '%s' for user approval", action_type)
        import uuid

        approval_id = f"appr-{uuid.uuid4().hex[:8]}"
        return ApprovalRequired(
            approval_id=approval_id,
            action_type=action_type,
            params=validated_params,
            agent=agent,
            provider=provider,
            message=f"Action '{action_type}' requires confirmation.",
        )

    # 3. Policy is 'act_alone': dispatch tool execution stub
    logger.info("Permission Gateway: policy 'act_alone', executing '%s'", action_type)

    # Stub tool execution
    undo_payload = None
    if action_type in ("file.move", "file.rename"):
        undo_payload = {
            "action_type": action_type,
            "reverse_params": {
                "source": validated_params.get("destination", ""),
                "destination": validated_params.get("source", ""),
            },
        }

    # Log to activity log with provider provenance (column: provider)
    action_id = log_action(
        action_type=action_type,
        params=validated_params,
        agent=agent,
        provider=provider,
        status="completed",
        undo_payload=undo_payload,
    )

    return Result(
        success=True,
        data={"message": f"Successfully executed {action_type} via {provider}"},
        action_id=action_id,
    )
