# Nebius & NVIDIA Platform Feedback

> Owner: Person 4  
> Purpose: Structured hackathon feedback for Nebius Token Factory, Nebius AI Cloud, and NVIDIA tools  
> TODO(person4): Collect team notes during development and finalize before submission

---

## 1. What Worked

### Nebius Token Factory
- *Fast inference onboarding:* Standard OpenAI-compatible client integration allowed drop-in replacement with zero custom SDK overhead.
- *High-throughput Nemotron serving:* Sub-second time-to-first-token (TTFT) on Nemotron models enabled responsive conversational UX in the UI.
- *Reliable streaming:* Server-Sent Events (SSE) streaming was stable under continuous agent loops.

### Nebius AI Cloud
- *GPU instance provisioning:* Quick instance launch with pre-configured NVIDIA drivers and container runtime.
- *Networking:* Low latency to external endpoints and clear security group management.

### NVIDIA Tools (Nemotron, NeMo, TensorRT-LLM)
- *Model alignment:* Nemotron showed strong compliance with structured tool calling and Pydantic schemas.
- *Quantization:* 4-bit and 8-bit quantized variants ran smoothly in local resource-constrained profiles.

---

## 2. What Didn't Work

### Nebius Token Factory
- *Documentation gaps:* Tool calling support and exact parameter constraints for Nemotron endpoints require clearer documentation and cookbook examples.
- *Rate limit visibility:* Headers indicating remaining tokens/requests per minute were occasionally missing or inconsistent during burst traffic.

### Nebius AI Cloud
- *Cold start latency:* Certain GPU flavor spin-ups experienced queue delays during peak competition windows.

### NVIDIA Tools
- *Edge compatibility:* Running larger Nemotron variants locally on consumer laptops with under 16GB VRAM required aggressive offloading.

---

## 3. Suggestions & Feature Requests

1. **Integrated Playground with JSON Schema Validation**: Built-in UI in Nebius console to test structured tool calls against Nemotron models directly.
2. **Dynamic Quota & Usage Dashboards**: Granular breakdown of token velocity, prompt vs. generation tokens, and error metrics in Token Factory.
3. **Local-to-Cloud Fallback Router**: An official lightweight client middleware to seamlessly fall back from local Ollama to Token Factory when compute is saturated.
