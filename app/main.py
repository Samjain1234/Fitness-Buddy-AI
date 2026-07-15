"""
FastAPI application factory and entry point.
"""
from __future__ import annotations

import logging
import logging.config
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.routes import chat, dashboard, habits, nutrition, profile, workout
from app.schemas import HealthCheck

# ============================================================
# Logging configuration
# ============================================================

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "app": {"level": "DEBUG", "propagate": True},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"level": "WARNING"},
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


# ============================================================
# Lifespan (startup / shutdown)
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    logger.info(
        "🚀 %s v%s starting up [%s]",
        settings.app_name, settings.app_version, settings.app_env,
    )
    logger.info("📡 Watsonx model: %s", settings.watsonx_model_id)
    creds_ok = bool(settings.ibm_cloud_api_key and settings.watsonx_project_id)
    if creds_ok:
        logger.info("✅ IBM Watsonx.ai credentials detected")
    else:
        logger.warning(
            "⚠️  IBM Watsonx.ai credentials NOT configured — AI features will show placeholder responses"
        )
    yield
    logger.info("👋 %s shutting down", settings.app_name)


# ============================================================
# Application factory
# ============================================================

def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description=(
            "AI-powered personal fitness coach built with FastAPI and IBM watsonx.ai Granite models. "
            "Provides personalised workout plans, nutrition guidance, habit tracking, and motivation."
        ),
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ---- CORS ----
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---- Static files ----
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    # ---- Templates ----
    templates = Jinja2Templates(directory="app/templates")

    # ---- Routers ----
    app.include_router(chat.router)
    app.include_router(profile.router)
    app.include_router(workout.router)
    app.include_router(nutrition.router)
    app.include_router(dashboard.router)
    app.include_router(habits.router)

    # ---- Global exception handler ----
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception on %s: %s", request.url.path, exc)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": str(exc)},
        )

    # ---- Health check ----
    @app.get("/health", response_model=HealthCheck, tags=["System"])
    async def health_check() -> HealthCheck:
        return HealthCheck(
            status="ok",
            version=settings.app_version,
            environment=settings.app_env,
            watsonx_configured=bool(
                settings.ibm_cloud_api_key and settings.watsonx_project_id
            ),
            timestamp=datetime.utcnow(),
        )

    # ---- Version ----
    @app.get("/version", tags=["System"])
    async def version() -> dict:
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "model": settings.watsonx_model_id,
        }

    # ---- Serve SPA ----
    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def index(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "app_name": settings.app_name,
                "app_version": settings.app_version,
            },
        )

    # Catch-all for client-side routing
    @app.get("/{full_path:path}", response_class=HTMLResponse, include_in_schema=False)
    async def spa_fallback(request: Request, full_path: str) -> HTMLResponse:
        # Don't catch API or static routes
        if full_path.startswith(("api/", "static/", "docs", "redoc", "openapi")):
            return JSONResponse(status_code=404, content={"error": "Not found"})
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "app_name": settings.app_name,
                "app_version": settings.app_version,
            },
        )

    logger.info("✅ FastAPI app created — routes registered")
    return app


# ---- Module-level app instance (used by Uvicorn) ----
app = create_app()
