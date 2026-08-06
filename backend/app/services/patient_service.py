from datetime import datetime
from typing import List

from app.schemas.patient import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientSummary,
    PatientStatistics,
    PatientHistory,
)


class PatientService:
    """
    Handles patient management operations.
    """

    def __init__(self):
        """
        Initialize patient service.

        Later this will initialize the database repository.

        Example:
            self.patient_repository = PatientRepository()
        """
        pass

    # =====================================================
    # Create Patient
    # =====================================================

    def create_patient(
        self,
        patient: PatientCreate,
        created_by: int,
    ) -> PatientResponse:
        """
        Create a new patient.
        """

        # TODO:
        # Validate duplicate patient
        # Save to database

        return PatientResponse(
            id=1,
            full_name=f"{patient.first_name} {patient.last_name}",
            first_name=patient.first_name,
            last_name=patient.last_name,
            age=patient.age,
            gender=patient.gender,
            phone=patient.phone,
            email=patient.email,
            address=patient.address,
            emergency_contact=patient.emergency_contact,
            medical_history=patient.medical_history,
            created_by=created_by,
            created_at=datetime.utcnow(),
            updated_at=None,
        )

    # =====================================================
    # Get Patient
    # =====================================================

    def get_patient(
        self,
        patient_id: int,
    ) -> PatientResponse:
        """
        Retrieve a patient by ID.
        """

        return PatientResponse(
            id=patient_id,
            full_name="John Doe",
            first_name="John",
            last_name="Doe",
            age=67,
            gender="Male",
            phone="+1-555-123456",
            email="john@example.com",
            address="New York",
            emergency_contact="Jane Doe",
            medical_history="Hypertension",
            created_by=1,
            created_at=datetime.utcnow(),
            updated_at=None,
        )

    # =====================================================
    # Get All Patients
    # =====================================================

    def get_patients(
        self,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
    ) -> List[PatientSummary]:
        patients = [
            PatientSummary(
                id=1,
                full_name="John Doe",
                age=67,
                gender="Male",
            ),
            PatientSummary(
                id=2,
                full_name="Jane Smith",
                age=61,
                gender="Female",
            ),
        ]

        if search:
            patients = [
                patient
                for patient in patients
                if search.lower() in patient.full_name.lower()
            ]

        return patients[skip:skip + limit]

    # =====================================================
    # Update Patient
    # =====================================================

    def update_patient(
        self,
        patient_id: int,
        patient: PatientUpdate,
    ) -> PatientResponse:
        """
        Update patient information.
        """

        # TODO:
        # Update database

        return PatientResponse(
            id=patient_id,
            full_name="John Doe",
            first_name=patient.first_name or "John",
            last_name=patient.last_name or "Doe",
            age=patient.age or 67,
            gender=patient.gender or "Male",
            phone=patient.phone,
            email=patient.email,
            address=patient.address,
            emergency_contact=patient.emergency_contact,
            medical_history=patient.medical_history,
            created_by=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    # =====================================================
    # Delete Patient
    # =====================================================

    def delete_patient(
        self,
        patient_id: int,
    ) -> dict:
        """
        Delete patient.
        """

        return {
            "message": f"Patient {patient_id} deleted successfully."
        }

    # =====================================================
    # Search Patients
    # =====================================================

    def search_patients(
        self,
        keyword: str,
    ) -> List[PatientSummary]:
        """
        Search patients by name.
        """

        return [
            PatientSummary(
                id=1,
                full_name="John Doe",
                age=67,
                gender="Male",
            )
        ]

    # =====================================================
    # Patient History
    # =====================================================

    def patient_history(
        self,
        patient_id: int,
    ) -> List[PatientHistory]:
        """
        Return prediction history for a patient.
        """

        return [
            PatientHistory(
                patient_id=patient_id,
                prediction_id=10,
                prediction="Parkinson Detected",
                confidence=96.4,
                risk_level="High Risk",
                prediction_date=datetime.utcnow(),
            )
        ]

    # =====================================================
    # Statistics
    # =====================================================

    def statistics(self) -> PatientStatistics:
        """
        Patient statistics.
        """

        return PatientStatistics(
            total_patients=250,
            male_patients=145,
            female_patients=100,
            other_patients=5,
            average_age=63.8,
        )
