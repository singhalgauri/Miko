# Owner: Person 2
# Purpose: Permissions configuration REST routes
# TODO(person2): Persist runtime overrides into SQLite permissions table

from backend.app.api.schemas import (
    PermissionsMapResponse,
    UpdatePermissionRequest,
    UpdatePermissionResponse,
)
from backend.app.core.logging import logger
from backend.app.gateway.permission_gateway import get_permissions_config
from fastapi import APIRouter

router = APIRouter(prefix="/api/permissions", tags=["permissions"])

# In-memory permissions store initialized from YAML defaults
_PERMISSIONS_CACHE: dict[str, str] = get_permissions_config()


@router.get("", response_model=PermissionsMapResponse)
async def get_permissions() -> PermissionsMapResponse:
    """Returns the current permissions policy mapping."""
    logger.info("GET /api/permissions")
    return PermissionsMapResponse(permissions=_PERMISSIONS_CACHE)


@router.post("", response_model=UpdatePermissionResponse)
async def update_permission(req: UpdatePermissionRequest) -> UpdatePermissionResponse:
    """Updates the policy rule for an action type (act_alone | ask_first | never)."""
    logger.info("POST /api/permissions update %s -> %s", req.action_type, req.policy)
    _PERMISSIONS_CACHE[req.action_type] = req.policy
    return UpdatePermissionResponse(
        success=True,
        action_type=req.action_type,
        policy=req.policy,
    )
