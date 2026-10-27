# Owner: Person 2
# Purpose: LangGraph workflow for document RAG search and citation generation
# TODO(person2): Add query expansion node and re-ranking step

from typing import Any, TypedDict

from backend.app.core.logging import logger
from backend.app.providers.base import ModelProvider


class DocumentState(TypedDict, total=False):
    query: str
    retrieved_chunks: list[dict[str, Any]]
    answer: str
    citations: list[dict[str, Any]]
    status: str


def create_document_graph(provider: ModelProvider):
    """Creates LangGraph document search and citation verification workflow."""

    def retrieve_node(state: DocumentState) -> DocumentState:
        logger.info("DocumentGraph: Retrieving chunks for query: %s", state.get("query"))
        return {
            **state,
            "retrieved_chunks": [
                {"text": "Termination clause snippet", "source": "contract.pdf", "page": 4}
            ],
            "status": "retrieved",
        }

    def generate_answer_node(state: DocumentState) -> DocumentState:
        logger.info("DocumentGraph: Generating cited response with provider %s", provider.name)
        return {
            **state,
            "answer": "According to [contract.pdf:p4], the contract terminates in 30 days.",
            "citations": [{"source": "contract.pdf", "page": 4}],
            "status": "completed",
        }

    return {
        "nodes": {
            "retrieve": retrieve_node,
            "generate": generate_answer_node,
        },
        "entry_point": "retrieve",
    }
