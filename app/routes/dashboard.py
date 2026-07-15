"""
Dashboard routes — aggregated stats, progress overview, and motivational content.
"""
from __future__ import annotations

import logging
import random

from fastapi import APIRouter, Depends

from app.dependencies import get_app_state, get_watsonx_service
from app.models import AppState
from app.schemas import DashboardStats
from app.services.bmi_service import BMIService
from app.services.motivation_service import MotivationService
from app.services.watsonx_service import WatsonxService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats, summary="Get dashboard statistics")
async def get_stats(state: AppState = Depends(get_app_state)) -> DashboardStats:
    """Return aggregated stats for the fitness dashboard."""
    p = state.user_profile
    bmi = BMIService.calculate_bmi(p.weight_kg, p.height_cm)
    streak = state.get_streak()

    # Build weekly progress from habit logs (last 7 days)
    from datetime import date, timedelta
    today = date.today()
    weekly = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        log = next((h for h in state.habit_logs if h.date == day), None)
        weekly.append({
            "date": day.isoformat(),
            "workout": log.workout_done if log else False,
            "steps": log.steps if log else 0,
            "water": log.water_glasses if log else 0,
            "mood": log.mood if log else 0,
        })

    quote = MotivationService.get_random_quote()

    return DashboardStats(
        total_workouts=state.total_workouts,
        current_streak_days=streak,
        calories_burned_today=random.uniform(200, 600),   # placeholder — replace with real tracker
        water_intake_ml=0.0,
        steps_today=0,
        bmi=bmi,
        bmi_category=BMIService.get_bmi_category(bmi),
        weekly_progress=weekly,
        motivational_quote=f'"{quote["quote"]}" — {quote["author"]}',
    )


@router.get("/motivation", summary="Get AI-powered motivational message")
async def get_motivation(
    state: AppState = Depends(get_app_state),
    watsonx: WatsonxService = Depends(get_watsonx_service),
) -> dict:
    """Get a personalised AI motivational message."""
    p = state.user_profile
    streak = state.get_streak()
    context = (
        f"User: {p.name}, Goal: {p.fitness_goal}, "
        f"Level: {p.fitness_level}, Streak: {streak} days\n"
        f"Total workouts completed: {state.total_workouts}"
    )
    message = await watsonx.generate_motivation(context)
    streak_msg = MotivationService.streak_message(streak)
    return {
        "ai_message": message,
        "streak_message": streak_msg,
        "current_streak": streak,
        "quote": MotivationService.get_random_quote(),
    }
