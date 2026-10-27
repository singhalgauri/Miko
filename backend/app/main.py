# Owner: Shared (P1 / P2 / P3 / P4)
# Purpose: FastAPI application entrypoint with route registration only
# TODO: Add CORS middleware origins and lifespan background manager startup

from contextlib import asynccontextmanager

from backend.app.api.routes_activity import router as activity_router
from backend.app.api.routes_agents import router as agents_router
from backend.app.api.routes_approvals import router as approvals_router
from backend.app.api.routes_permissions import router as permissions_router
from backend.app.api.routes_seed import router as seed_router
from backend.app.api.routes_settings import router as settings_router
from backend.app.api.schemas import HealthResponse
from backend.app.core.config import settings
from backend.app.core.db import init_db
from backend.app.core.logging import logger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle event handler for database initialization and background services."""
    logger.info("Starting Miko backend service...")
    init_db()
    yield
    logger.info("Shutting down Miko backend service...")


app = FastAPI(
    title="Miko",
    description="Miko: a free, local-first, always-on AI agent",
    version="0.1.0",
    lifespan=lifespan,
)

# Enable CORS for local web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """System health check endpoint."""
    return HealthResponse(
        status="ok",
        app="Miko",
        provider=settings.provider,
    )


# Route registration only
app.include_router(activity_router)
app.include_router(approvals_router)
app.include_router(permissions_router)
app.include_router(settings_router)
app.include_router(seed_router)
app.include_router(agents_router)
