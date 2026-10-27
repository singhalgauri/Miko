# Owner: Person 2
# Purpose: Activity log REST routes for viewing past actions and triggering one-click undo
# TODO(person2): Add pagination and action type filtering

from backend.app.api.schemas import (
    ActivityListResponse,
    ActivityLogItem,
    UndoRequest,
    UndoResponse,
)
from backend.app.core.activity_log import get_activity_logs, undo
from backend.app.core.logging import logger
from fastapi import APIRouter

router = APIRouter(prefix="/api/activity", tags=["activity"])


@router.get("", response_model=ActivityListResponse)
async def list_activity(limit: int = 50) -> ActivityListResponse:
    """Returns recent activity entries from the database with provider provenance."""
    logger.info("GET /api/activity limit=%d", limit)
    raw_logs = get_activity_logs(limit=limit)
    items = []
    for log in raw_logs:
        items.append(
            ActivityLogItem(
                id=str(log.get("id")),
                action_type=str(log.get("action_type")),
                params=log.get("params") or {},
                agent=str(log.get("agent")),
                provider=str(log.get("provider", "mock")),
                status=str(log.get("status")),
                undo_payload=log.get("undo_payload"),
                created_at=str(log.get("created_at") or ""),
            )
        )
    return ActivityListResponse(activities=items, total=len(items))


@router.post("/undo", response_model=UndoResponse)
async def undo_action(req: UndoRequest) -> UndoResponse:
    """Reverts an action using its recorded undo payload."""
    logger.info("POST /api/activity/undo action_id=%s", req.action_id)
    success = undo(req.action_id)
    return UndoResponse(
        success=success,
        action_id=req.action_id,
        message="Action successfully undone" if success else "Action could not be undone or not found",
    )
