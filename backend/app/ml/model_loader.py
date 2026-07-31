"""
Model Loader

Loads and manages trained machine learning artifacts.
"""

from pathlib import Path
from typing import Any, Optional

import joblib


class ModelLoader:
    """
    Singleton-like loader for model and scaler.
    """

    _model: Optional[Any] = None
    _scaler: Optional[Any] = None

    def __init__(
        self,
        model_path: str | Path = "models/model.pkl",
        scaler_path: str | Path = "models/scaler.pkl",
    ):
        self.model_path = Path(model_path)
        self.scaler_path = Path(scaler_path)

    # =====================================================
    # Load Model
    # =====================================================

    def load_model(self):
        """
        Load trained model.
        """

        if ModelLoader._model is None:

            if not self.model_path.exists():
                raise FileNotFoundError(
                    f"Model not found: {self.model_path}"
                )

            ModelLoader._model = joblib.load(
                self.model_path
            )

        return ModelLoader._model

    # =====================================================
    # Load Scaler
    # =====================================================

    def load_scaler(self):
        """
        Load trained scaler.
        """

        if ModelLoader._scaler is None:

            if not self.scaler_path.exists():
                raise FileNotFoundError(
                    f"Scaler not found: {self.scaler_path}"
                )

            ModelLoader._scaler = joblib.load(
                self.scaler_path
            )

        return ModelLoader._scaler

    # =====================================================
    # Load All
    # =====================================================

    def load(self):
        """
        Load both model and scaler.
        """

        return (
            self.load_model(),
            self.load_scaler(),
        )

    # =====================================================
    # Reload
    # =====================================================

    def reload(self):
        """
        Force reload artifacts from disk.
        """

        ModelLoader._model = None
        ModelLoader._scaler = None

        return self.load()

    # =====================================================
    # Model Metadata
    # =====================================================

    def model_info(self):
        """
        Return basic information about the model.
        """

        model = self.load_model()

        return {
            "model_name": model.__class__.__name__,
            "model_path": str(self.model_path),
            "scaler_path": str(self.scaler_path),
            "loaded": True,
        }

    # =====================================================
    # Availability Check
    # =====================================================

    def is_ready(self) -> bool:
        """
        Check if required artifacts exist.
        """

        return (
            self.model_path.exists()
            and self.scaler_path.exists()
        )

    # =====================================================
    # Unload
    # =====================================================

    def unload(self):
        """
        Clear cached objects.
        """

        ModelLoader._model = None
        ModelLoader._scaler = None

    # =====================================================
    # Get Cached Objects
    # =====================================================

    @property
    def model(self):
        """
        Return cached model.
        """

        return self.load_model()

    @property
    def scaler(self):
        """
        Return cached scaler.
        """

        return self.load_scaler()
