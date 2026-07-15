"""
BMI and body composition calculations.
All formulas follow WHO standards.
"""
from __future__ import annotations


BMI_CATEGORIES = [
    (0, 18.5, "Underweight"),
    (18.5, 25.0, "Normal weight"),
    (25.0, 30.0, "Overweight"),
    (30.0, 35.0, "Obese (Class I)"),
    (35.0, 40.0, "Obese (Class II)"),
    (40.0, float("inf"), "Obese (Class III)"),
]


class BMIService:
    """Provides BMI, TDEE, and ideal-weight calculations."""

    # ------------------------------------------------------------------
    # BMI
    # ------------------------------------------------------------------

    @staticmethod
    def calculate_bmi(weight_kg: float, height_cm: float) -> float:
        """Calculate Body Mass Index (kg/m²)."""
        height_m = height_cm / 100
        return round(weight_kg / (height_m ** 2), 2)

    @staticmethod
    def get_bmi_category(bmi: float) -> str:
        for low, high, label in BMI_CATEGORIES:
            if low <= bmi < high:
                return label
        return "Unknown"

    # ------------------------------------------------------------------
    # TDEE — Total Daily Energy Expenditure
    # ------------------------------------------------------------------

    @staticmethod
    def calculate_bmr(
        weight_kg: float,
        height_cm: float,
        age: int,
        gender: str,
    ) -> float:
        """
        Mifflin–St Jeor BMR formula.
        More accurate than Harris-Benedict for modern populations.
        """
        if gender.lower() == "female":
            return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
        return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5

    ACTIVITY_MULTIPLIERS = {
        "sedentary": 1.2,      # Little or no exercise
        "light": 1.375,        # Exercise 1-3 days/week
        "moderate": 1.55,      # Exercise 3-5 days/week
        "active": 1.725,       # Hard exercise 6-7 days/week
        "very_active": 1.9,    # Very hard exercise & physical job
    }

    @classmethod
    def calculate_tdee(
        cls,
        weight_kg: float,
        height_cm: float,
        age: int,
        gender: str,
        activity_level: str = "moderate",
    ) -> float:
        """Calculate Total Daily Energy Expenditure (kcal/day)."""
        bmr = cls.calculate_bmr(weight_kg, height_cm, age, gender)
        multiplier = cls.ACTIVITY_MULTIPLIERS.get(activity_level, 1.55)
        return round(bmr * multiplier, 2)

    # ------------------------------------------------------------------
    # Ideal weight
    # ------------------------------------------------------------------

    @staticmethod
    def ideal_weight_range(height_cm: float) -> tuple[float, float]:
        """Return (min_kg, max_kg) for a healthy BMI (18.5–24.9)."""
        h = height_cm / 100
        return round(18.5 * h ** 2, 1), round(24.9 * h ** 2, 1)

    # ------------------------------------------------------------------
    # Calorie targets
    # ------------------------------------------------------------------

    @staticmethod
    def calorie_target(tdee: float, goal: str) -> float:
        """Adjust TDEE based on fitness goal."""
        adjustments = {
            "weight_loss": -500,
            "muscle_gain": +300,
            "endurance": +200,
            "flexibility": 0,
            "general_fitness": 0,
            "stress_relief": 0,
        }
        return max(1200, round(tdee + adjustments.get(goal, 0), 0))
