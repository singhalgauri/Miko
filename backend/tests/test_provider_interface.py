# Owner: Person 1
# Purpose: Smoke tests for ModelProvider interface contract
# TODO(person1): Add contract validation tests for OllamaProvider and NebiusProvider

import pytest
from backend.app.providers.base import ModelProvider
from backend.app.providers.factory import get_provider
from backend.app.providers.mock_provider import MockProvider


@pytest.mark.asyncio
async def test_mock_provider_contract():
    """Verify MockProvider adheres to ModelProvider contract."""
    provider: ModelProvider = get_provider("mock")
    assert isinstance(provider, MockProvider)
    assert provider.name == "mock"

    # Chat contract
    chat_result = await provider.chat([{"role": "user", "content": "Hello Miko"}])
    assert chat_result.content != ""
    assert isinstance(chat_result.tool_calls, list)

    # Embed contract
    embeddings = await provider.embed(["test sentence"])
    assert len(embeddings) == 1
    assert len(embeddings[0]) == 384
