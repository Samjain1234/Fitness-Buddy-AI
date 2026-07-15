"""
Pydantic schemas for request / response validation.
All user-facing API contracts are defined here.
"""
# NOTE: do NOT use 'from __future__ import annotations' here —
# Pydantic v2 needs to resolve type annotations eagerly at class definition time.

import datetime as _dt
from datetime import date, datetime  # expose in module namespace for Pydantic
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ============================================================
# Enumerations
# ============================================================

class FitnessLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class FitnessGoal(str, Enum):
    weight_loss = "weight_loss"
    muscle_gain = "muscle_gain"
    endurance = "endurance"
    flexibility = "flexibility"
    general_fitness = "general_fitness"
    stress_relief = "stress_relief"


class WorkoutType(str, Enum):
    hiit = "hiit"
    strength = "strength"
    yoga = "yoga"
    cardio = "cardio"
    flexibility = "flexibility"
    home = "home"
    calisthenics = "calisthenics"


class DietPreference(str, Enum):
    vegetarian = "vegetarian"
    vegan = "vegan"
    non_vegetarian = "non_vegetarian"
    eggetarian = "eggetarian"


# ============================================================
# Chat Schemas
# ============================================================

class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., min_length=1)
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    conversation_history: List[ChatMessage] = Field(default_factory=list)
    user_profile: Optional["UserProfileSchema"] = None

    model_config = {"populate_by_name": True}


class ChatResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    reply: str
    tokens_used: Optional[int] = None
    model_id: Optional[str] = None
    timestamp: _dt.datetime = Field(default_factory=_dt.datetime.utcnow)


# ============================================================
# User Profile Schemas
# ============================================================

class UserProfileSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=10, le=100)
    gender: str = Field(..., pattern="^(male|female|other)$")
    height_cm: float = Field(..., gt=50, lt=300, description="Height in centimetres")
    weight_kg: float = Field(..., gt=10, lt=500, description="Weight in kilograms")
    fitness_level: FitnessLevel = FitnessLevel.beginner
    fitness_goal: FitnessGoal = FitnessGoal.general_fitness
    diet_preference: DietPreference = DietPreference.vegetarian
    available_days_per_week: int = Field(default=3, ge=1, le=7)
    available_minutes_per_session: int = Field(default=30, ge=10, le=120)
    medical_conditions: Optional[str] = Field(default=None, max_length=500)

    @field_validator("height_cm", "weight_kg")
    @classmethod
    def round_two_decimals(cls, v: float) -> float:
        return round(v, 2)


class UserProfileResponse(UserProfileSchema):
    bmi: float
    bmi_category: str
    tdee: float
    created_at: _dt.datetime = Field(default_factory=_dt.datetime.utcnow)


# ============================================================
# Workout Schemas
# ============================================================

class Exercise(BaseModel):
    name: str
    sets: Optional[int] = None
    reps: Optional[str] = None
    duration_seconds: Optional[int] = None
    rest_seconds: int = 30
    instructions: str
    muscles_targeted: List[str] = Field(default_factory=list)
    modifications: Optional[str] = None


class WorkoutPlan(BaseModel):
    day: str
    workout_type: str
    duration_minutes: int
    exercises: List[Exercise]
    warm_up: List[str]
    cool_down: List[str]
    notes: Optional[str] = None


class WorkoutRequest(BaseModel):
    workout_type: WorkoutType = WorkoutType.home
    duration_minutes: int = Field(default=30, ge=10, le=120)
    fitness_level: FitnessLevel = FitnessLevel.beginner
    goal: FitnessGoal = FitnessGoal.general_fitness
    focus_area: Optional[str] = Field(default=None, description="e.g. core, legs, upper body")


class WorkoutResponse(BaseModel):
    plan: List[WorkoutPlan]
    weekly_overview: str
    tips: List[str]
    generated_at: _dt.datetime = Field(default_factory=_dt.datetime.utcnow)


# ============================================================
# Nutrition Schemas
# ============================================================

class NutritionRequest(BaseModel):
    weight_kg: float = Field(..., gt=10)
    height_cm: float = Field(..., gt=50)
    age: int = Field(..., ge=10, le=100)
    gender: str = Field(..., pattern="^(male|female|other)$")
    activity_level: str = Field(default="moderate", pattern="^(sedentary|light|moderate|active|very_active)$")
    goal: FitnessGoal = FitnessGoal.general_fitness
    diet_preference: DietPreference = DietPreference.vegetarian


class MacroBreakdown(BaseModel):
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float


class NutritionResponse(BaseModel):
    daily_calories: float
    macros: MacroBreakdown
    meal_plan: Dict[str, List[str]]
    hydration_ml: float
    tips: List[str]
    disclaimer: str


# ============================================================
# Dashboard Schemas
# ============================================================

class ProgressEntry(BaseModel):
    date: _dt.date
    weight_kg: float
    notes: Optional[str] = None


class DashboardStats(BaseModel):
    total_workouts: int = 0
    current_streak_days: int = 0
    calories_burned_today: float = 0.0
    water_intake_ml: float = 0.0
    steps_today: int = 0
    bmi: float = 0.0
    bmi_category: str = ""
    weekly_progress: List[Dict] = Field(default_factory=list)
    motivational_quote: str = ""


# ============================================================
# Habits Schemas
# ============================================================

class HabitEntry(BaseModel):
    date: _dt.date = Field(default_factory=_dt.date.today)
    water_glasses: int = Field(default=0, ge=0, le=30)
    sleep_hours: float = Field(default=0.0, ge=0, le=24)
    steps: int = Field(default=0, ge=0)
    workout_done: bool = False
    mood: int = Field(default=5, ge=1, le=10, description="Mood score 1-10")
    notes: Optional[str] = None


class HabitResponse(BaseModel):
    entry: HabitEntry
    wellness_score: float
    feedback: str
    streak: int


# ============================================================
# Common Schemas
# ============================================================

class HealthCheck(BaseModel):
    status: str
    version: str
    environment: str
    watsonx_configured: bool
    timestamp: _dt.datetime = Field(default_factory=_dt.datetime.utcnow)


class APIError(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: _dt.datetime = Field(default_factory=_dt.datetime.utcnow)
