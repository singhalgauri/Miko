# Owner: Person 1
# Purpose: Loader and Pydantic-validated parser for config/models.registry.yaml

from pathlib import Path
from typing import Any

import yaml
from backend.app.core.logging import logger
from pydantic import BaseModel, ValidationError

# ── Pydantic schema ───────────────────────────────────────────────────────────

class ModelEntry(BaseModel):
    """Validated model registry entry."""

    id: str
    provider: str
    role: str
    ollama_tag: str = "n/a"
    model_id: str = ""                        # used for cloud / Nebius entries
    min_memory_gb_4bit: float = 0.0
    context_length: int = 4096
    licence: str = ""
    supports_vision: bool = False
    supports_tool_calling: bool = False


# ── Path resolution ───────────────────────────────────────────────────────────

def get_registry_path() -> Path:
    """Finds config/models.registry.yaml by walking up from this file's location."""
    current = Path(__file__).resolve().parent
    for _ in range(6):
        candidate = current / "config" / "models.registry.yaml"
        if candidate.exists():
            return candidate
        current = current.parent
    # Fallback relative to cwd (works when pytest is run from repo root)
    return Path("config/models.registry.yaml")


# ── Public helpers ────────────────────────────────────────────────────────────

def load_models_registry() -> list[dict[str, Any]]:
    """Loads, validates, and returns the models list from models.registry.yaml.

    Each entry is validated against ModelEntry. Invalid entries are skipped with
    a warning rather than crashing the whole app.
    Returns plain dicts (not ModelEntry objects) to preserve backward compatibility
    with existing callers.
    """
    path = get_registry_path()
    logger.info("Loading model registry from %s", path)

    if not path.exists():
        logger.warning("models.registry.yaml not found at %s", path)
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as exc:
        logger.error("Failed to parse models.registry.yaml: %s", exc)
        return []

    raw_models = data.get("models", [])
    validated: list[dict[str, Any]] = []
    for raw in raw_models:
        try:
            entry = ModelEntry(**raw)
            validated.append(entry.model_dump())
        except ValidationError as exc:
            logger.warning("Registry entry skipped (validation error): %s — %s", raw.get("id"), exc)

    logger.info("Registry loaded: %d valid model entries", len(validated))
    return validated


def get_model(role: str, provider: str) -> dict[str, Any] | None:
    """Returns the first registry entry matching the given role and provider.

    Useful for agents to look up the canonical model config without importing selector.
    Returns None if no match found.
    """
    models = load_models_registry()
    for m in models:
        if m.get("role") == role and m.get("provider") == provider:
            return m
    logger.warning("No model found for role=%s provider=%s", role, provider)
    return None
