# Owner: Person 1 & Person 2
# Purpose: Model registry and hardware selector package

from backend.app.registry.hardware import detect_hardware_memory
from backend.app.registry.loader import get_model, load_models_registry
from backend.app.registry.selector import select_model_for_task

__all__ = ["load_models_registry", "get_model", "detect_hardware_memory", "select_model_for_task"]
