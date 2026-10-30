# Owner: Person 1
# Purpose: Contract tests for ModelProvider interface, factory, and registry
# No network calls — all providers tested with HTTP stubs or mock responses.

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from backend.app.providers.base import ChatResult, ModelProvider, ToolCall, Usage
from backend.app.providers.factory import clear_provider_cache, get_provider
from backend.app.providers.mock_provider import MockProvider
from backend.app.providers.nebius_provider import NebiusProvider
from backend.app.providers.ollama_provider import OllamaProvider
from backend.app.registry.loader import ModelEntry, get_model, load_models_registry

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

async def _assert_provider_contract(provider: ModelProvider) -> None:
    """Assert all providers satisfy the ModelProvider interface contract."""
    # name property
    assert isinstance(provider.name, str) and provider.name != ""

    # chat — returns ChatResult with correct types
    result = await provider.chat([{"role": "user", "content": "hello"}])
    assert isinstance(result, ChatResult)
    assert isinstance(result.content, str)
    assert isinstance(result.tool_calls, list)
    assert isinstance(result.usage, Usage)
    assert isinstance(result.latency_ms, float)
    assert isinstance(result.provider, str)
    assert result.model != ""

    # chat with tools — tool_calls items are ToolCall objects
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather",
                "parameters": {
                    "type": "object",
                    "properties": {"city": {"type": "string"}},
                    "required": ["city"],
                },
            },
        }
    ]
    result_with_tools = await provider.chat(
        [{"role": "user", "content": "weather in Mumbai"}],
        tools=tools,
    )
    assert isinstance(result_with_tools, ChatResult)
    for tc in result_with_tools.tool_calls:
        assert isinstance(tc, ToolCall)
        assert isinstance(tc.name, str)
        assert isinstance(tc.args, dict)

    # embed — returns list of vectors
    embeddings = await provider.embed(["test sentence", "another sentence"])
    assert len(embeddings) == 2
    assert isinstance(embeddings[0], list)
    assert len(embeddings[0]) > 0
    assert all(isinstance(v, float) for v in embeddings[0])


# ─────────────────────────────────────────────────────────────────────────────
# MockProvider
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_mock_provider_contract():
    """MockProvider satisfies the full ModelProvider contract."""
    provider = MockProvider()
    await _assert_provider_contract(provider)


@pytest.mark.asyncio
async def test_mock_provider_canned_triage():
    """MockProvider returns the canned TriageResult JSON for triage messages."""
    provider = MockProvider()
    result = await provider.chat([
        {"role": "user", "content": "inbox triage all emails"},
    ])
    assert result.content != ""
    assert "category" in result.content or "Mock" in result.content


@pytest.mark.asyncio
async def test_mock_provider_canned_tool_call():
    """MockProvider returns a file.move ToolCall when 'move' is in the message."""
    provider = MockProvider()
    tools = [{"type": "function", "function": {"name": "file.move", "description": "Move file",
              "parameters": {"type": "object", "properties": {
                  "source": {"type": "string"}, "destination": {"type": "string"}
              }, "required": ["source", "destination"]}}}]
    result = await provider.chat(
        [{"role": "user", "content": "move the invoice file please"}],
        tools=tools,
    )
    assert len(result.tool_calls) == 1
    tc = result.tool_calls[0]
    assert tc.name == "file.move"
    assert "source" in tc.args
    assert "destination" in tc.args


@pytest.mark.asyncio
async def test_mock_provider_briefing():
    """MockProvider returns BriefingOutput JSON for briefing messages."""
    provider = MockProvider()
    result = await provider.chat([{"role": "user", "content": "generate morning briefing"}])
    assert "sections" in result.content


@pytest.mark.asyncio
async def test_mock_provider_embed_deterministic():
    """MockProvider embeddings are deterministic for same input."""
    provider = MockProvider()
    e1 = await provider.embed(["hello world"])
    e2 = await provider.embed(["hello world"])
    assert e1 == e2
    assert len(e1[0]) == 768


# ─────────────────────────────────────────────────────────────────────────────
# OllamaProvider (HTTP stub — no real Ollama needed)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ollama_provider_contract_with_stub():
    """OllamaProvider satisfies contract when Ollama is offline (graceful stub)."""
    # Offline Ollama → ConnectError → stub response (still valid ChatResult)
    provider = OllamaProvider(host="http://127.0.0.1:11434")
    result = await provider.chat([{"role": "user", "content": "hello"}])
    assert isinstance(result, ChatResult)
    assert isinstance(result.content, str)
    assert result.provider == "local"


@pytest.mark.asyncio
async def test_ollama_provider_contract_online_stub():
    """OllamaProvider parses a valid Ollama /api/chat response correctly."""
    fake_response = {
        "message": {
            "role": "assistant",
            "content": "Hello from Ollama!",
            "tool_calls": [
                {
                    "function": {
                        "name": "get_weather",
                        "arguments": {"city": "Mumbai"},
                    }
                }
            ],
        },
        "prompt_eval_count": 10,
        "eval_count": 8,
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = fake_response

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("backend.app.providers.ollama_provider.httpx.AsyncClient", return_value=mock_client):
        provider = OllamaProvider(host="http://127.0.0.1:11434")
        provider._chat_model = "nemotron-mini:4b"
        result = await provider.chat([{"role": "user", "content": "weather in Mumbai"}])

    assert result.content == "Hello from Ollama!"
    assert len(result.tool_calls) == 1
    assert result.tool_calls[0].name == "get_weather"
    assert result.tool_calls[0].args == {"city": "Mumbai"}
    assert result.usage.prompt_tokens == 10
    assert result.usage.completion_tokens == 8
    assert result.provider == "local"


def test_ollama_provider_rejects_non_local_host():
    """OllamaProvider raises ValueError for non-127.0.0.1 host."""
    with pytest.raises(ValueError, match="Security violation"):
        OllamaProvider(host="http://0.0.0.0:11434")


# ─────────────────────────────────────────────────────────────────────────────
# NebiusProvider (HTTP stub — no real key needed)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_nebius_provider_contract_no_key():
    """NebiusProvider returns a stub ChatResult when NEBIUS_API_KEY is not set."""
    provider = NebiusProvider(api_key="", base_url="https://api.tokenfactory.nebius.com/v1")
    result = await provider.chat([{"role": "user", "content": "hello"}])
    assert isinstance(result, ChatResult)
    assert "Stub" in result.content or "stub" in result.content.lower()
    assert result.provider == "nebius"


@pytest.mark.asyncio
async def test_nebius_provider_contract_with_stub():
    """NebiusProvider correctly maps OpenAI response to ChatResult."""
    # Build a fake OpenAI-compatible response
    fake_tool_call = MagicMock()
    fake_tool_call.id = "call-abc"
    fake_tool_call.function.name = "get_weather"
    fake_tool_call.function.arguments = json.dumps({"city": "Mumbai"})

    fake_choice = MagicMock()
    fake_choice.message.content = "Calling weather tool."
    fake_choice.message.tool_calls = [fake_tool_call]
    fake_choice.finish_reason = "tool_calls"

    fake_usage = MagicMock()
    fake_usage.prompt_tokens = 20
    fake_usage.completion_tokens = 10
    fake_usage.total_tokens = 30

    fake_response = MagicMock()
    fake_response.choices = [fake_choice]
    fake_response.model = "nvidia/Nemotron-3_5-Lightning"
    fake_response.usage = fake_usage

    mock_create = AsyncMock(return_value=fake_response)

    provider = NebiusProvider(api_key="test-key-stub")
    provider._client = MagicMock()
    provider._client.chat.completions.create = mock_create

    result = await provider.chat(
        [{"role": "user", "content": "weather in Mumbai"}],
        tools=[{"type": "function", "function": {"name": "get_weather"}}],
    )

    assert result.content == "Calling weather tool."
    assert len(result.tool_calls) == 1
    assert result.tool_calls[0].name == "get_weather"
    assert result.tool_calls[0].args == {"city": "Mumbai"}
    assert result.tool_calls[0].id == "call-abc"
    assert result.usage.completion_tokens == 10
    assert result.provider == "nebius"
    assert result.finish_reason == "tool_calls"


# ─────────────────────────────────────────────────────────────────────────────
# Factory
# ─────────────────────────────────────────────────────────────────────────────

def test_factory_picks_mock():
    clear_provider_cache()
    p = get_provider("mock")
    assert isinstance(p, MockProvider)
    assert p.name == "mock"


def test_factory_picks_nebius():
    clear_provider_cache()
    p = get_provider("nebius")
    assert isinstance(p, NebiusProvider)
    assert p.name == "nebius"


def test_factory_picks_local():
    clear_provider_cache()
    p = get_provider("local")
    assert isinstance(p, OllamaProvider)
    assert p.name == "local"


def test_factory_unknown_defaults_to_mock():
    clear_provider_cache()
    p = get_provider("unknown_provider_xyz")
    assert isinstance(p, MockProvider)


def test_factory_caches_same_instance():
    clear_provider_cache()
    p1 = get_provider("mock")
    p2 = get_provider("mock")
    assert p1 is p2


# ─────────────────────────────────────────────────────────────────────────────
# Registry
# ─────────────────────────────────────────────────────────────────────────────

def test_registry_loads_and_validates():
    """Registry loads >= 5 entries, all validated by ModelEntry Pydantic schema."""
    models = load_models_registry()
    assert len(models) >= 5

    ids = [m["id"] for m in models]
    assert "nemotron-3-nano-4b" in ids
    assert "nebius-nemotron-cloud" in ids
    assert "nomic-embed-text" in ids


def test_registry_confirmed_nebius_model_id():
    """Nebius primary model_id must be the confirmed value from docs/nebius-notes.md."""
    models = load_models_registry()
    nebius_cloud = next((m for m in models if m["id"] == "nebius-nemotron-cloud"), None)
    assert nebius_cloud is not None
    assert nebius_cloud["model_id"] == "nvidia/Nemotron-3_5-Lightning"
    assert nebius_cloud["supports_tool_calling"] is True
    assert nebius_cloud["context_length"] == 1_000_000


def test_registry_get_model_helper():
    """get_model(role, provider) returns the first matching entry."""
    cloud = get_model("cloud_primary", "nebius")
    assert cloud is not None
    assert cloud["provider"] == "nebius"
    assert cloud["role"] == "cloud_primary"

    missing = get_model("nonexistent_role", "nebius")
    assert missing is None


def test_registry_model_entry_validation():
    """ModelEntry Pydantic schema validates correctly."""
    entry = ModelEntry(
        id="test-model",
        provider="local",
        role="router",
        ollama_tag="test:latest",
        min_memory_gb_4bit=3.5,
        context_length=8192,
    )
    assert entry.id == "test-model"
    assert entry.supports_tool_calling is False
    assert entry.supports_vision is False
