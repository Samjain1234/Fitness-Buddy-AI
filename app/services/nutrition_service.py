"""
Nutrition service — calculates macros, generates meal suggestions, and
provides evidence-based dietary guidance.
"""
from __future__ import annotations

from typing import Dict, List

from app.services.bmi_service import BMIService


# ============================================================
# Meal suggestion library (Indian + International)
# ============================================================

MEAL_SUGGESTIONS: Dict[str, Dict[str, List[str]]] = {
    "vegetarian": {
        "breakfast": [
            "Oats porridge with banana and mixed nuts",
            "Besan chilla (gram-flour pancake) with mint chutney",
            "Idli (3) with sambar and coconut chutney",
            "Greek yogurt parfait with granola and berries",
            "Moong dal chilla with avocado",
            "Upma with vegetables",
        ],
        "mid_morning": [
            "Handful of mixed nuts and a fruit",
            "Roasted makhana (fox nuts) with spices",
            "Hummus with cucumber and carrot sticks",
            "A banana and a glass of buttermilk",
        ],
        "lunch": [
            "Dal + brown rice + sabzi + salad + curd",
            "Rajma curry with jowar roti and salad",
            "Quinoa salad with roasted vegetables and paneer",
            "Tofu stir-fry with mixed vegetables and brown rice",
            "Chole (chickpeas) with whole-wheat roti and raita",
            "Palak paneer with multigrain roti and dal",
        ],
        "snack": [
            "Sprouts chaat with lemon and spices",
            "Makhana (fox nut) trail mix",
            "Boiled peanuts with rock salt",
            "Fruit chaat with chaat masala",
            "Protein smoothie (milk + banana + peanut butter)",
        ],
        "dinner": [
            "Vegetable soup + multigrain roti + sabzi",
            "Khichdi (dal + rice) with ghee and pickle",
            "Mixed vegetable curry with brown rice",
            "Paneer tikka with mint chutney and salad",
            "Lentil soup (masoor dal) with whole-wheat bread",
        ],
    },
    "non_vegetarian": {
        "breakfast": [
            "Egg white omelette with vegetables and whole-wheat toast",
            "Boiled eggs (2) + oats porridge",
            "Greek yogurt with scrambled eggs",
            "Chicken sandwich on whole-grain bread",
        ],
        "mid_morning": [
            "Boiled eggs (1-2) with fruit",
            "Tuna on rice cakes",
            "Protein shake with milk",
        ],
        "lunch": [
            "Grilled chicken breast + brown rice + salad",
            "Fish curry (preferably baked/grilled) with rice and vegetables",
            "Chicken pulao with raita and salad",
            "Egg curry with whole-wheat roti and sabzi",
            "Prawn stir-fry with quinoa",
        ],
        "snack": [
            "Grilled chicken strips",
            "Hard-boiled eggs",
            "Greek yogurt",
            "Protein smoothie",
        ],
        "dinner": [
            "Baked/grilled fish with steamed vegetables",
            "Chicken soup with multigrain bread",
            "Stir-fried chicken with vegetables",
            "Egg fried rice (brown) with stir-fried vegetables",
        ],
    },
    "vegan": {
        "breakfast": [
            "Tofu scramble with vegetables on whole-grain toast",
            "Smoothie bowl: banana, spinach, plant milk, chia seeds",
            "Overnight oats with almond milk and fruit",
            "Idli with sambar (no ghee)",
            "Moong dal chilla with tomato chutney",
        ],
        "mid_morning": [
            "Mixed nuts and dried fruit",
            "Apple with almond butter",
            "Coconut yogurt with granola",
        ],
        "lunch": [
            "Lentil soup + brown rice + roasted vegetables",
            "Chickpea and spinach curry with whole-wheat roti",
            "Tofu Buddha bowl with tahini dressing",
            "Black bean tacos with guacamole",
        ],
        "snack": [
            "Hummus with vegetable sticks",
            "Roasted chickpeas",
            "Edamame with sea salt",
            "Fruit and nut energy balls",
        ],
        "dinner": [
            "Vegetable lentil stew with crusty bread",
            "Tofu and vegetable stir-fry with brown rice",
            "Dal makhani (vegan version) with roti",
            "Roasted sweet potato with black bean salad",
        ],
    },
}


class NutritionService:
    """Calculates nutritional targets and generates meal plans."""

    PROTEIN_RATIOS = {
        "weight_loss": 0.35,
        "muscle_gain": 0.40,
        "endurance": 0.25,
        "flexibility": 0.25,
        "general_fitness": 0.30,
        "stress_relief": 0.25,
    }

    CARB_RATIOS = {
        "weight_loss": 0.35,
        "muscle_gain": 0.45,
        "endurance": 0.55,
        "flexibility": 0.50,
        "general_fitness": 0.45,
        "stress_relief": 0.50,
    }

    @classmethod
    def calculate_macros(
        cls,
        weight_kg: float,
        height_cm: float,
        age: int,
        gender: str,
        activity_level: str,
        goal: str,
    ) -> Dict:
        tdee = BMIService.calculate_tdee(weight_kg, height_cm, age, gender, activity_level)
        calories = BMIService.calorie_target(tdee, goal)

        protein_ratio = cls.PROTEIN_RATIOS.get(goal, 0.30)
        carb_ratio = cls.CARB_RATIOS.get(goal, 0.45)
        fat_ratio = 1.0 - protein_ratio - carb_ratio

        protein_g = round((calories * protein_ratio) / 4, 1)  # 4 kcal/g
        carbs_g = round((calories * carb_ratio) / 4, 1)
        fat_g = round((calories * fat_ratio) / 9, 1)           # 9 kcal/g
        hydration_ml = round(weight_kg * 35, 0)                # 35 ml/kg

        return {
            "daily_calories": calories,
            "protein_g": protein_g,
            "carbs_g": carbs_g,
            "fat_g": fat_g,
            "hydration_ml": hydration_ml,
        }

    @classmethod
    def get_meal_plan(cls, diet_preference: str) -> Dict[str, List[str]]:
        """Return a sample daily meal plan."""
        import random
        pref = diet_preference if diet_preference in MEAL_SUGGESTIONS else "vegetarian"
        plan = MEAL_SUGGESTIONS[pref]
        return {meal: [random.choice(options)] for meal, options in plan.items()}

    @staticmethod
    def get_nutrition_tips(goal: str, diet_preference: str) -> List[str]:
        tips = [
            "Eat slowly and mindfully — it takes 20 min for satiety signals to reach the brain.",
            "Fill half your plate with colourful vegetables at every meal.",
            "Choose whole grains over refined: brown rice, oats, whole-wheat roti.",
            "Limit ultra-processed foods, sugary drinks, and excess sodium.",
            "Plan meals ahead to avoid impulsive unhealthy choices.",
        ]
        goal_tips = {
            "weight_loss": "Create a moderate deficit (~500 kcal/day) — avoid crash dieting.",
            "muscle_gain": "Eat protein within 30-60 minutes post-workout for optimal muscle synthesis.",
            "endurance": "Carb-load slightly 24 hours before long training sessions.",
        }
        if goal in goal_tips:
            tips.insert(0, goal_tips[goal])
        return tips
