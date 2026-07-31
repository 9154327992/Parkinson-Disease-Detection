"""
Health Assistant

Central AI agent for the Parkinson Disease Detection System.

This module orchestrates all AI assistant components and
provides educational guidance. It does NOT diagnose,
prescribe, or replace professional medical advice.
"""

from datetime import datetime
from typing import Dict, List

from app.ai_agent.exercise_planner import ExercisePlanner
from app.ai_agent.medication_reminder import MedicationReminder
from app.ai_agent.recommendation import RecommendationAgent
from app.ai_agent.symptom_explainer import SymptomExplainer


class HealthAssistant:
    """
    Central AI Health Assistant.
    """

    def __init__(self):

        self.symptoms = SymptomExplainer()

        self.recommendations = RecommendationAgent()

        self.exercise = ExercisePlanner()

        self.medication = MedicationReminder()

    # =====================================================
    # Patient Summary
    # =====================================================

    def patient_summary(
        self,
        prediction: str,
        confidence: float,
    ) -> Dict:
        """
        Generate patient-friendly summary.
        """

        return {
            "prediction": prediction,
            "confidence": confidence,
            "summary": self._summary(
                prediction,
                confidence,
            ),
            "generated_at": datetime.utcnow(),
        }

    # =====================================================
    # Explain Symptoms
    # =====================================================

    def explain_symptoms(
        self,
        symptoms: List[str],
    ) -> List[Dict]:
        """
        Explain symptoms.
        """

        explanations = []

        for symptom in symptoms:

            explanations.append(
                self.symptoms.explain(
                    symptom
                )
            )

        return explanations

    # =====================================================
    # Recommendations
    # =====================================================

    def recommendations_for_patient(
        self,
        risk_level: str,
    ) -> Dict:
        """
        Return AI recommendations.
        """

        return self.recommendations.generate(
            risk_level
        )

    # =====================================================
    # Exercise Plan
    # =====================================================

    def exercise_plan(
        self,
        risk_level: str,
    ):
        """
        Personalized exercise plan.
        """

        return self.exercise.generate_plan(
            risk_level
        )

    # =====================================================
    # Medication Reminders
    # =====================================================

    def medication_reminders(
        self,
        patient_id: int,
    ):
        """
        Medication reminders.
        """

        return self.medication.get_reminders(
            patient_id
        )

    # =====================================================
    # Dashboard
    # =====================================================

    def dashboard(
        self,
        prediction: str,
        confidence: float,
        risk_level: str,
    ):
        """
        Complete dashboard information.
        """

        return {
            "summary": self.patient_summary(
                prediction,
                confidence,
            ),
            "recommendations":
                self.recommendations_for_patient(
                    risk_level
                ),
            "exercise":
                self.exercise_plan(
                    risk_level
                ),
            "generated_at":
                datetime.utcnow(),
        }

    # =====================================================
    # Health Tips
    # =====================================================

    def health_tips(self):
        """
        General health guidance.
        """

        return [
            "Stay physically active.",
            "Maintain a balanced diet.",
            "Sleep 7–9 hours each night.",
            "Keep regular medical appointments.",
            "Practice balance and stretching exercises.",
            "Take medications exactly as prescribed.",
        ]

    # =====================================================
    # Greeting
    # =====================================================

    def greeting(
        self,
        patient_name: str,
    ) -> str:
        """
        Welcome message.
        """

        return (
            f"Hello {patient_name}. "
            "I'm your Parkinson Health Assistant. "
            "I can help explain symptoms, predictions, "
            "exercise recommendations, medication reminders, "
            "and healthy lifestyle guidance."
        )

    # =====================================================
    # Disclaimer
    # =====================================================

    def disclaimer(self):
        """
        Medical disclaimer.
        """

        return (
            "This AI assistant provides educational "
            "information only and should not be used "
            "as a substitute for professional medical advice, "
            "diagnosis, or treatment."
        )

    # =====================================================
    # Internal Summary
    # =====================================================

    def _summary(
        self,
        prediction: str,
        confidence: float,
    ) -> str:

        if prediction == "Parkinson Detected":

            return (
                f"The model detected patterns associated "
                f"with Parkinson disease with "
                f"{confidence:.2f}% confidence. "
                "This result is not a diagnosis. "
                "Please consult a neurologist for a "
                "comprehensive clinical evaluation."
            )

        return (
            f"The analyzed voice features were more "
            f"consistent with the healthy class "
            f"({confidence:.2f}% confidence). "
            "Continue maintaining a healthy lifestyle "
            "and seek medical advice if symptoms develop."
        )

    # =====================================================
    # Status
    # =====================================================

    def status(self):

        return {
            "assistant": "Online",
            "version": "1.0.0",
            "modules": {
                "symptom_explainer": True,
                "recommendation": True,
                "exercise_planner": True,
                "medication_reminder": True,
            },
        }
