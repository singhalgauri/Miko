# Owner: Person 1
# Purpose: ModelProvider factory resolving provider from settings
# TODO(person1): Add dynamic caching and reload on settings change

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.providers.base import ModelProvider
from backend.app.providers.mock_provider import MockProvider
from backend.app.providers.nebius_provider import NebiusProvider
from backend.app.providers.ollama_provider import OllamaProvider


def get_provider(provider_name: str | None = None) -> ModelProvider:
    """Returns the configured ModelProvider instance according to application settings."""
    chosen = (provider_name or settings.provider).lower()
    logger.info("Resolving ModelProvider for '%s'", chosen)

    if chosen == "local":
        return OllamaProvider()
    elif chosen == "nebius":
        return NebiusProvider()
    elif chosen == "mock":
        return MockProvider()
    else:
        logger.warning("Unknown provider '%s', defaulting to MockProvider", chosen)
        return MockProvider()
