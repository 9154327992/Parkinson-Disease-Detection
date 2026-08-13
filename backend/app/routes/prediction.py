from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)

from app.schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
)

from app.services.prediction_service import PredictionService
from app.services.report_service import report_service

from app.ml.audio_feature_service import (
    audio_feature_service,
)

from app.dependencies import get_current_user


# ==========================================================
# Router
# ==========================================================

router = APIRouter(
    tags=["Prediction"]
)


# ==========================================================
# Services
# ==========================================================

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
    request: PredictionRequest,
):
    """
    Predict Parkinson Disease.

    After a successful prediction, a report is automatically
    generated using the same patient and prediction data.
    """

    try:

        # --------------------------------------------------
        # Run prediction
        # --------------------------------------------------

        result = prediction_service.predict(
            request
        )

        # --------------------------------------------------
        # Automatically create report
        # --------------------------------------------------

        report_service.generate_from_prediction(
            request=request,
            prediction=result,
        )

        # --------------------------------------------------
        # Return prediction result
        # --------------------------------------------------

        return result

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}",
        )

# ==========================================================
# Predict From Audio File
# ==========================================================

@router.post(
    "/predict-audio",
    status_code=status.HTTP_200_OK,
)
async def predict_audio(
    patient_name: str,
    age: int,
    gender: str,
    file: UploadFile = File(...),
):
    """
    Upload a WAV audio file, extract the 22 voice features,
    and run the existing prediction pipeline.
    """

    try:

        # --------------------------------------------------
        # Validate file
        # --------------------------------------------------

        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Audio file is required.",
            )

        filename = file.filename.lower()

        if not filename.endswith(".wav"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only WAV audio files are supported.",
            )

        # --------------------------------------------------
        # Read uploaded audio
        # --------------------------------------------------

        audio_bytes = await file.read()

        if not audio_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded audio file is empty.",
            )

        # --------------------------------------------------
        # Save temporary audio file
        # --------------------------------------------------

        import tempfile

        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False,
        ) as temporary_file:

            temporary_file.write(
                audio_bytes
            )

            temporary_path = (
                temporary_file.name
            )

        # --------------------------------------------------
        # Extract 22 model features
        # --------------------------------------------------

        features_dict = (
            audio_feature_service.extract_features_from_file(
                temporary_path
            )
        )

        # --------------------------------------------------
        # Convert to model vector
        # --------------------------------------------------

        feature_vector = (
            audio_feature_service.to_feature_vector(
                features_dict
            )
        )

        # --------------------------------------------------
        # Build existing prediction request
        # --------------------------------------------------

        request = PredictionRequest(
            patient_name=patient_name,
            age=age,
            gender=gender,
            features=feature_vector,
        )

        # --------------------------------------------------
        # Run existing prediction pipeline
        # --------------------------------------------------

        result = prediction_service.predict(
            request
        )

        # --------------------------------------------------
        # Generate report
        # --------------------------------------------------

        report_service.generate_from_prediction(
            request=request,
            prediction=result,
        )

        return {
            "prediction": result,
            "features": features_dict,
            "feature_count": len(
                feature_vector
            ),
        }

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audio prediction failed: {str(e)}",
        )

# ==========================================================
# Model Information
# ==========================================================

@router.get(
    "/model-info",
    status_code=status.HTTP_200_OK,
)
def model_information(
    current_user=Depends(get_current_user),
):
    """
    Return ML model information.
    """

    return prediction_service.model_info()


# ==========================================================
# Prediction Statistics
# ==========================================================

@router.get(
    "/statistics",
    status_code=status.HTTP_200_OK,
)
def prediction_statistics(
    current_user=Depends(get_current_user),
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
    current_user=Depends(get_current_user),
):
    """
    Return prediction history for the current user.
    """

    return prediction_service.get_history(
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
    current_user=Depends(get_current_user),
):
    """
    Retrieve a prediction by ID.
    """

    prediction = prediction_service.get_prediction(
        prediction_id
    )

    if prediction is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found.",
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
    current_user=Depends(get_current_user),
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
            detail="Prediction not found.",
        )

    return {
        "message": "Prediction deleted successfully."
    }
