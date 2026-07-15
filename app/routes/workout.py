"""
Workout routes — generate and retrieve personalised workout plans.
"""
from __future__ import annotations

import logging
from datetime import datetime

from fastapi import APIRouter, Depends

from app.dependencies import get_app_state, get_watsonx_service
from app.models import AppState
from app.schemas import WorkoutRequest, WorkoutResponse
from app.services.fitness_service import FitnessService
from app.services.watsonx_service import WatsonxService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/workout", tags=["Workout"])


@router.post("/plan", response_model=WorkoutResponse, summary="Generate a personalised workout plan")
async def generate_workout_plan(
    request: WorkoutRequest,
    state: AppState = Depends(get_app_state),
    watsonx: WatsonxService = Depends(get_watsonx_service),
) -> WorkoutResponse:
    """
    Builds a structured weekly workout plan.
    Also calls Granite for AI motivational notes.
    """
    p = state.user_profile
    profile_ctx = (
        f"Name: {p.name}, Level: {p.fitness_level}, Goal: {p.fitness_goal}\n"
        f"Available: {p.available_days_per_week} days/week, "
        f"{p.available_minutes_per_session} min/session\n"
        f"Medical conditions: {p.medical_conditions or 'None'}"
    )

    # Build structured plan
    plans = FitnessService.build_weekly_plan(
        days_per_week=p.available_days_per_week,
        fitness_level=request.fitness_level.value,
        goal=request.goal.value,
        workout_type=request.workout_type.value,
        duration_minutes=request.duration_minutes,
        focus_area=request.focus_area,
    )
    tips = FitnessService.get_tips(request.goal.value, request.fitness_level.value)

    # Generate AI overview
    overview_result = await watsonx.generate(
        user_message=(
            f"Provide a brief, motivating weekly workout overview for a {request.fitness_level.value} "
            f"focused on {request.goal.value}. Mention the benefits of this plan in 3-4 sentences."
        ),
        system_context=profile_ctx,
    )

    return WorkoutResponse(
        plan=plans,
        weekly_overview=overview_result["text"],
        tips=tips,
        generated_at=datetime.utcnow(),
    )


@router.get("/quick/{workout_type}", summary="Get a quick workout for today")
async def quick_workout(
    workout_type: str,
    state: AppState = Depends(get_app_state),
) -> dict:
    """Return a single-session quick workout."""
    p = state.user_profile
    exercises = FitnessService.get_exercises_for_type(
        workout_type, p.fitness_level, count=5
    )
    return {
        "workout_type": workout_type,
        "exercises": [ex.model_dump() for ex in exercises],
        "duration_minutes": p.available_minutes_per_session,
    }
