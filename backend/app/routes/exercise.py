"""
Exercise API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_current_user

from app.schemas.exercise import (
    ExerciseRequest,
    ExercisePlan,
)

from app.services.exercise_service import ExerciseService


router = APIRouter(
    prefix="/exercises",
    tags=["Exercises"]
)

exercise_service = ExerciseService()


# ==========================================================
# Generate Exercise Plan
# ==========================================================

@router.post(
    "/",
    response_model=ExercisePlan,
    status_code=status.HTTP_200_OK
)
def generate_exercise_plan(
    request: ExerciseRequest,
    current_user=Depends(get_current_user)
):
    """
    Generate a personalized exercise plan.
    """

    try:

        return exercise_service.generate_plan(
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
            detail=f"Unable to generate exercise plan: {str(e)}"
        )


# ==========================================================
# Exercise by Risk Level
# ==========================================================

@router.get("/risk/{risk_level}")
def exercise_by_risk(
    risk_level: str,
    current_user=Depends(get_current_user)
):
    """
    Return exercises according to risk level.
    """

    return exercise_service.by_risk(
        risk_level
    )


# ==========================================================
# Exercise by Patient
# ==========================================================

@router.get("/patient/{patient_id}")
def patient_exercises(
    patient_id: int,
    current_user=Depends(get_current_user)
):
    """
    Return patient's exercise history.
    """

    return exercise_service.patient_plan(
        patient_id
    )


# ==========================================================
# Balance Exercises
# ==========================================================

@router.get("/balance")
def balance_exercises(
    current_user=Depends(get_current_user)
):
    """
    Balance improvement exercises.
    """

    return exercise_service.balance()


# ==========================================================
# Walking Exercises
# ==========================================================

@router.get("/walking")
def walking_exercises(
    current_user=Depends(get_current_user)
):
    """
    Walking and gait exercises.
    """

    return exercise_service.walking()


# ==========================================================
# Flexibility Exercises
# ==========================================================

@router.get("/flexibility")
def flexibility_exercises(
    current_user=Depends(get_current_user)
):
    """
    Stretching and flexibility exercises.
    """

    return exercise_service.flexibility()


# ==========================================================
# Strength Exercises
# ==========================================================

@router.get("/strength")
def strength_exercises(
    current_user=Depends(get_current_user)
):
    """
    Strength-building exercises.
    """

    return exercise_service.strength()


# ==========================================================
# Speech Therapy Exercises
# ==========================================================

@router.get("/speech")
def speech_exercises(
    current_user=Depends(get_current_user)
):
    """
    Speech therapy exercises.
    """

    return exercise_service.speech()


# ==========================================================
# Daily Exercise Schedule
# ==========================================================

@router.get("/schedule/{patient_id}")
def exercise_schedule(
    patient_id: int,
    current_user=Depends(get_current_user)
):
    """
    Daily exercise schedule.
    """

    return exercise_service.schedule(
        patient_id
    )
