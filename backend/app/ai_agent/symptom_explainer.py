"""
Symptom Explainer

Provides educational explanations for Parkinson disease
symptoms.

This module does NOT diagnose diseases or replace
professional medical advice.
"""

from datetime import datetime
from typing import Dict, List


class SymptomExplainer:
    """
    Parkinson symptom explanation engine.
    """

    def __init__(self):

        self.symptoms = self._load_symptoms()

    # =====================================================
    # Explain One Symptom
    # =====================================================

    def explain(
        self,
        symptom: str,
    ) -> Dict:
        """
        Explain a symptom.
        """

        key = symptom.lower()

        if key not in self.symptoms:

            return {
                "symptom": symptom,
                "found": False,
                "message": (
                    "Educational information for this symptom "
                    "is currently unavailable."
                ),
                "timestamp": datetime.utcnow(),
            }

        info = self.symptoms[key].copy()

        info["found"] = True
        info["timestamp"] = datetime.utcnow()

        return info

    # =====================================================
    # Explain Multiple Symptoms
    # =====================================================

    def explain_many(
        self,
        symptoms: List[str],
    ) -> List[Dict]:
        """
        Explain multiple symptoms.
        """

        return [
            self.explain(symptom)
            for symptom in symptoms
        ]

    # =====================================================
    # Available Symptoms
    # =====================================================

    def available_symptoms(
        self,
    ) -> List[str]:
        """
        Return supported symptoms.
        """

        return sorted(self.symptoms.keys())

    # =====================================================
    # Search
    # =====================================================

    def search(
        self,
        keyword: str,
    ) -> List[str]:
        """
        Search symptoms.
        """

        keyword = keyword.lower()

        return [
            symptom
            for symptom in self.symptoms
            if keyword in symptom
        ]

    # =====================================================
    # Educational Disclaimer
    # =====================================================

    def disclaimer(
        self,
    ) -> str:

        return (
            "These explanations are educational only. "
            "Symptoms may have many possible causes. "
            "Consult a qualified healthcare professional "
            "for diagnosis and treatment."
        )

    # =====================================================
    # Symptom Database
    # =====================================================

    def _load_symptoms(
        self,
    ) -> Dict:

        return {

            "tremor": {
                "symptom": "Tremor",
                "description":
                    "An involuntary rhythmic shaking that often "
                    "starts in one hand or fingers.",
                "daily_impact":
                    "May affect writing, eating, or holding objects.",
                "general_management": [
                    "Regular medical follow-up",
                    "Physical activity",
                    "Occupational therapy",
                ],
                "consult_when":
                    "If tremors worsen or interfere with daily activities.",
            },

            "rigidity": {
                "symptom": "Rigidity",
                "description":
                    "Muscle stiffness that can limit movement.",
                "daily_impact":
                    "Can make walking and turning more difficult.",
                "general_management": [
                    "Stretching exercises",
                    "Physical therapy",
                    "Maintain regular movement",
                ],
                "consult_when":
                    "If stiffness limits normal activities.",
            },

            "bradykinesia": {
                "symptom": "Bradykinesia",
                "description":
                    "Slowness of voluntary movement.",
                "daily_impact":
                    "Tasks such as dressing or eating may take longer.",
                "general_management": [
                    "Exercise",
                    "Physical therapy",
                    "Maintain daily activity",
                ],
                "consult_when":
                    "If movement becomes progressively slower.",
            },

            "balance": {
                "symptom": "Balance Problems",
                "description":
                    "Difficulty maintaining stability while standing or walking.",
                "daily_impact":
                    "May increase the risk of falls.",
                "general_management": [
                    "Balance exercises",
                    "Use assistive devices if recommended",
                    "Remove fall hazards at home",
                ],
                "consult_when":
                    "If falls occur or balance worsens.",
            },

            "speech": {
                "symptom": "Speech Changes",
                "description":
                    "Speech may become softer, slower, or less clear.",
                "daily_impact":
                    "Can affect communication with others.",
                "general_management": [
                    "Speech therapy",
                    "Voice exercises",
                    "Practice speaking clearly",
                ],
                "consult_when":
                    "If communication becomes difficult.",
            },

            "sleep": {
                "symptom": "Sleep Disturbances",
                "description":
                    "Difficulty falling asleep or staying asleep.",
                "daily_impact":
                    "May cause daytime fatigue.",
                "general_management": [
                    "Maintain regular sleep schedule",
                    "Reduce caffeine late in the day",
                    "Discuss persistent issues with a clinician",
                ],
                "consult_when":
                    "If sleep problems persist.",
            },

            "fatigue": {
                "symptom": "Fatigue",
                "description":
                    "Persistent feeling of tiredness or low energy.",
                "daily_impact":
                    "Can reduce participation in daily activities.",
                "general_management": [
                    "Balanced nutrition",
                    "Regular exercise",
                    "Adequate rest",
                ],
                "consult_when":
                    "If fatigue significantly affects quality of life.",
            },

            "walking": {
                "symptom": "Walking Difficulty",
                "description":
                    "Changes in walking speed or stride length.",
                "daily_impact":
                    "May increase fall risk and reduce mobility.",
                "general_management": [
                    "Walking exercises",
                    "Physical therapy",
                    "Regular mobility assessment",
                ],
                "consult_when":
                    "If walking becomes unsafe or progressively difficult.",
            },
        }

    # =====================================================
    # Status
    # =====================================================

    def status(
        self,
    ) -> Dict:

        return {
            "status": "Online",
            "supported_symptoms": len(self.symptoms),
            "version": "1.0.0",
        }
