# Owner: Person 1 & Person 2
# Purpose: Model registry and hardware selector package
# TODO(person1, person2): Export registry helpers

from backend.app.registry.hardware import detect_hardware_memory
from backend.app.registry.loader import load_models_registry
from backend.app.registry.selector import select_model_for_task

__all__ = ["load_models_registry", "detect_hardware_memory", "select_model_for_task"]
