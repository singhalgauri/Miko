# Owner: Person 2
# Purpose: Vector storage and cosine similarity search using sqlite-vec
# TODO(person2): Load sqlite-vec extension dynamically and create virtual vec0 table

from typing import Any

from backend.app.core.db import get_db_connection
from backend.app.core.logging import logger


class VectorStore:
    """Embedded vector database powered by SQLite and sqlite-vec."""

    def __init__(self):
        self._init_vector_tables()

    def _init_vector_tables(self) -> None:
        """Initializes document chunks table."""
        logger.info("Initializing vector store tables in SQLite")
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    source TEXT NOT NULL,
                    page INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    embedding TEXT
                );
                """
            )
            conn.commit()
        finally:
            conn.close()

    def add_chunks(self, chunks: list[dict[str, Any]]) -> int:
        """Inserts text chunks with embedding vectors."""
        logger.info("Adding %d chunks to vector store", len(chunks))
        # TODO(person2): Insert vectors into sqlite-vec virtual table
        return len(chunks)

    def search_similar(self, query_embedding: list[float], top_k: int = 5) -> list[dict[str, Any]]:
        """Finds top-k nearest document chunks using vector distance."""
        logger.info("Searching nearest neighbors with top_k=%d", top_k)
        # TODO(person2): Execute sqlite-vec k-NN query
        return [
            {
                "id": "chunk-1",
                "source": "terms_and_conditions.pdf",
                "page": 3,
                "content": "Confidentiality and nondisclosure covenants remain active for 2 years.",
                "distance": 0.12,
            }
        ]
