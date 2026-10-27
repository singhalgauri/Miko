# Owner: Person 2
# Purpose: Semantic retrieval engine returning grounded context and page citations
# TODO(person2): Implement reciprocal rank fusion (RRF) combining keyword and dense search

from typing import Any

from backend.app.core.logging import logger
from backend.app.providers.base import ModelProvider
from backend.app.rag.store import VectorStore


class DocumentRetriever:
    """Retrieves relevant document snippets with verified file and page citations."""

    def __init__(self, provider: ModelProvider, vector_store: VectorStore | None = None):
        self.provider = provider
        self.store = vector_store or VectorStore()

    async def retrieve_with_citations(self, query: str, top_k: int = 4) -> list[dict[str, Any]]:
        """Retrieves passages matching query along with citation metadata."""
        logger.info("Retrieving contexts for query: '%s'", query)

        # 1. Embed query
        embeddings = await self.provider.embed([query])
        query_vec = embeddings[0]

        # 2. Vector similarity search
        hits = self.store.search_similar(query_vec, top_k=top_k)

        # 3. Format citations
        results = []
        for hit in hits:
            results.append(
                {
                    "content": hit["content"],
                    "source": hit["source"],
                    "page": hit["page"],
                    "citation": f"[{hit['source']}:p{hit['page']}]",
                    "score": 1.0 - hit.get("distance", 0.0),
                }
            )
        return results
