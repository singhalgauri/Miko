#!/usr/bin/env python3
# Owner: Person 1
# Purpose: Smoke test for Nebius Token Factory — chat, tool calling, and embeddings.
#          Reads credentials from environment variables only; the key is NEVER printed or logged.
#
# Usage:
#   export NEBIUS_API_KEY="your-key-here"
#   export NEBIUS_BASE_URL="https://api.tokenfactory.nebius.com/v1"   # optional, this is the default
#   export NEBIUS_MODEL="nvidia/Nemotron-3_5-Lightning"               # optional, this is the default
#   export NEBIUS_EMBED_MODEL="BAAI/bge-en-icl"                       # optional; skip embeddings test if unset
#   py scripts/nebius_smoke_test.py
#
# Requirements: openai>=1.14.0  (pip install openai)

import json
import os
import time

from openai import OpenAI

# ── Config from environment ──────────────────────────────────────────────────
API_KEY = os.environ.get("NEBIUS_API_KEY", "")
BASE_URL = os.environ.get("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1")
MODEL = os.environ.get("NEBIUS_MODEL", "nvidia/Nemotron-3_5-Lightning")
EMBED_MODEL = os.environ.get("NEBIUS_EMBED_MODEL", "")  # leave blank to skip embeddings

if not API_KEY:
    raise SystemExit(
        "ERROR: NEBIUS_API_KEY environment variable is not set.\n"
        "Set it before running: export NEBIUS_API_KEY=<your-key>"
    )

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

SEPARATOR = "-" * 60
results: list[str] = []


def _latency_and_tps(start: float, end: float, completion_tokens: int) -> tuple[float, float, float]:
    latency_ms = (end - start) * 1000
    elapsed_s = end - start
    tps = completion_tokens / elapsed_s if elapsed_s > 0 else 0.0
    return latency_ms, elapsed_s, tps


def _print_metrics(label: str, latency_ms: float, completion_tokens: int, tps: float) -> None:
    print(f"  latency    : {latency_ms:.0f} ms")
    print(f"  completion : {completion_tokens} tokens")
    print(f"  tokens/sec : {tps:.1f} tok/s")


# ── Test A: plain chat ────────────────────────────────────────────────────────
print(SEPARATOR)
print("TEST A — plain chat")
print(SEPARATOR)
try:
    t0 = time.perf_counter()
    resp_a = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a terse assistant."},
            {"role": "user", "content": "In one sentence, what is Miko?"},
        ],
        max_tokens=128,
        temperature=0.2,
    )
    t1 = time.perf_counter()
    completion_tokens_a = resp_a.usage.completion_tokens if resp_a.usage else 0
    latency_ms_a, _, tps_a = _latency_and_tps(t0, t1, completion_tokens_a)
    print(f"  response   : {resp_a.choices[0].message.content!r}")
    _print_metrics("A", latency_ms_a, completion_tokens_a, tps_a)
    results.append("PASS  A: plain chat")
except Exception as exc:  # noqa: BLE001
    print(f"  ERROR: {exc}")
    results.append(f"FAIL  A: plain chat — {exc}")

# ── Test B: tool / function calling ──────────────────────────────────────────
print()
print(SEPARATOR)
print("TEST B — tool calling (get_weather)")
print(SEPARATOR)

DUMMY_TOOL = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Returns current weather for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"},
                },
                "required": ["city"],
            },
        },
    }
]

try:
    t0 = time.perf_counter()
    resp_b = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": "What's the weather in Mumbai right now?"},
        ],
        tools=DUMMY_TOOL,
        tool_choice="auto",
        max_tokens=256,
        temperature=0.0,
    )
    t1 = time.perf_counter()
    completion_tokens_b = resp_b.usage.completion_tokens if resp_b.usage else 0
    latency_ms_b, _, tps_b = _latency_and_tps(t0, t1, completion_tokens_b)
    choice_b = resp_b.choices[0]
    finish_b = choice_b.finish_reason

    tool_calls_b = choice_b.message.tool_calls or []
    if tool_calls_b:
        tc = tool_calls_b[0]
        args = json.loads(tc.function.arguments)
        print(f"  tool_name  : {tc.function.name}")
        print(f"  arguments  : {args}")
        print(f"  finish     : {finish_b}")
        _print_metrics("B", latency_ms_b, completion_tokens_b, tps_b)
        results.append("PASS  B: tool calling — tool_call returned")
    else:
        print(f"  WARNING: No tool_call in response. finish_reason={finish_b!r}")
        print(f"  content    : {choice_b.message.content!r}")
        _print_metrics("B", latency_ms_b, completion_tokens_b, tps_b)
        results.append(
            f"FAIL  B: tool calling — no tool_call returned (finish={finish_b!r}). "
            "Model may not support tool_choice='auto' for this prompt; try tool_choice={'type':'function',...}."
        )
except Exception as exc:  # noqa: BLE001
    print(f"  ERROR: {exc}")
    results.append(f"FAIL  B: tool calling — {exc}")

# ── Test C: embeddings (optional) ────────────────────────────────────────────
print()
print(SEPARATOR)
print("TEST C — embeddings")
print(SEPARATOR)
if not EMBED_MODEL:
    print("  SKIPPED: NEBIUS_EMBED_MODEL not set.")
    results.append("SKIP  C: embeddings — NEBIUS_EMBED_MODEL not set")
else:
    try:
        t0 = time.perf_counter()
        resp_c = client.embeddings.create(
            model=EMBED_MODEL,
            input=["Miko is a local-first always-on AI agent."],
            encoding_format="float",
        )
        t1 = time.perf_counter()
        vec = resp_c.data[0].embedding
        latency_ms_c = (t1 - t0) * 1000
        print(f"  model      : {EMBED_MODEL}")
        print(f"  dimensions : {len(vec)}")
        print(f"  latency    : {latency_ms_c:.0f} ms")
        results.append(f"PASS  C: embeddings — dim={len(vec)} model={EMBED_MODEL}")
    except Exception as exc:  # noqa: BLE001
        print(f"  ERROR: {exc}")
        results.append(f"FAIL  C: embeddings — {exc}")

# ── Summary ───────────────────────────────────────────────────────────────────
print()
print(SEPARATOR)
print("RESULTS")
print(SEPARATOR)
for r in results:
    print(r)
print(SEPARATOR)
