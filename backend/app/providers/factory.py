# Owner: Person 1
# Purpose: ModelProvider factory resolving provider from settings/env


from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.providers.base import ModelProvider
from backend.app.providers.mock_provider import MockProvider
from backend.app.providers.nebius_provider import NebiusProvider
from backend.app.providers.ollama_provider import OllamaProvider

# Cache: one instance per provider name within a process lifetime
_provider_cache: dict[str, ModelProvider] = {}


def get_provider(provider_name: str | None = None) -> ModelProvider:
    """Returns the configured ModelProvider instance.

    Reads PROVIDER env/setting (local | nebius | mock). Caches per name.
    Falls back to MockProvider for unknown values so main never breaks.
    """
    chosen = (provider_name or settings.provider).lower().strip()

    if chosen in _provider_cache:
        return _provider_cache[chosen]

    logger.info("Resolving ModelProvider for '%s'", chosen)

    if chosen == "local":
        provider: ModelProvider = OllamaProvider()
    elif chosen == "nebius":
        provider = NebiusProvider()
    elif chosen == "mock":
        provider = MockProvider()
    else:
        logger.warning("Unknown provider '%s', defaulting to MockProvider", chosen)
        provider = MockProvider()

    _provider_cache[chosen] = provider
    return provider


def clear_provider_cache() -> None:
    """Clears the provider cache — useful in tests to get a fresh instance."""
    _provider_cache.clear()
