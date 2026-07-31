"""
Exercise Planner

AI-powered exercise planning for Parkinson Disease Detection.

This module creates personalized exercise schedules using
educational guidance. It does not replace advice from a
physician or physiotherapist.
"""

from datetime import datetime
from typing import Dict, List


class ExercisePlanner:
    """
    AI Exercise Planner.
    """

    def __init__(self):
        pass

    # =====================================================
    # Generate Exercise Plan
    # =====================================================

    def generate_plan(
        self,
        risk_level: str,
    ) -> Dict:
        """
        Generate complete exercise plan.
        """

        return {
            "risk_level": risk_level,
            "daily_plan": self.daily_plan(risk_level),
            "weekly_plan": self.weekly_plan(risk_level),
            "safety_tips": self.safety_tips(),
            "motivation": self.motivation(),
            "generated_at": datetime.utcnow(),
        }

    # =====================================================
    # Daily Plan
    # =====================================================

    def daily_plan(
        self,
        risk_level: str,
    ) -> Dict:

        morning = [
            "10-minute stretching",
            "20-minute walk",
        ]

        afternoon = [
            "Balance exercises",
            "Chair exercises",
        ]

        evening = [
            "Breathing exercises",
            "Light stretching",
        ]

        if risk_level == "High Risk":
            afternoon.append(
                "Speech therapy exercises"
            )

        return {
            "Morning": morning,
            "Afternoon": afternoon,
            "Evening": evening,
        }

    # =====================================================
    # Weekly Plan
    # =====================================================

    def weekly_plan(
        self,
        risk_level: str,
    ) -> Dict:

        schedule = {}

        for day in [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]:

            schedule[day] = [
                "Walking",
                "Stretching",
            ]

        if risk_level in (
            "Moderate Risk",
            "High Risk",
        ):

            schedule["Tuesday"].append(
                "Balance training"
            )

            schedule["Thursday"].append(
                "Strength exercises"
            )

            schedule["Saturday"].append(
                "Speech exercises"
            )

        return schedule

    # =====================================================
    # Exercise Categories
    # =====================================================

    def exercise_categories(
        self,
    ) -> Dict:

        return {

            "Walking": [
                "Outdoor walking",
                "Indoor treadmill",
            ],

            "Balance": [
                "Heel-to-toe walk",
                "Single-leg stand",
            ],

            "Strength": [
                "Chair squats",
                "Wall push-ups",
            ],

            "Flexibility": [
                "Neck stretch",
                "Hamstring stretch",
                "Shoulder stretch",
            ],

            "Breathing": [
                "Deep breathing",
                "Diaphragmatic breathing",
            ],

            "Speech": [
                "Voice projection",
                "Reading aloud",
            ],
        }

    # =====================================================
    # Safety Tips
    # =====================================================

    def safety_tips(
        self,
    ) -> List[str]:

        return [
            "Consult your healthcare provider before starting a new exercise routine.",
            "Exercise in a safe, clutter-free environment.",
            "Wear supportive footwear.",
            "Stay hydrated.",
            "Stop exercising if you experience dizziness, chest pain, or severe discomfort.",
            "Use assistance if you are at risk of falling.",
        ]

    # =====================================================
    # Motivation
    # =====================================================

    def motivation(
        self,
    ) -> str:

        return (
            "Consistency is more important than intensity. "
            "Small amounts of regular physical activity can "
            "support mobility, balance, and overall well-being."
        )

    # =====================================================
    # Progress Goals
    # =====================================================

    def progress_goals(
        self,
    ) -> List[str]:

        return [
            "Complete at least 30 minutes of activity most days of the week.",
            "Improve flexibility through daily stretching.",
            "Practice balance exercises regularly.",
            "Maintain good posture during exercises.",
        ]

    # =====================================================
    # Exercise Duration
    # =====================================================

    def recommended_duration(
        self,
        risk_level: str,
    ) -> str:

        durations = {
            "Minimal Risk": "20–30 minutes/day",
            "Low Risk": "30 minutes/day",
            "Moderate Risk": "30–45 minutes/day",
            "High Risk": "30–45 minutes/day with professional supervision if needed",
        }

        return durations.get(
            risk_level,
            "30 minutes/day",
        )

    # =====================================================
    # Disclaimer
    # =====================================================

    def disclaimer(
        self,
    ) -> str:

        return (
            "Exercise recommendations are educational only. "
            "Follow the guidance of your healthcare provider "
            "or physiotherapist when starting or modifying an exercise program."
        )

    # =====================================================
    # Status
    # =====================================================

    def status(
        self,
    ) -> Dict:

        return {
            "status": "Online",
            "version": "1.0.0",
            "exercise_categories": len(
                self.exercise_categories()
            ),
        }
