from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
)

from app.services.prediction_service import PredictionService

from app.dependencies import get_current_user

router = APIRouter(
    tags=["Prediction"]
)

prediction_service = PredictionService()


# ==========================================================
# Predict Parkinson Disease
# ==========================================================

@router.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
)
def predict(
    request: PredictionRequest
):
    """
    Predict Parkinson Disease using the trained ML model.
    """

    try:

        result = prediction_service.predict(
            request=request
        )

        return result

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


# ==========================================================
# Model Information
# ==========================================================

@router.get(
    "/model-info",
    status_code=status.HTTP_200_OK,
)
def model_information(
    current_user=Depends(get_current_user)
):
    """
    Return ML model information.
    """

    return prediction_service.model_information()


# ==========================================================
# Prediction Statistics
# ==========================================================

@router.get(
    "/statistics",
    status_code=status.HTTP_200_OK,
)
def prediction_statistics(
    current_user=Depends(get_current_user)
):
    """
    Return prediction statistics.
    """

    return prediction_service.statistics()


# ==========================================================
# Prediction History
# ==========================================================

@router.get(
    "/history",
    status_code=status.HTTP_200_OK,
)
def prediction_history(
    current_user=Depends(get_current_user)
):
    """
    Return prediction history for the current user.
    """

    return prediction_service.history(
        current_user["id"]
    )


# ==========================================================
# Prediction by ID
# ==========================================================

@router.get(
    "/{prediction_id}",
    status_code=status.HTTP_200_OK,
)
def prediction_by_id(
    prediction_id: int,
    current_user=Depends(get_current_user)
):
    """
    Retrieve a prediction by its ID.
    """

    prediction = prediction_service.get_prediction(
        prediction_id
    )

    if prediction is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found."
        )

    return prediction


# ==========================================================
# Delete Prediction
# ==========================================================

@router.delete(
    "/{prediction_id}",
    status_code=status.HTTP_200_OK,
)
def delete_prediction(
    prediction_id: int,
    current_user=Depends(get_current_user)
):
    """
    Delete a prediction record.
    """

    deleted = prediction_service.delete_prediction(
        prediction_id
    )

    if not deleted:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found."
        )

    return {
        "message": "Prediction deleted successfully."
    }
