# Owner: Person 4
# Purpose: Top-level developer targets for Miko monorepo
# TODO(person4): Add automated packaging and release targets

.PHONY: help install-backend install-web install test lint build-web dev dev-backend dev-web clean

help:
	@echo "Miko Monorepo Developer Commands:"
	@echo "  make install        - Install backend and frontend dependencies"
	@echo "  make test           - Run backend test suite (pytest)"
	@echo "  make lint           - Lint backend with ruff"
	@echo "  make build-web      - Build web application"
	@echo "  make dev-backend    - Start backend server on 127.0.0.1:8000"
	@echo "  make dev-web        - Start frontend dev server"

install-backend:
	cd backend && pip install -e .

install-web:
	cd apps/web && npm install

install: install-backend install-web

test:
	cd backend && pytest -v

lint:
	cd backend && ruff check .

build-web:
	cd apps/web && npm run build

dev-backend:
	cd backend && uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

dev-web:
	cd apps/web && npm run dev

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
