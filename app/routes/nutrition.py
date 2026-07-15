"""
Nutrition routes — macro calculations, meal plans, and dietary advice.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends

from app.dependencies import get_app_state, get_watsonx_service
from app.models import AppState
from app.schemas import MacroBreakdown, NutritionRequest, NutritionResponse
from app.services.nutrition_service import NutritionService
from app.services.watsonx_service import WatsonxService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/nutrition", tags=["Nutrition"])

DISCLAIMER = (
    "⚠️ This information is for general wellness purposes only and does not constitute "
    "medical or dietary advice. Please consult a qualified healthcare professional or "
    "registered dietitian before making significant changes to your diet."
)


@router.post("/plan", response_model=NutritionResponse, summary="Generate personalised nutrition plan")
async def nutrition_plan(
    request: NutritionRequest,
    watsonx: WatsonxService = Depends(get_watsonx_service),
) -> NutritionResponse:
    macros = NutritionService.calculate_macros(
        weight_kg=request.weight_kg,
        height_cm=request.height_cm,
        age=request.age,
        gender=request.gender,
        activity_level=request.activity_level,
        goal=request.goal.value,
    )
    meal_plan = NutritionService.get_meal_plan(request.diet_preference.value)
    tips = NutritionService.get_nutrition_tips(request.goal.value, request.diet_preference.value)

    return NutritionResponse(
        daily_calories=macros["daily_calories"],
        macros=MacroBreakdown(
            calories=macros["daily_calories"],
            protein_g=macros["protein_g"],
            carbs_g=macros["carbs_g"],
            fat_g=macros["fat_g"],
        ),
        meal_plan=meal_plan,
        hydration_ml=macros["hydration_ml"],
        tips=tips,
        disclaimer=DISCLAIMER,
    )


@router.get("/advice", summary="Get AI-powered nutrition advice based on profile")
async def nutrition_advice(
    state: AppState = Depends(get_app_state),
    watsonx: WatsonxService = Depends(get_watsonx_service),
) -> dict:
    """Get personalised AI nutrition advice."""
    p = state.user_profile
    context = (
        f"User: {p.name}, Age: {p.age}, Gender: {p.gender}\n"
        f"Height: {p.height_cm} cm, Weight: {p.weight_kg} kg\n"
        f"Goal: {p.fitness_goal}, Diet: {p.diet_preference}\n"
        f"Medical conditions: {p.medical_conditions or 'None'}"
    )
    advice = await watsonx.generate_nutrition_advice(context)
    return {"advice": advice, "disclaimer": DISCLAIMER}
