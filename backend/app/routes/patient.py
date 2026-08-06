from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies import get_current_user

from app.schemas.patient import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientSummary
)

from app.services.patient_service import PatientService


router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)

patient_service = PatientService()


# ==========================================================
# Create Patient
# ==========================================================

@router.post(
    "/",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED
)
def create_patient(
    patient: PatientCreate,
    current_user=Depends(get_current_user)
):
    """
    Create a new patient.
    """

    return patient_service.create_patient(
        patient,
        current_user["id"]
    )


# ==========================================================
# Get All Patients
# ==========================================================

@router.get(
    "/",
    response_model=list[PatientSummary]
)
def get_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = None,
    current_user=Depends(get_current_user)
):
    """
    Return all patients.
    """

    return patient_service.get_patients(
        skip=skip,
        limit=limit,
        search=search
    )


# ==========================================================
# Get Patient By ID
# ==========================================================

@router.get(
    "/{patient_id}",
    response_model=PatientResponse
)
def get_patient(
    patient_id: int,
    current_user=Depends(get_current_user)
):
    """
    Return patient details.
    """

    patient = patient_service.get_patient(patient_id)

    if patient is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found."
        )

    return patient


# ==========================================================
# Update Patient
# ==========================================================

@router.put(
    "/{patient_id}",
    response_model=PatientResponse
)
def update_patient(
    patient_id: int,
    patient: PatientUpdate,
    current_user=Depends(get_current_user)
):
    """
    Update patient information.
    """

    updated = patient_service.update_patient(
        patient_id,
        patient
    )

    if updated is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found."
        )

    return updated


# ==========================================================
# Delete Patient
# ==========================================================

@router.delete(
    "/{patient_id}"
)
def delete_patient(
    patient_id: int,
    current_user=Depends(get_current_user)
):
    """
    Delete a patient.
    """

    deleted = patient_service.delete_patient(
        patient_id
    )

    if not deleted:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found."
        )

    return {
        "message": "Patient deleted successfully."
    }


# ==========================================================
# Patient Prediction History
# ==========================================================

@router.get(
    "/{patient_id}/predictions"
)
def patient_predictions(
    patient_id: int,
    current_user=Depends(get_current_user)
):
    """
    Return all predictions for a patient.
    """

    return patient_service.get_prediction_history(
        patient_id
    )


# ==========================================================
# Patient Reports
# ==========================================================

@router.get(
    "/{patient_id}/reports"
)
def patient_reports(
    patient_id: int,
    current_user=Depends(get_current_user)
):
    """
    Return reports generated for a patient.
    """

    return patient_service.get_reports(
        patient_id
    )
