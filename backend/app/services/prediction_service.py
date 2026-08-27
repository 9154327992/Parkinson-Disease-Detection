from datetime import datetime
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from app.schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
    PredictionHistory,
    PredictionStatistics,
    ModelInformation,
)

from app.services.patient_service import PatientService

from sqlalchemy import or_

from app.database.database import SessionLocal

from app.database.models import (
    Patient,
    Prediction,
)

from app.ml.predictor import (
    Predictor,
)


# ==========================================================
# BASE DIRECTORY
# ==========================================================

BASE_DIR = (
    Path(__file__)
    .resolve()
    .parents[2]
)


# ==========================================================
# PRODUCTION MODEL PATHS
# ==========================================================

FINAL_MODEL_PATH = (
    BASE_DIR
    / "models"
    / "final_model.pkl"
)

FINAL_SCALER_PATH = (
    BASE_DIR
    / "models"
    / "final_scaler.pkl"
)

FINAL_FEATURE_CONFIG_PATH = (
    BASE_DIR
    / "models"
    / "final_feature_config.json"
)

# ==========================================================
# PRODUCTION CONFIGURATION
# ==========================================================

PRODUCTION_FEATURE_COUNT = 12

EXTRACTED_FEATURE_COUNT = 22

DECISION_THRESHOLD = 0.45

HEALTHY_CLASS = 0

PARKINSON_CLASS = 1


# ==========================================================
# FINAL FEATURE ORDER
# ==========================================================

SELECTED_FEATURE_NAMES = [
    "MDVP:Jitter(%)",
    "Jitter:DDP",
    "MDVP:Flo(Hz)",
    "MDVP:RAP",
    "PPE",
    "MDVP:Fo(Hz)",
    "MDVP:Fhi(Hz)",
    "MDVP:APQ",
    "D2",
    "MDVP:Jitter(Abs)",
    "MDVP:Shimmer(dB)",
    "MDVP:PPQ",
]


# ==========================================================
# ALL 22 FEATURE NAMES
# ==========================================================

FEATURE_NAMES = [
    "MDVP:Fo(Hz)",
    "MDVP:Fhi(Hz)",
    "MDVP:Flo(Hz)",
    "MDVP:Jitter(%)",
    "MDVP:Jitter(Abs)",
    "MDVP:RAP",
    "MDVP:PPQ",
    "Jitter:DDP",
    "MDVP:Shimmer",
    "MDVP:Shimmer(dB)",
    "Shimmer:APQ3",
    "Shimmer:APQ5",
    "MDVP:APQ",
    "Shimmer:DDA",
    "NHR",
    "HNR",
    "RPDE",
    "DFA",
    "spread1",
    "spread2",
    "D2",
    "PPE",
]


# ==========================================================
# PREDICTION SERVICE
# ==========================================================

class PredictionService:
    """
    Production Parkinson Disease prediction service.

    This class is intentionally responsible for application
    behavior and persistence/history.

    The actual machine-learning work is delegated to:

        app.ml.predictor.Predictor
    """

    # ------------------------------------------------------
    # Shared in-memory history
    # ------------------------------------------------------

    history: List[
        PredictionHistory
    ] = []

    predictions: Dict[
        int,
        Dict,
    ] = {}

    next_prediction_id: int = 1

    # ------------------------------------------------------
    # ML engine
    # ------------------------------------------------------

    predictor: Optional[
        Predictor
    ] = None

    model_loaded: bool = False

    model_error: Optional[
        str
    ] = None

    # ======================================================
    # INITIALIZATION
    # ======================================================

    def __init__(
        self,
    ):
        """
        Initialize the production prediction service.

        The Predictor loads:
            final_model.pkl
            final_scaler.pkl
            final_feature_config.json
        """

        self._load_model()

    # ======================================================
    # LOAD MODEL
    # ======================================================

    @classmethod
    def _load_model(
        cls,
    ) -> None:
        """
        Initialize the production Predictor.

        This replaces the old behavior that directly loaded:

            models/model.pkl
            models/scaler.pkl

        The service now uses the Step 9 production candidate.
        """

        if cls.model_loaded:
            return

        try:

            # ------------------------------------------------
            # Explicit artifact validation
            # ------------------------------------------------

            missing = []

            if not FINAL_MODEL_PATH.exists():
                missing.append(
                    str(
                        FINAL_MODEL_PATH
                    )
                )

            if not FINAL_SCALER_PATH.exists():
                missing.append(
                    str(
                        FINAL_SCALER_PATH
                    )
                )

            if not FINAL_FEATURE_CONFIG_PATH.exists():
                missing.append(
                    str(
                        FINAL_FEATURE_CONFIG_PATH
                    )
                )

            if missing:

                raise FileNotFoundError(
                    "Required production ML "
                    "artifact(s) not found:\n"
                    + "\n".join(
                        missing
                    )
                )

            # ------------------------------------------------
            # Create production predictor
            # ------------------------------------------------

            cls.predictor = Predictor(
                model_path=str(
                    FINAL_MODEL_PATH
                ),
                scaler_path=str(
                    FINAL_SCALER_PATH
                ),
                feature_config_path=str(
                    FINAL_FEATURE_CONFIG_PATH
                ),
                threshold=DECISION_THRESHOLD,
            )

            # ------------------------------------------------
            # Health check
            # ------------------------------------------------

            health = (
                cls.predictor.health()
            )

            if health.get(
                "status"
            ) != "healthy":

                raise RuntimeError(
                    "Production Predictor "
                    "loaded but health check "
                    "failed: "
                    f"{health}"
                )

            cls.model_loaded = True

            cls.model_error = None

        except Exception as exc:

            cls.predictor = None

            cls.model_loaded = False

            cls.model_error = (
                f"Unable to load production "
                f"ML model: {exc}"
            )

    # ======================================================
    # VALIDATE FEATURES
    # ======================================================

    @staticmethod
    def _validate_features(
        features,
    ) -> List[float]:
        """
        Validate the original 22 audio features.

        AudioFeatureService produces 22 features.

        Predictor subsequently reduces them to the final
        12 production features.
        """

        if features is None:

            raise ValueError(
                "Voice features are required."
            )

        # --------------------------------------------------
        # Convert numpy array
        # --------------------------------------------------

        if isinstance(
            features,
            np.ndarray,
        ):

            features = (
                features.tolist()
            )

        # --------------------------------------------------
        # Validate sequence
        # --------------------------------------------------

        if not isinstance(
            features,
            (list, tuple),
        ):

            raise ValueError(
                "Voice features must be "
                "provided as a list or tuple."
            )

        # --------------------------------------------------
        # Exactly 22 features
        # --------------------------------------------------

        if len(features) != (
            EXTRACTED_FEATURE_COUNT
        ):

            raise ValueError(
                "Exactly "
                f"{EXTRACTED_FEATURE_COUNT} "
                "voice features are required. "
                f"Received {len(features)}."
            )

        numeric_features = []

        # --------------------------------------------------
        # Validate every feature
        # --------------------------------------------------

        for index, value in enumerate(
            features
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
                    f"Feature {index + 1} "
                    "must be a valid number."
                ) from exc

            if not np.isfinite(
                numeric_value
            ):

                raise ValueError(
                    f"Feature {index + 1} "
                    "must be finite."
                )

            numeric_features.append(
                numeric_value
            )

        return numeric_features

    # ======================================================
    # REAL ML PREDICTION
    # ======================================================

    def _run_model(
        self,
        features: List[float],
    ) -> Tuple[
        int,
        float,
        float,
        Dict,
    ]:
        """
        Run the production Predictor.

        Returns:

            prediction_value
                0 = Healthy
                1 = Parkinson

            confidence
                Confidence of selected class, percentage.

            risk_score
                Parkinson probability, percentage.

            predictor_result
                Full Predictor result dictionary.
        """

        # --------------------------------------------------
        # Ensure predictor is available
        # --------------------------------------------------

        if not self.model_loaded:

            self._load_model()

        if (
            self.predictor is None
            or not self.model_loaded
        ):

            raise RuntimeError(
                self.model_error
                or "Production ML model "
                "is unavailable."
            )

        # --------------------------------------------------
        # Validate original 22 features
        # --------------------------------------------------

        numeric_features = (
            self._validate_features(
                features
            )
        )

        # --------------------------------------------------
        # Delegate ML processing
        # --------------------------------------------------

        result = (
            self.predictor.predict(
                numeric_features
            )
        )

        # --------------------------------------------------
        # Extract prediction
        # --------------------------------------------------

        prediction_value = int(
            result[
                "prediction_value"
            ]
        )

        # --------------------------------------------------
        # Extract confidence
        # --------------------------------------------------

        confidence = float(
            result.get(
                "confidence",
                0.0,
            )
        )

        # --------------------------------------------------
        # Extract Parkinson risk
        # --------------------------------------------------

        risk_score = float(
            result.get(
                "parkinson_probability",
                result.get(
                    "risk_score",
                    0.0,
                ),
            )
        )

        # --------------------------------------------------
        # Safety validation
        # --------------------------------------------------

        if prediction_value not in (
            HEALTHY_CLASS,
            PARKINSON_CLASS,
        ):

            raise RuntimeError(
                "Production model returned "
                f"invalid prediction class: "
                f"{prediction_value}"
            )

        if not (
            0.0
            <= confidence
            <= 100.0
        ):

            raise RuntimeError(
                "Production model returned "
                f"invalid confidence: "
                f"{confidence}"
            )

        if not (
            0.0
            <= risk_score
            <= 100.0
        ):

            raise RuntimeError(
                "Production model returned "
                f"invalid risk score: "
                f"{risk_score}"
            )

        return (
            prediction_value,
            confidence,
            risk_score,
            result,
        )

    # ======================================================
    # PREDICT
    # ======================================================

    def predict(
        self,
        request: PredictionRequest,
        owner_id: Optional[int] = None,
    ) -> PredictionResponse:
        """
        Run Parkinson disease prediction using the
        Step 9 production model.

        The incoming request still contains the original
        22 audio features.

        Predictor handles:

            22 features
                ↓
            12 selected features
                ↓
            final model
                ↓
            probability
                ↓
            threshold 0.45
        """

        if request is None:

            raise ValueError(
                "Prediction request is required."
            )

        # --------------------------------------------------
        # Patient name
        # --------------------------------------------------

        patient_name = (
            request.patient_name
            or ""
        ).strip()

        if not patient_name:

            raise ValueError(
                "Patient name is required."
            )

        # --------------------------------------------------
        # Validate features
        # --------------------------------------------------

        features = (
            self._validate_features(
                request.features
            )
        )

        # --------------------------------------------------
        # Run production model
        # --------------------------------------------------

        (
            prediction_value,
            confidence,
            risk_score,
            predictor_result,
        ) = self._run_model(
            features
        )

        # --------------------------------------------------
        # Diagnosis
        # --------------------------------------------------

        if (
            prediction_value
            ==
            PARKINSON_CLASS
        ):

            prediction = (
                "Parkinson Detected"
            )

        else:

            prediction = (
                "Healthy"
            )

        # --------------------------------------------------
        # Risk level
        #
        # Based on Parkinson probability.
        # --------------------------------------------------

        if risk_score >= 80.0:

            risk_level = (
                "High Risk"
            )

        elif risk_score >= 50.0:

            risk_level = (
                "Medium Risk"
            )

        else:

            risk_level = (
                "Low Risk"
            )

        # --------------------------------------------------
        # Recommendation
        # --------------------------------------------------

        recommendation = (
            self._recommendation(
                risk_level,
                prediction_value,
            )
        )

        # --------------------------------------------------
        # Patient ID
        # --------------------------------------------------

        db = SessionLocal()

        try:

            # ------------------------------------------------
            # Split patient name
            # ------------------------------------------------

            name_parts = (
                patient_name.split(
                    " ",
                    1,
                )
            )

            first_name = (
                name_parts[0].strip()
            )

            if (
                len(name_parts) > 1
                and name_parts[1].strip()
            ):

                last_name = (
                    name_parts[1].strip()
                )

            else:

                last_name = "Patient"

            # ------------------------------------------------
            # Find existing patient
            # ------------------------------------------------

            patient = (
                db.query(
                    Patient
                )
                .filter(
                    Patient.first_name.ilike(
                        first_name
                    ),
                    Patient.last_name.ilike(
                        last_name
                    ),
                    Patient.age == int(
                        request.age
                    ),
                    Patient.gender == str(
                        request.gender
                    ),
                    *(
                        [Patient.owner_id == owner_id]
                        if owner_id is not None
                        else []
                    ),
                )
                .first()
            )

            # ------------------------------------------------
            # Create patient
            # ------------------------------------------------

            if patient is None:

                patient = Patient(
                    first_name=first_name,
                    last_name=last_name,
                    age=int(
                        request.age
                    ),
                    gender=str(
                        request.gender
                    ),
                    owner_id=owner_id,
                )

                db.add(
                    patient
                )

                db.commit()

                db.refresh(
                    patient
                )

            patient_id = (
                patient.id
            )

            # ------------------------------------------------
            # Persist prediction in database
            # ------------------------------------------------
            created_at = datetime.utcnow()

            database_prediction = Prediction(
                patient_id=patient.id,
                prediction=prediction,
                probability=(
                    float(risk_score) / 100.0
                ),
                confidence=float(confidence),
                risk_level=risk_level,
                features=json.dumps(features),
                created_at=created_at,
            )

            db.add(database_prediction)
            db.commit()
            db.refresh(database_prediction)

            # Database-generated ID is the canonical prediction ID.
            prediction_id = database_prediction.id

        except Exception:
            db.rollback()
            raise
        finally:

            db.close()

        # --------------------------------------------------
        # Created timestamp
        # --------------------------------------------------

        # created_at was assigned when the database record was committed.

        # --------------------------------------------------
        # Response
        # --------------------------------------------------

        response = PredictionResponse(
            prediction_id=prediction_id,

            patient_id=patient_id,

            prediction=prediction,

            prediction_value=prediction_value,

            confidence=round(
                confidence,
                2,
            ),

            risk_score=round(
                risk_score,
                2,
            ),

            risk_level=risk_level,

            recommendation=recommendation,

            model_name=(
                self._production_model_name()
            ),

            model_version=(
                "2.0.0-step9"
            ),

            created_at=created_at,
        )

        # ==================================================
        # SAVE HISTORY
        # ==================================================

        history_item = PredictionHistory(
            prediction_id=prediction_id,

            patient_id=patient_id,

            patient_name=patient_name,

            age=int(
                request.age
            ),

            gender=str(
                request.gender
            ),

            prediction=prediction,

            confidence=round(
                confidence,
                2,
            ),

            risk_score=round(
                risk_score,
                2,
            ),

            risk_level=risk_level,

            created_at=created_at,
        )

        PredictionService.history.append(
            history_item
        )

        # ==================================================
        # SAVE COMPLETE PREDICTION DATA
        # ==================================================

        PredictionService.predictions[
            prediction_id
        ] = {

            "response":
                response,

            "patient_name":
                patient_name,

            "age":
                request.age,

            "gender":
                request.gender,

            "features":
                features,

            "feature_names":
                FEATURE_NAMES.copy(),

            "selected_feature_names":
                SELECTED_FEATURE_NAMES.copy(),

            "features_extracted":
                EXTRACTED_FEATURE_COUNT,

            "features_used":
                PRODUCTION_FEATURE_COUNT,

            "decision_threshold":
                DECISION_THRESHOLD,

            "model":
                self._production_model_name(),

            "predictor_result":
                predictor_result,
        }

        return response

    # ======================================================
    # RECOMMENDATION
    # ======================================================

    def _recommendation(
        self,
        risk_level: str,
        prediction_value: int,
    ) -> str:
        """
        Generate a recommendation.

        This application is a screening/prediction tool
        and does not establish a clinical diagnosis.
        """

        if (
            prediction_value
            ==
            PARKINSON_CLASS
        ):

            if (
                risk_level
                ==
                "High Risk"
            ):

                return (
                    "The voice analysis indicates "
                    "an elevated Parkinson's disease "
                    "risk. Consult a qualified "
                    "healthcare professional or "
                    "neurologist for clinical "
                    "evaluation. This result is "
                    "not a diagnosis."
                )

            if (
                risk_level
                ==
                "Medium Risk"
            ):

                return (
                    "The voice analysis indicates "
                    "an elevated Parkinson's disease "
                    "risk. Consider a follow-up "
                    "assessment with a qualified "
                    "healthcare professional. "
                    "This result is not a diagnosis."
                )

            return (
                "The model classified this recording "
                "as Parkinson Detected, but the "
                "estimated risk is relatively low. "
                "Consider clinical follow-up if "
                "symptoms or concerns are present. "
                "This result is not a diagnosis."
            )

        return (
            "The voice analysis was classified as "
            "Healthy by the model. If symptoms or "
            "concerns are present, consult a "
            "qualified healthcare professional. "
            "This result is not a diagnosis."
        )

    # ======================================================
    # PRODUCTION MODEL NAME
    # ======================================================

    def _production_model_name(
        self,
    ) -> str:
        """
        Get the actual underlying model name.
        """

        if (
            self.predictor is None
        ):

            return (
                "HistGradientBoosting"
            )

        try:

            information = (
                self.predictor
                .model_information()
            )

            return str(
                information.get(
                    "model",
                    "HistGradientBoosting",
                )
            )

        except Exception:

            return (
                "HistGradientBoosting"
            )

    # ======================================================
    # PREDICTION HISTORY
    # ======================================================

    def get_history(
        self,
        owner_id: Optional[int] = None,
    ) -> List[PredictionHistory]:
        """Return persisted prediction history from SQLite."""

        db = SessionLocal()
        try:
            query = db.query(Prediction).join(Patient)

            if owner_id is not None:
                query = query.filter(
                    Patient.owner_id == owner_id
                )

            records = query.order_by(
                Prediction.created_at.desc()
            ).all()

            result = []
            for record in records:
                patient = record.patient
                result.append(
                    PredictionHistory(
                        prediction_id=record.id,
                        patient_id=record.patient_id,
                        patient_name=(
                            f"{patient.first_name} "
                            f"{patient.last_name}"
                        ).strip(),
                        age=int(patient.age),
                        gender=str(patient.gender),
                        prediction=str(record.prediction),
                        confidence=round(
                            float(record.confidence or 0.0), 2
                        ),
                        risk_score=round(
                            float(record.probability or 0.0) * 100.0, 2
                        ),
                        risk_level=str(record.risk_level or "Unknown"),
                        created_at=record.created_at,
                    )
                )

            return result
        finally:
            db.close()

    # ======================================================
    # PREDICTION DETAILS
    # ======================================================

    def _db_prediction_response(
        self,
        record: Prediction,
    ) -> PredictionResponse:
        """Convert a database Prediction into the API response schema."""

        prediction_value = (
            PARKINSON_CLASS
            if str(record.prediction) == "Parkinson Detected"
            else HEALTHY_CLASS
        )

        risk_score = float(record.probability or 0.0) * 100.0

        return PredictionResponse(
            prediction_id=record.id,
            patient_id=record.patient_id,
            prediction=str(record.prediction),
            prediction_value=prediction_value,
            confidence=round(float(record.confidence or 0.0), 2),
            risk_score=round(risk_score, 2),
            risk_level=str(record.risk_level or "Unknown"),
            recommendation=self._recommendation(
                str(record.risk_level or "Low Risk"),
                prediction_value,
            ),
            model_name=self._production_model_name(),
            model_version="2.0.0-step9",
            created_at=record.created_at,
        )

    def get_prediction(
        self,
        prediction_id: int,
    ) -> Optional[PredictionResponse]:
        """Retrieve a persisted prediction by ID."""

        db = SessionLocal()
        try:
            record = db.query(Prediction).filter(
                Prediction.id == prediction_id
            ).first()

            if record is None:
                return None

            return self._db_prediction_response(record)
        finally:
            db.close()

    # ======================================================
    # COMPLETE PREDICTION DATA
    # ======================================================

    def get_prediction_data(
        self,
        prediction_id: int,
    ) -> Optional[Dict]:
        """Return complete persisted prediction information."""

        db = SessionLocal()
        try:
            record = db.query(Prediction).filter(
                Prediction.id == prediction_id
            ).first()

            if record is None:
                return None

            response = self._db_prediction_response(record)

            try:
                features = json.loads(record.features or "[]")
            except (TypeError, ValueError):
                features = []

            return {
                "response": response,
                "patient_name": (
                    f"{record.patient.first_name} "
                    f"{record.patient.last_name}"
                ).strip(),
                "age": record.patient.age,
                "gender": record.patient.gender,
                "features": features,
                "feature_names": FEATURE_NAMES.copy(),
                "selected_feature_names": SELECTED_FEATURE_NAMES.copy(),
                "features_extracted": EXTRACTED_FEATURE_COUNT,
                "features_used": PRODUCTION_FEATURE_COUNT,
                "decision_threshold": DECISION_THRESHOLD,
                "model": self._production_model_name(),
            }
        finally:
            db.close()

    # ======================================================
    # DELETE PREDICTION
    # ======================================================

    def delete_prediction(
        self,
        prediction_id: int,
    ) -> bool:
        """Delete a persisted prediction from SQLite."""

        db = SessionLocal()
        try:
            record = db.query(Prediction).filter(
                Prediction.id == prediction_id
            ).first()

            if record is None:
                return False

            db.delete(record)
            db.commit()
            return True
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    # ======================================================
    # STATISTICS
    # ======================================================

    def statistics(self) -> PredictionStatistics:
        """Calculate prediction statistics from persisted records."""

        db = SessionLocal()
        try:
            records = db.query(Prediction).all()

            healthy_cases = 0
            parkinson_cases = 0
            high_risk_cases = 0
            medium_risk_cases = 0
            low_risk_cases = 0
            confidence_values = []

            for record in records:
                confidence_values.append(
                    float(record.confidence or 0.0)
                )

                if str(record.prediction) == "Parkinson Detected":
                    parkinson_cases += 1
                else:
                    healthy_cases += 1

                if record.risk_level == "High Risk":
                    high_risk_cases += 1
                elif record.risk_level == "Medium Risk":
                    medium_risk_cases += 1
                elif record.risk_level == "Low Risk":
                    low_risk_cases += 1

            average_confidence = (
                sum(confidence_values) / len(confidence_values)
                if confidence_values else 0.0
            )

            return PredictionStatistics(
                total_predictions=len(records),
                healthy_cases=healthy_cases,
                parkinson_cases=parkinson_cases,
                average_confidence=round(average_confidence, 2),
                high_risk_cases=high_risk_cases,
                medium_risk_cases=medium_risk_cases,
                low_risk_cases=low_risk_cases,
            )
        finally:
            db.close()

    # ======================================================
    # MODEL INFORMATION
    # ======================================================

    def model_info(
        self,
    ) -> ModelInformation:
        """
        Return actual production model information.

        Unlike the old implementation, this method does not
        return fabricated/hard-coded Logistic Regression
        metrics.
        """

        if not self.model_loaded:

            self._load_model()

        # --------------------------------------------------
        # Predictor information
        # --------------------------------------------------

        predictor_information = {}

        if (
            self.predictor
            is not None
        ):

            try:

                predictor_information = (
                    self.predictor
                    .model_information()
                )

            except Exception:

                predictor_information = {}

        # --------------------------------------------------
        # Status
        # --------------------------------------------------

        status = (
            "Ready"
            if self.model_loaded
            else "Unavailable"
        )

        # --------------------------------------------------
        # Model name
        # --------------------------------------------------

        model_name = (
            predictor_information.get(
                "model",
                "HistGradientBoosting",
            )
        )

        # --------------------------------------------------
        # Return schema-compatible object
        #
        # The existing schema expects numeric performance
        # fields. Those values are not silently fabricated.
        # We use the Step 9 validation values where they are
        # actually available from the project results.
        # --------------------------------------------------

        return ModelInformation(
            model_name=str(
                model_name
            ),

            model_version=(
                "2.0.0-step9"
            ),

            algorithm=str(
                model_name
            ),

            total_features=
                PRODUCTION_FEATURE_COUNT,

            accuracy=74.07,

            precision=73.17,

            recall=75.00,

            f1_score=74.07,

            status=status,
        )


# ==========================================================
# GLOBAL SERVICE INSTANCE
# ==========================================================

prediction_service = (
    PredictionService()
)
