from pathlib import Path
from typing import Any, Dict, List

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
    Main Parkinson prediction engine.

    Input:
        22 extracted audio features

    Output:
        prediction
        diagnosis
        Parkinson probability
        risk score
        risk level
        confidence
        recommendation
    """

    # ======================================================
    # Initialization
    # ======================================================

    def __init__(
        self,
        model_path: str = str(
            MODEL_PATH
        ),
        scaler_path: str = str(
            SCALER_PATH
        ),
    ):

        self.model_path = Path(
            model_path
        )

        self.scaler_path = Path(
            scaler_path
        )

        self.model = None

        self.preprocessor = None

        self.is_pipeline = False

        self._load()

    # ======================================================
    # Load Model
    # ======================================================

    def _load(self):
        """
        Load the trained model.

        Supports both:

        1. A normal sklearn classifier +
           separate scaler.pkl

        2. A sklearn Pipeline containing:
           imputer -> scaler -> model
        """

        if not self.model_path.exists():

            raise FileNotFoundError(
                "Model not found: "
                f"{self.model_path}"
            )

        # --------------------------------------------------
        # Load model
        # --------------------------------------------------

        self.model = joblib.load(
            self.model_path
        )

        # --------------------------------------------------
        # Detect Pipeline
        # --------------------------------------------------

        if hasattr(
            self.model,
            "named_steps",
        ):

            self.is_pipeline = True

            # --------------------------------------------------
            # Pipeline itself handles scaling.
            # --------------------------------------------------

            self.preprocessor = None

        else:

            self.is_pipeline = False

            # --------------------------------------------------
            # Old architecture requires scaler.
            # --------------------------------------------------

            if not self.scaler_path.exists():

                raise FileNotFoundError(
                    "Scaler not found: "
                    f"{self.scaler_path}"
                )

            self.preprocessor = (
                Preprocessor(
                    scaler_path=self.scaler_path
                )
            )

        # --------------------------------------------------
        # Validate feature count
        # --------------------------------------------------

        self._validate_model_features()

    # ======================================================
    # Validate Model Features
    # ======================================================

    def _validate_model_features(
        self,
    ) -> None:

        # --------------------------------------------------
        # Pipeline
        # --------------------------------------------------

        if self.is_pipeline:

            try:

                model = (
                    self.model
                    .named_steps
                    .get("model")
                )

                if model is not None:

                    feature_count = getattr(
                        model,
                        "n_features_in_",
                        None,
                    )

                    if (
                        feature_count is not None
                        and feature_count
                        != TOTAL_FEATURES
                    ):

                        raise ValueError(
                            "Model expects "
                            f"{feature_count} features, "
                            f"but application requires "
                            f"{TOTAL_FEATURES}."
                        )

            except AttributeError:

                pass

            return

        # --------------------------------------------------
        # Normal classifier
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
                f"but application requires "
                f"{TOTAL_FEATURES}."
            )

        # --------------------------------------------------
        # Scaler
        # --------------------------------------------------

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
                f"but application requires "
                f"{TOTAL_FEATURES}."
            )

    # ======================================================
    # Validate Input
    # ======================================================

    def _validate_features(
        self,
        features: List[float],
    ) -> List[float]:
        """
        Validate exactly 22 numeric features.
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
    # Prepare Input
    # ======================================================

    def _prepare_input(
        self,
        features: List[float],
    ) -> np.ndarray:
        """
        Prepare features for prediction.

        Pipeline model:
            raw features are passed directly.

        Old model:
            features are scaled using scaler.pkl.
        """

        array = np.asarray(
            features,
            dtype=np.float64,
        ).reshape(
            1,
            TOTAL_FEATURES,
        )

        if self.is_pipeline:

            return array

        return self.preprocessor.scale(
            features
        )

    # ======================================================
    # Predict Class
    # ======================================================

    def _predict_class(
        self,
        prepared_features: np.ndarray,
    ) -> int:
        """
        Return:

            0 = Healthy
            1 = Parkinson
        """

        prediction = self.model.predict(
            prepared_features
        )[0]

        try:

            return int(
                prediction
            )

        except (
            TypeError,
            ValueError,
        ):

            normalized = (
                str(prediction)
                .strip()
                .lower()
            )

            if normalized in {
                "1",
                "parkinson",
                "parkinson's",
                "parkinson detected",
                "positive",
                "pd",
            }:

                return 1

            return 0

    # ======================================================
    # Parkinson Probability
    # ======================================================

    def _parkinson_probability(
        self,
        prepared_features: np.ndarray,
    ) -> float:
        """
        Return probability of class 1.
        """

        if not hasattr(
            self.model,
            "predict_proba",
        ):

            prediction = (
                self._predict_class(
                    prepared_features
                )
            )

            return (
                1.0
                if prediction == 1
                else 0.0
            )

        probabilities = (
            self.model.predict_proba(
                prepared_features
            )[0]
        )

        classes = getattr(
            self.model,
            "classes_",
            None,
        )

        # --------------------------------------------------
        # Pipeline
        # --------------------------------------------------

        if classes is None and self.is_pipeline:

            classifier = (
                self.model
                .named_steps
                .get("model")
            )

            if classifier is not None:

                classes = getattr(
                    classifier,
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
        # Find numeric class 1
        # --------------------------------------------------

        if 1 in classes_list:

            index = classes_list.index(
                1
            )

            return float(
                probabilities[index]
            )

        # --------------------------------------------------
        # String labels
        # --------------------------------------------------

        normalized_classes = [
            str(value)
            .strip()
            .lower()
            for value in classes_list
        ]

        parkinson_labels = {
            "1",
            "parkinson",
            "parkinson's",
            "parkinson detected",
            "positive",
            "pd",
        }

        for index, label in enumerate(
            normalized_classes
        ):

            if label in parkinson_labels:

                return float(
                    probabilities[index]
                )

        raise ValueError(
            "Unable to identify "
            "Parkinson class in model."
        )

    # ======================================================
    # Confidence
    # ======================================================

    def _confidence(
        self,
        prepared_features: np.ndarray,
    ) -> float:

        if not hasattr(
            self.model,
            "predict_proba",
        ):

            return 0.0

        probabilities = (
            self.model.predict_proba(
                prepared_features
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
        General screening recommendation.

        This is not a medical diagnosis.
        """

        if prediction == 1:

            if risk_score >= 75:

                return (
                    "The screening result indicates "
                    "a higher likelihood of a "
                    "Parkinson-related pattern. "
                    "Please consult a qualified "
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
        # Prepare
        # --------------------------------------------------

        prepared_features = (
            self._prepare_input(
                features
            )
        )

        # --------------------------------------------------
        # Class
        # --------------------------------------------------

        prediction = (
            self._predict_class(
                prepared_features
            )
        )

        # --------------------------------------------------
        # Parkinson probability
        # --------------------------------------------------

        parkinson_probability = (
            self._parkinson_probability(
                prepared_features
            )
        )

        # --------------------------------------------------
        # Confidence
        # --------------------------------------------------

        confidence = (
            self._confidence(
                prepared_features
            )
        )

        # --------------------------------------------------
        # Percentages
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
        # Risk
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
        # Result
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

            "healthy_probability":
                round(
                    (
                        1.0
                        - parkinson_probability
                    )
                    * 100.0,
                    2,
                ),

            "recommendation":
                recommendation,

            "model":
                self.model.__class__.__name__,

            "features_used":
                TOTAL_FEATURES,

            "model_type":
                (
                    "pipeline"
                    if self.is_pipeline
                    else "classifier"
                ),
        }

    # ======================================================
    # Batch Prediction
    # ======================================================

    def predict_batch(
        self,
        features: List[List[float]],
    ) -> List[Dict[str, Any]]:

        if not features:

            return []

        results = []

        for row in features:

            results.append(
                self.predict(
                    row
                )
            )

        return results

    # ======================================================
    # Model Information
    # ======================================================

    def model_information(
        self,
    ) -> Dict[str, Any]:

        classes = getattr(
            self.model,
            "classes_",
            [],
        )

        if not classes and self.is_pipeline:

            classifier = (
                self.model
                .named_steps
                .get("model")
            )

            if classifier is not None:

                classes = getattr(
                    classifier,
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
                (
                    self.is_pipeline
                    or self.preprocessor is not None
                ),

            "pipeline":
                self.is_pipeline,
        }

    # ======================================================
    # Health
    # ======================================================

    def health(
        self,
    ) -> Dict[str, Any]:

        try:

            return {
                "healthy": True,
                "model_loaded":
                    self.model is not None,
                "pipeline":
                    self.is_pipeline,
                "features":
                    TOTAL_FEATURES,
            }

        except Exception as exc:

            return {
                "healthy": False,
                "error":
                    str(exc),
            }


# ==========================================================
# Shared Predictor
# ==========================================================

predictor = ParkinsonPredictor()


# ==========================================================
# Convenience Function
# ==========================================================

def predict(
    features: List[float],
) -> Dict[str, Any]:

    return predictor.predict(
        features
    )


# ==========================================================
# Standalone Test
# ==========================================================

if __name__ == "__main__":

    sample_features = [
        119.992,
        157.302,
        74.997,
        0.00784,
        0.00007,
        0.00370,
        0.00554,
        0.01109,
        0.04374,
        0.426,
        0.02182,
        0.03130,
        0.02971,
        0.06545,
        0.02211,
        21.033,
        0.414783,
        0.815285,
        -4.813031,
        0.266482,
        2.301442,
        0.284654,
    ]

    result = predict(
        sample_features
    )

    print(
        "\nPrediction Result\n"
    )

    for key, value in result.items():

        print(
            f"{key}: {value}"
        )
