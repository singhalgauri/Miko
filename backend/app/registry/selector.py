# Owner: Person 2
# Purpose: Model selection engine gating purely on memory fit rather than parameter count
# TODO(person2): Add user override preferences and quantization level trade-offs

from typing import Any

from backend.app.core.logging import logger
from backend.app.registry.hardware import detect_hardware_memory
from backend.app.registry.loader import load_models_registry


def select_model_for_task(role: str = "general", provider_filter: str = "local") -> dict[str, Any] | None:
    """Selects an optimal model from registry that safely fits within available memory."""
    hardware = detect_hardware_memory()
    available_mem = hardware["vram_gb"] if hardware["vram_gb"] > 0 else hardware["ram_gb"]
    logger.info("Selecting model for role='%s' provider='%s' (available memory: %.1f GB)", role, provider_filter, available_mem)

    models = load_models_registry()

    # Filter candidate models matching role and provider
    candidates = [
        m for m in models
        if m.get("provider") == provider_filter and (m.get("role") == role or role == "general")
    ]

    # Gate strictly on memory fit (min_memory_gb_4bit <= available_mem)
    fitting_models = [
        m for m in candidates
        if m.get("min_memory_gb_4bit", 0.0) <= available_mem
    ]

    if fitting_models:
        # Pick the most capable model that fits memory
        chosen = max(fitting_models, key=lambda m: m.get("min_memory_gb_4bit", 0.0))
        logger.info("Selected model: %s (requires %.1f GB)", chosen.get("id"), chosen.get("min_memory_gb_4bit", 0.0))
        return chosen

    # If no local model fits, return fallback or first entry
    if candidates:
        logger.warning("No model strictly fits available memory; returning smallest candidate")
        return min(candidates, key=lambda m: m.get("min_memory_gb_4bit", 0.0))

    return None
