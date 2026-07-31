"""
Preprocessing Module

Handles preprocessing of Parkinson voice features before
training and prediction.
"""

from pathlib import Path
from typing import List, Union

import joblib
import numpy as np

# ==========================================================
# Constants
# ==========================================================

TOTAL_FEATURES = 22


# ==========================================================
# Preprocessor
# ==========================================================

class Preprocessor:
    """
    Handles preprocessing of feature vectors.
    """

    def __init__(
        self,
        scaler_path: Union[str, Path] = "models/scaler.pkl",
    ):
        """
        Initialize the preprocessor.
        """

        self.scaler_path = Path(scaler_path)
        self.scaler = self._load_scaler()

    # ======================================================
    # Load Scaler
    # ======================================================

    def _load_scaler(self):
        """
        Load trained scaler.
        """

        if not self.scaler_path.exists():
            raise FileNotFoundError(
                f"Scaler not found: {self.scaler_path}"
            )

        return joblib.load(self.scaler_path)

    # ======================================================
    # Validate Features
    # ======================================================

    def validate_features(
        self,
        features: List[float],
    ) -> None:
        """
        Validate input features.
        """

        if len(features) != TOTAL_FEATURES:
            raise ValueError(
                f"Expected {TOTAL_FEATURES} features, "
                f"received {len(features)}."
            )

    # ======================================================
    # Convert to NumPy
    # ======================================================

    def to_numpy(
        self,
        features: List[float],
    ) -> np.ndarray:
        """
        Convert list to NumPy array.
        """

        self.validate_features(features)

        return np.asarray(
            features,
            dtype=np.float64,
        ).reshape(1, -1)

    # ======================================================
    # Scale Features
    # ======================================================

    def scale(
        self,
        features: List[float],
    ) -> np.ndarray:
        """
        Scale feature vector.
        """

        data = self.to_numpy(features)

        return self.scaler.transform(data)

    # ======================================================
    # Inverse Transform
    # ======================================================

    def inverse_scale(
        self,
        scaled_features: np.ndarray,
    ) -> np.ndarray:
        """
        Reverse scaling.
        """

        return self.scaler.inverse_transform(
            scaled_features
        )

    # ======================================================
    # Fit Scaler
    # ======================================================

    def fit(
        self,
        data: np.ndarray,
    ):
        """
        Fit scaler.

        Used during training only.
        """

        self.scaler.fit(data)

    # ======================================================
    # Fit & Transform
    # ======================================================

    def fit_transform(
        self,
        data: np.ndarray,
    ) -> np.ndarray:
        """
        Fit and scale training data.
        """

        return self.scaler.fit_transform(data)

    # ======================================================
    # Transform Dataset
    # ======================================================

    def transform(
        self,
        data: np.ndarray,
    ) -> np.ndarray:
        """
        Scale dataset.
        """

        return self.scaler.transform(data)

    # ======================================================
    # Save Scaler
    # ======================================================

    def save(
        self,
        output_path: Union[str, Path] = None,
    ):
        """
        Save trained scaler.
        """

        path = Path(output_path or self.scaler_path)

        joblib.dump(
            self.scaler,
            path,
        )
