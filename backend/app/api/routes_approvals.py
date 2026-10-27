# Owner: Person 2
# Purpose: Approval management REST routes for reviewing and deciding pending actions
# TODO(person2): Persist approvals in dedicated SQLite table and support webhook callbacks

from backend.app.api.schemas import (
    ApprovalDecisionRequest,
    ApprovalDecisionResponse,
    ApprovalItem,
    ApprovalsListResponse,
)
from backend.app.core.logging import logger
from fastapi import APIRouter

router = APIRouter(prefix="/api/approvals", tags=["approvals"])

# In-memory stub list for skeleton
_STUB_APPROVALS: list[ApprovalItem] = [
    ApprovalItem(
        id="appr-101",
        action_type="file.move",
        params={"source": "Downloads/tax_return_2025.pdf", "destination": "Documents/Taxes/tax_return_2025.pdf"},
        agent="file_organiser",
        provider="nebius",
        prompt="Miko wants to move 'tax_return_2025.pdf' to your 'Documents/Taxes' folder.",
        status="pending",
        created_at="2026-10-27T10:00:00Z",
    )
]


@router.get("", response_model=ApprovalsListResponse)
async def list_approvals() -> ApprovalsListResponse:
    """Returns all pending approval requests."""
    logger.info("GET /api/approvals")
    return ApprovalsListResponse(approvals=_STUB_APPROVALS, total=len(_STUB_APPROVALS))


@router.post("/{approval_id}/decide", response_model=ApprovalDecisionResponse)
async def decide_approval(approval_id: str, req: ApprovalDecisionRequest) -> ApprovalDecisionResponse:
    """Submits user decision (approve or reject) for a pending approval."""
    logger.info("POST /api/approvals/%s/decide approved=%s", approval_id, req.approved)
    status_str = "approved" if req.approved else "rejected"
    return ApprovalDecisionResponse(
        id=approval_id,
        status=status_str,
        message=f"Action {approval_id} was {status_str} by user.",
    )
