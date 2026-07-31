"""
Recommendation Service

Business logic for personalized recommendations.
"""

from app.schemas.recommendation import (
    RecommendationRequest,
    RecommendationResponse,
    RecommendationSummary,
    RecommendationHistory,
    LifestyleRecommendation,
    DietRecommendation,
    ExerciseRecommendation,
    FollowUpRecommendation,
    MedicationGuidance,
)


class RecommendationService:
    """
    Generate personalized recommendations.
    """

    def __init__(self):
        pass

    # =====================================================
    # Generate Recommendation
    # =====================================================

    def generate_recommendation(
        self,
        request: RecommendationRequest,
    ) -> RecommendationResponse:
        """
        Generate recommendations based on prediction.
        """

        recommendation = self._general_recommendation(
            request.risk_level
        )

        return RecommendationResponse(
            patient_id=request.patient_id,
            risk_level=request.risk_level,
            recommendation=recommendation,
            lifestyle=self.get_lifestyle(
                request.risk_level
            ),
            diet=self.get_diet(),
            exercises=self.get_exercises(
                request.risk_level
            ),
            follow_up=self.get_follow_up(
                request.risk_level
            ),
            medication=self.get_medication_guidance(),
            warning=self.get_warning(
                request.risk_level
            ),
        )

    # =====================================================
    # General Recommendation
    # =====================================================

    def _general_recommendation(
        self,
        risk_level: str,
    ) -> str:

        recommendations = {
            "High Risk":
                (
                    "Consult a neurologist as soon as possible "
                    "for a comprehensive clinical evaluation."
                ),

            "Medium Risk":
                (
                    "Arrange a follow-up assessment and monitor "
                    "symptoms regularly."
                ),

            "Low Risk":
                (
                    "Continue healthy habits and maintain regular "
                    "medical check-ups."
                ),
        }

        return recommendations.get(
            risk_level,
            "Consult a healthcare professional."
        )

    # =====================================================
    # Lifestyle
    # =====================================================

    def get_lifestyle(
        self,
        risk_level: str,
    ) -> list[LifestyleRecommendation]:

        items = [
            LifestyleRecommendation(
                title="Sleep",
                description="Aim for 7–8 hours of quality sleep each night."
            ),
            LifestyleRecommendation(
                title="Stress Management",
                description="Practice meditation, yoga, or breathing exercises."
            ),
            LifestyleRecommendation(
                title="Hydration",
                description="Drink sufficient water throughout the day."
            ),
        ]

        if risk_level == "High Risk":
            items.append(
                LifestyleRecommendation(
                    title="Medical Evaluation",
                    description="Seek specialist evaluation promptly."
                )
            )

        return items

    # =====================================================
    # Diet
    # =====================================================

    def get_diet(self) -> list[DietRecommendation]:

        return [
            DietRecommendation(
                title="Balanced Diet",
                description="Eat fruits, vegetables, whole grains, and lean protein."
            ),
            DietRecommendation(
                title="Omega-3",
                description="Include fish, walnuts, and flaxseed."
            ),
            DietRecommendation(
                title="Limit Processed Foods",
                description="Reduce high-sugar and highly processed foods."
            ),
        ]

    # =====================================================
    # Exercises
    # =====================================================

    def get_exercises(
        self,
        risk_level: str,
    ) -> list[ExerciseRecommendation]:

        exercises = [
            ExerciseRecommendation(
                name="Walking",
                duration="30 minutes",
                frequency="5 days/week",
                description="Moderate walking."
            ),
            ExerciseRecommendation(
                name="Stretching",
                duration="15 minutes",
                frequency="Daily",
                description="Improve flexibility."
            ),
            ExerciseRecommendation(
                name="Balance Training",
                duration="20 minutes",
                frequency="3 days/week",
                description="Improve stability and reduce fall risk."
            ),
        ]

        if risk_level == "High Risk":
            exercises.append(
                ExerciseRecommendation(
                    name="Speech Therapy",
                    duration="30 minutes",
                    frequency="Weekly",
                    description="Improve speech and swallowing function."
                )
            )

        return exercises

    # =====================================================
    # Follow-up
    # =====================================================

    def get_follow_up(
        self,
        risk_level: str,
    ) -> FollowUpRecommendation:

        if risk_level == "High Risk":
            return FollowUpRecommendation(
                next_visit="Within 7 days",
                specialist="Neurologist",
                notes="Bring previous medical records."
            )

        if risk_level == "Medium Risk":
            return FollowUpRecommendation(
                next_visit="Within 30 days",
                specialist="Primary Care Physician",
                notes="Monitor symptoms."
            )

        return FollowUpRecommendation(
            next_visit="Routine annual visit",
            specialist="Primary Care Physician",
            notes="Maintain healthy lifestyle."
        )

    # =====================================================
    # Medication Guidance
    # =====================================================

    def get_medication_guidance(
        self,
    ) -> MedicationGuidance:

        return MedicationGuidance(
            note=(
                "Take medications only as prescribed by your healthcare provider."
            ),
            disclaimer=(
                "This application does not prescribe or adjust medications."
            ),
        )

    # =====================================================
    # Warning
    # =====================================================

    def get_warning(
        self,
        risk_level: str,
    ) -> str:

        if risk_level == "High Risk":
            return (
                "Seek immediate medical attention if symptoms rapidly worsen."
            )

        return (
            "These recommendations are educational and should not replace "
            "professional medical advice."
        )

    # =====================================================
    # Recommendation Summary
    # =====================================================

    def get_summary(
        self,
        patient_id: int,
    ) -> RecommendationSummary:

        return RecommendationSummary(
            patient_id=patient_id,
            risk_level="Medium Risk",
            recommendation="Schedule a follow-up assessment."
        )

    # =====================================================
    # Recommendation History
    # =====================================================

    def get_history(
        self,
        patient_id: int,
    ) -> list[RecommendationHistory]:

        return [
            RecommendationHistory(
                patient_id=patient_id,
                prediction_id=1,
                recommendation="Consult a neurologist.",
                risk_level="High Risk",
                created_at="2026-07-31T10:30:00",
            )
        ]
