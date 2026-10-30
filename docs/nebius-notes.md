# Nebius Token Factory & Nemotron Notes

> Owner: Person 1 (Backend Lead)  
> Purpose: Verified setup notes for Nebius Token Factory endpoints, Nemotron model IDs, tool calling, embeddings, and limits.  
> Priority: Critical blocking dependency for all team members  
> Last updated: 2026-10-30

---

## 1. Verified Base URL & Authentication

- **Base URL:** `https://api.tokenfactory.nebius.com/v1`
- **Auth Header:** `Authorization: Bearer <NEBIUS_API_KEY>`
- **OpenAI SDK:** Drop-in compatible — set `base_url` and `api_key` in `AsyncOpenAI(...)`, no custom headers needed.

```python
from openai import AsyncOpenAI
import os

client = AsyncOpenAI(
    api_key=os.environ["NEBIUS_API_KEY"],
    base_url="https://api.tokenfactory.nebius.com/v1",
)
```

**Verification curl:**
```bash
curl -X GET "$NEBIUS_BASE_URL/models" \
  -H "Authorization: Bearer $NEBIUS_API_KEY"
```

---

## 2. Nemotron Model Identifiers (Confirmed via Nebius docs + community references)

| Target Role | Model ID (direct API) | Context Window | Notes |
| :--- | :--- | :--- | :--- |
| **Primary (fast, tool calling)** | `nvidia/Nemotron-3_5-Lightning` | 1 000 000 tokens | ✅ CHOSEN: 30B MoE (3B active), fast, tool-call support |
| Heavy synthesis / reasoning | `nvidia/nemotron-3-super-120b-a12b` | 128 000 tokens | Larger, slower, better quality |
| Ultra / frontier | `nvidia/Nemotron-3-Ultra-550b-a55b` | 128 000 tokens | Largest available |
| Nano 30B | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` | 32 768 tokens | Lighter option |

**Chosen primary model for Miko:** `nvidia/Nemotron-3_5-Lightning`  
Reasons: fastest (MoE, 3B active params), 1M context window, native tool-calling support, good throughput/cost ratio.

> ⚠️ Note: some router libraries (LiteLLM, Mastra) prefix with `nebius/` → `nebius/nvidia/Nemotron-3_5-Lightning`. The direct Nebius API does NOT need the `nebius/` prefix.

---

## 3. Function & Tool Calling Support

- **Native Tool Calling:** ✅ YES — `nvidia/Nemotron-3_5-Lightning` supports standard OpenAI `tools` schema via `/v1/chat/completions`.
- **Parallel Tool Calls:** ✅ Supported (multiple tool_calls objects in one response turn).
- **Structured Outputs / JSON Mode:** ✅ `response_format={"type": "json_object"}` works via the OpenAI-compatible endpoint.
- **Streaming with Tools:** ✅ SSE streaming stable; `tool_calls` chunks arrive in delta format as with OpenAI.
- **Verification:** Run `scripts/nebius_smoke_test.py` — Test B exercises tool calling.

---

## 4. Embeddings

- **Available:** ✅ YES — Nebius hosts BAAI embedding models (not NVIDIA/Nemotron-specific).
- **Primary Embedding Model:** `BAAI/bge-en-icl`
- **Context Window:** 32 768 tokens
- **Endpoint:** `POST https://api.tokenfactory.nebius.com/v1/embeddings`
- **Dimensions:** Model-dependent (check model card for exact dim; typically 4096 for bge-en-icl).
- **Note:** No NVIDIA-branded embedding model is currently listed in the Nebius Token Factory catalogue. Use `BAAI/bge-en-icl` for cloud embeddings; use `nomic-embed-text` via Ollama for local embeddings.

```bash
curl --request POST \
  --url https://api.tokenfactory.nebius.com/v1/embeddings \
  --header "Authorization: Bearer $NEBIUS_API_KEY" \
  --header "Content-Type: application/json" \
  --data '{
    "model": "BAAI/bge-en-icl",
    "input": "Your text here",
    "encoding_format": "float"
  }'
```

---

## 5. Rate Limits & Quotas

- **System:** Dynamic / elastic — NOT fixed static caps.
- **Scale-up rule:** If average usage in a 15-minute window ≥ 80 % of current cap, limits auto-expand by 20 % (×1.2) for the next window.
- **Ceiling:** Can auto-scale up to 20× base allocation.
- **Enterprise:** Dedicated capacity + formal SLA if sustained burst needed.
- **Recommended client strategy:** Exponential backoff with jitter on 429/503 (implemented in `nebius_provider.py`).
- **Backoff config in provider:** initial_delay=1 s, max_delay=60 s, jitter=±0.5 s, max_retries=3.

---

## 6. Latency & Performance Benchmark

<!-- TODO(person1): Fill in actual numbers after running scripts/nebius_smoke_test.py with production key -->

| Test | Latency (ms) | Completion Tokens | Tokens/sec |
| :--- | :--- | :--- | :--- |
| A — plain chat | TODO | TODO | TODO |
| B — tool calling | TODO | TODO | TODO |
| C — embeddings (BAAI/bge-en-icl) | TODO | n/a | n/a |

> **Run command to fill this table:**
> ```bash
> export NEBIUS_API_KEY="<your-key>"
> export NEBIUS_EMBED_MODEL="BAAI/bge-en-icl"
> py scripts/nebius_smoke_test.py
> ```
> Then paste the output here and remove this TODO block.

---

## 7. Surprises & Gotchas

1. **Model ID underscore vs dot:** The model ID uses an underscore: `Nemotron-3_5-Lightning` (not `3.5`). Sending `3.5` returns a 404.
2. **No `nebius/` prefix needed for direct API:** Only needed when routing through LiteLLM or Mastra proxy.
3. **Embeddings are BAAI, not Nemotron:** No NVIDIA-branded embedding model is in the public catalogue. Use `BAAI/bge-en-icl`.
4. **Dynamic rate limits:** Limits grow automatically — no need to pre-request quota increases for hackathon traffic.
5. **1M context window:** `Nemotron-3_5-Lightning` has a 1M-token context window — ideal for long conversation histories and document RAG.
6. **Tool calling only via chat completions:** The `/v1/completions` (raw completion) endpoint does NOT support tools; always use `/v1/chat/completions`.
