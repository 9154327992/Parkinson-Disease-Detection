from datetime import datetime
from typing import Dict, List, Optional

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
    Patient management service.

    Stores patients in memory for the current application session.
    """

    _patients: Dict[int, PatientResponse] = {}
    _next_patient_id: int = 1

    def __init__(self):
        pass

    # =====================================================
    # Create Patient
    # =====================================================

    def create_patient(
        self,
        patient: PatientCreate,
        created_by: int,
    ) -> PatientResponse:

        patient_id = (
            PatientService._next_patient_id
        )

        PatientService._next_patient_id += 1

        now = datetime.utcnow()

        new_patient = PatientResponse(
            id=patient_id,

            full_name=(
                f"{patient.first_name} "
                f"{patient.last_name}"
            ).strip(),

            first_name=patient.first_name,
            last_name=patient.last_name,

            age=patient.age,
            gender=patient.gender,

            phone=patient.phone,
            email=patient.email,
            address=patient.address,

            emergency_contact=(
                patient.emergency_contact
            ),

            medical_history=(
                patient.medical_history
            ),

            created_by=created_by,

            created_at=now,
            updated_at=None,
        )

        PatientService._patients[
            patient_id
        ] = new_patient

        return new_patient

    # =====================================================
    # Get Patient
    # =====================================================

    def get_patient(
        self,
        patient_id: int,
    ) -> Optional[PatientResponse]:

        return PatientService._patients.get(
            patient_id
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

        patients = list(
            PatientService._patients.values()
        )

        if search:

            keyword = search.lower()

            patients = [
                patient
                for patient in patients
                if keyword
                in patient.full_name.lower()
            ]

        patients = patients[
            skip:skip + limit
        ]

        return [
            PatientSummary(
                id=patient.id,

                full_name=patient.full_name,

                age=patient.age,

                gender=patient.gender,
            )
            for patient in patients
        ]

    # =====================================================
    # Update Patient
    # =====================================================

    def update_patient(
        self,
        patient_id: int,
        patient: PatientUpdate,
    ) -> Optional[PatientResponse]:

        existing = PatientService._patients.get(
            patient_id
        )

        if existing is None:
            return None

        first_name = (
            patient.first_name
            or existing.first_name
        )

        last_name = (
            patient.last_name
            or existing.last_name
        )

        updated = existing.model_copy(
            update={
                "first_name": first_name,
                "last_name": last_name,

                "full_name": (
                    f"{first_name} "
                    f"{last_name}"
                ).strip(),

                "age": (
                    patient.age
                    if patient.age is not None
                    else existing.age
                ),

                "gender": (
                    patient.gender
                    if patient.gender is not None
                    else existing.gender
                ),

                "phone": patient.phone,
                "email": patient.email,
                "address": patient.address,

                "emergency_contact":
                    patient.emergency_contact,

                "medical_history":
                    patient.medical_history,

                "updated_at":
                    datetime.utcnow(),
            }
        )

        PatientService._patients[
            patient_id
        ] = updated

        return updated

    # =====================================================
    # Delete Patient
    # =====================================================

    def delete_patient(
        self,
        patient_id: int,
    ) -> dict:

        if patient_id not in PatientService._patients:

            return {
                "message": "Patient not found."
            }

        del PatientService._patients[
            patient_id
        ]

        return {
            "message":
                f"Patient {patient_id} deleted successfully."
        }

    # =====================================================
    # Search Patients
    # =====================================================

    def search_patients(
        self,
        keyword: str,
    ) -> List[PatientSummary]:

        return self.get_patients(
            search=keyword
        )

    # =====================================================
    # Patient History
    # =====================================================

    def patient_history(
        self,
        patient_id: int,
    ) -> List[PatientHistory]:

        return []

    # =====================================================
    # Statistics
    # =====================================================

    def statistics(
        self,
    ) -> PatientStatistics:

        patients = list(
            PatientService._patients.values()
        )

        total_patients = len(
            patients
        )

        male_patients = sum(
            1
            for patient in patients
            if str(
                patient.gender
            ).lower()
            == "male"
        )

        female_patients = sum(
            1
            for patient in patients
            if str(
                patient.gender
            ).lower()
            == "female"
        )

        other_patients = (
            total_patients
            - male_patients
            - female_patients
        )

        ages = [
            patient.age
            for patient in patients
            if patient.age is not None
        ]

        average_age = (
            sum(ages) / len(ages)
            if ages
            else 0.0
        )

        return PatientStatistics(
            total_patients=total_patients,

            male_patients=male_patients,

            female_patients=female_patients,

            other_patients=other_patients,

            average_age=round(
                average_age,
                2,
            ),
        )
