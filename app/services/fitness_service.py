"""
Fitness service — generates workout plans and exercise recommendations.
Provides structured workout data used by both the API and AI prompts.
"""
from __future__ import annotations

import random
from typing import Dict, List

from app.schemas import (
    Exercise,
    FitnessGoal,
    FitnessLevel,
    WorkoutPlan,
    WorkoutType,
)


# ============================================================
# Exercise Library
# ============================================================

EXERCISE_LIBRARY: Dict[str, List[Exercise]] = {
    "strength": [
        Exercise(name="Push-Ups", sets=3, reps="10-15", rest_seconds=45,
                 instructions="Keep your body straight, lower chest to floor, push back up.",
                 muscles_targeted=["chest", "triceps", "shoulders"],
                 modifications="Do knee push-ups if needed."),
        Exercise(name="Squats", sets=3, reps="15-20", rest_seconds=45,
                 instructions="Feet shoulder-width apart, lower until thighs are parallel to floor.",
                 muscles_targeted=["quads", "glutes", "hamstrings"],
                 modifications="Hold a chair for balance."),
        Exercise(name="Dumbbell Rows", sets=3, reps="10-12", rest_seconds=45,
                 instructions="Hinge at hips, pull dumbbell to hip, squeeze back.",
                 muscles_targeted=["back", "biceps"],
                 modifications="Use a water bottle if no dumbbells."),
        Exercise(name="Lunges", sets=3, reps="12 each leg", rest_seconds=45,
                 instructions="Step forward, lower knee toward floor, return to standing.",
                 muscles_targeted=["quads", "glutes", "hamstrings"]),
        Exercise(name="Shoulder Press", sets=3, reps="10-12", rest_seconds=45,
                 instructions="Press dumbbells overhead, keep core braced.",
                 muscles_targeted=["shoulders", "triceps"]),
        Exercise(name="Glute Bridge", sets=3, reps="15-20", rest_seconds=30,
                 instructions="Lie on back, feet flat, drive hips up, squeeze glutes.",
                 muscles_targeted=["glutes", "hamstrings", "core"]),
    ],
    "cardio": [
        Exercise(name="Jumping Jacks", sets=3, duration_seconds=30, rest_seconds=15,
                 instructions="Jump feet wide while raising arms overhead, return.",
                 muscles_targeted=["full body", "cardio"]),
        Exercise(name="High Knees", sets=3, duration_seconds=30, rest_seconds=15,
                 instructions="Run in place bringing knees to waist height.",
                 muscles_targeted=["core", "legs", "cardio"]),
        Exercise(name="Burpees", sets=3, reps="8-12", rest_seconds=30,
                 instructions="Squat, jump feet back to plank, push-up optional, jump up.",
                 muscles_targeted=["full body", "cardio"],
                 modifications="Step back instead of jumping."),
        Exercise(name="Mountain Climbers", sets=3, duration_seconds=30, rest_seconds=20,
                 instructions="Plank position, alternate driving knees to chest rapidly.",
                 muscles_targeted=["core", "cardio"]),
        Exercise(name="Jump Rope (Skipping)", sets=3, duration_seconds=60, rest_seconds=30,
                 instructions="Keep elbows close, use wrists to turn rope, land softly.",
                 muscles_targeted=["cardio", "calves", "coordination"]),
    ],
    "yoga": [
        Exercise(name="Surya Namaskar (Sun Salutation)", sets=1, reps="5 cycles", rest_seconds=30,
                 instructions="Flow through 12 postures: Pranamasana → Hasta Uttanasana → Uttanasana → Ashwa Sanchalanasana → Dandasana → Ashtanga Namaskara → Bhujangasana → Adho Mukha Svanasana → Ashwa Sanchalanasana → Uttanasana → Hasta Uttanasana → Pranamasana.",
                 muscles_targeted=["full body", "flexibility", "mindfulness"],
                 modifications="Take breaks between cycles."),
        Exercise(name="Warrior I (Virabhadrasana I)", sets=1, reps="Hold 30s each side", rest_seconds=15,
                 instructions="Step one foot back, front knee bent at 90°, arms raised overhead.",
                 muscles_targeted=["legs", "hips", "shoulders"]),
        Exercise(name="Warrior II (Virabhadrasana II)", sets=1, reps="Hold 30s each side", rest_seconds=15,
                 instructions="Wide stance, front knee over ankle, arms parallel to floor, gaze forward.",
                 muscles_targeted=["quads", "hips", "core"]),
        Exercise(name="Downward Dog (Adho Mukha Svanasana)", sets=1, duration_seconds=60, rest_seconds=15,
                 instructions="Inverted V shape, push heels toward floor, lengthen spine.",
                 muscles_targeted=["hamstrings", "calves", "shoulders", "back"]),
        Exercise(name="Child's Pose (Balasana)", sets=1, duration_seconds=60, rest_seconds=0,
                 instructions="Kneel, sit back on heels, extend arms forward, forehead to mat.",
                 muscles_targeted=["back", "hips", "relaxation"]),
    ],
    "hiit": [
        Exercise(name="Jump Squats", sets=4, reps="15", rest_seconds=20,
                 instructions="Perform squat then explode into jump, land softly.",
                 muscles_targeted=["quads", "glutes", "cardio"],
                 modifications="Remove jump for beginners."),
        Exercise(name="Push-Up to T-Rotation", sets=3, reps="8 each side", rest_seconds=20,
                 instructions="Do push-up, rotate to side plank, raise top arm to sky.",
                 muscles_targeted=["chest", "core", "shoulders"]),
        Exercise(name="Squat Thrusts", sets=4, duration_seconds=30, rest_seconds=15,
                 instructions="From standing, squat, place hands down, jump feet to plank, jump back, stand.",
                 muscles_targeted=["full body", "cardio"]),
        Exercise(name="Plank Hold", sets=3, duration_seconds=45, rest_seconds=20,
                 instructions="Maintain straight line from head to heels, engage core throughout.",
                 muscles_targeted=["core", "shoulders", "stability"]),
        Exercise(name="Speed Skaters", sets=3, duration_seconds=30, rest_seconds=20,
                 instructions="Leap sideways, land on one leg, swing opposite leg behind.",
                 muscles_targeted=["legs", "glutes", "cardio"]),
    ],
    "flexibility": [
        Exercise(name="Standing Hamstring Stretch", sets=1, duration_seconds=30, rest_seconds=10,
                 instructions="Stand tall, hinge forward at hips keeping back straight.",
                 muscles_targeted=["hamstrings"]),
        Exercise(name="Hip Flexor Stretch", sets=1, reps="Hold 30s each", rest_seconds=10,
                 instructions="Low lunge, push hips forward, feel stretch in front hip.",
                 muscles_targeted=["hip flexors", "quads"]),
        Exercise(name="Pigeon Pose", sets=1, reps="Hold 45s each side", rest_seconds=15,
                 instructions="From plank, bring one knee to wrist, extend other leg back.",
                 muscles_targeted=["hips", "glutes", "piriformis"]),
        Exercise(name="Thoracic Spine Rotation", sets=2, reps="10 each side", rest_seconds=15,
                 instructions="Seated or kneeling, rotate upper body, keep hips square.",
                 muscles_targeted=["thoracic spine", "obliques"]),
    ],
    "calisthenics": [
        Exercise(name="Diamond Push-Ups", sets=3, reps="8-12", rest_seconds=45,
                 instructions="Hands form diamond shape under chest, elbows track back.",
                 muscles_targeted=["triceps", "inner chest"]),
        Exercise(name="Pike Push-Ups", sets=3, reps="10-12", rest_seconds=45,
                 instructions="Inverted V position, lower head toward floor.",
                 muscles_targeted=["shoulders", "triceps"]),
        Exercise(name="Pseudo Planche Lean", sets=3, duration_seconds=20, rest_seconds=30,
                 instructions="Push-up position, lean forward on fingers, protract shoulders.",
                 muscles_targeted=["wrists", "shoulders", "core"]),
        Exercise(name="L-Sit Hold", sets=3, duration_seconds=10, rest_seconds=30,
                 instructions="Support on two chairs, legs extended parallel to floor.",
                 muscles_targeted=["core", "hip flexors", "triceps"]),
    ],
}

WARM_UP_OPTIONS = [
    "5 min light jog or march in place",
    "Arm circles — 10 forward, 10 backward",
    "Leg swings — 10 each leg, front-back and side-side",
    "Hip circles — 10 each direction",
    "Cat-Cow stretch — 10 repetitions",
    "Neck rolls — 5 each direction (slow)",
    "Ankle rotations — 10 each foot",
    "Torso twists — 10 each side",
]

COOL_DOWN_OPTIONS = [
    "5 min slow walk or gentle march",
    "Seated forward fold — hold 30 seconds",
    "Supine spinal twist — 30 seconds each side",
    "Child's Pose — hold 60 seconds",
    "Diaphragmatic breathing — 10 deep breaths",
    "Shoulder cross-body stretch — 30 seconds each",
    "Quad stretch standing — 30 seconds each leg",
    "Calf stretch against wall — 30 seconds each",
]


class FitnessService:
    """Generates workout plans and exercise recommendations."""

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    @staticmethod
    def get_exercises_for_type(
        workout_type: str,
        fitness_level: str,
        count: int = 5,
    ) -> List[Exercise]:
        """Select exercises matching the workout type."""
        pool = EXERCISE_LIBRARY.get(workout_type, EXERCISE_LIBRARY["strength"])

        # Adjust reps/sets based on level
        selected = random.sample(pool, min(count, len(pool)))
        for ex in selected:
            if fitness_level == FitnessLevel.beginner:
                ex.sets = max(2, (ex.sets or 3) - 1)
            elif fitness_level == FitnessLevel.advanced:
                ex.sets = (ex.sets or 3) + 1
        return selected

    @classmethod
    def build_weekly_plan(
        cls,
        days_per_week: int,
        fitness_level: str,
        goal: str,
        workout_type: str,
        duration_minutes: int,
        focus_area: str | None = None,
    ) -> List[WorkoutPlan]:
        """Build a multi-day workout plan."""
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        active_days = cls._pick_days(days_per_week)
        plans: List[WorkoutPlan] = []

        for day_idx in active_days:
            day_type = cls._day_workout_type(day_idx, workout_type, goal)
            exercises = cls.get_exercises_for_type(day_type, fitness_level)
            plans.append(
                WorkoutPlan(
                    day=day_names[day_idx],
                    workout_type=day_type.replace("_", " ").title(),
                    duration_minutes=duration_minutes,
                    exercises=exercises,
                    warm_up=random.sample(WARM_UP_OPTIONS, 3),
                    cool_down=random.sample(COOL_DOWN_OPTIONS, 3),
                    notes=cls._day_note(goal, fitness_level),
                )
            )
        return plans

    @staticmethod
    def get_tips(goal: str, fitness_level: str) -> List[str]:
        tips_map = {
            "weight_loss": [
                "Stay in a moderate calorie deficit — aim for 0.5 kg/week loss.",
                "Combine cardio with strength training for best fat-loss results.",
                "NEAT (non-exercise activity) matters — take the stairs, walk more.",
                "Prioritise protein to preserve muscle while losing fat.",
            ],
            "muscle_gain": [
                "Progressive overload is key — add reps or weight weekly.",
                "Eat enough protein: aim for 1.6–2 g per kg of bodyweight.",
                "Prioritise compound movements: squats, push-ups, rows.",
                "Sleep 7-9 hours — most muscle repair happens during sleep.",
            ],
            "general_fitness": [
                "Consistency > intensity. Show up even on low-energy days.",
                "Mix cardio, strength, and flexibility for balanced fitness.",
                "Track your workouts to see progress over time.",
                "Stay hydrated — drink water before, during, and after exercise.",
            ],
        }
        return tips_map.get(goal, tips_map["general_fitness"])

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _pick_days(days_per_week: int) -> List[int]:
        """Spread workout days evenly across the week (Mon=0 .. Sun=6)."""
        patterns = {
            1: [1],
            2: [1, 4],
            3: [1, 3, 5],
            4: [1, 2, 4, 5],
            5: [1, 2, 3, 4, 5],
            6: [0, 1, 2, 3, 4, 5],
            7: list(range(7)),
        }
        return patterns.get(days_per_week, [1, 3, 5])

    @staticmethod
    def _day_workout_type(day_idx: int, base_type: str, goal: str) -> str:
        """Vary workout type across the week for balance."""
        if base_type == "home":
            rotation = ["strength", "cardio", "flexibility", "hiit", "yoga", "strength", "cardio"]
            return rotation[day_idx % len(rotation)]
        return base_type

    @staticmethod
    def _day_note(goal: str, level: str) -> str:
        notes = {
            "weight_loss": "Focus on keeping heart rate elevated. Rest 30-45 s between sets.",
            "muscle_gain": "Use controlled tempo — 2s down, 1s hold, 2s up.",
            "endurance": "Focus on total time under tension; keep rest periods short.",
            "flexibility": "Hold each stretch for at least 30 seconds; never bounce.",
        }
        return notes.get(goal, "Maintain good form throughout. Quality over quantity.")
