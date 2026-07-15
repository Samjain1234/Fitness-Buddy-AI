"""
FastAPI dependency injection helpers.
Provides reusable dependencies for routes.
"""
from __future__ import annotations

from fastapi import Depends

from app.config import Settings, get_settings
from app.models import AppState, app_state
from app.services.watsonx_service import WatsonxService


# ---- Settings dependency ----
def get_app_settings() -> Settings:
    return get_settings()


# ---- App-state dependency (in-memory store) ----
def get_app_state() -> AppState:
    """Return the global in-memory application state."""
    return app_state


# ---- Watsonx service dependency ----
_watsonx_service: WatsonxService | None = None


def get_watsonx_service(
    settings: Settings = Depends(get_app_settings),
) -> WatsonxService:
    """
    Return a cached WatsonxService instance.
    The service is initialised once on first request.
    """
    global _watsonx_service
    if _watsonx_service is None:
        _watsonx_service = WatsonxService(settings)
    return _watsonx_service
