"""
Medication API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_current_user

from app.schemas.medication import (
    MedicationRequest,
    MedicationResponse,
    MedicationSchedule,
)

from app.services.medication_service import MedicationService


router = APIRouter(
    prefix="/medications",
    tags=["Medications"]
)

medication_service = MedicationService()


# ==========================================================
# Generate Medication Guidance
# ==========================================================

@router.post(
    "/",
    response_model=MedicationResponse,
    status_code=status.HTTP_200_OK
)
def medication_guidance(
    request: MedicationRequest,
    current_user=Depends(get_current_user)
):
    """
    Generate medication guidance based on
    patient information.

    Note:
    This endpoint provides educational information
    and reminders only. It does not prescribe
    medications.
    """

    try:

        return medication_service.generate(
            request=request,
            user=current_user
        )

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==========================================================
# Patient Medication Schedule
# ==========================================================

@router.get(
    "/patient/{patient_id}",
    response_model=MedicationSchedule
)
def patient_schedule(
    patient_id: int,
    current_user=Depends(get_current_user)
):
    """
    Return medication schedule
    for a patient.
    """

    return medication_service.schedule(
        patient_id
    )


# ==========================================================
# Daily Reminders
# ==========================================================

@router.get("/reminders/{patient_id}")
def reminders(
    patient_id: int,
    current_user=Depends(get_current_user)
):
    """
    Daily medication reminders.
    """

    return medication_service.reminders(
        patient_id
    )


# ==========================================================
# Drug Interactions
# ==========================================================

@router.post("/interactions")
def interactions(
    medications: list[str],
    current_user=Depends(get_current_user)
):
    """
    Check possible medication interactions.
    """

    return medication_service.interactions(
        medications
    )


# ==========================================================
# Medication Information
# ==========================================================

@router.get("/{medication_name}")
def medication_information(
    medication_name: str,
    current_user=Depends(get_current_user)
):
    """
    Return educational information about
    a medication.
    """

    information = medication_service.information(
        medication_name
    )

    if information is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found."
        )

    return information


# ==========================================================
# Common Parkinson Medications
# ==========================================================

@router.get("/")
def medication_list(
    current_user=Depends(get_current_user)
):
    """
    Return common medications used in
    Parkinson disease management.

    Educational reference only.
    """

    return medication_service.list_all()
