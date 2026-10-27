# Owner: Person 2
# Purpose: Hardware detection for system RAM and GPU VRAM
# TODO(person2): Add accurate NVIDIA NVML/nvidia-smi VRAM detection and Apple Silicon unified memory check

from typing import Any

from backend.app.core.logging import logger


def detect_hardware_memory() -> dict[str, Any]:
    """Detects available system RAM and GPU VRAM in gigabytes."""
    logger.info("Detecting hardware memory profile")
    ram_gb = 16.0  # Default fallback detection
    vram_gb = 0.0

    try:
        # Cross-platform basic RAM detection via standard library or fallback
        import os

        if hasattr(os, "sysconf"):
            if "SC_PAGE_SIZE" in os.sysconf_names and "SC_PHYS_PAGES" in os.sysconf_names:
                ram_bytes = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
                ram_gb = round(ram_bytes / (1024**3), 1)
    except Exception as e:
        logger.debug("System RAM query fallback: %s", e)

    # TODO(person2): Execute nvidia-smi query or pynvml if present
    # Stub: Assume standard desktop workstation profile
    return {
        "ram_gb": ram_gb,
        "vram_gb": vram_gb,
        "gpu_available": vram_gb > 0,
        "device_name": "CPU/Default",
    }
