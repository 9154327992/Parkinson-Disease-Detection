"""
Prediction Engine

Runs Parkinson disease prediction using the trained model.
"""

from typing import Dict, List

import numpy as np

from app.ml.model_loader import ModelLoader
from app.ml.preprocessing import Preprocessor


class Predictor:
    """
    Parkinson Disease Predictor.
    """

    def __init__(self):
        """
        Initialize predictor.
        """

        self.loader = ModelLoader()
        self.preprocessor = Preprocessor()

        self.model = self.loader.model
        self.scaler = self.loader.scaler

    # =====================================================
    # Predict
    # =====================================================

    def predict(
        self,
        features: List[float],
    ) -> Dict:
        """
        Predict Parkinson disease.
        """

        scaled = self.preprocessor.scale(features)

        prediction = int(
            self.model.predict(scaled)[0]
        )

        probability = self._probability(
            scaled,
            prediction,
        )

        return {
            "prediction": prediction,
            "label": self._label(prediction),
            "probability": round(probability, 4),
            "confidence": round(probability * 100, 2),
            "risk_level": self._risk_level(probability),
        }

    # =====================================================
    # Predict Batch
    # =====================================================

    def predict_batch(
        self,
        dataset: np.ndarray,
    ) -> List[Dict]:
        """
        Predict multiple samples.
        """

        scaled = self.scaler.transform(dataset)

        predictions = self.model.predict(scaled)

        probabilities = self._batch_probability(
            scaled,
            predictions,
        )

        results = []

        for pred, prob in zip(
            predictions,
            probabilities,
        ):

            results.append(
                {
                    "prediction": int(pred),
                    "label": self._label(int(pred)),
                    "confidence": round(prob * 100, 2),
                    "risk_level": self._risk_level(prob),
                }
            )

        return results

    # =====================================================
    # Probability
    # =====================================================

    def _probability(
        self,
        sample,
        prediction: int,
    ) -> float:
        """
        Return prediction probability.
        """

        if hasattr(
            self.model,
            "predict_proba",
        ):

            return float(
                self.model.predict_proba(sample)[0][prediction]
            )

        return 1.0

    # =====================================================
    # Batch Probability
    # =====================================================

    def _batch_probability(
        self,
        samples,
        predictions,
    ) -> List[float]:
        """
        Batch probabilities.
        """

        if hasattr(
            self.model,
            "predict_proba",
        ):

            probs = self.model.predict_proba(samples)

            return [
                float(probs[i][pred])
                for i, pred in enumerate(predictions)
            ]

        return [1.0] * len(predictions)

    # =====================================================
    # Risk Level
    # =====================================================

    def _risk_level(
        self,
        probability: float,
    ) -> str:
        """
        Determine risk level.
        """

        if probability >= 0.90:
            return "High Risk"

        if probability >= 0.70:
            return "Moderate Risk"

        if probability >= 0.50:
            return "Low Risk"

        return "Minimal Risk"

    # =====================================================
    # Label
    # =====================================================

    def _label(
        self,
        prediction: int,
    ) -> str:
        """
        Human-readable label.
        """

        return (
            "Parkinson Detected"
            if prediction == 1
            else "Healthy"
        )

    # =====================================================
    # Explain Prediction
    # =====================================================

    def explain(
        self,
        prediction: int,
        probability: float,
    ) -> str:
        """
        Generate a simple explanation.
        """

        if prediction == 1:

            return (
                f"The model detected voice patterns associated "
                f"with Parkinson disease with approximately "
                f"{probability * 100:.2f}% confidence. "
                "This result is a screening prediction and "
                "should be confirmed through clinical evaluation."
            )

        return (
            f"The analyzed voice features were more consistent "
            f"with the healthy class, with approximately "
            f"{probability * 100:.2f}% confidence. "
            "This prediction is not a medical diagnosis."
        )

    # =====================================================
    # Model Information
    # =====================================================

    def model_information(self):
        """
        Return model metadata.
        """

        return self.loader.model_info()

    # =====================================================
    # Health Check
    # =====================================================

    def health(self):
        """
        Verify prediction engine.
        """

        return {
            "model_loaded": self.model is not None,
            "scaler_loaded": self.scaler is not None,
            "status": "Ready",
        }
