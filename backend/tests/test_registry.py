# Owner: Person 2
# Purpose: Smoke tests for Model Registry loader and hardware memory selector
# TODO(person2): Add tests with simulated VRAM limits (4GB, 8GB, 24GB)

from backend.app.registry.hardware import detect_hardware_memory
from backend.app.registry.loader import load_models_registry
from backend.app.registry.selector import select_model_for_task


def test_registry_loading():
    """Verify registry loader successfully reads models.registry.yaml."""
    models = load_models_registry()
    assert len(models) >= 5
    ids = [m["id"] for m in models]
    assert "nemotron-3-nano-4b" in ids
    assert "nebius-nemotron-cloud" in ids


def test_hardware_and_selector():
    """Verify hardware detection and memory-gated model selection."""
    hw = detect_hardware_memory()
    assert "ram_gb" in hw
    assert hw["ram_gb"] > 0

    selected = select_model_for_task(role="router", provider_filter="local")
    assert selected is not None
    assert "min_memory_gb_4bit" in selected
