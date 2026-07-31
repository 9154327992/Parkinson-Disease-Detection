"""
Exercise Service

Business logic for exercise recommendations.
"""

from app.schemas.recommendation import ExerciseRecommendation


class ExerciseService:
    """
    Service for exercise recommendations.
    """

    def __init__(self):
        pass

    # =====================================================
    # Exercise Plan by Risk Level
    # =====================================================

    def get_exercise_plan(
        self,
        risk_level: str,
    ) -> list[ExerciseRecommendation]:
        """
        Return a complete exercise plan.
        """

        exercises = []

        exercises.extend(self.get_walking_exercises())
        exercises.extend(self.get_balance_exercises())
        exercises.extend(self.get_flexibility_exercises())
        exercises.extend(self.get_strength_exercises())

        if risk_level == "High Risk":
            exercises.extend(self.get_speech_exercises())

        return exercises

    # =====================================================
    # Walking Exercises
    # =====================================================

    def get_walking_exercises(
        self,
    ) -> list[ExerciseRecommendation]:
        """
        Walking exercises.
        """

        return [
            ExerciseRecommendation(
                name="Walking",
                duration="30 minutes",
                frequency="5 days/week",
                description=(
                    "Walk at a comfortable pace to improve mobility, "
                    "balance, and cardiovascular health."
                ),
            )
        ]

    # =====================================================
    # Balance Exercises
    # =====================================================

    def get_balance_exercises(
        self,
    ) -> list[ExerciseRecommendation]:
        """
        Balance exercises.
        """

        return [
            ExerciseRecommendation(
                name="Single-Leg Stand",
                duration="10 minutes",
                frequency="3 days/week",
                description=(
                    "Practice standing on one leg while holding a stable "
                    "surface if needed."
                ),
            ),
            ExerciseRecommendation(
                name="Heel-to-Toe Walk",
                duration="10 minutes",
                frequency="3 days/week",
                description=(
                    "Walk in a straight line placing one foot directly "
                    "in front of the other."
                ),
            ),
        ]

    # =====================================================
    # Flexibility Exercises
    # =====================================================

    def get_flexibility_exercises(
        self,
    ) -> list[ExerciseRecommendation]:
        """
        Stretching and flexibility.
        """

        return [
            ExerciseRecommendation(
                name="Neck Stretch",
                duration="5 minutes",
                frequency="Daily",
                description="Gentle neck stretches to improve mobility.",
            ),
            ExerciseRecommendation(
                name="Shoulder Stretch",
                duration="5 minutes",
                frequency="Daily",
                description="Increase shoulder flexibility.",
            ),
            ExerciseRecommendation(
                name="Hamstring Stretch",
                duration="10 minutes",
                frequency="Daily",
                description="Improve lower body flexibility.",
            ),
        ]

    # =====================================================
    # Strength Exercises
    # =====================================================

    def get_strength_exercises(
        self,
    ) -> list[ExerciseRecommendation]:
        """
        Strength training.
        """

        return [
            ExerciseRecommendation(
                name="Chair Squats",
                duration="15 minutes",
                frequency="3 days/week",
                description=(
                    "Strengthen leg muscles using body weight or chair support."
                ),
            ),
            ExerciseRecommendation(
                name="Wall Push-Ups",
                duration="15 minutes",
                frequency="3 days/week",
                description=(
                    "Improve upper body strength with wall-supported push-ups."
                ),
            ),
        ]

    # =====================================================
    # Speech Exercises
    # =====================================================

    def get_speech_exercises(
        self,
    ) -> list[ExerciseRecommendation]:
        """
        Speech therapy exercises.
        """

        return [
            ExerciseRecommendation(
                name="Voice Projection",
                duration="20 minutes",
                frequency="Daily",
                description=(
                    "Practice speaking loudly and clearly to improve vocal strength."
                ),
            ),
            ExerciseRecommendation(
                name="Breathing Exercises",
                duration="15 minutes",
                frequency="Daily",
                description=(
                    "Improve breath control to support speech production."
                ),
            ),
        ]

    # =====================================================
    # Daily Exercise Schedule
    # =====================================================

    def get_daily_schedule(
        self,
    ) -> dict:
        """
        Suggested daily exercise schedule.
        """

        return {
            "Morning": [
                "Walking",
                "Neck Stretch",
                "Shoulder Stretch",
            ],
            "Afternoon": [
                "Chair Squats",
                "Wall Push-Ups",
            ],
            "Evening": [
                "Hamstring Stretch",
                "Breathing Exercises",
            ],
        }

    # =====================================================
    # Exercise Safety Tips
    # =====================================================

    def get_safety_tips(
        self,
    ) -> list[str]:
        """
        General exercise safety recommendations.
        """

        return [
            "Consult your healthcare provider before starting a new exercise program.",
            "Begin slowly and increase intensity gradually.",
            "Stop exercising if you experience dizziness, chest pain, or severe discomfort.",
            "Stay hydrated during physical activity.",
            "Use supportive footwear and exercise in a safe environment.",
            "Have assistance available if you are at risk of falling.",
        ]
