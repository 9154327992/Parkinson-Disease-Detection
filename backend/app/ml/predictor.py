from pathlib import Path
from typing import List, Dict, Any

import joblib
import numpy as np

from app.ml.preprocessing import Preprocessor


# ==========================================================
# Constants
# ==========================================================

TOTAL_FEATURES = 22

MODEL_PATH = Path(
    "models/model.pkl"
)

SCALER_PATH = Path(
    "models/scaler.pkl"
)


# ==========================================================
# Parkinson Predictor
# ==========================================================

class ParkinsonPredictor:
    """
    Parkinson Disease prediction wrapper.

    Pipeline:

        22 features
            ↓
        StandardScaler
            ↓
        RandomForestClassifier
            ↓
        Prediction
    """

    def __init__(
        self,
        model_path: str = str(
            MODEL_PATH
        ),
        scaler_path: str = str(
            SCALER_PATH
        ),
    ):
        """
        Initialize predictor.
        """

        self.model_path = Path(
            model_path
        )

        self.scaler_path = Path(
            scaler_path
        )

        self.model = None

        self.preprocessor = None

        self._load()


    # ======================================================
    # Load Model + Scaler
    # ======================================================

    def _load(self):
        """
        Load trained Random Forest model
        and StandardScaler.
        """

        if not self.model_path.exists():

            raise FileNotFoundError(
                "Model not found: "
                f"{self.model_path}"
            )


        if not self.scaler_path.exists():

            raise FileNotFoundError(
                "Scaler not found: "
                f"{self.scaler_path}"
            )


        self.model = joblib.load(
            self.model_path
        )


        self.preprocessor = (
            Preprocessor(
                scaler_path=self.scaler_path
            )
        )


        # --------------------------------------------------
        # Validate feature count
        # --------------------------------------------------

        model_features = getattr(
            self.model,
            "n_features_in_",
            None,
        )


        if (
            model_features is not None
            and model_features
            != TOTAL_FEATURES
        ):

            raise ValueError(
                "Model expects "
                f"{model_features} features, "
                f"but this application "
                f"requires {TOTAL_FEATURES}."
            )


        scaler_features = getattr(
            self.preprocessor.scaler,
            "n_features_in_",
            None,
        )


        if (
            scaler_features is not None
            and scaler_features
            != TOTAL_FEATURES
        ):

            raise ValueError(
                "Scaler expects "
                f"{scaler_features} features, "
                f"but this application "
                f"requires {TOTAL_FEATURES}."
            )


    # ======================================================
    # Validate Input
    # ======================================================

    def _validate_features(
        self,
        features: List[float],
    ) -> List[float]:
        """
        Validate the 22 feature values.
        """

        if features is None:

            raise ValueError(
                "Features are required."
            )


        if len(features) != TOTAL_FEATURES:

            raise ValueError(
                "Exactly "
                f"{TOTAL_FEATURES} "
                "features are required. "
                f"Received {len(features)}."
            )


        validated = []


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
                    "must be numeric."
                )


            if not np.isfinite(
                numeric_value
            ):

                raise ValueError(
                    f"Feature {index + 1} "
                    "must be finite."
                )


            validated.append(
                numeric_value
            )


        return validated


    # ======================================================
    # Scale Features
    # ======================================================

    def _scale(
        self,
        features: List[float],
    ) -> np.ndarray:
        """
        Scale the 22 features using
        the trained StandardScaler.
        """

        return self.preprocessor.scale(
            features
        )


    # ======================================================
    # Predict Class
    # ======================================================

    def _predict_class(
        self,
        scaled_features: np.ndarray,
    ) -> int:
        """
        Return predicted class.

        Dataset convention:

            0 = Healthy
            1 = Parkinson
        """

        prediction = self.model.predict(
            scaled_features
        )[0]


        try:

            return int(
                prediction
            )

        except (
            TypeError,
            ValueError,
        ):

            return (
                1
                if str(
                    prediction
                ).lower()
                in {
                    "1",
                    "parkinson",
                    "parkinson's",
                    "parkinson detected",
                }
                else 0
            )


    # ======================================================
    # Parkinson Probability
    # ======================================================

    def _parkinson_probability(
        self,
        scaled_features: np.ndarray,
    ) -> float:
        """
        Return probability of Parkinson class.

        IMPORTANT:
        This explicitly finds class 1 instead of
        assuming that the predicted class index
        represents the Parkinson probability.
        """

        if not hasattr(
            self.model,
            "predict_proba",
        ):

            prediction = (
                self._predict_class(
                    scaled_features
                )
            )


            return (
                1.0
                if prediction == 1
                else 0.0
            )


        probabilities = (
            self.model.predict_proba(
                scaled_features
            )[0]
        )


        classes = getattr(
            self.model,
            "classes_",
            None,
        )


        if classes is None:

            raise ValueError(
                "Model does not expose "
                "class information."
            )


        classes_list = list(
            classes
        )


        # --------------------------------------------------
        # Find Parkinson class = 1
        # --------------------------------------------------

        if 1 in classes_list:

            parkinson_index = (
                classes_list.index(1)
            )

            return float(
                probabilities[
                    parkinson_index
                ]
            )


        # --------------------------------------------------
        # Fallback for string labels
        # --------------------------------------------------

        normalized_classes = [
            str(value)
            .strip()
            .lower()
            for value in classes_list
        ]


        possible_parkinson_labels = {
            "1",
            "parkinson",
            "parkinson's",
            "parkinson detected",
            "positive",
        }


        for index, label in enumerate(
            normalized_classes
        ):

            if label in (
                possible_parkinson_labels
            ):

                return float(
                    probabilities[
                        index
                    ]
                )


        raise ValueError(
            "Unable to identify the "
            "Parkinson class in the model."
        )


    # ======================================================
    # Confidence
    # ======================================================

    def _confidence(
        self,
        scaled_features: np.ndarray,
    ) -> float:
        """
        Return confidence of the model's
        predicted class.
        """

        if not hasattr(
            self.model,
            "predict_proba",
        ):

            return 0.0


        probabilities = (
            self.model.predict_proba(
                scaled_features
            )[0]
        )


        return float(
            np.max(
                probabilities
            )
        )


    # ======================================================
    # Risk Level
    # ======================================================

    @staticmethod
    def _risk_level(
        risk_score: float,
    ) -> str:
        """
        Convert Parkinson probability
        into a human-readable risk level.
        """

        if risk_score >= 75:

            return "High Risk"


        if risk_score >= 40:

            return "Medium Risk"


        return "Low Risk"


    # ======================================================
    # Diagnosis
    # ======================================================

    @staticmethod
    def _diagnosis(
        prediction: int,
    ) -> str:
        """
        Convert model class into diagnosis.
        """

        if prediction == 1:

            return (
                "Parkinson Detected"
            )


        return "Healthy"


    # ======================================================
    # Recommendation
    # ======================================================

    @staticmethod
    def _recommendation(
        prediction: int,
        risk_score: float,
    ) -> str:
        """
        Generate a general recommendation.

        This is an AI-assisted screening result,
        not a medical diagnosis.
        """

        if prediction == 1:

            if risk_score >= 75:

                return (
                    "The screening result indicates "
                    "a higher likelihood of Parkinson's "
                    "disease. Please consult a qualified "
                    "healthcare professional or "
                    "neurologist for clinical evaluation."
                )


            return (
                "The screening result indicates "
                "a possible Parkinson-related pattern. "
                "Consider discussing the result with "
                "a qualified healthcare professional."
            )


        return (
            "The screening result does not indicate "
            "a strong Parkinson-related pattern. "
            "Continue routine healthcare and consult "
            "a healthcare professional if symptoms "
            "are present."
        )


    # ======================================================
    # Main Prediction
    # ======================================================

    def predict(
        self,
        features: List[float],
    ) -> Dict[str, Any]:
        """
        Run complete prediction pipeline.

        Returns:

            prediction
            diagnosis
            risk_score
            risk_level
            confidence
        """

        # --------------------------------------------------
        # Validate
        # --------------------------------------------------

        features = (
            self._validate_features(
                features
            )
        )


        # --------------------------------------------------
        # Scale
        # --------------------------------------------------

        scaled_features = (
            self._scale(
                features
            )
        )


        # --------------------------------------------------
        # Prediction
        # --------------------------------------------------

        prediction = (
            self._predict_class(
                scaled_features
            )
        )


        # --------------------------------------------------
        # Parkinson Probability
        # --------------------------------------------------

        parkinson_probability = (
            self._parkinson_probability(
                scaled_features
            )
        )


        # --------------------------------------------------
        # Confidence
        # --------------------------------------------------

        confidence = (
            self._confidence(
                scaled_features
            )
        )


        # --------------------------------------------------
        # Convert to percentages
        # --------------------------------------------------

        risk_score = (
            parkinson_probability
            * 100.0
        )


        confidence_score = (
            confidence
            * 100.0
        )


        # --------------------------------------------------
        # Diagnosis
        # --------------------------------------------------

        diagnosis = (
            self._diagnosis(
                prediction
            )
        )


        # --------------------------------------------------
        # Risk Level
        # --------------------------------------------------

        risk_level = (
            self._risk_level(
                risk_score
            )
        )


        # --------------------------------------------------
        # Recommendation
        # --------------------------------------------------

        recommendation = (
            self._recommendation(
                prediction,
                risk_score,
            )
        )


        # --------------------------------------------------
        # Return
        # --------------------------------------------------

        return {
            "prediction":
                diagnosis,

            "prediction_value":
                prediction,

            "diagnosis":
                diagnosis,

            "risk_score":
                round(
                    risk_score,
                    2,
                ),

            "risk_level":
                risk_level,

            "confidence":
                round(
                    confidence_score,
                    2,
                ),

            "parkinson_probability":
                round(
                    risk_score,
                    2,
                ),

            "recommendation":
                recommendation,

            "model":
                self.model.__class__.__name__,

            "features_used":
                TOTAL_FEATURES,
        }


    # ======================================================
    # Batch Prediction
    # ======================================================

    def predict_batch(
        self,
        features: List[List[float]],
    ) -> List[Dict[str, Any]]:
        """
        Run predictions for multiple
        22-feature vectors.
        """

        if not features:

            return []


        results = []


        for row in features:

            results.append(
                self.predict(row)
            )


        return results


    # ======================================================
    # Model Information
    # ======================================================

    def model_information(
        self,
    ) -> Dict[str, Any]:
        """
        Return information about the
        loaded model.
        """

        classes = getattr(
            self.model,
            "classes_",
            [],
        )


        return {
            "model":
                self.model.__class__.__name__,

            "model_path":
                str(
                    self.model_path
                ),

            "scaler_path":
                str(
                    self.scaler_path
                ),

            "features":
                TOTAL_FEATURES,

            "classes":
                [
                    str(value)
                    for value in classes
                ],

            "model_loaded":
                self.model is not None,

            "scaler_loaded":
                self.preprocessor
                is not None,
        }


# ==========================================================
# Shared Predictor
# ==========================================================

predictor = ParkinsonPredictor()
