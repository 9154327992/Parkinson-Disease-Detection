"""
Model Training Module

Trains the Parkinson Disease Detection model and
saves the trained model and scaler.
"""

from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split

from app.ml.feature_engineering import FeatureEngineering
from app.ml.preprocessing import Preprocessor


class ModelTrainer:
    """
    Train Parkinson Disease Detection model.
    """

    def __init__(
        self,
        dataset_path: str = "datasets/parkinsons.csv",
        model_path: str = "models/model.pkl",
        scaler_path: str = "models/scaler.pkl",
    ):

        self.dataset_path = Path(dataset_path)
        self.model_path = Path(model_path)
        self.scaler_path = Path(scaler_path)

        self.feature_engineering = FeatureEngineering()
        self.preprocessor = Preprocessor(
            scaler_path=self.scaler_path
        )

        self.model = RandomForestClassifier(
            n_estimators=200,
            random_state=42,
        )

    # =====================================================
    # Load Dataset
    # =====================================================

    def load_dataset(self) -> pd.DataFrame:

        if not self.dataset_path.exists():
            raise FileNotFoundError(
                f"Dataset not found: {self.dataset_path}"
            )

        return pd.read_csv(self.dataset_path)

    # =====================================================
    # Prepare Dataset
    # =====================================================

    def prepare_data(self):

        dataframe = self.load_dataset()

        dataframe = self.feature_engineering.fill_missing(
            dataframe
        )

        X, y = (
            self.feature_engineering.prepare_training_data(
                dataframe
            )
        )

        return train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=42,
            stratify=y,
        )

    # =====================================================
    # Train Model
    # =====================================================

    def train(self):

        (
            X_train,
            X_test,
            y_train,
            y_test,
        ) = self.prepare_data()

        X_train_scaled = (
            self.preprocessor.fit_transform(
                X_train.values
            )
        )

        X_test_scaled = (
            self.preprocessor.transform(
                X_test.values
            )
        )

        self.model.fit(
            X_train_scaled,
            y_train,
        )

        predictions = self.model.predict(
            X_test_scaled
        )

        metrics = {
            "accuracy": accuracy_score(
                y_test,
                predictions,
            ),
            "classification_report":
                classification_report(
                    y_test,
                    predictions,
                    output_dict=True,
                ),
            "confusion_matrix":
                confusion_matrix(
                    y_test,
                    predictions,
                ).tolist(),
        }

        return metrics

    # =====================================================
    # Save Artifacts
    # =====================================================

    def save(self):

        self.model_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.scaler_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        joblib.dump(
            self.model,
            self.model_path,
        )

        self.preprocessor.save(
            self.scaler_path
        )

    # =====================================================
    # Train + Save
    # =====================================================

    def train_and_save(self):

        metrics = self.train()

        self.save()

        return metrics

    # =====================================================
    # Feature Importance
    # =====================================================

    def feature_importance(self):

        return (
            self.feature_engineering.feature_importance(
                self.model,
                self.load_dataset(),
            )
        )

    # =====================================================
    # Model Information
    # =====================================================

    def model_information(self):

        return {
            "algorithm":
                self.model.__class__.__name__,
            "dataset":
                str(self.dataset_path),
            "model_path":
                str(self.model_path),
            "scaler_path":
                str(self.scaler_path),
            "features":
                self.feature_engineering.total_features(),
        }


# =========================================================
# Standalone Training
# =========================================================

if __name__ == "__main__":

    trainer = ModelTrainer()

    metrics = trainer.train_and_save()

    print("\nTraining Complete\n")

    print(
        f"Accuracy : {metrics['accuracy']:.4f}"
    )

    print(
        "\nModel saved successfully."
    )
