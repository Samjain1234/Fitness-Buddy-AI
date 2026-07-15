"""
User profile routes — create, read, and update the fitness profile.
"""
from __future__ import annotations

import logging
from datetime import datetime

from fastapi import APIRouter, Depends

from app.dependencies import get_app_state
from app.models import AppState, UserProfile
from app.schemas import UserProfileResponse, UserProfileSchema
from app.services.bmi_service import BMIService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/profile", tags=["Profile"])


def _build_response(profile: UserProfile) -> UserProfileResponse:
    bmi = BMIService.calculate_bmi(profile.weight_kg, profile.height_cm)
    tdee = BMIService.calculate_tdee(
        profile.weight_kg, profile.height_cm, profile.age, profile.gender
    )
    return UserProfileResponse(
        **profile.model_dump(),
        bmi=bmi,
        bmi_category=BMIService.get_bmi_category(bmi),
        tdee=round(tdee, 1),
    )


@router.get("", response_model=UserProfileResponse, summary="Get current user profile")
async def get_profile(state: AppState = Depends(get_app_state)) -> UserProfileResponse:
    return _build_response(state.user_profile)


@router.post("", response_model=UserProfileResponse, summary="Create or update user profile")
async def upsert_profile(
    body: UserProfileSchema,
    state: AppState = Depends(get_app_state),
) -> UserProfileResponse:
    state.update_profile(body.model_dump())
    logger.info("Profile updated for user: %s", body.name)
    return _build_response(state.user_profile)
