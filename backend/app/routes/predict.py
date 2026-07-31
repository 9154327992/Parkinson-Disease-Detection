"""
Prediction API Routes
"""

from fastapi import APIRouter, HTTPException

from app.schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
)

from app.services.prediction_service import PredictionService


router = APIRouter()

prediction_service = PredictionService()


# ==========================================================
# Predict Parkinson Disease
# ==========================================================

@router.post(
    "/",
    response_model=PredictionResponse
)
def predict(request: PredictionRequest):
    """
    Predict Parkinson disease from
    patient's voice measurements.
    """

    try:

        result = prediction_service.predict(request)

        return result

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==========================================================
# Model Information
# ==========================================================

@router.get("/model")
def model_information():
    """
    Return model information.
    """

    return prediction_service.model_information()


# ==========================================================
# Prediction Statistics
# ==========================================================

@router.get("/stats")
def prediction_statistics():
    """
    Prediction statistics.
    """

    return prediction_service.statistics()
