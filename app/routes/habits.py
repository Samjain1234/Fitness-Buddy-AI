"""
Habits routes — daily habit tracking and wellness scoring.
"""
from __future__ import annotations

import logging
from datetime import date

from fastapi import APIRouter, Depends

from app.dependencies import get_app_state
from app.models import AppState, HabitLog
from app.schemas import HabitEntry, HabitResponse
from app.services.motivation_service import MotivationService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/habits", tags=["Habits"])


@router.post("/log", response_model=HabitResponse, summary="Log today's habits")
async def log_habits(
    entry: HabitEntry,
    state: AppState = Depends(get_app_state),
) -> HabitResponse:
    """Log daily habits and receive a wellness score and feedback."""
    habit = HabitLog(
        date=entry.date,
        water_glasses=entry.water_glasses,
        sleep_hours=entry.sleep_hours,
        steps=entry.steps,
        workout_done=entry.workout_done,
        mood=entry.mood,
        notes=entry.notes,
    )
    state.log_habit(habit)

    if entry.workout_done:
        state.total_workouts += 1

    score = MotivationService.calculate_wellness_score(
        water_glasses=entry.water_glasses,
        sleep_hours=entry.sleep_hours,
        steps=entry.steps,
        workout_done=entry.workout_done,
        mood=entry.mood,
    )
    feedback = MotivationService.get_habit_feedback(score)
    streak = state.get_streak()

    return HabitResponse(
        entry=entry,
        wellness_score=score,
        feedback=feedback,
        streak=streak,
    )


@router.get("/today", summary="Get today's habit log")
async def get_today(state: AppState = Depends(get_app_state)) -> dict:
    today = date.today()
    log = next((h for h in state.habit_logs if h.date == today), None)
    if log:
        return log.model_dump()
    return {
        "date": today.isoformat(),
        "water_glasses": 0,
        "sleep_hours": 0,
        "steps": 0,
        "workout_done": False,
        "mood": 5,
        "notes": None,
    }


@router.get("/history", summary="Get last 30 days of habit logs")
async def get_history(state: AppState = Depends(get_app_state)) -> dict:
    from datetime import timedelta
    cutoff = date.today() - timedelta(days=30)
    logs = [h.model_dump() for h in state.habit_logs if h.date >= cutoff]
    logs.sort(key=lambda x: x["date"], reverse=True)
    return {"logs": logs, "total": len(logs)}
