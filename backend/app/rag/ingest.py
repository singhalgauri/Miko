# Owner: Person 2
# Purpose: Document ingestion pipeline (chunking, embedding, indexing)
# TODO(person2): Add file watcher for automatic folder indexing

from pathlib import Path
from typing import Any

from backend.app.core.logging import logger
from backend.app.providers.base import ModelProvider
from backend.app.rag.parse_pdf import parse_pdf_document
from backend.app.rag.store import VectorStore


class DocumentIngestionPipeline:
    """Pipelines documents from disk into chunks, embeddings, and vector store."""

    def __init__(self, provider: ModelProvider, vector_store: VectorStore | None = None):
        self.provider = provider
        self.store = vector_store or VectorStore()

    async def ingest_file(self, file_path: str | Path) -> dict[str, Any]:
        """Ingests a file, splits into chunks, embeds via provider, and saves."""
        logger.info("Ingesting file: %s with provider %s", file_path, self.provider.name)

        # 1. Parse text from file
        pages = parse_pdf_document(file_path)

        # 2. Generate embeddings
        texts = [p["text"] for p in pages]
        embeddings = await self.provider.embed(texts)

        # 3. Store in vector database
        chunks = [
            {
                "id": f"{Path(file_path).stem}-p{p['page']}",
                "document_id": str(file_path),
                "source": Path(file_path).name,
                "page": p["page"],
                "content": p["text"],
                "embedding": str(embeddings[idx]),
            }
            for idx, p in enumerate(pages)
        ]
        count = self.store.add_chunks(chunks)

        return {"file": str(file_path), "chunks_indexed": count, "pages": len(pages)}
