# Owner: Person 2
# Purpose: Optical Character Recognition (OCR) fallback for scanned documents and images
# TODO(person2): Integrate local lightweight Tesseract or rapidocr engine

from pathlib import Path

from backend.app.core.logging import logger


def run_ocr_on_image(image_path: str | Path) -> str:
    """Extracts text from scanned image or unselectable PDF page."""
    logger.info("Running OCR extraction on %s", image_path)
    # TODO(person2): Implement local OCR inference
    return "[OCR Stub Extracted Text: Invoice #1029 Date: 2026-10-27 Total: $142.50]"
