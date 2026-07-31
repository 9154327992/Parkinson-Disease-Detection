"""
Prediction Entry Point

Provides a simple interface for making Parkinson disease
predictions using the trained machine learning model.
"""

from typing import Dict, List

from app.ml.predictor import Predictor


class ParkinsonPredictor:
    """
    High-level prediction interface.
    """

    def __init__(self):
        """
        Initialize predictor.
        """
        self.predictor = Predictor()

    # =====================================================
    # Predict
    # =====================================================

    def predict(
        self,
        features: List[float],
    ) -> Dict:
        """
        Predict Parkinson disease.

        Parameters
        ----------
        features : List[float]
            List containing the 22 voice features.

        Returns
        -------
        Dict
            Prediction result.
        """

        return self.predictor.predict(features)

    # =====================================================
    # Predict Batch
    # =====================================================

    def predict_batch(
        self,
        dataset,
    ):
        """
        Predict multiple samples.
        """

        return self.predictor.predict_batch(dataset)

    # =====================================================
    # Model Information
    # =====================================================

    def model_info(self):
        """
        Return model information.
        """

        return self.predictor.model_information()

    # =====================================================
    # Health Check
    # =====================================================

    def health(self):
        """
        Verify prediction engine.
        """

        return self.predictor.health()


# ==========================================================
# Convenience Function
# ==========================================================

def predict(features: List[float]) -> Dict:
    """
    Convenience function for prediction.

    Example
    -------
    result = predict(features)
    """

    predictor = ParkinsonPredictor()

    return predictor.predict(features)


# ==========================================================
# Example Usage
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

    predictor = ParkinsonPredictor()

    result = predictor.predict(sample_features)

    print("\nPrediction Result\n")

    for key, value in result.items():
        print(f"{key}: {value}")
