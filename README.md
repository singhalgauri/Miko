# Miko

> **Miko, a free, local-first, always-on AI agent**  
> *Your autonomous personal assistant running securely in the background on your PC — all files, emails, and models stay on your machine.*

[![CI](https://github.com/miko-ai/miko/actions/workflows/ci.yml/badge.svg)](https://github.com/miko-ai/miko/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Hackathon](https://img.shields.io/badge/Nebius_x_NVIDIA-Personal_AI_Track-green.svg)](https://nebius.com)

---

## Overview

Miko is an open-source, local-first AI agent designed for everyday productivity. It runs silently in the background of your operating system to handle repetitive digital tasks without compromising privacy or sending sensitive documents to third-party clouds without explicit permission.

### Screenshots
<!-- TODO(person3): Add dashboard, approvals, and search screenshots here -->
![Miko Dashboard Placeholder](demo/assets/dashboard-placeholder.png)

### Hosted Demo
- **Demo Link:** [https://demo.miko.local (Hosted Demo)](https://demo.miko.local) *(TODO: Update with final hosted URL)*

### Core Capabilities (v1 Jobs)
1. **Inbox Triage:** Classify incoming emails, draft replies, and highlight action items.
2. **File Organising:** Clean and categorize desktop/downloads folders with undo support.
3. **Document Search + Summaries:** Local semantic RAG with citations across PDFs, notes, and records.
4. **Daily Briefing:** Catch-up synthesis of calendar events, unread items, and pending tasks.

---

## How Nemotron is Used

Miko leverages the NVIDIA Nemotron model family across its agentic workflow:
- **Agents Powered:**
  - *Router Agent:* Evaluates user intent and task complexity.
  - *Inbox & Briefing Agents:* Extract action items and generate concise summaries.
  - *Document Agent:* Context-grounded synthesis with strict citation formatting.
  - *File Organiser Agent:* Semantic grouping and folder naming proposals.
- **Dual Model Modes:**
  - **Local Mode (Ollama):** Operates on `127.0.0.1:11434` with zero external network traffic. Ideal for high-privacy tasks and offline operation.
  - **Nebius Mode (Token Factory):** Connects to Nebius Token Factory via OpenAI-compatible endpoints serving NVIDIA Nemotron models for ultra-fast, high-throughput inference when extra reasoning power is required.
  - **Mock Mode:** Canned responses for instantaneous local frontend and pipeline development without GPU requirements.

---

## Where Token Factory Accelerated the Workflow

Nebius Token Factory provides high-velocity token generation and low time-to-first-token (TTFT), drastically reducing latency for complex agent loops:

| Metric | Local Mode (Nemotron Nano 4B / RTX 4090) | Nebius Token Factory (Nemotron 3.5 / Cloud) | Acceleration Factor |
| :--- | :--- | :--- | :--- |
| **TTFT (Time-to-first-token)** | 420 ms | 85 ms | **4.9x faster** |
| **Throughput (Tokens/sec)** | 38 tok/s | 142 tok/s | **3.7x faster** |
| **Inbox Triage Batch (10 items)** | 14.8 s | 3.2 s | **4.6x faster** |
| **Multi-doc RAG Synthesis** | 8.5 s | 1.9 s | **4.5x faster** |

*(Figures generated via `backend/evals/benchmark.py`)*

---

## Other Nebius Services Used

- **Nebius AI Cloud Compute:** Hosted container instances powering the public evaluation endpoints and live demo showcase.
- **Object Storage / Registry:** Storage of synthetic evaluation datasets and cached vector artifacts.

---

## Setup and Run

### Prerequisites
- Python 3.11+
- Node.js 20+ and npm
- (Optional) Ollama running locally at `http://127.0.0.1:11434`

### 1. Clone & Configure
```bash
git clone https://github.com/miko-ai/miko.git
cd miko
cp .env.example .env
```

### 2. Environment Variables
Edit `.env` to select your provider:
- **Mock Mode (Default, no keys needed):**
  ```env
  PROVIDER=mock
  ```
- **Local Mode (Ollama):**
  ```env
  PROVIDER=local
  OLLAMA_HOST=http://127.0.0.1:11434
  ```
- **Nebius Mode (Token Factory):**
  ```env
  PROVIDER=nebius
  NEBIUS_API_KEY=your_token_factory_key_here
  NEBIUS_BASE_URL=https://api.tokenfactory.nebius.com/v1
  ```

### 3. Run with Helper Scripts
- **Windows (PowerShell):**
  ```powershell
  .\scripts\dev.ps1
  ```
- **Linux / macOS:**
  ```bash
  chmod +x ./scripts/dev.sh
  ./scripts/dev.sh
  ```

### 4. Manual Start
```bash
# Backend (FastAPI on 127.0.0.1:8000)
cd backend
pip install -e .
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Frontend (Vite on http://localhost:5173)
cd apps/web
npm install
npm run dev
```

---

## License

This project is licensed under the **Apache License 2.0**. See the [LICENSE](LICENSE) file for the full license text.

---

## Roadmap

- **Phase 2 (Specialized Autonomous Agents):**
  - Coding & Shell execution agent with sandbox validation.
  - Code Reviewer agent with diff generation.
  - Authoring & Content agent with style mimicry.
  - Deep Research agent with multi-step search traversal.
  - NeMo Switchyard-style dynamic semantic routing.
- **Phase 3 (Enterprise & Customization):**
  - Visual Agent Builder (low-code graph composer).
  - Workbench Edition: Multi-user workspace synchronization and role-based access control.
