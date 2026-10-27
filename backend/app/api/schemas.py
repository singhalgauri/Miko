# Owner: Shared (P1 / P2 / P3 / P4)
# Purpose: Pydantic request and response schemas for all Miko REST API endpoints
# TODO: Synchronize schema changes with TypeScript types in apps/web/src/api/types.ts

from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------
# Health Schemas
# ---------------------------------------------------------
class HealthResponse(BaseModel):
    status: str = "ok"
    app: str = "Miko"
    provider: str = "mock"


# ---------------------------------------------------------
# Activity Schemas
# ---------------------------------------------------------
class ActivityLogItem(BaseModel):
    id: str
    action_type: str
    params: dict[str, Any]
    agent: str
    provider: str
    status: str
    undo_payload: dict[str, Any] | None = None
    created_at: str | None = None


class ActivityListResponse(BaseModel):
    activities: list[ActivityLogItem]
    total: int


class UndoRequest(BaseModel):
    action_id: str


class UndoResponse(BaseModel):
    success: bool
    action_id: str
    message: str


# ---------------------------------------------------------
# Approvals Schemas
# ---------------------------------------------------------
class ApprovalItem(BaseModel):
    id: str
    action_type: str
    params: dict[str, Any]
    agent: str
    provider: str
    prompt: str
    status: str = "pending"
    created_at: str | None = None


class ApprovalsListResponse(BaseModel):
    approvals: list[ApprovalItem]
    total: int


class ApprovalDecisionRequest(BaseModel):
    approved: bool
    reason: str | None = None


class ApprovalDecisionResponse(BaseModel):
    id: str
    status: str  # approved | rejected
    message: str


# ---------------------------------------------------------
# Permissions Schemas
# ---------------------------------------------------------
class PermissionsMapResponse(BaseModel):
    permissions: dict[str, str] = Field(
        ...,
        description="Map of action_type to policy (act_alone | ask_first | never)",
    )


class UpdatePermissionRequest(BaseModel):
    action_type: str
    policy: str = Field(..., pattern="^(act_alone|ask_first|never)$")


class UpdatePermissionResponse(BaseModel):
    success: bool
    action_type: str
    policy: str


# ---------------------------------------------------------
# Settings Schemas
# ---------------------------------------------------------
class SettingsResponse(BaseModel):
    provider: str = "mock"  # local | nebius | mock
    offline_mode: bool = False
    byo_api_key_enabled: bool = False
    telemetry: bool = False
    nebius_base_url: str = "https://api.tokenfactory.nebius.com/v1"
    ollama_host: str = "http://127.0.0.1:11434"


class UpdateSettingsRequest(BaseModel):
    provider: str | None = None
    offline_mode: bool | None = None
    byo_api_key_enabled: bool | None = None
    telemetry: bool | None = None


# ---------------------------------------------------------
# Seed Schemas
# ---------------------------------------------------------
class ResetSeedResponse(BaseModel):
    status: str
    message: str
    seeded_items: int


# ---------------------------------------------------------
# Agent Run Schemas
# ---------------------------------------------------------
class AgentRunRequest(BaseModel):
    input_text: str = ""
    parameters: dict[str, Any] = Field(default_factory=dict)


class AgentRunResponse(BaseModel):
    agent: str
    provider: str
    status: str
    output: Any
