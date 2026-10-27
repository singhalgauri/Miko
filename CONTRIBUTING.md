# Contributing to Miko

> Owner: Person 4  
> Purpose: Team contribution guidelines, branching conventions, PR workflow, and ownership table  
> TODO(person4): Update PR template and review turnaround expectations

Welcome to the Miko monorepo! Miko is an open-source, local-first, always-on AI agent built for the Nebius x NVIDIA Global AI Hackathon.

---

## 1. Branch Naming Conventions

All contributors should branch off `main` using descriptive prefixes:

- `person1/<feature-or-fix-name>` (or `person1-core`)
- `person2/<feature-or-fix-name>` (or `person2-safety`)
- `person3/<feature-or-fix-name>` (or `person3-frontend`)
- `person4/<feature-or-fix-name>` (or `person4-deploy`)
- `feat/<short-description>`
- `fix/<short-description>`
- `chore/<short-description>`

Examples:
- `feat/nebius-provider-auth`
- `fix/permission-gateway-timeout`
- `chore/ci-caching`

---

## 2. Commit Message Style

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat(scope): add new feature`
- `fix(scope): resolve bug`
- `docs(scope): update documentation`
- `refactor(scope): refactor code without behavior change`
- `test(scope): add or modify tests`
- `chore(scope): build, tooling, or dependency updates`

Examples:
- `feat(providers): implement Nebius Token Factory client integration`
- `fix(gateway): enforce ask_first check on file moves`
- `docs(readme): add Nemotron benchmark acceleration table`

---

## 3. Pull Request (PR) Rules

1. **Keep PRs Small & Focused**: Avoid sweeping multi-module changes without coordination.
2. **Review Requirements**:
   - Every PR touching dedicated modules must be reviewed and approved by the module owner (see Ownership Table below).
   - Any PR touching **Shared Modules** (`main.py`, `schemas.py`, `architecture.md`, `pyproject.toml`, `package.json`) requires explicit review from all affected leads.
3. **CI Must Pass**:
   - `ruff check backend/` must pass with zero errors.
   - `pytest -v backend/tests/` must pass with 100% green tests in mock mode.
   - `npm run build` in `apps/web` must complete without errors.
4. **No Secrets**: Never commit API keys or production tokens. All secrets belong in `.env`.

---

## 4. Ownership Table

| Role / Team Lead | Primary Responsibility | Owned Paths |
| :--- | :--- | :--- |
| **Person 1**<br>Core Agents & Model Layer | Model providers, model registry, core agents (router, inbox, briefing), validation, nebius notes | `backend/app/providers/`<br>`config/models.registry.yaml`<br>`backend/app/registry/loader.py`<br>`backend/app/agents/router.py, inbox.py, briefing.py`<br>`backend/app/graphs/router_graph.py, inbox_graph.py, briefing_graph.py`<br>`backend/app/validation/`<br>`backend/tests/test_provider_interface.py`<br>`docs/nebius-notes.md` |
| **Person 2**<br>Safety, Data & Background Services | Permission gateway, DB, activity log with undo, tools, file organiser & document agents, RAG, hardware selector, background service | `backend/app/gateway/`<br>`config/permissions.default.yaml`<br>`backend/app/core/`<br>`backend/app/tools/`<br>`backend/app/agents/file_organiser.py, document.py`<br>`backend/app/graphs/file_organiser_graph.py, document_graph.py`<br>`backend/app/rag/`<br>`backend/app/registry/hardware.py, selector.py`<br>`backend/app/service/`<br>`scripts/install_service_*`<br>`backend/tests/test_gateway.py, test_registry.py` |
| **Person 3**<br>Frontend, Desktop & Demo | Web UI, Tauri desktop shell, synthetic seed data, video demo script and shot list | `apps/web/`<br>`apps/desktop/`<br>`backend/app/seed/`<br>`docs/demo-video-plan.md`<br>`demo/` |
| **Person 4**<br>Deployment, Evals & Submission | Root config, Docker/Compose, CI/CD, evals & benchmarks, release docs, submission checklist, dev scripts | Root configs (`LICENSE`, `.gitignore`, `Makefile`, `.env.example`, `CONTRIBUTING.md`, `.github/`)<br>`deploy/`<br>`docs/release.md`<br>`backend/evals/`<br>`README.md`<br>`FEEDBACK.md`<br>`docs/submission-checklist.md`<br>`scripts/dev.*, seed.*` |
| **Shared**<br>All Leads | Common API contracts, main entry points, root package manifests | `backend/app/main.py`<br>`backend/app/api/schemas.py`<br>`docs/architecture.md`<br>`backend/pyproject.toml`<br>`apps/web/package.json` |
