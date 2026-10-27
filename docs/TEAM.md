# Team Ownership & Responsibilities

> Owner: Shared  
> Purpose: Explicit mapping of modules, files, and deliverables across all 4 team members  
> Reference: See also `CONTRIBUTING.md` and `.github/CODEOWNERS`

---

## Ownership Matrix

| Member | Primary Focus | Direct Module Ownership | Key Deliverables |
| :--- | :--- | :--- | :--- |
| **Person 1** | Core agents and model layer (Backend Lead) | • `backend/app/providers/` (base, ollama, nebius, mock, factory)<br>• `config/models.registry.yaml`<br>• `backend/app/registry/loader.py`<br>• `backend/app/agents/` (router.py, inbox.py, briefing.py)<br>• `backend/app/graphs/` (router_graph.py, inbox_graph.py, briefing_graph.py)<br>• `backend/app/validation/`<br>• `backend/tests/test_provider_interface.py`<br>• `docs/nebius-notes.md` | • Abstract `ModelProvider` contract<br>• Reliable Ollama and Nebius Token Factory clients<br>• Core agent graphs in LangGraph<br>• Day-1 Nebius endpoint confirmation |
| **Person 2** | Safety, data, and background services | • `backend/app/gateway/`<br>• `config/permissions.default.yaml`<br>• `backend/app/core/` (db, activity_log with undo, config, logging)<br>• `backend/app/tools/`<br>• `backend/app/agents/` (file_organiser.py, document.py)<br>• `backend/app/graphs/` (file_organiser_graph.py, document_graph.py)<br>• `backend/app/rag/`<br>• `backend/app/registry/` (hardware.py, selector.py)<br>• `backend/app/service/`<br>• `scripts/install_service_*.md`<br>• `backend/tests/` (test_gateway.py, test_registry.py) | • Central Permission Gateway (`execute_tool`)<br>• SQLite storage and Activity Log with Undo<br>• File and Document RAG engines<br>• Background scheduler and catchup service |
| **Person 3** | Frontend, desktop shell, and demo content | • `apps/web/` (React + TypeScript + Vite UI)<br>• `apps/desktop/` (Tauri desktop shell)<br>• `backend/app/seed/` (synthetic mailbox, calendar, documents, reset)<br>• `docs/demo-video-plan.md`<br>• `demo/` (script.md, shot-list.md, assets) | • Full responsive web dashboard & pages<br>• "Prompts leave this machine" banner<br>• Activity log with one-click undo<br>• Realistic synthetic test data<br>• 3-minute demo script and shot list |
| **Person 4** | Deployment, evals, and hackathon submission | • Root files (`LICENSE`, `.gitignore`, `.editorconfig`, `Makefile`, `.env.example`, `CONTRIBUTING.md`, `.github/`)<br>• `deploy/` (Dockerfile, docker-compose.yml, nebius/README.md)<br>• `docs/release.md`<br>• `backend/evals/` (run_evals.py, benchmark.py, datasets)<br>• `README.md`, `FEEDBACK.md`<br>• `docs/submission-checklist.md`<br>• `scripts/` (dev.sh, dev.ps1, seed.sh) | • Reproducible CI/CD pipeline<br>• Multi-stage Docker container build<br>• Evaluation and benchmarking harness<br>• Polished submission assets & checklist |

---

## Shared Contracts & Cross-Review Rules

The following files require cross-review by affected leads before merge:
- `backend/app/main.py`: Route registration only; no business logic.
- `backend/app/api/schemas.py`: Pydantic models for all API endpoints. Must be finalized early for frontend consumption.
- `docs/architecture.md`: System-wide specifications and data flow diagrams.
- `backend/pyproject.toml`: Shared Python dependencies.
- `apps/web/package.json`: Shared JavaScript/TypeScript dependencies.
