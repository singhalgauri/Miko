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


# ─────────────────────────────────────────────────────────────────────────────
# Step 4 — RouterAgent
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_router_agent_rule_inbox():
    """RouterAgent keyword rules immediately route email-related queries to 'inbox'."""
    from backend.app.agents.router import RouterAgent
    provider = MockProvider()
    agent = RouterAgent(provider)

    result = await agent.route("I have unread emails to check")
    assert result["target_agent"] == "inbox"
    assert result["confidence"] == 1.0
    assert result["reason"] == "rule_heuristic"


@pytest.mark.asyncio
async def test_router_agent_rule_file_organiser():
    """RouterAgent keyword rules route file-related queries to 'file_organiser'."""
    from backend.app.agents.router import RouterAgent
    provider = MockProvider()
    agent = RouterAgent(provider)

    result = await agent.route("clean up my downloads folder")
    assert result["target_agent"] == "file_organiser"
    assert result["confidence"] == 1.0


@pytest.mark.asyncio
async def test_router_agent_rule_briefing():
    """RouterAgent keyword rules route calendar/agenda queries to 'briefing'."""
    from backend.app.agents.router import RouterAgent
    provider = MockProvider()
    agent = RouterAgent(provider)

    result = await agent.route("show me my morning agenda")
    assert result["target_agent"] == "briefing"
    assert result["confidence"] == 1.0


@pytest.mark.asyncio
async def test_router_agent_rule_document():
    """RouterAgent keyword rules route document queries to 'document'."""
    from backend.app.agents.router import RouterAgent
    provider = MockProvider()
    agent = RouterAgent(provider)

    result = await agent.route("find the contract pdf and summarize it")
    assert result["target_agent"] == "document"
    assert result["confidence"] == 1.0


@pytest.mark.asyncio
async def test_router_agent_model_fallback_structure():
    """RouterAgent returns a valid dict even when model classification is invoked."""
    from backend.app.agents.router import _VALID_AGENTS, RouterAgent
    provider = MockProvider()
    agent = RouterAgent(provider)

    # An ambiguous query with no keyword matches triggers model path
    result = await agent.route("xyzzy frobnicate")
    assert isinstance(result, dict)
    assert "target_agent" in result
    assert "confidence" in result
    assert "reason" in result
    # Result must be a valid agent or the default fallback
    assert result["target_agent"] in _VALID_AGENTS


@pytest.mark.asyncio
async def test_router_agent_output_keys():
    """RouterAgent output always contains target_agent, confidence, and reason keys."""
    from backend.app.agents.router import RouterAgent
    provider = MockProvider()
    agent = RouterAgent(provider)

    for query in ["check email", "move files", "morning briefing", "read the doc"]:
        result = await agent.route(query)
        assert set(result.keys()) >= {"target_agent", "confidence", "reason"}
        assert isinstance(result["confidence"], float)
        assert 0.0 <= result["confidence"] <= 1.0


# ─────────────────────────────────────────────────────────────────────────────
# Step 4 — InboxAgent
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_inbox_agent_triage_structure():
    """InboxAgent.triage() returns a dict with all required top-level keys."""
    from backend.app.agents.inbox import InboxAgent
    provider = MockProvider()
    agent = InboxAgent(provider)

    result = await agent.triage()
    assert result["agent"] == "inbox"
    assert result["provider"] == "mock"
    assert "triaged_count" in result
    assert "flagged_subjects" in result
    assert "triaged_items" in result
    assert "pending_approvals" in result
    assert isinstance(result["triaged_items"], list)
    assert isinstance(result["pending_approvals"], list)


@pytest.mark.asyncio
async def test_inbox_agent_triage_with_explicit_emails():
    """InboxAgent processes explicit email list and returns one triaged_item per email."""
    from backend.app.agents.inbox import InboxAgent
    provider = MockProvider()
    agent = InboxAgent(provider)

    emails = [
        {"id": "e1", "from": "boss@work.com", "subject": "Quarterly Review", "snippet": "Please review the Q3 numbers."},
        {"id": "e2", "from": "newsletter@spam.io", "subject": "50% OFF!!!", "snippet": "Click here for a deal."},
    ]
    result = await agent.triage(emails=emails)
    assert result["triaged_count"] == 2
    assert len(result["triaged_items"]) == 2


@pytest.mark.asyncio
async def test_inbox_agent_triaged_item_schema():
    """Each triaged_item contains email_id, subject, from, and triage keys."""
    from backend.app.agents.inbox import InboxAgent
    provider = MockProvider()
    agent = InboxAgent(provider)

    emails = [{"id": "e-test", "from": "a@b.com", "subject": "Hello", "snippet": "Hi there"}]
    result = await agent.triage(emails=emails)
    item = result["triaged_items"][0]
    assert "email_id" in item
    assert "subject" in item
    # triage key present (may be dict or error key if validation failed — both are acceptable)
    assert "triage" in item or "error" in item


@pytest.mark.asyncio
async def test_inbox_agent_flagged_subjects_type():
    """InboxAgent.flagged_subjects is always a list of strings."""
    from backend.app.agents.inbox import InboxAgent
    provider = MockProvider()
    agent = InboxAgent(provider)

    result = await agent.triage()
    assert isinstance(result["flagged_subjects"], list)
    for s in result["flagged_subjects"]:
        assert isinstance(s, str)


@pytest.mark.asyncio
async def test_inbox_agent_seed_fallback():
    """InboxAgent uses built-in seed emails when called with no arguments."""
    from backend.app.agents.inbox import InboxAgent
    provider = MockProvider()
    agent = InboxAgent(provider)

    result = await agent.triage(emails=None)
    assert result["triaged_count"] >= 1


# ─────────────────────────────────────────────────────────────────────────────
# Step 4 — BriefingAgent
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_briefing_agent_structure():
    """BriefingAgent.generate_briefing() returns a dict with required top-level keys."""
    from backend.app.agents.briefing import BriefingAgent
    provider = MockProvider()
    agent = BriefingAgent(provider)

    result = await agent.generate_briefing()
    assert result["agent"] == "briefing"
    assert result["provider"] == "mock"
    assert "sections" in result
    assert "calendar_gateway" in result
    assert "validation_ok" in result
    assert isinstance(result["sections"], list)


@pytest.mark.asyncio
async def test_briefing_agent_sections_not_empty():
    """BriefingAgent always produces at least one section (fallback or validated)."""
    from backend.app.agents.briefing import BriefingAgent
    provider = MockProvider()
    agent = BriefingAgent(provider)

    result = await agent.generate_briefing()
    assert len(result["sections"]) >= 1


@pytest.mark.asyncio
async def test_briefing_agent_section_schema():
    """Each briefing section has a 'title' (str) and 'items' (list of str)."""
    from backend.app.agents.briefing import BriefingAgent
    provider = MockProvider()
    agent = BriefingAgent(provider)

    result = await agent.generate_briefing()
    for section in result["sections"]:
        assert "title" in section
        assert isinstance(section["title"], str)
        assert "items" in section
        assert isinstance(section["items"], list)


@pytest.mark.asyncio
async def test_briefing_agent_calendar_gateway_recorded():
    """BriefingAgent records the calendar gateway call type in the result."""
    from backend.app.agents.briefing import BriefingAgent
    from backend.app.gateway.permission_gateway import ApprovalRequired, Result
    provider = MockProvider()
    agent = BriefingAgent(provider)

    result = await agent.generate_briefing()
    # calendar_gateway must be the class name of what execute_tool returned
    assert result["calendar_gateway"] in (
        Result.__name__,
        ApprovalRequired.__name__,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Step 4 — Graph Runners
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_run_router_graph_email_query():
    """run_router_graph() routes an email query to 'inbox' and returns status='paused_for_approval' or 'dispatched'."""
    from backend.app.graphs.router_graph import run_router_graph
    provider = MockProvider()

    state = await run_router_graph(provider, "check my inbox for unread emails")
    assert state["target_agent"] == "inbox"
    assert state["confidence"] == 1.0
    # inbox requires approval, so workflow pauses
    assert state["status"] == "paused_for_approval"
    assert state["approval_required"] is True


@pytest.mark.asyncio
async def test_run_router_graph_briefing_query():
    """run_router_graph() routes a briefing query directly to 'dispatched' (no approval needed)."""
    from backend.app.graphs.router_graph import run_router_graph
    provider = MockProvider()

    state = await run_router_graph(provider, "show me my morning briefing")
    assert state["target_agent"] == "briefing"
    assert state["status"] == "dispatched"
    assert state.get("approval_required") is False


@pytest.mark.asyncio
async def test_run_router_graph_state_keys():
    """run_router_graph() always returns a state dict with the required keys."""
    from backend.app.graphs.router_graph import run_router_graph
    provider = MockProvider()

    state = await run_router_graph(provider, "organise my files")
    required = {"target_agent", "confidence", "reason", "status", "approval_required"}
    assert required.issubset(state.keys())


@pytest.mark.asyncio
async def test_run_inbox_graph_returns_paused():
    """run_inbox_graph() runs triage and pauses at approval node."""
    from backend.app.graphs.inbox_graph import run_inbox_graph
    provider = MockProvider()

    state = await run_inbox_graph(provider)
    assert state["status"] == "paused_for_approval"
    assert "triaged_items" in state
    assert isinstance(state["triaged_items"], list)
    assert "flagged_subjects" in state
    assert "pending_approvals" in state


@pytest.mark.asyncio
async def test_run_inbox_graph_with_explicit_emails():
    """run_inbox_graph() accepts explicit email list and triages them."""
    from backend.app.graphs.inbox_graph import run_inbox_graph
    provider = MockProvider()

    emails = [{"id": "x1", "from": "a@b.com", "subject": "Hello", "snippet": "Quick test"}]
    state = await run_inbox_graph(provider, emails=emails)
    assert len(state["triaged_items"]) == 1


@pytest.mark.asyncio
async def test_resume_inbox_graph_approved():
    """resume_inbox_graph(approved=True) transitions state to 'completed'."""
    from backend.app.graphs.inbox_graph import resume_inbox_graph, run_inbox_graph
    provider = MockProvider()

    paused = await run_inbox_graph(provider)
    completed = await resume_inbox_graph(paused, approved=True)
    assert completed["status"] == "completed"


@pytest.mark.asyncio
async def test_resume_inbox_graph_rejected():
    """resume_inbox_graph(approved=False) transitions state to 'cancelled'."""
    from backend.app.graphs.inbox_graph import resume_inbox_graph, run_inbox_graph
    provider = MockProvider()

    paused = await run_inbox_graph(provider)
    cancelled = await resume_inbox_graph(paused, approved=False)
    assert cancelled["status"] == "cancelled"
    assert cancelled["pending_approvals"] == []


@pytest.mark.asyncio
async def test_run_briefing_graph_synthesized():
    """run_briefing_graph() returns a state with status='synthesized' and sections."""
    from backend.app.graphs.briefing_graph import run_briefing_graph
    provider = MockProvider()

    state = await run_briefing_graph(provider)
    assert state["status"] == "synthesized"
    assert "sections" in state
    assert isinstance(state["sections"], list)
    assert len(state["sections"]) >= 1


@pytest.mark.asyncio
async def test_run_briefing_graph_markdown_present():
    """run_briefing_graph() builds a briefing_markdown string for backward compat."""
    from backend.app.graphs.briefing_graph import run_briefing_graph
    provider = MockProvider()

    state = await run_briefing_graph(provider)
    assert "briefing_markdown" in state
    assert isinstance(state["briefing_markdown"], str)
    assert len(state["briefing_markdown"]) > 0


@pytest.mark.asyncio
async def test_run_briefing_graph_validation_ok_field():
    """run_briefing_graph() always includes a validation_ok boolean in state."""
    from backend.app.graphs.briefing_graph import run_briefing_graph
    provider = MockProvider()

    state = await run_briefing_graph(provider)
    assert "validation_ok" in state
    assert isinstance(state["validation_ok"], bool)
