# Owner: Person 1
# Purpose: Loader and parser for config/models.registry.yaml
# TODO(person1): Add validation schema for registry entries

from pathlib import Path
from typing import Any

import yaml
from backend.app.core.logging import logger


def get_registry_path() -> Path:
    """Finds the models.registry.yaml file in the repo config directory."""
    # Try traversing upwards to find config/models.registry.yaml
    current = Path(__file__).resolve().parent
    for _ in range(5):
        candidate = current / "config" / "models.registry.yaml"
        if candidate.exists():
            return candidate
        current = current.parent
    # Fallback default path relative to repo root
    return Path("config/models.registry.yaml")


def load_models_registry() -> list[dict[str, Any]]:
    """Loads and parses models list from models.registry.yaml."""
    path = get_registry_path()
    logger.info("Loading model registry from %s", path)
    if not path.exists():
        logger.warning("models.registry.yaml not found at %s", path)
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data.get("models", [])
    except Exception as e:
        logger.error("Failed to load models.registry.yaml: %s", e)
        return []
