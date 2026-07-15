"""
In-memory data store models.
In production, replace with a proper database (PostgreSQL, SQLite, etc.)
using SQLAlchemy or SQLModel.
"""

import datetime as _dt
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    """Stored user profile (in-memory session)."""
    name: str = "Fitness Enthusiast"
    age: int = 25
    gender: str = "other"
    height_cm: float = 170.0
    weight_kg: float = 70.0
    fitness_level: str = "beginner"
    fitness_goal: str = "general_fitness"
    diet_preference: str = "vegetarian"
    available_days_per_week: int = 3
    available_minutes_per_session: int = 30
    medical_conditions: Optional[str] = None
    created_at: _dt.datetime = Field(default_factory=_dt.datetime.utcnow)
    updated_at: _dt.datetime = Field(default_factory=_dt.datetime.utcnow)


class HabitLog(BaseModel):
    """Daily habit tracking entry."""
    date: _dt.date = Field(default_factory=_dt.date.today)
    water_glasses: int = 0
    sleep_hours: float = 0.0
    steps: int = 0
    workout_done: bool = False
    mood: int = 5
    notes: Optional[str] = None


class ConversationTurn(BaseModel):
    """Single turn in a conversation."""
    role: str        # 'user' | 'assistant'
    content: str
    timestamp: _dt.datetime = Field(default_factory=_dt.datetime.utcnow)


class AppState:
    """
    Application-level in-memory state.
    Acts as a lightweight singleton store during a session.
    Replace with a real DB for multi-user / persistent deployments.
    """

    def __init__(self) -> None:
        self.user_profile: UserProfile = UserProfile()
        self.habit_logs: List[HabitLog] = []
        self.conversation_history: List[ConversationTurn] = []
        self.total_workouts: int = 0
        self.workout_streak: int = 0

    # ---- Profile helpers ----
    def update_profile(self, data: Dict) -> None:
        for key, value in data.items():
            if hasattr(self.user_profile, key):
                setattr(self.user_profile, key, value)
        self.user_profile.updated_at = _dt.datetime.utcnow()

    # ---- Habit helpers ----
    def log_habit(self, entry: HabitLog) -> None:
        # Overwrite today's entry if it already exists
        self.habit_logs = [h for h in self.habit_logs if h.date != entry.date]
        self.habit_logs.append(entry)

    def get_streak(self) -> int:
        if not self.habit_logs:
            return 0
        sorted_logs = sorted(self.habit_logs, key=lambda h: h.date, reverse=True)
        streak = 0
        current = _dt.date.today()
        for log in sorted_logs:
            if log.date == current and log.workout_done:
                streak += 1
                current -= _dt.timedelta(days=1)
            else:
                break
        return streak


# Global singleton — replace with proper DI/DB in production
app_state = AppState()
