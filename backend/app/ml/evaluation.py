"""
Model Evaluation Module

Provides evaluation metrics and visualizations for the
Parkinson Disease Detection model.
"""

from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    ConfusionMatrixDisplay,
    RocCurveDisplay,
    classification_report,
)


class ModelEvaluator:
    """
    Evaluate trained machine learning models.
    """

    def __init__(
        self,
        model_path: str = "models/model.pkl",
    ):

        self.model_path = Path(model_path)
        self.model = self.load_model()

    # =====================================================
    # Load Model
    # =====================================================

    def load_model(self):

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model not found: {self.model_path}"
            )

        return joblib.load(self.model_path)

    # =====================================================
    # Evaluate Model
    # =====================================================

    def evaluate(
        self,
        X_test,
        y_test,
    ) -> dict:
        """
        Compute evaluation metrics.
        """

        predictions = self.model.predict(X_test)

        metrics = {
            "accuracy": accuracy_score(
                y_test,
                predictions,
            ),
            "precision": precision_score(
                y_test,
                predictions,
            ),
            "recall": recall_score(
                y_test,
                predictions,
            ),
            "f1_score": f1_score(
                y_test,
                predictions,
            ),
        }

        if hasattr(self.model, "predict_proba"):

            probabilities = self.model.predict_proba(
                X_test
            )[:, 1]

            metrics["roc_auc"] = roc_auc_score(
                y_test,
                probabilities,
            )

        return metrics

    # =====================================================
    # Classification Report
    # =====================================================

    def classification_report(
        self,
        X_test,
        y_test,
    ) -> dict:
        """
        Return classification report.
        """

        predictions = self.model.predict(
            X_test
        )

        return classification_report(
            y_test,
            predictions,
            output_dict=True,
        )

    # =====================================================
    # Confusion Matrix
    # =====================================================

    def confusion_matrix(
        self,
        X_test,
        y_test,
    ):
        """
        Generate confusion matrix.
        """

        predictions = self.model.predict(
            X_test
        )

        cm = confusion_matrix(
            y_test,
            predictions,
        )

        disp = ConfusionMatrixDisplay(
            confusion_matrix=cm
        )

        disp.plot()

        plt.title(
            "Confusion Matrix"
        )

        plt.show()

        return cm

    # =====================================================
    # ROC Curve
    # =====================================================

    def roc_curve(
        self,
        X_test,
        y_test,
    ):
        """
        Plot ROC curve.
        """

        if not hasattr(
            self.model,
            "predict_proba",
        ):
            return None

        RocCurveDisplay.from_estimator(
            self.model,
            X_test,
            y_test,
        )

        plt.title(
            "ROC Curve"
        )

        plt.show()

    # =====================================================
    # Feature Importance
    # =====================================================

    def feature_importance(
        self,
        feature_names,
    ) -> pd.DataFrame:
        """
        Return feature importance.
        """

        if not hasattr(
            self.model,
            "feature_importances_",
        ):
            return pd.DataFrame()

        importance = pd.DataFrame(
            {
                "Feature": feature_names,
                "Importance":
                    self.model.feature_importances_,
            }
        )

        importance = importance.sort_values(
            by="Importance",
            ascending=False,
        )

        return importance

    # =====================================================
    # Plot Feature Importance
    # =====================================================

    def plot_feature_importance(
        self,
        feature_names,
    ):
        """
        Plot feature importance.
        """

        importance = self.feature_importance(
            feature_names
        )

        if importance.empty:
            return

        plt.figure(figsize=(10, 6))

        plt.barh(
            importance["Feature"],
            importance["Importance"],
        )

        plt.title(
            "Feature Importance"
        )

        plt.xlabel(
            "Importance"
        )

        plt.gca().invert_yaxis()

        plt.tight_layout()

        plt.show()

    # =====================================================
    # Compare Models
    # =====================================================

    def compare_models(
        self,
        models: dict,
        X_test,
        y_test,
    ) -> pd.DataFrame:
        """
        Compare multiple models.
        """

        rows = []

        for name, model in models.items():

            predictions = model.predict(
                X_test
            )

            rows.append(
                {
                    "Model": name,
                    "Accuracy": accuracy_score(
                        y_test,
                        predictions,
                    ),
                    "Precision": precision_score(
                        y_test,
                        predictions,
                    ),
                    "Recall": recall_score(
                        y_test,
                        predictions,
                    ),
                    "F1 Score": f1_score(
                        y_test,
                        predictions,
                    ),
                }
            )

        return pd.DataFrame(rows)

    # =====================================================
    # Save Metrics
    # =====================================================

    def save_metrics(
        self,
        metrics: dict,
        output_path="evaluation_metrics.csv",
    ):
        """
        Save metrics to CSV.
        """

        df = pd.DataFrame(
            [metrics]
        )

        df.to_csv(
            output_path,
            index=False,
        )

        return output_path
