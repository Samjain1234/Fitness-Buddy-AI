"""
Motivation service — curates motivational quotes, streaks, and
habit coaching messages.
"""
from __future__ import annotations

import random
from typing import List


QUOTES = [
    ("The only bad workout is the one that didn't happen.", "Unknown"),
    ("Strength does not come from the body. It comes from the will of the soul.", "Mahatma Gandhi"),
    ("Take care of your body. It's the only place you have to live.", "Jim Rohn"),
    ("Your body can stand almost anything. It's your mind you have to convince.", "Unknown"),
    ("The pain you feel today will be the strength you feel tomorrow.", "Arnold Schwarzenegger"),
    ("Don't wish for it. Work for it.", "Unknown"),
    ("It never gets easier, you just get stronger.", "Unknown"),
    ("One workout at a time. One day at a time.", "Unknown"),
    ("Success is what comes after you stop making excuses.", "Luis Galarza"),
    ("Fitness is not about being better than someone else. It's about being better than you used to be.", "Unknown"),
    ("Wake up with determination. Go to bed with satisfaction.", "Unknown"),
    ("Sweat is just fat crying.", "Unknown"),
    ("Push yourself because no one else is going to do it for you.", "Unknown"),
    ("Great things never came from comfort zones.", "Unknown"),
    ("You don't have to be great to start, but you have to start to be great.", "Zig Ziglar"),
    ("Karo ya na karo, koshish toh karo. (Do it or don't — but at least try.)", "Indian Proverb"),
    ("Swaasthya hi sampada hai. (Health is wealth.)", "Indian Proverb"),
    ("Consistency is the true foundation of trust.", "Roy T. Bennett"),
    ("The secret of getting ahead is getting started.", "Mark Twain"),
    ("Small steps in the right direction are better than big steps in the wrong one.", "Unknown"),
]


HABIT_FEEDBACK = {
    "excellent": [
        "🌟 Outstanding! You're building unstoppable momentum!",
        "🔥 You're on fire! Keep this energy going!",
        "💪 Top-tier effort today. Your future self thanks you!",
    ],
    "good": [
        "✅ Great job today! You're making real progress!",
        "👍 Solid effort! Stay consistent and results will follow.",
        "🎯 Good work! Every session counts.",
    ],
    "average": [
        "😊 A decent day! Tomorrow, let's push a little more.",
        "💡 You showed up — that's already a win! Can you add one more habit tomorrow?",
        "🚀 Not your best day, but you're still moving forward!",
    ],
    "below_average": [
        "🌱 Every expert was once a beginner. Tomorrow is a fresh start!",
        "💬 Small progress is still progress. What can you improve tomorrow?",
        "🌤️ Today was tough? That's okay. Rest is part of the process.",
    ],
}


class MotivationService:
    """Provides motivational content and wellness feedback."""

    @staticmethod
    def get_random_quote() -> dict:
        quote, author = random.choice(QUOTES)
        return {"quote": quote, "author": author}

    @staticmethod
    def get_habit_feedback(wellness_score: float) -> str:
        if wellness_score >= 80:
            return random.choice(HABIT_FEEDBACK["excellent"])
        elif wellness_score >= 60:
            return random.choice(HABIT_FEEDBACK["good"])
        elif wellness_score >= 40:
            return random.choice(HABIT_FEEDBACK["average"])
        return random.choice(HABIT_FEEDBACK["below_average"])

    @staticmethod
    def calculate_wellness_score(
        water_glasses: int,
        sleep_hours: float,
        steps: int,
        workout_done: bool,
        mood: int,
    ) -> float:
        """
        Compute a 0-100 wellness score from daily habits.
        Weights: sleep 30%, hydration 20%, activity 25%, mood 15%, workout 10%.
        """
        sleep_score = min(sleep_hours / 8.0, 1.0) * 30
        water_score = min(water_glasses / 8.0, 1.0) * 20
        steps_score = min(steps / 10000.0, 1.0) * 20
        workout_score = 10.0 if workout_done else 0.0
        mood_score = (mood / 10.0) * 20

        return round(sleep_score + water_score + steps_score + workout_score + mood_score, 1)

    @staticmethod
    def streak_message(streak: int) -> str:
        if streak == 0:
            return "Start your streak today — every journey begins with a single step! 🚀"
        elif streak < 3:
            return f"🔥 {streak}-day streak! You've started something great. Keep going!"
        elif streak < 7:
            return f"💪 {streak}-day streak! You're building a powerful habit!"
        elif streak < 14:
            return f"⚡ {streak}-day streak! You're in the zone. Don't break the chain!"
        elif streak < 30:
            return f"🏆 {streak}-day streak! Incredible dedication. You're unstoppable!"
        return f"🌟 {streak}-day streak! You're a fitness legend. Inspire others!"
