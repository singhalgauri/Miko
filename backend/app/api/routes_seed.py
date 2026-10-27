# Owner: Person 3
# Purpose: Seed data reset API route for interactive demo and testing
# TODO(person3): Add support for selecting specific synthetic datasets (e.g. busy vs empty inbox)

from backend.app.api.schemas import ResetSeedResponse
from backend.app.core.logging import logger
from backend.app.seed.reset import reset_all_sample_data
from fastapi import APIRouter

router = APIRouter(prefix="/api/seed", tags=["seed"])


@router.post("/reset", response_model=ResetSeedResponse)
async def reset_seed() -> ResetSeedResponse:
    """Resets database and loads synthetic demonstration data."""
    logger.info("POST /api/seed/reset triggered")
    res = reset_all_sample_data()
    return ResetSeedResponse(
        status=res.get("status", "success"),
        message=res.get("message", "Reset complete"),
        seeded_items=res.get("seeded_items", 0),
    )
