from pathlib import Path
from typing import Dict, List

import json
import warnings

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import (
    HistGradientBoostingClassifier,
)

from sklearn.impute import (
    SimpleImputer,
)

from sklearn.pipeline import (
    Pipeline,
)

from sklearn.preprocessing import (
    StandardScaler,
)

from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from sklearn.model_selection import (
    StratifiedKFold,
    cross_val_predict,
)

from sklearn.base import (
    clone,
)


warnings.filterwarnings(
    "ignore"
)


# ==========================================================
# CONSTANTS
# ==========================================================

TARGET_COLUMN = "status"

HEALTHY = 0

PARKINSON = 1

RANDOM_STATE = 42

DECISION_THRESHOLD = 0.45

DATASET_PATH = (
    "models/audio_training_features.csv"
)

SELECTED_FEATURES_PATH = (
    "models/selected_features.json"
)

BEST_MODEL_PATH = (
    "models/best_model_configuration.json"
)

OUTPUT_DIRECTORY = (
    "models"
)

FINAL_MODEL_PATH = (
    "models/final_model.pkl"
)

FINAL_SCALER_PATH = (
    "models/final_scaler.pkl"
)

FINAL_METADATA_PATH = (
    "models/final_model_metadata.json"
)

FINAL_FEATURE_CONFIG_PATH = (
    "models/final_feature_config.json"
)

FINAL_REPORT_PATH = (
    "models/final_training_report.json"
)

FINAL_TEXT_REPORT_PATH = (
    "models/final_training_report.txt"
)


# ==========================================================
# FINAL MODEL TRAINER
# ==========================================================

class FinalModelTrainer:
    """
    Train the final production candidate.

    The model is trained on the complete dataset after
    validation and threshold optimization have finished.
    """

    # ======================================================
    # INITIALIZATION
    # ======================================================

    def __init__(
        self,
        dataset_path: str = DATASET_PATH,
        selected_features_path: str = (
            SELECTED_FEATURES_PATH
        ),
        best_model_path: str = (
            BEST_MODEL_PATH
        ),
        output_directory: str = (
            OUTPUT_DIRECTORY
        ),
        final_model_path: str = (
            FINAL_MODEL_PATH
        ),
        final_scaler_path: str = (
            FINAL_SCALER_PATH
        ),
        threshold: float = (
            DECISION_THRESHOLD
        ),
        random_state: int = (
            RANDOM_STATE
        ),
    ):

        self.dataset_path = Path(
            dataset_path
        )

        self.selected_features_path = Path(
            selected_features_path
        )

        self.best_model_path = Path(
            best_model_path
        )

        self.output_directory = Path(
            output_directory
        )

        self.final_model_path = Path(
            final_model_path
        )

        self.final_scaler_path = Path(
            final_scaler_path
        )

        self.threshold = float(
            threshold
        )

        self.random_state = int(
            random_state
        )

        self.dataframe = None

        self.selected_features = []

        self.model = None

        self.pipeline = None

        self.best_model_name = (
            "HistGradientBoosting"
        )

    # ======================================================
    # LOAD DATASET
    # ======================================================

    def load_dataset(
        self,
    ) -> pd.DataFrame:

        if not self.dataset_path.exists():

            raise FileNotFoundError(
                "Feature dataset not found:\n"
                f"{self.dataset_path.resolve()}\n\n"
                "Run:\n"
                "python -m app.ml.train_model"
            )

        dataframe = pd.read_csv(
            self.dataset_path
        )

        if dataframe.empty:

            raise ValueError(
                "Feature dataset is empty."
            )

        if TARGET_COLUMN not in (
            dataframe.columns
        ):

            raise ValueError(
                "Target column 'status' "
                "was not found."
            )

        self.dataframe = dataframe

        return dataframe

    # ======================================================
    # LOAD SELECTED FEATURES
    # ======================================================

    def load_selected_features(
        self,
    ) -> List[str]:

        if not self.selected_features_path.exists():

            raise FileNotFoundError(
                "Selected feature configuration "
                "not found:\n"
                f"{self.selected_features_path.resolve()}\n\n"
                "Run Step 5 first."
            )

        with open(
            self.selected_features_path,
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(
                file
            )

        features = data.get(
            "features"
        )

        if features is None:

            features = data.get(
                "selected_features"
            )

        if features is None:

            selected_set = data.get(
                "selected_feature_set"
            )

            if isinstance(
                selected_set,
                dict,
            ):

                features = selected_set.get(
                    "features"
                )

        if not isinstance(
            features,
            list,
        ):

            raise ValueError(
                "Could not find selected "
                "features in:\n"
                f"{self.selected_features_path}"
            )

        if len(features) != 12:

            raise ValueError(
                "Step 9 expected exactly "
                f"12 selected features, "
                f"but found {len(features)}."
            )

        missing = [
            feature
            for feature in features
            if feature not in self.dataframe.columns
        ]

        if missing:

            raise ValueError(
                "Selected features are missing "
                f"from dataset: {missing}"
            )

        self.selected_features = (
            features
        )

        return features

    # ======================================================
    # LOAD STEP 6 MODEL INFORMATION
    # ======================================================

    def load_model_configuration(
        self,
    ) -> Dict:

        if not self.best_model_path.exists():

            print()

            print(
                "WARNING:"
            )

            print(
                "Step 6 model configuration "
                "was not found."
            )

            print(
                "Using HistGradientBoosting "
                "configuration directly."
            )

            return {}

        try:

            with open(
                self.best_model_path,
                "r",
                encoding="utf-8",
            ) as file:

                data = json.load(
                    file
                )

        except Exception:

            print(
                "WARNING: Could not read "
                "Step 6 model configuration."
            )

            return {}

        model_name = data.get(
            "best_model"
        )

        if isinstance(
            model_name,
            dict,
        ):

            model_name = model_name.get(
                "model"
            )

        if model_name:

            self.best_model_name = (
                str(
                    model_name
                )
            )

        return data

    # ======================================================
    # VALIDATE TARGET
    # ======================================================

    def validate_target(
        self,
    ) -> None:

        labels = pd.to_numeric(
            self.dataframe[
                TARGET_COLUMN
            ],
            errors="coerce",
        )

        if labels.isna().any():

            raise ValueError(
                "Target column contains "
                "invalid values."
            )

        labels = labels.astype(
            int
        )

        unique_values = sorted(
            labels.unique().tolist()
        )

        if unique_values != [
            HEALTHY,
            PARKINSON,
        ]:

            raise ValueError(
                "Expected target classes "
                "0 and 1. Found: "
                f"{unique_values}"
            )

        counts = (
            labels.value_counts()
        )

        print(
            f"Healthy recordings : "
            f"{counts.get(HEALTHY, 0)}"
        )

        print(
            f"Parkinson recordings: "
            f"{counts.get(PARKINSON, 0)}"
        )

    # ======================================================
    # CREATE FINAL MODEL
    # ======================================================

    def create_final_pipeline(
        self,
    ) -> Pipeline:

        """
        Create the exact Step-6 winning model.

        Step 6:
            HistGradientBoosting

        Configuration:
            max_iter=150
            learning_rate=0.05
            max_leaf_nodes=15
            l2_regularization=1.0
        """

        model = (
            HistGradientBoostingClassifier(
                max_iter=150,
                learning_rate=0.05,
                max_leaf_nodes=15,
                l2_regularization=1.0,
                random_state=self.random_state,
            )
        )

        pipeline = Pipeline(
            steps=[
                (
                    "imputer",
                    SimpleImputer(
                        strategy="median"
                    ),
                ),
                (
                    "scaler",
                    StandardScaler(),
                ),
                (
                    "model",
                    model,
                ),
            ]
        )

        self.model = model

        self.pipeline = pipeline

        return pipeline

    # ======================================================
    # PREPARE TRAINING DATA
    # ======================================================

    def prepare_data(
        self,
    ):

        X = self.dataframe[
            self.selected_features
        ].copy()

        y = self.dataframe[
            TARGET_COLUMN
        ].astype(
            int
        )

        # --------------------------------------------------
        # Ensure all selected features are numeric.
        # --------------------------------------------------

        for feature in (
            self.selected_features
        ):

            X[
                feature
            ] = pd.to_numeric(
                X[
                    feature
                ],
                errors="coerce",
            )

        if X.isna().all().any():

            invalid_features = (
                X.columns[
                    X.isna().all()
                ]
                .tolist()
            )

            raise ValueError(
                "The following selected "
                "features contain no valid "
                f"numeric values: "
                f"{invalid_features}"
            )

        return X, y

    # ======================================================
    # VALIDATION BEFORE FINAL FIT
    # ======================================================

    def validation_before_final_fit(
        self,
        X,
        y,
    ) -> Dict:

        """
        Perform one final sanity-check validation before
        fitting on all 81 recordings.

        This is NOT the Step 7 result.

        It is simply a reproducible final check using
        stratified 5-fold CV.

        The final model is subsequently trained on all data.
        """

        print()

        print(
            "FINAL PRE-FIT SANITY CHECK"
        )

        print(
            "-" * 70
        )

        cv = StratifiedKFold(
            n_splits=5,
            shuffle=True,
            random_state=self.random_state,
        )

        pipeline = (
            self.create_final_pipeline()
        )

        # --------------------------------------------------
        # OOF probabilities
        # --------------------------------------------------

        probabilities = (
            cross_val_predict(
                pipeline,
                X,
                y,
                cv=cv,
                method="predict_proba",
            )[:, 1]
        )

        predictions_default = (
            probabilities
            >= 0.50
        ).astype(
            int
        )

        predictions_threshold = (
            probabilities
            >= self.threshold
        ).astype(
            int
        )

        default_metrics = (
            self.calculate_metrics(
                y,
                predictions_default,
                probabilities,
            )
        )

        threshold_metrics = (
            self.calculate_metrics(
                y,
                predictions_threshold,
                probabilities,
            )
        )

        print(
            "Default threshold = 0.50"
        )

        self.print_metrics(
            default_metrics
        )

        print()

        print(
            f"Optimized threshold = "
            f"{self.threshold:.2f}"
        )

        self.print_metrics(
            threshold_metrics
        )

        return {
            "default_threshold":
                default_metrics,

            "optimized_threshold":
                threshold_metrics,
        }

    # ======================================================
    # METRICS
    # ======================================================

    @staticmethod
    def calculate_metrics(
        y_true,
        predictions,
        probabilities,
    ) -> Dict:

        accuracy = (
            accuracy_score(
                y_true,
                predictions,
            )
        )

        balanced = (
            balanced_accuracy_score(
                y_true,
                predictions,
            )
        )

        precision = (
            precision_score(
                y_true,
                predictions,
                zero_division=0,
            )
        )

        recall = (
            recall_score(
                y_true,
                predictions,
                zero_division=0,
            )
        )

        f1 = (
            f1_score(
                y_true,
                predictions,
                zero_division=0,
            )
        )

        matrix = (
            confusion_matrix(
                y_true,
                predictions,
                labels=[
                    HEALTHY,
                    PARKINSON,
                ],
            )
        )

        tn = int(
            matrix[0, 0]
        )

        fp = int(
            matrix[0, 1]
        )

        fn = int(
            matrix[1, 0]
        )

        tp = int(
            matrix[1, 1]
        )

        specificity = (
            tn
            /
            (tn + fp)
            if (
                tn + fp
            ) > 0
            else 0.0
        )

        try:

            auc = (
                roc_auc_score(
                    y_true,
                    probabilities,
                )
            )

        except Exception:

            auc = float(
                "nan"
            )

        return {
            "accuracy":
                float(
                    accuracy
                ),

            "balanced_accuracy":
                float(
                    balanced
                ),

            "precision":
                float(
                    precision
                ),

            "recall":
                float(
                    recall
                ),

            "sensitivity":
                float(
                    recall
                ),

            "specificity":
                float(
                    specificity
                ),

            "f1":
                float(
                    f1
                ),

            "roc_auc":
                float(
                    auc
                ),

            "tn":
                tn,

            "fp":
                fp,

            "fn":
                fn,

            "tp":
                tp,
        }

    # ======================================================
    # PRINT METRICS
    # ======================================================

    @staticmethod
    def print_metrics(
        metrics: Dict,
    ) -> None:

        print(
            f"Accuracy          : "
            f"{metrics['accuracy']:.4f}"
        )

        print(
            f"Balanced Accuracy : "
            f"{metrics['balanced_accuracy']:.4f}"
        )

        print(
            f"Precision         : "
            f"{metrics['precision']:.4f}"
        )

        print(
            f"Sensitivity       : "
            f"{metrics['sensitivity']:.4f}"
        )

        print(
            f"Specificity       : "
            f"{metrics['specificity']:.4f}"
        )

        print(
            f"F1                : "
            f"{metrics['f1']:.4f}"
        )

        print(
            f"ROC-AUC           : "
            f"{metrics['roc_auc']:.4f}"
        )

        print(
            f"TN                : "
            f"{metrics['tn']}"
        )

        print(
            f"FP                : "
            f"{metrics['fp']}"
        )

        print(
            f"FN                : "
            f"{metrics['fn']}"
        )

        print(
            f"TP                : "
            f"{metrics['tp']}"
        )

    # ======================================================
    # FIT FINAL MODEL
    # ======================================================

    def fit_final_model(
        self,
        X,
        y,
    ) -> Pipeline:

        print()

        print(
            "TRAINING FINAL MODEL"
        )

        print(
            "-" * 70
        )

        print(
            "Training on complete dataset."
        )

        print(
            f"Samples : {len(X)}"
        )

        print(
            f"Features: {len(self.selected_features)}"
        )

        self.pipeline = (
            self.create_final_pipeline()
        )

        self.pipeline.fit(
            X,
            y,
        )

        print(
            "Final model training complete."
        )

        return self.pipeline

    # ======================================================
    # SAVE FINAL MODEL
    # ======================================================

    def save_final_model(
        self,
    ) -> None:

        self.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        # --------------------------------------------------
        # Save the COMPLETE pipeline.
        #
        # This contains:
        #
        #     imputer
        #     scaler
        #     HistGradientBoosting
        #
        # Keeping them together prevents preprocessing
        # mismatches during prediction.
        # --------------------------------------------------

        joblib.dump(
            self.pipeline,
            self.final_model_path,
        )

        # --------------------------------------------------
        # Save scaler separately as a compatibility artifact.
        # --------------------------------------------------

        scaler = (
            self.pipeline.named_steps[
                "scaler"
            ]
        )

        joblib.dump(
            scaler,
            self.final_scaler_path,
        )

        print()

        print(
            "FINAL MODEL ARTIFACTS"
        )

        print(
            "-" * 70
        )

        print(
            f"Model    : "
            f"{self.final_model_path.resolve()}"
        )

        print(
            f"Scaler   : "
            f"{self.final_scaler_path.resolve()}"
        )

    # ======================================================
    # SAVE FEATURE CONFIGURATION
    # ======================================================

    def save_feature_configuration(
        self,
    ) -> Dict:

        configuration = {
            "version":
                "step9_final",

            "feature_count":
                len(
                    self.selected_features
                ),

            "features":
                self.selected_features,

            "feature_order":
                self.selected_features,

            "target_column":
                TARGET_COLUMN,

            "healthy_class":
                HEALTHY,

            "parkinson_class":
                PARKINSON,

            "decision_threshold":
                self.threshold,

            "model":
                self.best_model_name,

            "preprocessing":
                [
                    "SimpleImputer(strategy='median')",
                    "StandardScaler",
                ],

            "model_parameters":
                {
                    "max_iter":
                        150,

                    "learning_rate":
                        0.05,

                    "max_leaf_nodes":
                        15,

                    "l2_regularization":
                        1.0,

                    "random_state":
                        self.random_state,
                },

            "production_model_changed":
                False,
        }

        with open(
            self.output_directory
            / "final_feature_config.json",
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                configuration,
                file,
                indent=4,
            )

        return configuration

    # ======================================================
    # MODEL METADATA
    # ======================================================

    def save_metadata(
        self,
        sanity_metrics: Dict,
    ) -> Dict:

        metadata = {
            "step":
                9,

            "model_type":
                self.best_model_name,

            "training_samples":
                int(
                    len(
                        self.dataframe
                    )
                ),

            "healthy_samples":
                int(
                    (
                        self.dataframe[
                            TARGET_COLUMN
                        ]
                        == HEALTHY
                    ).sum()
                ),

            "parkinson_samples":
                int(
                    (
                        self.dataframe[
                            TARGET_COLUMN
                        ]
                        == PARKINSON
                    ).sum()
                ),

            "feature_count":
                int(
                    len(
                        self.selected_features
                    )
                ),

            "features":
                self.selected_features,

            "decision_threshold":
                self.threshold,

            "model_parameters":
                {
                    "max_iter":
                        150,

                    "learning_rate":
                        0.05,

                    "max_leaf_nodes":
                        15,

                    "l2_regularization":
                        1.0,

                    "random_state":
                        self.random_state,
                },

            "preprocessing":
                {
                    "imputer":
                        "median",

                    "scaler":
                        "StandardScaler",
                },

            "sanity_validation":
                sanity_metrics,

            "source_dataset":
                str(
                    self.dataset_path.resolve()
                ),

            "production_model_path":
                str(
                    self.final_model_path.resolve()
                ),

            "production_scaler_path":
                str(
                    self.final_scaler_path.resolve()
                ),

            "existing_model_preserved":
                True,

            "clinical_warning":
                (
                    "This model is a research "
                    "candidate and is not a clinical "
                    "diagnostic device."
                ),
        }

        with open(
            self.output_directory
            / "final_model_metadata.json",
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                metadata,
                file,
                indent=4,
            )

        return metadata

    # ======================================================
    # SAVE TRAINING REPORT
    # ======================================================

    def save_training_report(
        self,
        sanity_metrics: Dict,
    ) -> Dict:

        y = (
            self.dataframe[
                TARGET_COLUMN
            ].astype(
                int
            )
        )

        report = {
            "step":
                9,

            "status":
                "complete",

            "dataset":
                str(
                    self.dataset_path.resolve()
                ),

            "total_recordings":
                int(
                    len(
                        self.dataframe
                    )
                ),

            "healthy_recordings":
                int(
                    (
                        y
                        == HEALTHY
                    ).sum()
                ),

            "parkinson_recordings":
                int(
                    (
                        y
                        == PARKINSON
                    ).sum()
                ),

            "features":
                self.selected_features,

            "feature_count":
                int(
                    len(
                        self.selected_features
                    )
                ),

            "model":
                self.best_model_name,

            "model_parameters":
                {
                    "max_iter":
                        150,

                    "learning_rate":
                        0.05,

                    "max_leaf_nodes":
                        15,

                    "l2_regularization":
                        1.0,

                    "random_state":
                        self.random_state,
                },

            "decision_threshold":
                self.threshold,

            "sanity_validation":
                sanity_metrics,

            "artifacts":
                {
                    "model":
                        str(
                            self.final_model_path.resolve()
                        ),

                    "scaler":
                        str(
                            self.final_scaler_path.resolve()
                        ),

                    "metadata":
                        str(
                            (
                                self.output_directory
                                /
                                "final_model_metadata.json"
                            ).resolve()
                        ),

                    "feature_config":
                        str(
                            (
                                self.output_directory
                                /
                                "final_feature_config.json"
                            ).resolve()
                        ),
                },

            "existing_model_replaced":
                False,

            "next_step":
                (
                    "Step 10 - production "
                    "integration and end-to-end testing."
                ),
        }

        with open(
            self.output_directory
            / "final_training_report.json",
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                report,
                file,
                indent=4,
            )

        self.save_text_report(
            report
        )

        return report

    # ======================================================
    # TEXT REPORT
    # ======================================================

    def save_text_report(
        self,
        report: Dict,
    ) -> None:

        sanity = report[
            "sanity_validation"
        ]

        optimized = sanity[
            "optimized_threshold"
        ]

        lines = []

        lines.append(
            "=" * 70
        )

        lines.append(
            "STEP 9 - FINAL MODEL TRAINING"
        )

        lines.append(
            "=" * 70
        )

        lines.append("")

        lines.append(
            "DATASET"
        )

        lines.append(
            "-" * 70
        )

        lines.append(
            f"Total recordings : "
            f"{report['total_recordings']}"
        )

        lines.append(
            f"Healthy          : "
            f"{report['healthy_recordings']}"
        )

        lines.append(
            f"Parkinson        : "
            f"{report['parkinson_recordings']}"
        )

        lines.append("")

        lines.append(
            "FEATURES"
        )

        lines.append(
            "-" * 70
        )

        lines.append(
            f"Feature count: "
            f"{report['feature_count']}"
        )

        for index, feature in enumerate(
            report[
                "features"
            ],
            start=1,
        ):

            lines.append(
                f"{index:02d}. {feature}"
            )

        lines.append("")

        lines.append(
            "MODEL"
        )

        lines.append(
            "-" * 70
        )

        lines.append(
            f"Model: "
            f"{report['model']}"
        )

        lines.append(
            f"max_iter: "
            f"{report['model_parameters']['max_iter']}"
        )

        lines.append(
            f"learning_rate: "
            f"{report['model_parameters']['learning_rate']}"
        )

        lines.append(
            f"max_leaf_nodes: "
            f"{report['model_parameters']['max_leaf_nodes']}"
        )

        lines.append(
            f"l2_regularization: "
            f"{report['model_parameters']['l2_regularization']}"
        )

        lines.append("")

        lines.append(
            "DECISION THRESHOLD"
        )

        lines.append(
            "-" * 70
        )

        lines.append(
            f"Threshold: "
            f"{report['decision_threshold']:.2f}"
        )

        lines.append("")

        lines.append(
            "FINAL SANITY VALIDATION"
        )

        lines.append(
            "-" * 70
        )

        lines.append(
            "Optimized threshold:"
        )

        lines.append(
            f"Accuracy: "
            f"{optimized['accuracy']:.4f}"
        )

        lines.append(
            f"Balanced Accuracy: "
            f"{optimized['balanced_accuracy']:.4f}"
        )

        lines.append(
            f"Precision: "
            f"{optimized['precision']:.4f}"
        )

        lines.append(
            f"Sensitivity: "
            f"{optimized['sensitivity']:.4f}"
        )

        lines.append(
            f"Specificity: "
            f"{optimized['specificity']:.4f}"
        )

        lines.append(
            f"F1: "
            f"{optimized['f1']:.4f}"
        )

        lines.append(
            f"ROC-AUC: "
            f"{optimized['roc_auc']:.4f}"
        )

        lines.append("")

        lines.append(
            "ARTIFACTS"
        )

        lines.append(
            "-" * 70
        )

        lines.append(
            f"Model: "
            f"{report['artifacts']['model']}"
        )

        lines.append(
            f"Scaler: "
            f"{report['artifacts']['scaler']}"
        )

        lines.append(
            f"Metadata: "
            f"{report['artifacts']['metadata']}"
        )

        lines.append(
            f"Feature config: "
            f"{report['artifacts']['feature_config']}"
        )

        lines.append("")

        lines.append(
            "IMPORTANT"
        )

        lines.append(
            "-" * 70
        )

        lines.append(
            "Existing model.pkl was NOT replaced."
        )

        lines.append(
            "Existing scaler.pkl was NOT replaced."
        )

        lines.append(
            "The final model is a production "
            "candidate pending Step 10 testing."
        )

        lines.append(
            "This model is not a clinical "
            "diagnostic device."
        )

        lines.append("")

        lines.append(
            "=" * 70
        )

        with open(
            self.output_directory
            / "final_training_report.txt",
            "w",
            encoding="utf-8",
        ) as file:

            file.write(
                "\n".join(
                    lines
                )
            )

    # ======================================================
    # PRINT FINAL SUMMARY
    # ======================================================

    def print_summary(
        self,
        report: Dict,
    ) -> None:

        sanity = report[
            "sanity_validation"
        ]

        optimized = sanity[
            "optimized_threshold"
        ]

        print()

        print(
            "=" * 70
        )

        print(
            "STEP 9 - FINAL MODEL TRAINING COMPLETE"
        )

        print(
            "=" * 70
        )

        print()

        print(
            "FINAL DATASET"
        )

        print(
            "-" * 70
        )

        print(
            f"Total recordings : "
            f"{report['total_recordings']}"
        )

        print(
            f"Healthy          : "
            f"{report['healthy_recordings']}"
        )

        print(
            f"Parkinson        : "
            f"{report['parkinson_recordings']}"
        )

        print()

        print(
            "FINAL FEATURES"
        )

        print(
            "-" * 70
        )

        print(
            f"Feature count: "
            f"{report['feature_count']}"
        )

        for index, feature in enumerate(
            report[
                "features"
            ],
            start=1,
        ):

            print(
                f"{index:02d}. {feature}"
            )

        print()

        print(
            "FINAL MODEL"
        )

        print(
            "-" * 70
        )

        print(
            f"Model: "
            f"{report['model']}"
        )

        print(
            "HistGradientBoosting"
        )

        print()

        print(
            "DECISION THRESHOLD"
        )

        print(
            "-" * 70
        )

        print(
            f"Threshold: "
            f"{report['decision_threshold']:.2f}"
        )

        print()

        print(
            "FINAL SANITY VALIDATION"
        )

        print(
            "-" * 70
        )

        self.print_metrics(
            optimized
        )

        print()

        print(
            "ARTIFACTS"
        )

        print(
            "-" * 70
        )

        print(
            f"Model : "
            f"{self.final_model_path.resolve()}"
        )

        print(
            f"Scaler: "
            f"{self.final_scaler_path.resolve()}"
        )

        print(
            f"Config: "
            f"{(
                self.output_directory
                /
                'final_feature_config.json'
            ).resolve()}"
        )

        print(
            f"Report: "
            f"{(
                self.output_directory
                /
                'final_training_report.json'
            ).resolve()}"
        )

        print()

        print(
            "PRODUCTION MODEL"
        )

        print(
            "-" * 70
        )

        print(
            "model.pkl was NOT replaced."
        )

        print(
            "scaler.pkl was NOT replaced."
        )

        print()

        print(
            "Next:"
        )

        print(
            "STEP 10 - Production integration "
            "and end-to-end testing."
        )

        print()

        print(
            "=" * 70
        )

    # ======================================================
    # MAIN TRAINING PIPELINE
    # ======================================================

    def train_and_save(
        self,
    ) -> Dict:

        # --------------------------------------------------
        # Load
        # --------------------------------------------------

        self.load_dataset()

        self.load_selected_features()

        self.load_model_configuration()

        # --------------------------------------------------
        # Header
        # --------------------------------------------------

        print()

        print(
            "=" * 70
        )

        print(
            "STEP 9 - FINAL MODEL TRAINING"
        )

        print(
            "=" * 70
        )

        print()

        print(
            f"Dataset : "
            f"{len(self.dataframe)} recordings"
        )

        print(
            f"Model   : "
            f"{self.best_model_name}"
        )

        print(
            f"Features: "
            f"{len(self.selected_features)}"
        )

        print(
            f"Threshold: "
            f"{self.threshold:.2f}"
        )

        print()

        self.validate_target()

        # --------------------------------------------------
        # Prepare
        # --------------------------------------------------

        X, y = (
            self.prepare_data()
        )

        # --------------------------------------------------
        # Final sanity validation
        # --------------------------------------------------

        sanity_metrics = (
            self.validation_before_final_fit(
                X,
                y,
            )
        )

        # --------------------------------------------------
        # Final complete-data fit
        # --------------------------------------------------

        self.fit_final_model(
            X,
            y,
        )

        # --------------------------------------------------
        # Save model
        # --------------------------------------------------

        self.save_final_model()

        # --------------------------------------------------
        # Save configuration
        # --------------------------------------------------

        self.save_feature_configuration()

        # --------------------------------------------------
        # Save metadata
        # --------------------------------------------------

        self.save_metadata(
            sanity_metrics
        )

        # --------------------------------------------------
        # Save report
        # --------------------------------------------------

        report = (
            self.save_training_report(
                sanity_metrics
            )
        )

        # --------------------------------------------------
        # Summary
        # --------------------------------------------------

        self.print_summary(
            report
        )

        return report


# ==========================================================
# STANDALONE EXECUTION
# ==========================================================

if __name__ == "__main__":

    trainer = (
        FinalModelTrainer(
            dataset_path=(
                DATASET_PATH
            ),
            selected_features_path=(
                SELECTED_FEATURES_PATH
            ),
            best_model_path=(
                BEST_MODEL_PATH
            ),
            output_directory=(
                OUTPUT_DIRECTORY
            ),
            final_model_path=(
                FINAL_MODEL_PATH
            ),
            final_scaler_path=(
                FINAL_SCALER_PATH
            ),
            threshold=(
                DECISION_THRESHOLD
            ),
            random_state=(
                RANDOM_STATE
            ),
        )
    )

    try:

        trainer.train_and_save()

    except Exception as exc:

        print()

        print(
            "=" * 70
        )

        print(
            "FINAL MODEL TRAINING FAILED"
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
