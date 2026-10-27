# Owner: Person 2
# Purpose: System settings REST routes (provider selection, offline mode, telemetry)
# TODO(person2): Sync settings changes with persistent SQLite config table

from typing import Any

from backend.app.api.schemas import SettingsResponse, UpdateSettingsRequest
from backend.app.core.config import settings
from backend.app.core.logging import logger
from fastapi import APIRouter

router = APIRouter(prefix="/api/settings", tags=["settings"])

# Dynamic settings state
_RUNTIME_SETTINGS: dict[str, Any] = {
    "provider": settings.provider,
    "offline_mode": settings.offline_mode,
    "byo_api_key_enabled": settings.byo_api_key_enabled,
    "telemetry": settings.telemetry,
    "nebius_base_url": settings.nebius_base_url,
    "ollama_host": settings.ollama_host,
}


@router.get("", response_model=SettingsResponse)
async def get_settings() -> SettingsResponse:
    """Returns the current application settings."""
    logger.info("GET /api/settings")
    return SettingsResponse(**_RUNTIME_SETTINGS)


@router.post("", response_model=SettingsResponse)
async def update_settings(req: UpdateSettingsRequest) -> SettingsResponse:
    """Updates runtime settings such as active model provider."""
    logger.info("POST /api/settings: %s", req.model_dump(exclude_unset=True))
    if req.provider is not None:
        _RUNTIME_SETTINGS["provider"] = req.provider.lower()
        settings.provider = req.provider.lower()
    if req.offline_mode is not None:
        _RUNTIME_SETTINGS["offline_mode"] = req.offline_mode
        settings.offline_mode = req.offline_mode
    if req.byo_api_key_enabled is not None:
        _RUNTIME_SETTINGS["byo_api_key_enabled"] = req.byo_api_key_enabled
    if req.telemetry is not None:
        _RUNTIME_SETTINGS["telemetry"] = req.telemetry

    return SettingsResponse(**_RUNTIME_SETTINGS)
