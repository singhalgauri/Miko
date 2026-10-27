# Owner: Person 4
# Purpose: Multi-stage Dockerfile packaging Vite React frontend + FastAPI backend into single image
# Image Name: miko
# TODO(person4): Add non-root user security hardening and production healthcheck probe

# -------------------------------------------------------------
# Stage 1: Build React Frontend
# -------------------------------------------------------------
FROM node:20-alpine AS frontend-builder
WORKDIR /build

COPY apps/web/package*.json ./
RUN npm ci || npm install

COPY apps/web/ ./
RUN npm run build

# -------------------------------------------------------------
# Stage 2: Runtime Backend & Static File Serving
# -------------------------------------------------------------
FROM python:3.11-slim AS runner

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python backend
COPY backend/pyproject.toml ./backend/
COPY backend/app/ ./backend/app/
COPY config/ /config/

RUN pip install --no-cache-dir -e "./backend"

# Copy built frontend assets from Stage 1
COPY --from=frontend-builder /build/dist /app/static

ENV PROVIDER=mock
ENV HOST=0.0.0.0
ENV PORT=8000

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
