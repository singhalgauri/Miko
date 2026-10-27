# Owner: Person 2
# Purpose: PDF text and metadata extraction using PyMuPDF (fitz)
# TODO(person2): Add layout analysis and table structure extraction

from pathlib import Path
from typing import Any

from backend.app.core.logging import logger


def parse_pdf_document(pdf_path: str | Path) -> list[dict[str, Any]]:
    """Extracts text per page from PDF document.

    Returns list of page dictionaries: [{'page': int, 'text': str}].
    """
    logger.info("Parsing PDF document at %s", pdf_path)
    # TODO(person2): import fitz; doc = fitz.open(pdf_path)
    # Stub: Return simulated page breakdown
    return [
        {
            "page": 1,
            "text": "Sample document header and introduction text.",
        },
        {
            "page": 2,
            "text": "Section 4: Termination clauses and governing law provisions.",
        },
    ]
