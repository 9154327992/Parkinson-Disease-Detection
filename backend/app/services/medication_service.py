"""
Medication Service

Educational medication guidance for Parkinson Disease.
This service does NOT prescribe, modify, or recommend medications.
"""

from typing import List


class MedicationService:
    """
    Educational medication service.
    """

    def __init__(self):
        pass

    # =====================================================
    # Educational Medication Information
    # =====================================================

    def get_medication_information(
        self,
        medication_name: str,
    ) -> dict:
        """
        Return educational information for a medication.
        """

        medications = {
            "Levodopa": {
                "name": "Levodopa",
                "purpose": (
                    "Commonly used to help manage movement symptoms "
                    "associated with Parkinson disease."
                ),
                "common_side_effects": [
                    "Nausea",
                    "Dizziness",
                    "Sleepiness",
                ],
                "important_notes": [
                    "Take exactly as prescribed.",
                    "Do not stop suddenly without medical advice.",
                ],
            },
            "Carbidopa-Levodopa": {
                "name": "Carbidopa-Levodopa",
                "purpose": (
                    "Frequently prescribed combination therapy "
                    "for Parkinson symptoms."
                ),
                "common_side_effects": [
                    "Low blood pressure",
                    "Dizziness",
                    "Nausea",
                ],
                "important_notes": [
                    "Follow your physician's instructions.",
                    "Report unusual movements to your healthcare provider.",
                ],
            },
        }

        return medications.get(
            medication_name,
            {
                "name": medication_name,
                "message": (
                    "Educational information is currently unavailable."
                ),
            },
        )

    # =====================================================
    # Medication Reminder
    # =====================================================

    def get_medication_reminders(
        self,
        patient_id: int,
    ) -> List[dict]:
        """
        Return medication reminders.

        Replace with database records in production.
        """

        return [
            {
                "patient_id": patient_id,
                "medication": "Levodopa",
                "time": "08:00",
                "frequency": "Daily",
            },
            {
                "patient_id": patient_id,
                "medication": "Levodopa",
                "time": "20:00",
                "frequency": "Daily",
            },
        ]

    # =====================================================
    # Drug Interaction Check
    # =====================================================

    def check_interactions(
        self,
        medications: List[str],
    ) -> dict:
        """
        Educational interaction checker.

        This is NOT a substitute for a pharmacist
        or physician review.
        """

        warnings = []

        if (
            "Levodopa" in medications
            and "Iron Supplement" in medications
        ):
            warnings.append(
                "Iron supplements may reduce the absorption of Levodopa."
            )

        if (
            "Levodopa" in medications
            and "High Protein Diet" in medications
        ):
            warnings.append(
                "Large amounts of dietary protein may affect Levodopa absorption."
            )

        return {
            "checked_medications": medications,
            "warnings": warnings,
            "disclaimer": (
                "Always consult your physician or pharmacist "
                "before combining medications or supplements."
            ),
        }

    # =====================================================
    # Medication Safety Tips
    # =====================================================

    def get_safety_guidance(
        self,
    ) -> List[str]:
        """
        General medication safety guidance.
        """

        return [
            "Take medications exactly as prescribed.",
            "Do not stop medications without consulting your physician.",
            "Store medications according to label instructions.",
            "Inform your healthcare provider about all medicines and supplements you take.",
            "Report any unusual side effects promptly.",
            "Keep medications out of reach of children.",
        ]

    # =====================================================
    # Frequently Asked Questions
    # =====================================================

    def get_faq(self) -> List[dict]:
        """
        Medication-related FAQs.
        """

        return [
            {
                "question": "Can I stop taking Parkinson medication if I feel better?",
                "answer": (
                    "Do not stop taking prescribed medication without "
                    "consulting your healthcare provider."
                ),
            },
            {
                "question": "What should I do if I miss a dose?",
                "answer": (
                    "Follow your healthcare provider's instructions or "
                    "the medication label. If you are unsure, contact "
                    "your pharmacist or physician."
                ),
            },
            {
                "question": "Can supplements interact with Parkinson medication?",
                "answer": (
                    "Yes. Some supplements and foods may interact with "
                    "certain medications. Discuss all supplements with "
                    "your healthcare provider."
                ),
            },
        ]

    # =====================================================
    # Educational Disclaimer
    # =====================================================

    def get_disclaimer(
        self,
    ) -> str:
        """
        Return the service disclaimer.
        """

        return (
            "This service provides educational information only. "
            "It does not prescribe medications, adjust treatment plans, "
            "or replace professional medical advice. Always consult "
            "a qualified healthcare professional regarding medications."
        )
