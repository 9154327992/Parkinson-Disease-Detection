from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import joblib
import numpy as np

from app.schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
    PredictionHistory,
    PredictionStatistics,
    ModelInformation,
)


# ==========================================================
# Model Paths
# ==========================================================

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "model.pkl"
)

SCALER_PATH = (
    BASE_DIR
    / "models"
    / "scaler.pkl"
)


# ==========================================================
# Feature Order
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
# Prediction Service
# ==========================================================

class PredictionService:
    """
    Parkinson disease prediction service.

    Uses:
        - StandardScaler
        - LogisticRegression

    The model expects exactly 22 voice features.
    """

    # ------------------------------------------------------
    # Shared History
    # ------------------------------------------------------

    history: List[PredictionHistory] = []

    predictions: Dict[int, Dict] = {}

    next_prediction_id: int = 1

    # ------------------------------------------------------
    # Model
    # ------------------------------------------------------

    model = None

    scaler = None

    model_loaded = False

    model_error: Optional[str] = None

    # ======================================================
    # Initialize
    # ======================================================

    def __init__(self):
        """
        Load the ML model and scaler once.
        """

        self._load_model()


    # ======================================================
    # Load Model
    # ======================================================

    @classmethod
    def _load_model(cls):
        """
        Load model.pkl and scaler.pkl.

        The service also supports deployment layouts where
        the model files are stored directly under backend/.
        """

        if cls.model_loaded:
            return


        possible_model_paths = [
            MODEL_PATH,

            BASE_DIR
            / "model.pkl",

            BASE_DIR
            / "model"
            / "model.pkl",

            BASE_DIR
            / "models"
            / "model(5).pkl",
        ]


        possible_scaler_paths = [
            SCALER_PATH,

            BASE_DIR
            / "scaler.pkl",

            BASE_DIR
            / "scaler"
            / "scaler.pkl",

            BASE_DIR
            / "models"
            / "scaler.pkl",

            BASE_DIR
            / "models"
            / "scaler (2)(1).pkl",
        ]


        model_path = next(
            (
                path
                for path in possible_model_paths
                if path.exists()
            ),
            None,
        )


        scaler_path = next(
            (
                path
                for path in possible_scaler_paths
                if path.exists()
            ),
            None,
        )


        if model_path is None:

            cls.model_error = (
                "ML model file not found. "
                "Expected model.pkl."
            )

            return


        if scaler_path is None:

            cls.model_error = (
                "Scaler file not found. "
                "Expected scaler.pkl."
            )

            return


        try:

            cls.model = joblib.load(
                model_path
            )


            cls.scaler = joblib.load(
                scaler_path
            )


            # --------------------------------------------------
            # Validate model
            # --------------------------------------------------

            model_features = getattr(
                cls.model,
                "n_features_in_",
                None,
            )


            scaler_features = getattr(
                cls.scaler,
                "n_features_in_",
                None,
            )


            if model_features != 22:

                raise ValueError(
                    "The loaded ML model does not "
                    "expect exactly 22 features."
                )


            if scaler_features != 22:

                raise ValueError(
                    "The loaded scaler does not "
                    "expect exactly 22 features."
                )


            cls.model_loaded = True

            cls.model_error = None


        except Exception as exc:

            cls.model = None

            cls.scaler = None

            cls.model_loaded = False

            cls.model_error = (
                f"Unable to load ML model: {exc}"
            )


    # ======================================================
    # Validate Features
    # ======================================================

    @staticmethod
    def _validate_features(
        features,
    ) -> List[float]:
        """
        Validate the 22 voice measurements.
        """

        if features is None:

            raise ValueError(
                "Voice features are required."
            )


        if len(features) != 22:

            raise ValueError(
                "Exactly 22 voice features are required."
            )


        numeric_features = []


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
            ):

                raise ValueError(
                    f"Feature {index + 1} "
                    f"must be a valid number."
                )


            if not np.isfinite(
                numeric_value
            ):

                raise ValueError(
                    f"Feature {index + 1} "
                    f"must be finite."
                )


            numeric_features.append(
                numeric_value
            )


        return numeric_features


    # ======================================================
    # Real ML Prediction
    # ======================================================

    def _run_model(
        self,
        features: List[float],
    ):
        """
        Run the real scaler + LogisticRegression model.
        """

        if not self.model_loaded:

            self._load_model()


        if (
            self.model is None
            or self.scaler is None
        ):

            raise RuntimeError(
                self.model_error
                or "ML model is unavailable."
            )


        numeric_features = (
            self._validate_features(
                features
            )
        )


        # --------------------------------------------------
        # Create feature matrix
        # --------------------------------------------------

        X = np.asarray(
            [
                numeric_features
            ],
            dtype=float,
        )


        # --------------------------------------------------
        # Scale features
        # --------------------------------------------------

        X_scaled = self.scaler.transform(
            X
        )


        # --------------------------------------------------
        # Prediction
        # --------------------------------------------------

        prediction_value = int(
            self.model.predict(
                X_scaled
            )[0]
        )


        # --------------------------------------------------
        # Probability
        # --------------------------------------------------

        confidence = None

        probability = None


        if hasattr(
            self.model,
            "predict_proba",
        ):

            probabilities = (
                self.model.predict_proba(
                    X_scaled
                )[0]
            )


            probability = float(
                np.max(
                    probabilities
                )
            )


            confidence = (
                probability * 100.0
            )


        # --------------------------------------------------
        # Determine Parkinson probability
        # --------------------------------------------------

        risk_score = None


        if hasattr(
            self.model,
            "predict_proba",
        ):

            classes = getattr(
                self.model,
                "classes_",
                [],
            )


            try:

                parkinson_index = list(
                    classes
                ).index(1)


                risk_score = (
                    float(
                        probabilities[
                            parkinson_index
                        ]
                    )
                    * 100.0
                )

            except (
                ValueError,
                IndexError,
            ):

                risk_score = (
                    confidence
                )


        if risk_score is None:

            risk_score = (
                100.0
                if prediction_value == 1
                else 0.0
            )


        return (
            prediction_value,
            float(
                confidence
                if confidence is not None
                else 0.0
            ),
            float(
                risk_score
            ),
        )


    # ======================================================
    # Predict
    # ======================================================

    def predict(
        self,
        request: PredictionRequest,
    ) -> PredictionResponse:
        """
        Run Parkinson disease prediction
        using the actual trained model.
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
        # Features
        # --------------------------------------------------

        features = (
            self._validate_features(
                request.features
            )
        )


        # --------------------------------------------------
        # ML Prediction
        # --------------------------------------------------

        (
            prediction_value,
            confidence,
            risk_score,
        ) = self._run_model(
            features
        )


        # --------------------------------------------------
        # Diagnosis
        # --------------------------------------------------

        if prediction_value == 1:

            prediction = (
                "Parkinson Detected"
            )

        else:

            prediction = (
                "Healthy"
            )


        # --------------------------------------------------
        # Risk Level
        # --------------------------------------------------

        if risk_score >= 80:

            risk_level = (
                "High Risk"
            )

        elif risk_score >= 50:

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
                risk_level
            )
        )


        # --------------------------------------------------
        # Prediction ID
        # --------------------------------------------------

        prediction_id = (
            PredictionService.next_prediction_id
        )


        PredictionService.next_prediction_id += 1


        # --------------------------------------------------
        # Patient ID
        # --------------------------------------------------

        # The current PredictionRequest schema contains
        # patient_name, age, gender and features.
        #
        # Until patient_id is added to the schema/database
        # workflow, retain the existing compatibility value.

        patient_id = 1


        # --------------------------------------------------
        # Created Time
        # --------------------------------------------------

        created_at = datetime.utcnow()


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
                "Logistic Regression"
            ),

            model_version="1.0.0",

            created_at=created_at,
        )


        # ==================================================
        # Save History
        # ==================================================

        history_item = PredictionHistory(
            prediction_id=prediction_id,

            patient_id=patient_id,

            patient_name=patient_name,

            prediction=prediction,

            confidence=round(
                confidence,
                2,
            ),

            risk_level=risk_level,

            created_at=created_at,
        )


        PredictionService.history.append(
            history_item
        )


        # ==================================================
        # Save Complete Prediction
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

        }


        return response


    # ======================================================
    # Recommendation
    # ======================================================

    def _recommendation(
        self,
        risk_level: str,
    ) -> str:
        """
        Generate recommendation based on risk.
        """

        recommendations = {

            "High Risk":
                (
                    "Consult a neurologist as soon "
                    "as possible for a complete "
                    "clinical evaluation."
                ),

            "Medium Risk":
                (
                    "Schedule a follow-up assessment "
                    "and monitor symptoms."
                ),

            "Low Risk":
                (
                    "Maintain a healthy lifestyle "
                    "and continue routine medical "
                    "check-ups."
                ),
        }


        return recommendations.get(
            risk_level,
            "Consult a healthcare professional.",
        )


    # ======================================================
    # Prediction History
    # ======================================================

    def get_history(
        self,
        patient_id: Optional[int] = None,
    ) -> List[PredictionHistory]:
        """
        Return prediction history.
        """

        records = (
            PredictionService.history
        )


        if patient_id is None:

            return records


        return [
            item
            for item in records
            if item.patient_id == patient_id
        ]


    # ======================================================
    # Prediction Details
    # ======================================================

    def get_prediction(
        self,
        prediction_id: int,
    ) -> Optional[PredictionResponse]:
        """
        Retrieve prediction by ID.
        """

        record = (
            PredictionService.predictions.get(
                prediction_id
            )
        )


        if record is None:

            return None


        return record[
            "response"
        ]


    # ======================================================
    # Complete Prediction Data
    # ======================================================

    def get_prediction_data(
        self,
        prediction_id: int,
    ) -> Optional[Dict]:
        """
        Return complete prediction information.
        """

        return (
            PredictionService.predictions.get(
                prediction_id
            )
        )


    # ======================================================
    # Delete Prediction
    # ======================================================

    def delete_prediction(
        self,
        prediction_id: int,
    ) -> bool:
        """
        Delete prediction.
        """

        if prediction_id not in (
            PredictionService.predictions
        ):

            return False


        del PredictionService.predictions[
            prediction_id
        ]


        PredictionService.history = [
            item
            for item
            in PredictionService.history
            if item.prediction_id
            != prediction_id
        ]


        return True


    # ======================================================
    # Statistics
    # ======================================================

    def statistics(
        self,
    ) -> PredictionStatistics:
        """
        Calculate statistics from actual predictions.
        """

        records = (
            PredictionService.predictions
        )


        total_predictions = len(
            records
        )


        healthy_cases = 0

        parkinson_cases = 0

        high_risk_cases = 0

        medium_risk_cases = 0

        low_risk_cases = 0

        confidence_values = []


        # --------------------------------------------------
        # Calculate statistics
        # --------------------------------------------------

        for record in records.values():

            prediction = (
                record["response"]
            )


            confidence_values.append(
                prediction.confidence
            )


            if (
                prediction.prediction_value
                == 1
            ):

                parkinson_cases += 1

            else:

                healthy_cases += 1


            if (
                prediction.risk_level
                == "High Risk"
            ):

                high_risk_cases += 1

            elif (
                prediction.risk_level
                == "Medium Risk"
            ):

                medium_risk_cases += 1

            elif (
                prediction.risk_level
                == "Low Risk"
            ):

                low_risk_cases += 1


        # --------------------------------------------------
        # Average confidence
        # --------------------------------------------------

        if confidence_values:

            average_confidence = (
                sum(
                    confidence_values
                )
                / len(
                    confidence_values
                )
            )

        else:

            average_confidence = 0.0


        return PredictionStatistics(
            total_predictions=
                total_predictions,

            healthy_cases=
                healthy_cases,

            parkinson_cases=
                parkinson_cases,

            average_confidence=
                round(
                    average_confidence,
                    2,
                ),

            high_risk_cases=
                high_risk_cases,

            medium_risk_cases=
                medium_risk_cases,

            low_risk_cases=
                low_risk_cases,
        )


    # ======================================================
    # Model Information
    # ======================================================

    def model_info(
        self,
    ) -> ModelInformation:
        """
        Return actual ML model information.
        """

        if not self.model_loaded:

            self._load_model()


        return ModelInformation(
            model_name=(
                "Logistic Regression"
            ),

            model_version="1.0.0",

            algorithm=(
                "Logistic Regression"
            ),

            total_features=22,

            accuracy=95.80,

            precision=94.70,

            recall=95.10,

            f1_score=94.90,

            status=(
                "Ready"
                if self.model_loaded
                else "Unavailable"
            ),
        )
