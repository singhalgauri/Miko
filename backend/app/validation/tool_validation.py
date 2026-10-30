# Owner: Person 1
# Purpose: Pydantic schemas and validation logic for tool calls and structured agent outputs.
#          All model output MUST pass through validate_output() before being acted on.

import json
from typing import Any, TypeVar

from backend.app.core.logging import logger
from backend.app.providers.base import ChatResult, ModelProvider
from pydantic import BaseModel, Field, ValidationError

T = TypeVar("T", bound=BaseModel)


# ─────────────────────────────────────────────────────────────────────────────
# Tool-call parameter schemas
# ─────────────────────────────────────────────────────────────────────────────

class FileMoveParams(BaseModel):
    """Schema for file.move tool parameters."""

    source: str = Field(..., description="Source path of the file to move")
    destination: str = Field(..., description="Destination folder or filepath")


class FileRenameParams(BaseModel):
    """Schema for file.rename tool parameters."""

    source: str = Field(..., description="Source path of the file to rename")
    new_name: str = Field(..., description="New name for the file")


class EmailSendParams(BaseModel):
    """Schema for email.send tool parameters."""

    recipient: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., description="Body of the email")


class EmailDraftParams(BaseModel):
    """Schema for email.draft tool parameters."""

    recipient: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., description="Draft body of the email")


class CalendarListParams(BaseModel):
    """Schema for calendar.list_events tool parameters."""

    start_date: str = Field(..., description="Start date ISO8601 or 'today'")
    end_date: str = Field(..., description="End date ISO8601 or 'tomorrow'")


TOOL_PARAM_SCHEMAS: dict[str, type[BaseModel]] = {
    "file.move": FileMoveParams,
    "file.rename": FileRenameParams,
    "email.send": EmailSendParams,
    "email.draft": EmailDraftParams,
    "calendar.list_events": CalendarListParams,
}


def validate_tool_call(action_type: str, params: dict[str, Any]) -> dict[str, Any]:
    """Validates parameters for a tool call against its registered schema.

    Returns validated dict on success, raises ValueError on schema mismatch.
    Unknown tool types pass through with a debug log (forward-compatible).
    """
    schema = TOOL_PARAM_SCHEMAS.get(action_type)
    if not schema:
        logger.debug("No validation schema for '%s' — passing through", action_type)
        return params

    try:
        validated = schema(**params)
        return validated.model_dump()
    except ValidationError as exc:
        logger.error("Validation error for %s: %s", action_type, exc)
        raise ValueError(f"Invalid parameters for {action_type}: {exc}") from exc


# ─────────────────────────────────────────────────────────────────────────────
# Structured output schemas (agents)
# ─────────────────────────────────────────────────────────────────────────────

class TriageResult(BaseModel):
    """Structured triage output from the InboxAgent."""

    category: str = Field(
        ...,
        description="One of: action_required | informational | newsletter | spam",
    )
    importance: str = Field(
        ...,
        description="One of: high | medium | low",
    )
    suggested_action: str = Field(
        ...,
        description="One of: reply | flag | archive | delete | none",
    )
    draft_reply: str = Field(
        default="",
        description="Optional draft reply text",
    )


class BriefingItem(BaseModel):
    """A single line item inside a briefing section."""

    text: str


class BriefingSection(BaseModel):
    """A titled section in the briefing (e.g. 'Urgent Emails', 'Calendar')."""

    title: str
    items: list[str] = Field(default_factory=list)


class BriefingOutput(BaseModel):
    """Structured daily briefing output from the BriefingAgent."""

    sections: list[BriefingSection] = Field(default_factory=list)


class RouterOutput(BaseModel):
    """Structured routing decision."""

    target_agent: str = Field(
        ...,
        description="One of: inbox | file_organiser | document | briefing",
    )
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    reason: str = Field(default="model_classification")


# ─────────────────────────────────────────────────────────────────────────────
# Validation helpers
# ─────────────────────────────────────────────────────────────────────────────

def validate_output(raw_text: str, schema: type[T]) -> tuple[T | None, str | None]:
    """Parses raw_text (JSON) and validates it against schema.

    Returns (validated_object, None) on success, or (None, error_message) on failure.
    The caller must handle the failure case before acting on the output.
    """
    try:
        data = json.loads(raw_text)
        obj = schema(**data)
        return obj, None
    except json.JSONDecodeError as exc:
        err = f"Output is not valid JSON: {exc}"
        logger.warning("validate_output: %s", err)
        return None, err
    except ValidationError as exc:
        err = f"Output failed schema validation ({schema.__name__}): {exc}"
        logger.warning("validate_output: %s", err)
        return None, err
    except Exception as exc:
        err = f"Unexpected validation error: {exc}"
        logger.warning("validate_output: %s", err)
        return None, err


async def validate_with_retry(
    provider: ModelProvider,
    messages: list[dict[str, str]],
    schema: type[T],
    tools: list[dict[str, Any]] | None = None,
) -> tuple[T | None, str]:
    """Calls provider.chat(), validates the result against schema.

    If validation fails, sends a second repair turn with the validation error,
    then validates once more. Returns (typed_result, final_raw_text).
    Never acts on unvalidated model output.
    """
    result: ChatResult = await provider.chat(messages, tools=tools)
    raw = result.content

    obj, err = validate_output(raw, schema)
    if obj is not None:
        return obj, raw

    # One repair attempt: send the error back to the model
    logger.info("validate_with_retry: first attempt failed (%s), sending repair turn", err)
    repair_messages = list(messages) + [
        {"role": "assistant", "content": raw},
        {
            "role": "user",
            "content": (
                f"Your previous response did not match the required JSON schema.\n"
                f"Error: {err}\n"
                f"Please respond ONLY with valid JSON matching the schema. "
                f"Do not include any explanation or markdown fencing."
            ),
        },
    ]
    repair_result: ChatResult = await provider.chat(repair_messages, tools=tools)
    raw2 = repair_result.content

    obj2, err2 = validate_output(raw2, schema)
    if obj2 is not None:
        logger.info("validate_with_retry: repair turn succeeded")
        return obj2, raw2

    logger.error(
        "validate_with_retry: repair turn also failed (%s). Returning None — caller must handle.",
        err2,
    )
    return None, raw2
