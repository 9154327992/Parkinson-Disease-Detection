# ==========================================================
# STANDARD LIBRARY
# ==========================================================

import os
import tempfile


# ==========================================================
# THIRD-PARTY
# ==========================================================

import librosa
import numpy as np


# ==========================================================
# FASTAPI
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
# APPLICATION SCHEMAS
# ==========================================================

from app.schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
)


# ==========================================================
# APPLICATION SERVICES
# ==========================================================

from app.services.prediction_service import (
    PredictionService,
)

from app.services.report_service import (
    report_service,
)


# ==========================================================
# AUDIO FEATURE SERVICE
# ==========================================================

from app.ml.audio_feature_service import (
    audio_feature_service,
)


# ==========================================================
# AUTHENTICATION
# ==========================================================

from app.dependencies import (
    get_current_user,
)


# ==========================================================
# ROUTER
# ==========================================================

router = APIRouter(
    tags=["Prediction"]
)


# ==========================================================
# PREDICTION SERVICE
# ==========================================================

prediction_service = (
    PredictionService()
)


# ==========================================================
# AUDIO CONFIGURATION
# ==========================================================

MIN_AUDIO_DURATION_SECONDS = 2.0

SUPPORTED_AUDIO_EXTENSION = ".wav"

EXPECTED_FEATURE_COUNT = 22


# ==========================================================
# PRODUCTION FEATURE COUNT
# ==========================================================

PRODUCTION_FEATURE_COUNT = 12


# ==========================================================
# PRODUCTION THRESHOLD
# ==========================================================

PRODUCTION_THRESHOLD = 0.45


# ==========================================================
# PREDICT FROM FEATURE VECTOR
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

    The PredictionService passes the features to the
    production Predictor.

    Production model:

        HistGradientBoostingClassifier

    Production feature count:

        12

    Decision threshold:

        0.45
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
# AUDIO DURATION
# ==========================================================

def get_audio_duration(
    file_path: str,
) -> float:
    """
    Determine the duration of an uploaded audio file.

    librosa is intentionally used instead of Python's
    standard-library wave module.

    Reason
    ------
    The project's dataset contains WAV files using
    IEEE Float WAV format. Python's wave module can reject
    those files with:

        unknown extended format:
        00000003-0000-0010-8000-00aa00389b71

    librosa can read the same audio format used by the
    existing AudioFeatureService.

    Parameters
    ----------
    file_path:
        Path to temporary WAV file.

    Returns
    -------
    float
        Audio duration in seconds.
    """

    try:

        duration = librosa.get_duration(
            path=file_path
        )

        duration = float(
            duration
        )

    except Exception as exc:

        raise ValueError(
            "Unable to read the uploaded WAV audio file."
        ) from exc

    # ------------------------------------------------------
    # Validate duration value
    # ------------------------------------------------------

    if not np.isfinite(
        duration
    ):

        raise ValueError(
            "Audio file has an invalid duration."
        )

    if duration <= 0:

        raise ValueError(
            "Audio file contains no usable audio."
        )

    return duration


# ==========================================================
# VALIDATE AUDIO DURATION
# ==========================================================

def validate_audio_duration(
    file_path: str,
) -> float:
    """
    Require a minimum recording duration.

    Current production requirement:

        2.0 seconds
    """

    duration = get_audio_duration(
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
# VALIDATE FEATURE VECTOR
# ==========================================================

def validate_feature_vector(
    feature_vector,
) -> list:
    """
    Validate that AudioFeatureService returned
    exactly 22 model features.
    """

    # ------------------------------------------------------
    # Convert numpy array
    # ------------------------------------------------------

    if isinstance(
        feature_vector,
        np.ndarray,
    ):

        feature_vector = (
            feature_vector.tolist()
        )

    # ------------------------------------------------------
    # Validate sequence
    # ------------------------------------------------------

    if not isinstance(
        feature_vector,
        (list, tuple),
    ):

        raise ValueError(
            "Audio feature vector must be "
            "a list or tuple."
        )

    # ------------------------------------------------------
    # Validate feature count
    # ------------------------------------------------------

    if len(
        feature_vector
    ) != EXPECTED_FEATURE_COUNT:

        raise ValueError(
            "Audio feature extraction returned "
            f"{len(feature_vector)} features. "
            f"Expected {EXPECTED_FEATURE_COUNT}."
        )

    validated = []

    # ------------------------------------------------------
    # Validate values
    # ------------------------------------------------------

    for index, value in enumerate(
        feature_vector
    ):

        try:

            numeric_value = float(
                value
            )

        except (
            TypeError,
            ValueError,
        ) as exc:

            raise ValueError(
                f"Audio feature {index + 1} "
                "is not a valid number."
            ) from exc

        if not np.isfinite(
            numeric_value
        ):

            raise ValueError(
                f"Audio feature {index + 1} "
                "is not finite."
            )

        validated.append(
            numeric_value
        )

    return validated


# ==========================================================
# PREDICT FROM AUDIO
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
    Upload a WAV audio recording and run the
    production Parkinson Disease prediction pipeline.

    Input requirements
    ------------------

    File:
        WAV

    Minimum duration:
        2.0 seconds

    Feature extraction:
        22 features

    Production model:
        HistGradientBoostingClassifier

    Production features:
        12

    Decision threshold:
        0.45
    """

    temporary_path = None

    try:

        # ==================================================
        # 1. Validate uploaded filename
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
        # WAV only
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
            patient_name.strip()
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

        # --------------------------------------------------
        # Age
        # --------------------------------------------------

        if age <= 0:

            raise HTTPException(
                status_code=(
                    status.HTTP_400_BAD_REQUEST
                ),
                detail=(
                    "Age must be greater than zero."
                ),
            )

        # --------------------------------------------------
        # Gender
        # --------------------------------------------------

        gender = (
            str(gender).strip()
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
        # 5. Validate WAV duration
        # ==================================================

        duration = (
            validate_audio_duration(
                temporary_path
            )
        )

        # ==================================================
        # 6. Extract 22 audio features
        # ==================================================

        features_dict = (
            audio_feature_service
            .extract_features_from_file(
                temporary_path
            )
        )

        # ==================================================
        # 7. Convert dictionary to vector
        # ==================================================

        feature_vector = (
            audio_feature_service
            .to_feature_vector(
                features_dict
            )
        )

        # ==================================================
        # 8. Validate extracted features
        # ==================================================

        feature_vector = (
            validate_feature_vector(
                feature_vector
            )
        )

        # ==================================================
        # 9. Build prediction request
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
        # 12. Return response
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

            "production_feature_count":
                PRODUCTION_FEATURE_COUNT,

            "decision_threshold":
                PRODUCTION_THRESHOLD,
        }

    # ======================================================
    # HTTP exceptions
    # ======================================================

    except HTTPException:

        raise

    # ======================================================
    # Validation errors
    # ======================================================

    except ValueError as exc:

        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=str(exc),
        )

    # ======================================================
    # Unexpected errors
    # ======================================================

    except Exception as exc:

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                f"Audio prediction failed: {exc}"
            ),
        )

    # ======================================================
    # Always remove temporary file
    # ======================================================

    finally:

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
# MODEL INFORMATION
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
# PREDICTION STATISTICS
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
# PREDICTION HISTORY
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
    Return prediction history for the current user.
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
# PREDICTION BY ID
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
# DELETE PREDICTION
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
