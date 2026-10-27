# Owner: Person 1
# Purpose: Pydantic schemas and validation logic for tool calls and structured outputs
# TODO(person1): Add validation for calendar and document search tool parameters

from typing import Any

from backend.app.core.logging import logger
from pydantic import BaseModel, Field, ValidationError


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


TOOL_PARAM_SCHEMAS: dict[str, type[BaseModel]] = {
    "file.move": FileMoveParams,
    "file.rename": FileRenameParams,
    "email.send": EmailSendParams,
}


def validate_tool_call(action_type: str, params: dict[str, Any]) -> dict[str, Any]:
    """Validates parameters for a tool call against its schema.

    Returns validated dict or raises ValueError.
    """
    schema = TOOL_PARAM_SCHEMAS.get(action_type)
    if not schema:
        logger.debug("No validation schema found for '%s', passing through", action_type)
        return params

    try:
        validated = schema(**params)
        return validated.model_dump()
    except ValidationError as e:
        logger.error("Validation error for %s: %s", action_type, e)
        raise ValueError(f"Invalid parameters for {action_type}: {e}") from e
