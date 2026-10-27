# Nebius Token Factory & Nemotron Notes

> Owner: Person 1 (Backend Lead)  
> Purpose: Day-1 verification notes for Nebius Token Factory endpoints, Nemotron model identifiers, and tool calling capabilities  
> Priority: Critical blocking dependency for all team members

---

## 1. Verified Base URLs & Authentication

- [ ] **Base URL:** `TODO_CONFIRM_FROM_NEBIUS_DOCS` (e.g., `https://api.tokenfactory.nebius.com/v1` or `https://api.studio.nebius.com/v1`)
- [ ] **Auth Header Format:** `Authorization: Bearer <NEBIUS_API_KEY>` (TODO: Confirm format)
- [ ] **OpenAI SDK Compatibility:** TODO: Confirm client configuration options and default headers

```bash
# Verification curl command (TODO: test on Day 1)
curl -X GET "$NEBIUS_BASE_URL/models" \
  -H "Authorization: Bearer $NEBIUS_API_KEY"
```

---

## 2. Nemotron Model Identifiers

| Target Role | Candidate Model ID | Status | Context Window | Notes |
| :--- | :--- | :--- | :--- | :--- |
| Primary Router | `nvidia/nemotron-3-nano-4b` | TODO: Confirm | TODO | Fast routing heuristics |
| High-Throughput Reasoning | `nvidia/nemotron-3.5-lightning` | TODO: Confirm | TODO | Complex triage and RAG |
| Heavy Synthesis | `nvidia/nemotron-3-nano-30b` | TODO: Confirm | TODO | Comprehensive briefings |
| Fallback Cloud Model | `TODO_CONFIRM_FROM_NEBIUS_DOCS` | TODO: Confirm | TODO | Confirmed endpoint from Nebius catalog |

---

## 3. Function & Tool Calling Support

- [ ] **Native Tool Calling:** Does the Token Factory Nemotron endpoint support standard OpenAI `tools` schema format? (TODO: verify)
- [ ] **Parallel Tool Calls:** Supported or single call per completion turn? (TODO: verify)
- [ ] **Structured Outputs / JSON Mode:** Supported via `response_format={"type": "json_object"}`? (TODO: verify)
- [ ] **Streaming with Tools:** Does delta streaming correctly package `tool_calls` chunks? (TODO: verify)

---

## 4. Rate Limits & Quotas

- **Requests per Minute (RPM):** TODO: Confirm
- **Tokens per Minute (TPM):** TODO: Confirm
- **Concurrent Connections:** TODO: Confirm
- **Error Backoff Strategy:** Implement exponential backoff in `nebius_provider.py` with jitter.
