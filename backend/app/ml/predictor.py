from pathlib import Path
from typing import Any, Dict, List, Sequence

import json
import math

import joblib
import numpy as np


# ==========================================================
# PATHS
# ==========================================================

BASE_MODEL_DIRECTORY = Path(
    "models"
)

FINAL_MODEL_PATH = (
    BASE_MODEL_DIRECTORY
    / "final_model.pkl"
)

FINAL_SCALER_PATH = (
    BASE_MODEL_DIRECTORY
    / "final_scaler.pkl"
)

FINAL_FEATURE_CONFIG_PATH = (
    BASE_MODEL_DIRECTORY
    / "final_feature_config.json"
)

FINAL_METADATA_PATH = (
    BASE_MODEL_DIRECTORY
    / "final_model_metadata.json"
)


# ==========================================================
# MODEL CONFIGURATION
# ==========================================================

EXTRACTED_FEATURE_COUNT = 22

PRODUCTION_FEATURE_COUNT = 12

DEFAULT_THRESHOLD = 0.45

HEALTHY_CLASS = 0

PARKINSON_CLASS = 1


# ==========================================================
# ALL 22 EXTRACTED FEATURES
# ==========================================================

ALL_FEATURE_NAMES = [
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
# FINAL 12 FEATURES
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
# FEATURE INDEX MAP
# ==========================================================

FEATURE_INDEX = {
    name: index
    for index, name in enumerate(
        ALL_FEATURE_NAMES
    )
}


# ==========================================================
# PREDICTOR
# ==========================================================

class Predictor:
    """
    Production Parkinson prediction engine.

    The predictor receives the 22 original voice features
    and converts them into the 12-feature representation
    required by the final model.
    """

    # ======================================================
    # INITIALIZATION
    # ======================================================

    def __init__(
        self,
        model_path: str = str(
            FINAL_MODEL_PATH
        ),
        scaler_path: str = str(
            FINAL_SCALER_PATH
        ),
        feature_config_path: str = str(
            FINAL_FEATURE_CONFIG_PATH
        ),
        threshold: float = DEFAULT_THRESHOLD,
    ):
        """
        Initialize the prediction engine.

        Parameters
        ----------
        model_path:
            Path to final_model.pkl.

        scaler_path:
            Path to final_scaler.pkl.

        feature_config_path:
            Path to final_feature_config.json.

        threshold:
            Parkinson decision threshold.
        """

        self.model_path = Path(
            model_path
        )

        self.scaler_path = Path(
            scaler_path
        )

        self.feature_config_path = Path(
            feature_config_path
        )

        self.model = None

        self.scaler = None

        self.feature_config = {}

        self.threshold = float(
            threshold
        )

        self.is_pipeline = False

        self.model_loaded = False

        self.scaler_loaded = False

        self._load_feature_configuration()

        self._load_model()

        self._load_scaler()

    # ======================================================
    # LOAD FEATURE CONFIGURATION
    # ======================================================

    def _load_feature_configuration(
        self,
    ) -> None:
        """
        Load final feature configuration.

        The configuration is validated against the
        hard-coded production feature order.
        """

        if not self.feature_config_path.exists():
            raise FileNotFoundError(
                "Final feature configuration not found: "
                f"{self.feature_config_path.resolve()}"
            )

        try:

            with open(
                self.feature_config_path,
                "r",
                encoding="utf-8",
            ) as file:

                configuration = json.load(
                    file
                )

        except json.JSONDecodeError as exc:

            raise ValueError(
                "Invalid final feature configuration JSON: "
                f"{self.feature_config_path.resolve()}"
            ) from exc

        if not isinstance(
            configuration,
            dict,
        ):
            raise ValueError(
                "Final feature configuration must "
                "contain a JSON object."
            )

        self.feature_config = (
            configuration
        )

        configured_features = (
            configuration.get(
                "features"
            )
        )

        if configured_features is None:

            configured_features = (
                configuration.get(
                    "feature_order"
                )
            )

        if configured_features is not None:

            if configured_features != (
                SELECTED_FEATURE_NAMES
            ):

                raise ValueError(
                    "Feature order mismatch.\n\n"
                    "Expected:\n"
                    f"{SELECTED_FEATURE_NAMES}\n\n"
                    "Configuration contains:\n"
                    f"{configured_features}"
                )

        configured_count = (
            configuration.get(
                "feature_count"
            )
        )

        if configured_count is not None:

            if int(
                configured_count
            ) != PRODUCTION_FEATURE_COUNT:

                raise ValueError(
                    "Final model configuration "
                    "does not contain exactly "
                    "12 features."
                )

        configured_threshold = (
            configuration.get(
                "decision_threshold"
            )
        )

        if configured_threshold is not None:

            self.threshold = float(
                configured_threshold
            )

        if not (
            0.0
            <
            self.threshold
            <
            1.0
        ):

            raise ValueError(
                "Decision threshold must be "
                "between 0 and 1."
            )

    # ======================================================
    # LOAD MODEL
    # ======================================================

    def _load_model(
        self,
    ) -> None:
        """
        Load final_model.pkl.
        """

        if not self.model_path.exists():

            raise FileNotFoundError(
                "Final prediction model not found: "
                f"{self.model_path.resolve()}"
            )

        try:

            self.model = joblib.load(
                self.model_path
            )

        except Exception as exc:

            raise RuntimeError(
                "Unable to load final prediction "
                f"model: {self.model_path.resolve()}"
            ) from exc

        if self.model is None:

            raise RuntimeError(
                "Loaded final model is None."
            )

        self.is_pipeline = (
            hasattr(
                self.model,
                "named_steps",
            )
            and hasattr(
                self.model,
                "predict",
            )
        )

        self.model_loaded = True

    # ======================================================
    # LOAD SCALER
    # ======================================================

    def _load_scaler(
        self,
    ) -> None:
        """
        Load final_scaler.pkl.

        The scaler is retained for compatibility.

        If final_model.pkl is already a Pipeline containing
        preprocessing, the scaler is NOT applied separately.
        """

        if not self.scaler_path.exists():

            raise FileNotFoundError(
                "Final scaler not found: "
                f"{self.scaler_path.resolve()}"
            )

        try:

            self.scaler = joblib.load(
                self.scaler_path
            )

        except Exception as exc:

            raise RuntimeError(
                "Unable to load final scaler: "
                f"{self.scaler_path.resolve()}"
            ) from exc

        self.scaler_loaded = (
            self.scaler is not None
        )

    # ======================================================
    # VALIDATE FEATURES
    # ======================================================

    def _validate_features(
        self,
        features: Sequence[float],
    ) -> List[float]:
        """
        Validate the incoming 22-feature vector.

        The audio feature service produces 22 features.
        """

        if features is None:

            raise ValueError(
                "Features cannot be None."
            )

        if isinstance(
            features,
            np.ndarray,
        ):

            features = (
                features.tolist()
            )

        if not isinstance(
            features,
            (list, tuple),
        ):

            raise ValueError(
                "Features must be a list "
                "or tuple of numeric values."
            )

        if len(features) != (
            EXTRACTED_FEATURE_COUNT
        ):

            raise ValueError(
                "Exactly "
                f"{EXTRACTED_FEATURE_COUNT} "
                "audio features are required. "
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
            ) as exc:

                raise ValueError(
                    "Feature "
                    f"{index + 1} is not numeric: "
                    f"{value}"
                ) from exc

            if not math.isfinite(
                numeric_value
            ):

                raise ValueError(
                    "Feature "
                    f"{index + 1} contains "
                    "NaN or infinite value."
                )

            validated.append(
                numeric_value
            )

        return validated

    # ======================================================
    # SELECT 12 FEATURES
    # ======================================================

    def _select_production_features(
        self,
        features: List[float],
    ) -> np.ndarray:
        """
        Convert 22 extracted features into the exact
        12-feature production vector.

        IMPORTANT:
        The order here must NEVER be changed unless the
        final model is retrained with a different order.
        """

        selected = []

        for feature_name in (
            SELECTED_FEATURE_NAMES
        ):

            index = FEATURE_INDEX.get(
                feature_name
            )

            if index is None:

                raise RuntimeError(
                    "Unknown production feature: "
                    f"{feature_name}"
                )

            selected.append(
                features[index]
            )

        array = np.asarray(
            selected,
            dtype=np.float64,
        )

        if array.shape != (
            PRODUCTION_FEATURE_COUNT,
        ):

            raise RuntimeError(
                "Production feature vector "
                "does not contain exactly "
                "12 values."
            )

        return array

    # ======================================================
    # PREPARE INPUT
    # ======================================================

    def _prepare_input(
        self,
        features: List[float],
    ) -> np.ndarray:
        """
        Prepare 12-feature model input.
        """

        validated = (
            self._validate_features(
                features
            )
        )

        selected = (
            self._select_production_features(
                validated
            )
        )

        return selected.reshape(
            1,
            PRODUCTION_FEATURE_COUNT,
        )

    # ======================================================
    # MODEL INPUT
    # ======================================================

    def _model_input(
        self,
        prepared_features: np.ndarray,
    ) -> np.ndarray:
        """
        Apply preprocessing when required.

        Step 9 final_model.pkl is a Pipeline containing:

            SimpleImputer
            StandardScaler
            HistGradientBoosting

        Therefore applying final_scaler.pkl again would
        incorrectly double-scale the data.

        If a plain classifier is supplied instead, the
        separately saved scaler is applied.
        """

        if self.is_pipeline:

            return prepared_features

        if self.scaler is None:

            raise RuntimeError(
                "Model is not a pipeline and "
                "final scaler is unavailable."
            )

        try:

            return self.scaler.transform(
                prepared_features
            )

        except Exception as exc:

            raise RuntimeError(
                "Failed to transform "
                "12-feature input using "
                "final scaler."
            ) from exc

    # ======================================================
    # PREDICT PROBABILITY
    # ======================================================

    def _parkinson_probability(
        self,
        prepared_features: np.ndarray,
    ) -> float:
        """
        Return probability of Parkinson class.
        """

        model_input = (
            self._model_input(
                prepared_features
            )
        )

        if not hasattr(
            self.model,
            "predict_proba",
        ):

            raise RuntimeError(
                "Final model does not provide "
                "predict_proba()."
            )

        try:

            probabilities = (
                self.model.predict_proba(
                    model_input
                )
            )

        except Exception as exc:

            raise RuntimeError(
                "Final model probability "
                "prediction failed."
            ) from exc

        probabilities = np.asarray(
            probabilities
        )

        if probabilities.ndim != 2:

            raise RuntimeError(
                "Unexpected probability "
                "output shape: "
                f"{probabilities.shape}"
            )

        if probabilities.shape[0] != 1:

            raise RuntimeError(
                "Expected exactly one "
                "prediction."
            )

        # --------------------------------------------------
        # Binary classification.
        #
        # Normally:
        #
        # probability[:, 0] = HC
        # probability[:, 1] = PD
        #
        # We explicitly handle class ordering below.
        # --------------------------------------------------

        classes = getattr(
            self.model,
            "classes_",
            None,
        )

        if classes is None and hasattr(
            self.model,
            "named_steps",
        ):

            final_model = (
                self.model.named_steps.get(
                    "model"
                )
            )

            classes = getattr(
                final_model,
                "classes_",
                None,
            )

        if classes is None:

            if probabilities.shape[1] != 2:

                raise RuntimeError(
                    "Unable to determine "
                    "binary model classes."
                )

            return float(
                probabilities[0, 1]
            )

        classes = list(
            classes
        )

        try:

            pd_index = classes.index(
                PARKINSON_CLASS
            )

        except ValueError as exc:

            raise RuntimeError(
                "Final model does not contain "
                "Parkinson class 1."
            ) from exc

        probability = float(
            probabilities[
                0,
                pd_index,
            ]
        )

        if not (
            0.0
            <= probability
            <= 1.0
        ):

            raise RuntimeError(
                "Model returned an invalid "
                f"Parkinson probability: "
                f"{probability}"
            )

        return probability

    # ======================================================
    # PREDICT CLASS USING THRESHOLD
    # ======================================================

    def _predict_class(
        self,
        parkinson_probability: float,
    ) -> int:
        """
        Convert probability to class using Step 8
        decision threshold.
        """

        if (
            parkinson_probability
            >= self.threshold
        ):

            return PARKINSON_CLASS

        return HEALTHY_CLASS

    # ======================================================
    # CONFIDENCE
    # ======================================================

    def _confidence(
        self,
        parkinson_probability: float,
    ) -> float:
        """
        Confidence is the probability of the selected
        class.

        For PD:
            confidence = PD probability

        For HC:
            confidence = HC probability
        """

        if (
            parkinson_probability
            >= self.threshold
        ):

            return float(
                parkinson_probability
            )

        return float(
            1.0
            -
            parkinson_probability
        )

    # ======================================================
    # DIAGNOSIS
    # ======================================================

    def _diagnosis(
        self,
        prediction: int,
    ) -> str:
        """
        Convert numeric class to diagnosis label.
        """

        if (
            int(prediction)
            ==
            PARKINSON_CLASS
        ):

            return (
                "Parkinson's Disease"
            )

        return (
            "Healthy Control"
        )

    # ======================================================
    # RISK LEVEL
    # ======================================================

    def _risk_level(
        self,
        risk_score: float,
    ) -> str:
        """
        Convert Parkinson probability into a simple
        risk category.

        This is an application-level classification,
        not a clinical diagnosis.
        """

        if risk_score < 30.0:

            return "Low"

        if risk_score < 60.0:

            return "Moderate"

        if risk_score < 80.0:

            return "High"

        return "Very High"

    # ======================================================
    # RECOMMENDATION
    # ======================================================

    def _recommendation(
        self,
        prediction: int,
        risk_score: float,
    ) -> str:
        """
        Generate a safe application recommendation.
        """

        if (
            prediction
            ==
            PARKINSON_CLASS
        ):

            return (
                "The voice analysis indicates "
                "an elevated Parkinson's disease "
                "risk. Please consult a qualified "
                "healthcare professional for "
                "clinical evaluation. This result "
                "is not a diagnosis."
            )

        return (
            "The voice analysis does not indicate "
            "an elevated Parkinson's disease risk "
            "based on this model. If you have "
            "symptoms or concerns, consult a "
            "qualified healthcare professional. "
            "This result is not a diagnosis."
        )

    # ======================================================
    # MAIN PREDICTION
    # ======================================================

    def predict(
        self,
        features: List[float],
    ) -> Dict[str, Any]:
        """
        Run a complete Parkinson prediction.

        Input:
            22 extracted voice features.

        Output:
            Structured prediction dictionary.
        """

        # --------------------------------------------------
        # Prepare 22 -> 12
        # --------------------------------------------------

        prepared_features = (
            self._prepare_input(
                features
            )
        )

        # --------------------------------------------------
        # Probability
        # --------------------------------------------------

        parkinson_probability = (
            self._parkinson_probability(
                prepared_features
            )
        )

        # --------------------------------------------------
        # Threshold decision
        # --------------------------------------------------

        prediction = (
            self._predict_class(
                parkinson_probability
            )
        )

        # --------------------------------------------------
        # Confidence
        # --------------------------------------------------

        confidence = (
            self._confidence(
                parkinson_probability
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

        healthy_probability = (
            1.0
            -
            parkinson_probability
        )

        healthy_score = (
            healthy_probability
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
        # Return
        # --------------------------------------------------

        return {
            "prediction":
                diagnosis,

            "prediction_value":
                int(
                    prediction
                ),

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
                    healthy_score,
                    2,
                ),

            "decision_threshold":
                round(
                    self.threshold,
                    4,
                ),

            "recommendation":
                recommendation,

            "model":
                self._model_name(),

            "model_path":
                str(
                    self.model_path
                ),

            "features_extracted":
                EXTRACTED_FEATURE_COUNT,

            "features_used":
                PRODUCTION_FEATURE_COUNT,

            "selected_features":
                SELECTED_FEATURE_NAMES.copy(),

            "model_type":
                (
                    "pipeline"
                    if self.is_pipeline
                    else "classifier"
                ),
        }

    # ======================================================
    # MODEL NAME
    # ======================================================

    def _model_name(
        self,
    ) -> str:
        """
        Return underlying model name.
        """

        if hasattr(
            self.model,
            "named_steps",
        ):

            model_step = (
                self.model.named_steps.get(
                    "model"
                )
            )

            if model_step is not None:

                return (
                    model_step.__class__.__name__
                )

        return (
            self.model.__class__.__name__
        )

    # ======================================================
    # BATCH PREDICTION
    # ======================================================

    def predict_batch(
        self,
        dataset,
    ):
        """
        Predict multiple samples.

        Accepted input:
            - pandas DataFrame
            - list of 22-feature lists
            - numpy array

        If a DataFrame contains the 22 named audio
        features, they are converted using the same
        production feature order.
        """

        # --------------------------------------------------
        # Pandas DataFrame
        # --------------------------------------------------

        try:

            import pandas as pd

        except ImportError:

            pd = None

        if (
            pd is not None
            and isinstance(
                dataset,
                pd.DataFrame,
            )
        ):

            missing = [
                feature
                for feature in ALL_FEATURE_NAMES
                if feature not in dataset.columns
            ]

            if missing:

                raise ValueError(
                    "Batch dataframe is missing "
                    "required features: "
                    + ", ".join(
                        missing
                    )
                )

            rows = (
                dataset[
                    ALL_FEATURE_NAMES
                ]
                .values
                .tolist()
            )

        else:

            if isinstance(
                dataset,
                np.ndarray,
            ):

                dataset = (
                    dataset.tolist()
                )

            if not isinstance(
                dataset,
                (list, tuple),
            ):

                raise ValueError(
                    "Batch dataset must be "
                    "a DataFrame, list, tuple, "
                    "or numpy array."
                )

            rows = dataset

        results = []

        for row in rows:

            results.append(
                self.predict(
                    row
                )
            )

        return results

    # ======================================================
    # MODEL INFORMATION
    # ======================================================

    def model_information(
        self,
    ) -> Dict[str, Any]:
        """
        Return model and production configuration.
        """

        return {
            "status":
                "loaded"
                if self.model_loaded
                else "not_loaded",

            "model":
                self._model_name()
                if self.model is not None
                else None,

            "model_path":
                str(
                    self.model_path.resolve()
                ),

            "scaler_path":
                str(
                    self.scaler_path.resolve()
                ),

            "feature_config_path":
                str(
                    self.feature_config_path.resolve()
                ),

            "features_extracted":
                EXTRACTED_FEATURE_COUNT,

            "features_used":
                PRODUCTION_FEATURE_COUNT,

            "selected_features":
                SELECTED_FEATURE_NAMES.copy(),

            "decision_threshold":
                self.threshold,

            "healthy_class":
                HEALTHY_CLASS,

            "parkinson_class":
                PARKINSON_CLASS,

            "pipeline":
                self.is_pipeline,

            "scaler_loaded":
                self.scaler_loaded,

            "model_loaded":
                self.model_loaded,

            "production_candidate":
                True,
        }

    # ======================================================
    # HEALTH
    # ======================================================

    def health(
        self,
    ) -> Dict[str, Any]:
        """
        Verify that the prediction engine is ready.
        """

        healthy = (
            self.model_loaded
            and self.scaler_loaded
            and self.model is not None
        )

        return {
            "status":
                "healthy"
                if healthy
                else "unhealthy",

            "model_loaded":
                self.model_loaded,

            "scaler_loaded":
                self.scaler_loaded,

            "model":
                self._model_name()
                if self.model is not None
                else None,

            "features_extracted":
                EXTRACTED_FEATURE_COUNT,

            "features_used":
                PRODUCTION_FEATURE_COUNT,

            "threshold":
                self.threshold,

            "model_path_exists":
                self.model_path.exists(),

            "scaler_path_exists":
                self.scaler_path.exists(),

            "feature_config_exists":
                self.feature_config_path.exists(),
        }


# ==========================================================
# HIGH-LEVEL PREDICTOR
# ==========================================================

class ParkinsonPredictor:
    """
    High-level prediction interface.

    This class preserves compatibility with the existing
    application code.
    """

    # ======================================================
    # INITIALIZATION
    # ======================================================

    def __init__(
        self,
    ):

        self.predictor = (
            Predictor()
        )

    # ======================================================
    # PREDICT
    # ======================================================

    def predict(
        self,
        features: List[float],
    ) -> Dict[str, Any]:
        """
        Predict Parkinson disease from 22 voice features.
        """

        return (
            self.predictor.predict(
                features
            )
        )

    # ======================================================
    # BATCH
    # ======================================================

    def predict_batch(
        self,
        dataset,
    ):

        return (
            self.predictor.predict_batch(
                dataset
            )
        )

    # ======================================================
    # MODEL INFORMATION
    # ======================================================

    def model_info(
        self,
    ):

        return (
            self.predictor.model_information()
        )

    # ======================================================
    # HEALTH
    # ======================================================

    def health(
        self,
    ):

        return (
            self.predictor.health()
        )


# ==========================================================
# GLOBAL PREDICTOR
# ==========================================================

predictor = (
    Predictor()
)


# ==========================================================
# CONVENIENCE FUNCTION
# ==========================================================

def predict(
    features: List[float],
) -> Dict[str, Any]:
    """
    Convenience prediction function.

    Example
    -------
    result = predict(features)
    """

    return (
        predictor.predict(
            features
        )
    )


# ==========================================================
# MAIN TEST
# ==========================================================

if __name__ == "__main__":

    print()

    print(
        "=" * 70
    )

    print(
        "PREDICTOR STEP 10 SELF TEST"
    )

    print(
        "=" * 70
    )

    print()

    try:

        test_predictor = (
            Predictor()
        )

        # --------------------------------------------------
        # Display health
        # --------------------------------------------------

        health = (
            test_predictor.health()
        )

        print(
            "HEALTH"
        )

        print(
            "-" * 70
        )

        for key, value in (
            health.items()
        ):

            print(
                f"{key}: {value}"
            )

        print()

        # --------------------------------------------------
        # Display model information
        # --------------------------------------------------

        information = (
            test_predictor.model_information()
        )

        print(
            "MODEL INFORMATION"
        )

        print(
            "-" * 70
        )

        print(
            f"Model: "
            f"{information['model']}"
        )

        print(
            f"Features extracted: "
            f"{information['features_extracted']}"
        )

        print(
            f"Features used: "
            f"{information['features_used']}"
        )

        print(
            f"Threshold: "
            f"{information['decision_threshold']}"
        )

        print()

        # --------------------------------------------------
        # Sample 22-feature vector
        # --------------------------------------------------

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

        print(
            "PREDICTION TEST"
        )

        print(
            "-" * 70
        )

        result = (
            test_predictor.predict(
                sample_features
            )
        )

        for key, value in (
            result.items()
        ):

            print(
                f"{key}: {value}"
            )

        print()

        print(
            "=" * 70
        )

        print(
            "PREDICTOR SELF TEST COMPLETE"
        )

        print(
            "=" * 70
        )

    except Exception as exc:

        print()

        print(
            "=" * 70
        )

        print(
            "PREDICTOR SELF TEST FAILED"
        )

        print(
            "=" * 70
        )

        print(
            str(exc)
        )

        print(
            "=" * 70
        )

        raise
