"""
Recommendation API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_current_user

from app.schemas.recommendation import (
    RecommendationRequest,
    RecommendationResponse,
)

from app.services.recommendation_service import RecommendationService


router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"]
)

recommendation_service = RecommendationService()


# ==========================================================
# Generate Recommendation
# ==========================================================

@router.post(
    "/",
    response_model=RecommendationResponse,
    status_code=status.HTTP_200_OK
)
def generate_recommendation(
    request: RecommendationRequest,
    current_user=Depends(get_current_user)
):
    """
    Generate personalized recommendations
    based on prediction and patient profile.
    """

    try:

        return recommendation_service.generate(
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
            detail=f"Recommendation generation failed: {str(e)}"
        )


# ==========================================================
# Recommendation by Risk Level
# ==========================================================

@router.get("/risk/{risk_level}")
def recommendation_by_risk(
    risk_level: str,
    current_user=Depends(get_current_user)
):
    """
    Standard recommendation for a risk level.
    """

    return recommendation_service.by_risk(
        risk_level
    )


# ==========================================================
# Recommendation by Prediction
# ==========================================================

@router.get("/prediction/{prediction_id}")
def recommendation_by_prediction(
    prediction_id: int,
    current_user=Depends(get_current_user)
):
    """
    Recommendation for an existing prediction.
    """

    recommendation = recommendation_service.by_prediction(
        prediction_id
    )

    if recommendation is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found."
        )

    return recommendation


# ==========================================================
# Patient Recommendations
# ==========================================================

@router.get("/patient/{patient_id}")
def patient_recommendations(
    patient_id: int,
    current_user=Depends(get_current_user)
):
    """
    Return recommendation history
    for a patient.
    """

    return recommendation_service.patient_history(
        patient_id
    )


# ==========================================================
# Lifestyle Recommendations
# ==========================================================

@router.get("/lifestyle")
def lifestyle_recommendations(
    current_user=Depends(get_current_user)
):
    """
    General lifestyle recommendations.
    """

    return recommendation_service.lifestyle()


# ==========================================================
# Diet Recommendations
# ==========================================================

@router.get("/diet")
def diet_recommendations(
    current_user=Depends(get_current_user)
):
    """
    General diet recommendations
    for Parkinson patients.
    """

    return recommendation_service.diet()


# ==========================================================
# Follow-up Schedule
# ==========================================================

@router.get("/follow-up/{patient_id}")
def follow_up_schedule(
    patient_id: int,
    current_user=Depends(get_current_user)
):
    """
    Suggested follow-up schedule.
    """

    return recommendation_service.follow_up(
        patient_id
    )
