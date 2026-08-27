# ==========================================================
# Standard Library
# ==========================================================

import os
import tempfile
import wave


# ==========================================================
# FastAPI
# ==========================================================

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)


# ==========================================================
# Application Schemas
# ==========================================================

from app.schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
)


# ==========================================================
# Application Services
# ==========================================================

from app.services.prediction_service import (
    PredictionService,
)

from app.services.report_service import (
    report_service,
)


# ==========================================================
# ML Audio Service
# ==========================================================

from app.ml.audio_feature_service import (
    audio_feature_service,
)


# ==========================================================
# Authentication
# ==========================================================

from app.dependencies import (
    get_current_user,
)


# ==========================================================
# Router
# ==========================================================

router = APIRouter(
    tags=["Prediction"]
)


# ==========================================================
# Prediction Service
# ==========================================================

prediction_service = (
    PredictionService()
)


# ==========================================================
# Audio Configuration
# ==========================================================

MIN_AUDIO_DURATION_SECONDS = 2.0

SUPPORTED_AUDIO_EXTENSION = ".wav"


# ==========================================================
# Predict Parkinson Disease From Features
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
    Predict Parkinson Disease from an existing
    22-feature voice vector.

    The PredictionService passes the 22 features into
    the production Predictor.

    The Predictor selects the final 12 production
    features and uses:

        final_model.pkl
        final_scaler.pkl
        final_feature_config.json
        threshold = 0.45

    After prediction, a report is generated.
    """

    try:

        # --------------------------------------------------
        # Run prediction
        # --------------------------------------------------

        result = (
            prediction_service.predict(
                request
            )
        )

        # --------------------------------------------------
        # Generate report
        # --------------------------------------------------

        report_service.generate_from_prediction(
            request=request,
            prediction=result,
        )

        # --------------------------------------------------
        # Return result
        # --------------------------------------------------

        return result

    except ValueError as exc:

        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=str(exc),
        )

    except HTTPException:

        raise

    except Exception as exc:

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                f"Prediction failed: {exc}"
            ),
        )


# ==========================================================
# WAV Duration Validation
# ==========================================================

def get_wav_duration(
    file_path: str,
) -> float:
    """
    Return WAV duration in seconds.

    Uses Python's standard-library wave module so that
    duration validation does not depend on librosa.

    Parameters
    ----------
    file_path:
        Temporary WAV file path.

    Returns
    -------
    float:
        Duration in seconds.

    Raises
    ------
    ValueError:
        If the file is not a valid WAV file or has
        invalid audio metadata.
    """

    try:

        with wave.open(
            file_path,
            "rb",
        ) as wav_file:

            frame_count = (
                wav_file.getnframes()
            )

            sample_rate = (
                wav_file.getframerate()
            )

            # ------------------------------------------------
            # Validate WAV metadata
            # ------------------------------------------------

            if frame_count <= 0:

                raise ValueError(
                    "Audio file contains no audio frames."
                )

            if sample_rate <= 0:

                raise ValueError(
                    "Audio file has an invalid sample rate."
                )

            duration = (
                frame_count
                / float(sample_rate)
            )

            return float(
                duration
            )

    except wave.Error as exc:

        raise ValueError(
            "Uploaded file is not a valid WAV audio file."
        ) from exc

    except EOFError as exc:

        raise ValueError(
            "Uploaded WAV file is incomplete or corrupted."
        ) from exc


# ==========================================================
# Validate Audio Duration
# ==========================================================

def validate_audio_duration(
    file_path: str,
) -> float:
    """
    Validate that a WAV recording is at least
    MIN_AUDIO_DURATION_SECONDS long.

    Returns the duration if valid.

    Raises
    ------
    ValueError
        When the recording is shorter than the
        required minimum.
    """

    duration = get_wav_duration(
        file_path
    )

    if duration < (
        MIN_AUDIO_DURATION_SECONDS
    ):

        raise ValueError(
            "Audio recording is too short. "
            f"Minimum duration is "
            f"{MIN_AUDIO_DURATION_SECONDS:.1f} seconds. "
            f"Received {duration:.2f} seconds."
        )

    return duration


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
    Upload a WAV audio file, validate its duration,
    extract the 22 voice features, and run the
    production prediction pipeline.

    Required minimum recording duration:

        2.0 seconds

    Feature flow:

        WAV
         ↓
        22 audio features
         ↓
        Predictor
         ↓
        12 selected features
         ↓
        HistGradientBoostingClassifier
         ↓
        threshold 0.45
    """

    temporary_path = None

    try:

        # ==================================================
        # 1. Validate filename
        # ==================================================

        if not file.filename:

            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "Audio file is required."
                ),
            )

        filename = (
            file.filename
            .strip()
            .lower()
        )

        # --------------------------------------------------
        # Only WAV
        # --------------------------------------------------

        if not filename.endswith(
            SUPPORTED_AUDIO_EXTENSION
        ):

            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "Only WAV audio files are supported."
                ),
            )

        # ==================================================
        # 2. Validate patient information
        # ==================================================

        patient_name = (
            patient_name
            .strip()
        )

        if not patient_name:

            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "Patient name is required."
                ),
            )

        if age <= 0:

            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "Age must be greater than zero."
                ),
            )

        gender = (
            str(gender)
            .strip()
        )

        if not gender:

            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "Gender is required."
                ),
            )

        # ==================================================
        # 3. Read uploaded audio
        # ==================================================

        audio_bytes = (
            await file.read()
        )

        if not audio_bytes:

            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "Uploaded audio file is empty."
                ),
            )

        # ==================================================
        # 4. Save temporary WAV
        # ==================================================

        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False,
        ) as temporary_file:

            temporary_file.write(
                audio_bytes
            )

            temporary_file.flush()

            temporary_path = (
                temporary_file.name
            )

        # ==================================================
        # 5. CHECK AUDIO DURATION
        # ==================================================

        duration = validate_audio_duration(
            temporary_path
        )

        # ==================================================
        # 6. Extract 22 features
        # ==================================================

        features_dict = (
            audio_feature_service
            .extract_features_from_file(
                temporary_path
            )
        )

        # ==================================================
        # 7. Convert features to vector
        # ==================================================

        feature_vector = (
            audio_feature_service
            .to_feature_vector(
                features_dict
            )
        )

        # ==================================================
        # 8. Validate feature count
        # ==================================================

        if len(
            feature_vector
        ) != 22:

            raise ValueError(
                "Audio feature extraction "
                "returned an unexpected number "
                f"of features: "
                f"{len(feature_vector)}. "
                "Expected 22."
            )

        # ==================================================
        # 9. Build PredictionRequest
        # ==================================================

        request = PredictionRequest(
            patient_name=patient_name,
            age=age,
            gender=gender,
            features=feature_vector,
        )

        # ==================================================
        # 10. Run production prediction
        # ==================================================

        result = (
            prediction_service.predict(
                request
            )
        )

        # ==================================================
        # 11. Generate report
        # ==================================================

        report_service.generate_from_prediction(
            request=request,
            prediction=result,
        )

        # ==================================================
        # 12. Return result
        # ==================================================

        return {
            "prediction": result,

            "features": features_dict,

            "feature_count": len(
                feature_vector
            ),

            "audio_duration_seconds": round(
                duration,
                3,
            ),
        }

    except HTTPException:

        raise

    except ValueError as exc:

        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=str(exc),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                f"Audio prediction failed: {exc}"
            ),
        )

    finally:

        # ==================================================
        # Always remove temporary WAV
        # ==================================================

        if (
            temporary_path
            and os.path.exists(
                temporary_path
            )
        ):

            try:

                os.remove(
                    temporary_path
                )

            except OSError:

                pass


# ==========================================================
# Model Information
# ==========================================================

@router.get(
    "/model-info",
    status_code=status.HTTP_200_OK,
)
def model_information(
    current_user=Depends(
        get_current_user
    ),
):
    """
    Return production model information.
    """

    try:

        return (
            prediction_service
            .model_info()
        )

    except Exception as exc:

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                f"Unable to retrieve model information: "
                f"{exc}"
            ),
        )


# ==========================================================
# Prediction Statistics
# ==========================================================

@router.get(
    "/statistics",
    status_code=status.HTTP_200_OK,
)
def prediction_statistics(
    current_user=Depends(
        get_current_user
    ),
):
    """
    Return prediction statistics.
    """

    try:

        return (
            prediction_service
            .statistics()
        )

    except Exception as exc:

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                f"Unable to retrieve prediction "
                f"statistics: {exc}"
            ),
        )


# ==========================================================
# Prediction History
# ==========================================================

@router.get(
    "/history",
    status_code=status.HTTP_200_OK,
)
def prediction_history(
    current_user=Depends(
        get_current_user
    ),
):
    """
    Return prediction history.

    The existing PredictionService history behavior
    is preserved.
    """

    try:

        return (
            prediction_service
            .get_history(
                current_user["id"]
            )
        )

    except Exception as exc:

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                f"Unable to retrieve prediction "
                f"history: {exc}"
            ),
        )


# ==========================================================
# Prediction By ID
# ==========================================================

@router.get(
    "/{prediction_id}",
    status_code=status.HTTP_200_OK,
)
def prediction_by_id(
    prediction_id: int,
    current_user=Depends(
        get_current_user
    ),
):
    """
    Retrieve a prediction by ID.
    """

    try:

        prediction = (
            prediction_service
            .get_prediction(
                prediction_id
            )
        )

        if prediction is None:

            raise HTTPException(
                status_code=(
                    status.HTTP_404_NOT_FOUND
                ),
                detail=(
                    "Prediction not found."
                ),
            )

        return prediction

    except HTTPException:

        raise

    except Exception as exc:

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                f"Unable to retrieve prediction: "
                f"{exc}"
            ),
        )


# ==========================================================
# Delete Prediction
# ==========================================================

@router.delete(
    "/{prediction_id}",
    status_code=status.HTTP_200_OK,
)
def delete_prediction(
    prediction_id: int,
    current_user=Depends(
        get_current_user
    ),
):
    """
    Delete a prediction record.
    """

    try:

        deleted = (
            prediction_service
            .delete_prediction(
                prediction_id
            )
        )

        if not deleted:

            raise HTTPException(
                status_code=(
                    status.HTTP_404_NOT_FOUND
                ),
                detail=(
                    "Prediction not found."
                ),
            )

        return {
            "message": (
                "Prediction deleted successfully."
            )
        }

    except HTTPException:

        raise

    except Exception as exc:

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                f"Unable to delete prediction: "
                f"{exc}"
            ),
        )
