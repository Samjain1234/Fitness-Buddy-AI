"""
Chat routes — AI-powered conversation with Fitness Buddy.
"""
from __future__ import annotations

import logging
from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.dependencies import get_watsonx_service
from app.schemas import ChatRequest, ChatResponse
from app.services.watsonx_service import WatsonxService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse, summary="Send a message to Fitness Buddy AI")
async def chat(
    request: ChatRequest,
    watsonx: WatsonxService = Depends(get_watsonx_service),
) -> ChatResponse:
    """
    Send a message and receive an AI-powered fitness coaching reply.
    Maintains conversation history for contextual responses.
    """
    # Build profile context if provided
    system_context: str | None = None
    if request.user_profile:
        p = request.user_profile
        system_context = (
            f"User: {p.name}, Age: {p.age}, Gender: {p.gender}\n"
            f"Height: {p.height_cm} cm, Weight: {p.weight_kg} kg\n"
            f"Fitness Level: {p.fitness_level.value}, Goal: {p.fitness_goal.value}\n"
            f"Diet: {p.diet_preference.value}\n"
            f"Available: {p.available_days_per_week} days/week, "
            f"{p.available_minutes_per_session} min/session\n"
            f"Medical conditions: {p.medical_conditions or 'None stated'}"
        )

    history = [
        {"role": m.role, "content": m.content}
        for m in request.conversation_history
    ]

    result = await watsonx.generate(
        user_message=request.message,
        conversation_history=history,
        system_context=system_context,
    )

    return ChatResponse(
        reply=result["text"],
        tokens_used=result.get("tokens_used"),
        model_id=result.get("model_id"),
        timestamp=datetime.utcnow(),
    )
