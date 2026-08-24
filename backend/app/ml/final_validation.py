from pathlib import Path
from typing import Dict, List, Optional, Tuple

import json
import warnings

import numpy as np
import pandas as pd

from sklearn.ensemble import (
    HistGradientBoostingClassifier,
)

from sklearn.impute import (
    SimpleImputer,
)

from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from sklearn.model_selection import (
    RepeatedStratifiedKFold,
    StratifiedKFold,
)

from sklearn.pipeline import (
    Pipeline,
)

from sklearn.preprocessing import (
    StandardScaler,
)


warnings.filterwarnings(
    "ignore"
)


# ==========================================================
# Constants
# ==========================================================

TARGET_COLUMN = "status"

HEALTHY = 0

PARKINSON = 1

RANDOM_STATE = 42

DEFAULT_CSV = (
    "models/audio_training_features.csv"
)

DEFAULT_SELECTED_FEATURES = (
    "models/selected_features.json"
)

DEFAULT_BEST_MODEL = (
    "models/best_model_configuration.json"
)

DEFAULT_OUTPUT = (
    "models"
)


# ==========================================================
# Final Validator
# ==========================================================

class FinalValidator:
    """
    Robust validation of the optimized Parkinson
    voice model.
    """

    # ======================================================
    # Initialization
    # ======================================================

    def __init__(
        self,
        csv_path: str = DEFAULT_CSV,
        selected_features_path: str = (
            DEFAULT_SELECTED_FEATURES
        ),
        best_model_path: str = (
            DEFAULT_BEST_MODEL
        ),
        output_directory: str = DEFAULT_OUTPUT,
        random_state: int = RANDOM_STATE,
        folds: int = 5,
        repeats: int = 10,
    ):

        self.csv_path = Path(
            csv_path
        )

        self.selected_features_path = (
            Path(
                selected_features_path
            )
        )

        self.best_model_path = (
            Path(
                best_model_path
            )
        )

        self.output_directory = (
            Path(
                output_directory
            )
        )

        self.random_state = (
            random_state
        )

        self.requested_folds = (
            folds
        )

        self.repeats = (
            repeats
        )

        self.dataframe = None

        self.selected_features = []

        self.best_model_name = (
            "HistGradientBoosting"
        )

        self.best_model_parameters = {}

    # ======================================================
    # Load Dataset
    # ======================================================

    def load_dataset(
        self,
    ) -> pd.DataFrame:

        if not self.csv_path.exists():

            raise FileNotFoundError(
                "Feature dataset not found:\n"
                f"{self.csv_path.resolve()}\n\n"
                "Run:\n"
                "python -m app.ml.train_model"
            )

        dataframe = pd.read_csv(
            self.csv_path
        )

        if dataframe.empty:

            raise ValueError(
                "Feature dataset is empty."
            )

        if TARGET_COLUMN not in (
            dataframe.columns
        ):

            raise ValueError(
                "Dataset does not contain "
                "'status' column."
            )

        self.dataframe = dataframe

        return dataframe

    # ======================================================
    # Load Selected Features
    # ======================================================

    def load_selected_features(
        self,
    ) -> List[str]:

        if not self.selected_features_path.exists():

            raise FileNotFoundError(
                "selected_features.json not found:\n"
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

        if not isinstance(
            features,
            list,
        ):

            raise ValueError(
                "Invalid selected feature list."
            )

        if len(features) < 2:

            raise ValueError(
                "At least two features "
                "are required."
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
    # Load Best Model Configuration
    # ======================================================

    def load_model_configuration(
        self,
    ) -> Dict:

        if not self.best_model_path.exists():

            raise FileNotFoundError(
                "best_model_configuration.json "
                "not found:\n"
                f"{self.best_model_path.resolve()}\n\n"
                "Run Step 6 first."
            )

        with open(
            self.best_model_path,
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(
                file
            )

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

        if not model_name:

            model_name = (
                "HistGradientBoosting"
            )

        self.best_model_name = (
            model_name
        )

        return data

    # ======================================================
    # Validate Dataset
    # ======================================================

    def validate_dataset(
        self,
    ) -> None:

        if self.dataframe is None:

            raise RuntimeError(
                "Dataset not loaded."
            )

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

        unique_labels = sorted(
            labels.unique().tolist()
        )

        if unique_labels != [
            HEALTHY,
            PARKINSON,
        ]:

            raise ValueError(
                "Expected classes 0 and 1. "
                f"Found: {unique_labels}"
            )

        class_counts = (
            labels.value_counts()
        )

        print(
            f"Healthy recordings : "
            f"{class_counts.get(HEALTHY, 0)}"
        )

        print(
            f"Parkinson recordings: "
            f"{class_counts.get(PARKINSON, 0)}"
        )

    # ======================================================
    # Create Optimized Model
    # ======================================================

    def create_optimized_model(
        self,
    ):

        """
        Exact Step-6 winning configuration.

        HistGradientBoosting:

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

        return pipeline

    # ======================================================
    # Create Baseline Model
    # ======================================================

    def create_baseline_model(
        self,
    ):
        """
        Approximate original 22-feature baseline.

        This is used only for comparison.

        It does not modify the production model.
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

        return Pipeline(
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

    # ======================================================
    # Get All 22 Features
    # ======================================================

    def get_all_features(
        self,
    ) -> List[str]:

        return [
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

    # ======================================================
    # Metrics
    # ======================================================

    @staticmethod
    def calculate_metrics(
        y_true,
        y_pred,
        probabilities,
    ) -> Dict:

        accuracy = accuracy_score(
            y_true,
            y_pred,
        )

        balanced = (
            balanced_accuracy_score(
                y_true,
                y_pred,
            )
        )

        precision = precision_score(
            y_true,
            y_pred,
            zero_division=0,
        )

        recall = recall_score(
            y_true,
            y_pred,
            zero_division=0,
        )

        f1 = f1_score(
            y_true,
            y_pred,
            zero_division=0,
        )

        try:

            roc_auc = roc_auc_score(
                y_true,
                probabilities,
            )

        except Exception:

            roc_auc = float(
                "nan"
            )

        matrix = confusion_matrix(
            y_true,
            y_pred,
            labels=[
                HEALTHY,
                PARKINSON,
            ],
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
            tn / (tn + fp)
            if (
                tn + fp
            ) > 0
            else 0.0
        )

        npv = (
            tn / (tn + fn)
            if (
                tn + fn
            ) > 0
            else 0.0
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
                    roc_auc
                ),

            "npv":
                float(
                    npv
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
    # Repeated Cross Validation
    # ======================================================

    def repeated_validation(
        self,
    ) -> Tuple[
        pd.DataFrame,
        pd.DataFrame,
    ]:

        X = self.dataframe[
            self.selected_features
        ].copy()

        y = self.dataframe[
            TARGET_COLUMN
        ].astype(
            int
        )

        minimum_class = int(
            y.value_counts().min()
        )

        folds = min(
            self.requested_folds,
            minimum_class,
        )

        if folds < 2:

            raise ValueError(
                "Not enough samples for "
                "cross-validation."
            )

        cv = RepeatedStratifiedKFold(
            n_splits=folds,
            n_repeats=self.repeats,
            random_state=self.random_state,
        )

        oof_predictions = np.full(
            len(y),
            np.nan,
            dtype=float,
        )

        oof_probabilities = np.full(
            len(y),
            np.nan,
            dtype=float,
        )

        fold_rows = []

        print()

        print(
            "REPEATED STRATIFIED "
            "CROSS-VALIDATION"
        )

        print(
            "-" * 70
        )

        split_number = 0

        for repeat_index, (
            train_indices,
            test_indices,
        ) in enumerate(
            cv.split(
                X,
                y,
            ),
            start=1,
        ):

            split_number += 1

            model = (
                self.create_optimized_model()
            )

            X_train = X.iloc[
                train_indices
            ]

            X_test = X.iloc[
                test_indices
            ]

            y_train = y.iloc[
                train_indices
            ]

            y_test = y.iloc[
                test_indices
            ]

            model.fit(
                X_train,
                y_train,
            )

            predictions = model.predict(
                X_test
            )

            probabilities = (
                model.predict_proba(
                    X_test
                )[:, 1]
            )

            metrics = (
                self.calculate_metrics(
                    y_test,
                    predictions,
                    probabilities,
                )
            )

            fold_rows.append(
                {
                    "Repeat":
                        repeat_index,

                    "Split":
                        split_number,

                    "TrainSamples":
                        len(
                            train_indices
                        ),

                    "TestSamples":
                        len(
                            test_indices
                        ),

                    "Accuracy":
                        metrics[
                            "accuracy"
                        ],

                    "BalancedAccuracy":
                        metrics[
                            "balanced_accuracy"
                        ],

                    "Precision":
                        metrics[
                            "precision"
                        ],

                    "Recall":
                        metrics[
                            "recall"
                        ],

                    "Specificity":
                        metrics[
                            "specificity"
                        ],

                    "F1":
                        metrics[
                            "f1"
                        ],

                    "ROCAUC":
                        metrics[
                            "roc_auc"
                        ],
                }
            )

            # ------------------------------------------------
            # Save only the final repeat as true OOF.
            #
            # Repeated CV predicts each sample multiple times.
            # For the OOF report we average probabilities and
            # predictions across all repeats.
            # ------------------------------------------------

            for position, index in enumerate(
                test_indices
            ):

                if np.isnan(
                    oof_probabilities[
                        index
                    ]
                ):

                    oof_probabilities[
                        index
                    ] = probabilities[
                        position
                    ]

                    oof_predictions[
                        index
                    ] = predictions[
                        position
                    ]

                else:

                    oof_probabilities[
                        index
                    ] = (
                        oof_probabilities[
                            index
                        ]
                        +
                        probabilities[
                            position
                        ]
                    ) / 2.0

                    # ------------------------------------------------
                    # Average probability determines final prediction.
                    # ------------------------------------------------

                    oof_predictions[
                        index
                    ] = int(
                        oof_probabilities[
                            index
                        ]
                        >= 0.5
                    )

            print(
                f"Repeat {repeat_index:02d} "
                f"Split {split_number:02d}: "
                f"Accuracy="
                f"{metrics['accuracy']:.4f} "
                f"Recall="
                f"{metrics['recall']:.4f} "
                f"Specificity="
                f"{metrics['specificity']:.4f} "
                f"AUC="
                f"{metrics['roc_auc']:.4f}"
            )

        fold_dataframe = pd.DataFrame(
            fold_rows
        )

        # --------------------------------------------------
        # Final averaged OOF predictions
        # --------------------------------------------------

        oof_rows = []

        for index in range(
            len(
                self.dataframe
            )
        ):

            probability = (
                oof_probabilities[
                    index
                ]
            )

            prediction = int(
                probability >= 0.5
            )

            actual = int(
                y.iloc[
                    index
                ]
            )

            oof_rows.append(
                {
                    "Index":
                        index,

                    "Actual":
                        actual,

                    "Prediction":
                        prediction,

                    "Probability_PD":
                        float(
                            probability
                        ),

                    "Probability_HC":
                        float(
                            1.0
                            - probability
                        ),

                    "Correct":
                        bool(
                            actual
                            == prediction
                        ),

                    "Confidence":
                        float(
                            max(
                                probability,
                                1.0
                                - probability,
                            )
                        ),
                }
            )

        oof_dataframe = pd.DataFrame(
            oof_rows
        )

        return (
            fold_dataframe,
            oof_dataframe,
        )

    # ======================================================
    # Overall OOF Metrics
    # ======================================================

    def overall_oof_metrics(
        self,
        oof_dataframe: pd.DataFrame,
    ) -> Dict:

        y_true = (
            oof_dataframe[
                "Actual"
            ].values
        )

        y_pred = (
            oof_dataframe[
                "Prediction"
            ].values
        )

        probabilities = (
            oof_dataframe[
                "Probability_PD"
            ].values
        )

        return self.calculate_metrics(
            y_true,
            y_pred,
            probabilities,
        )

    # ======================================================
    # Error Analysis
    # ======================================================

    def error_analysis(
        self,
        oof_dataframe: pd.DataFrame,
    ) -> pd.DataFrame:

        errors = (
            oof_dataframe[
                oof_dataframe[
                    "Correct"
                ]
                == False
            ]
            .copy()
        )

        if errors.empty:

            return errors

        # --------------------------------------------------
        # Add filename/patient information if available.
        # --------------------------------------------------

        possible_name_columns = [
            "filename",
            "file",
            "audio_file",
            "recording",
            "name",
            "patient_name",
        ]

        name_column = None

        for column in (
            possible_name_columns
        ):

            if column in (
                self.dataframe.columns
            ):

                name_column = column

                break

        if name_column is not None:

            errors[
                "Recording"
            ] = (
                self.dataframe
                .loc[
                    errors[
                        "Index"
                    ],
                    name_column,
                ]
                .values
            )

        else:

            errors[
                "Recording"
            ] = errors[
                "Index"
            ].apply(
                lambda value:
                f"recording_{int(value):03d}"
            )

        errors[
            "ActualClass"
        ] = errors[
            "Actual"
        ].map(
            {
                0: "HC",
                1: "PD",
            }
        )

        errors[
            "PredictedClass"
        ] = errors[
            "Prediction"
        ].map(
            {
                0: "HC",
                1: "PD",
            }
        )

        errors[
            "ErrorType"
        ] = np.where(
            (
                errors[
                    "Actual"
                ]
                == 0
            )
            &
            (
                errors[
                    "Prediction"
                ]
                == 1
            ),
            "False Positive",
            "False Negative",
        )

        return errors[
            [
                "Index",
                "Recording",
                "ActualClass",
                "PredictedClass",
                "ErrorType",
                "Probability_PD",
                "Confidence",
            ]
        ]

    # ======================================================
    # Confidence Analysis
    # ======================================================

    def confidence_analysis(
        self,
        oof_dataframe: pd.DataFrame,
    ) -> Dict:

        confidence = (
            oof_dataframe[
                "Confidence"
            ]
        )

        correct = (
            oof_dataframe[
                "Correct"
            ]
        )

        incorrect = (
            ~correct
        )

        return {
            "mean_confidence":
                float(
                    confidence.mean()
                ),

            "median_confidence":
                float(
                    confidence.median()
                ),

            "correct_mean_confidence":
                float(
                    confidence[
                        correct
                    ].mean()
                )
                if correct.any()
                else 0.0,

            "incorrect_mean_confidence":
                float(
                    confidence[
                        incorrect
                    ].mean()
                )
                if incorrect.any()
                else 0.0,

            "high_confidence_threshold":
                0.80,

            "high_confidence_count":
                int(
                    (
                        confidence
                        >= 0.80
                    ).sum()
                ),

            "high_confidence_errors":
                int(
                    (
                        (
                            confidence
                            >= 0.80
                        )
                        &
                        incorrect
                    ).sum()
                ),
        }

    # ======================================================
    # Participant Leakage Inspection
    # ======================================================

    def inspect_participant_columns(
        self,
    ) -> Dict:

        columns = [
            str(column)
            for column in self.dataframe.columns
        ]

        possible_columns = [
            "patient_id",
            "patient",
            "subject_id",
            "subject",
            "participant_id",
            "participant",
            "speaker_id",
            "speaker",
            "patient_name",
        ]

        found = []

        for column in possible_columns:

            if column in columns:

                found.append(
                    column
                )

        return {
            "participant_columns_found":
                found,

            "leakage_check_possible":
                bool(
                    found
                ),

            "message":
                (
                    "Participant-aware validation "
                    "should be used if multiple recordings "
                    "belong to the same participant."
                    if found
                    else
                    "No explicit participant identifier "
                    "was found in the feature CSV. "
                    "Participant-level leakage cannot be "
                    "verified from this file alone."
                ),
        }

    # ======================================================
    # Compare With 22 Features
    # ======================================================

    def baseline_comparison(
        self,
    ) -> Dict:

        all_features = (
            self.get_all_features()
        )

        X = self.dataframe[
            all_features
        ].copy()

        y = self.dataframe[
            TARGET_COLUMN
        ].astype(
            int
        )

        minimum_class = int(
            y.value_counts().min()
        )

        folds = min(
            self.requested_folds,
            minimum_class,
        )

        cv = StratifiedKFold(
            n_splits=folds,
            shuffle=True,
            random_state=self.random_state,
        )

        model = (
            self.create_optimized_model()
        )

        accuracies = []

        balanced_scores = []

        f1_scores = []

        auc_scores = []

        recalls = []

        specificities = []

        print()

        print(
            "22-FEATURE COMPARISON"
        )

        print(
            "-" * 70
        )

        for train_indices, test_indices in (
            cv.split(
                X,
                y,
            )
        ):

            X_train = X.iloc[
                train_indices
            ]

            X_test = X.iloc[
                test_indices
            ]

            y_train = y.iloc[
                train_indices
            ]

            y_test = y.iloc[
                test_indices
            ]

            model.fit(
                X_train,
                y_train,
            )

            predictions = (
                model.predict(
                    X_test
                )
            )

            probabilities = (
                model.predict_proba(
                    X_test
                )[:, 1]
            )

            metrics = (
                self.calculate_metrics(
                    y_test,
                    predictions,
                    probabilities,
                )
            )

            accuracies.append(
                metrics[
                    "accuracy"
                ]
            )

            balanced_scores.append(
                metrics[
                    "balanced_accuracy"
                ]
            )

            f1_scores.append(
                metrics[
                    "f1"
                ]
            )

            auc_scores.append(
                metrics[
                    "roc_auc"
                ]
            )

            recalls.append(
                metrics[
                    "recall"
                ]
            )

            specificities.append(
                metrics[
                    "specificity"
                ]
            )

        return {
            "feature_count":
                22,

            "accuracy":
                float(
                    np.mean(
                        accuracies
                    )
                ),

            "balanced_accuracy":
                float(
                    np.mean(
                        balanced_scores
                    )
                ),

            "f1":
                float(
                    np.mean(
                        f1_scores
                    )
                ),

            "roc_auc":
                float(
                    np.mean(
                        auc_scores
                    )
                ),

            "recall":
                float(
                    np.mean(
                        recalls
                    )
                ),

            "specificity":
                float(
                    np.mean(
                        specificities
                    )
                ),
        }

    # ======================================================
    # Save OOF
    # ======================================================

    def save_oof(
        self,
        oof_dataframe: pd.DataFrame,
    ) -> None:

        self.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        oof_dataframe.to_csv(
            self.output_directory
            / "final_validation_oof.csv",
            index=False,
        )

    # ======================================================
    # Save Fold Results
    # ======================================================

    def save_fold_results(
        self,
        fold_dataframe: pd.DataFrame,
    ) -> None:

        fold_dataframe.to_csv(
            self.output_directory
            / "final_validation_folds.csv",
            index=False,
        )

    # ======================================================
    # Save Errors
    # ======================================================

    def save_errors(
        self,
        errors: pd.DataFrame,
    ) -> None:

        errors.to_csv(
            self.output_directory
            / "final_validation_errors.csv",
            index=False,
        )

    # ======================================================
    # Save Report
    # ======================================================

    def save_report(
        self,
        metrics: Dict,
        confidence: Dict,
        leakage: Dict,
        baseline: Dict,
        errors: pd.DataFrame,
        fold_dataframe: pd.DataFrame,
    ) -> None:

        self.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        report = {
            "step":
                7,

            "validation_type":
                "Repeated Stratified Cross-Validation",

            "dataset":
                str(
                    self.csv_path.resolve()
                ),

            "recordings":
                int(
                    len(
                        self.dataframe
                    )
                ),

            "feature_count":
                int(
                    len(
                        self.selected_features
                    )
                ),

            "features":
                self.selected_features,

            "model":
                self.best_model_name,

            "repeats":
                self.repeats,

            "requested_folds":
                self.requested_folds,

            "fold_count":
                int(
                    fold_dataframe[
                        "TestSamples"
                    ].count()
                    and
                    self.requested_folds
                ),

            "metrics":
                metrics,

            "confidence":
                confidence,

            "error_count":
                int(
                    len(
                        errors
                    )
                ),

            "error_rate":
                float(
                    len(errors)
                    /
                    len(
                        self.dataframe
                    )
                ),

            "leakage_inspection":
                leakage,

            "baseline_22_feature_comparison":
                baseline,

            "production_model_changed":
                False,

            "warning":
                "Validation on 81 recordings "
                "is still limited. Results should "
                "not be interpreted as clinical "
                "performance.",
        }

        with open(
            self.output_directory
            / "final_validation_report.json",
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                report,
                file,
                indent=4,
            )

        self.write_text_report(
            report,
            errors,
            fold_dataframe,
        )

    # ======================================================
    # Text Report
    # ======================================================

    def write_text_report(
        self,
        report: Dict,
        errors: pd.DataFrame,
        fold_dataframe: pd.DataFrame,
    ) -> None:

        metrics = report[
            "metrics"
        ]

        baseline = report[
            "baseline_22_feature_comparison"
        ]

        lines = []

        lines.append(
            "=" * 70
        )

        lines.append(
            "STEP 7 - ROBUST FINAL VALIDATION"
        )

        lines.append(
            "=" * 70
        )

        lines.append("")

        lines.append(
            "DATASET"
        )

        lines.append(
            f"Recordings : "
            f"{report['recordings']}"
        )

        lines.append(
            f"Features   : "
            f"{report['feature_count']}"
        )

        lines.append(
            f"Model      : "
            f"{report['model']}"
        )

        lines.append(
            f"Validation : "
            f"{report['validation_type']}"
        )

        lines.append(
            f"Repeats    : "
            f"{report['repeats']}"
        )

        lines.append("")

        lines.append(
            "FEATURES"
        )

        lines.append(
            "-" * 70
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
            "OVERALL OOF RESULTS"
        )

        lines.append(
            "-" * 70
        )

        lines.append(
            f"Accuracy          : "
            f"{metrics['accuracy']:.4f}"
        )

        lines.append(
            f"Balanced Accuracy : "
            f"{metrics['balanced_accuracy']:.4f}"
        )

        lines.append(
            f"Precision         : "
            f"{metrics['precision']:.4f}"
        )

        lines.append(
            f"Recall/Sensitivity: "
            f"{metrics['recall']:.4f}"
        )

        lines.append(
            f"Specificity       : "
            f"{metrics['specificity']:.4f}"
        )

        lines.append(
            f"F1                : "
            f"{metrics['f1']:.4f}"
        )

        lines.append(
            f"ROC-AUC           : "
            f"{metrics['roc_auc']:.4f}"
        )

        lines.append(
            f"NPV               : "
            f"{metrics['npv']:.4f}"
        )

        lines.append("")

        lines.append(
            "CONFUSION MATRIX"
        )

        lines.append(
            "-" * 70
        )

        lines.append(
            "                Predicted"
        )

        lines.append(
            "                HC    PD"
        )

        lines.append(
            f"Actual HC       "
            f"{metrics['tn']:4d}  "
            f"{metrics['fp']:4d}"
        )

        lines.append(
            f"Actual PD       "
            f"{metrics['fn']:4d}  "
            f"{metrics['tp']:4d}"
        )

        lines.append("")

        lines.append(
            "ERROR ANALYSIS"
        )

        lines.append(
            "-" * 70
        )

        lines.append(
            f"Errors     : "
            f"{report['error_count']}"
        )

        lines.append(
            f"Error rate : "
            f"{report['error_rate']:.4f}"
        )

        if not errors.empty:

            false_positive_count = int(
                (
                    errors[
                        "ErrorType"
                    ]
                    ==
                    "False Positive"
                ).sum()
            )

            false_negative_count = int(
                (
                    errors[
                        "ErrorType"
                    ]
                    ==
                    "False Negative"
                ).sum()
            )

            lines.append(
                f"False positives: "
                f"{false_positive_count}"
            )

            lines.append(
                f"False negatives: "
                f"{false_negative_count}"
            )

            lines.append("")

            for _, row in (
                errors.iterrows()
            ):

                lines.append(
                    f"{row['Recording']} | "
                    f"{row['ErrorType']} | "
                    f"PD probability="
                    f"{row['Probability_PD']:.4f} | "
                    f"confidence="
                    f"{row['Confidence']:.4f}"
                )

        lines.append("")

        lines.append(
            "CONFIDENCE"
        )

        lines.append(
            "-" * 70
        )

        confidence = report[
            "confidence"
        ]

        lines.append(
            f"Mean confidence: "
            f"{confidence['mean_confidence']:.4f}"
        )

        lines.append(
            f"Median confidence: "
            f"{confidence['median_confidence']:.4f}"
        )

        lines.append(
            f"Correct confidence: "
            f"{confidence['correct_mean_confidence']:.4f}"
        )

        lines.append(
            f"Incorrect confidence: "
            f"{confidence['incorrect_mean_confidence']:.4f}"
        )

        lines.append(
            f"High-confidence errors: "
            f"{confidence['high_confidence_errors']}"
        )

        lines.append("")

        lines.append(
            "22-FEATURE COMPARISON"
        )

        lines.append(
            "-" * 70
        )

        lines.append(
            f"22-feature accuracy: "
            f"{baseline['accuracy']:.4f}"
        )

        lines.append(
            f"12-feature accuracy: "
            f"{metrics['accuracy']:.4f}"
        )

        lines.append(
            f"22-feature ROC-AUC: "
            f"{baseline['roc_auc']:.4f}"
        )

        lines.append(
            f"12-feature ROC-AUC: "
            f"{metrics['roc_auc']:.4f}"
        )

        lines.append("")

        lines.append(
            "PARTICIPANT LEAKAGE"
        )

        lines.append(
            "-" * 70
        )

        lines.append(
            report[
                "leakage_inspection"
            ][
                "message"
            ]
        )

        lines.append("")

        lines.append(
            "IMPORTANT"
        )

        lines.append(
            "-" * 70
        )

        lines.append(
            "The production model.pkl was NOT "
            "replaced."
        )

        lines.append(
            "Validation results are based on "
            "81 recordings and should not be "
            "interpreted as clinical accuracy."
        )

        lines.append(
            "Independent external validation is "
            "required before clinical use."
        )

        lines.append("")

        lines.append(
            "=" * 70
        )

        with open(
            self.output_directory
            / "final_validation_report.txt",
            "w",
            encoding="utf-8",
        ) as file:

            file.write(
                "\n".join(
                    lines
                )
            )

    # ======================================================
    # Print Summary
    # ======================================================

    def print_summary(
        self,
        metrics: Dict,
        confidence: Dict,
        leakage: Dict,
        baseline: Dict,
        errors: pd.DataFrame,
        fold_dataframe: pd.DataFrame,
    ) -> None:

        print()

        print(
            "=" * 70
        )

        print(
            "STEP 7 - ROBUST FINAL VALIDATION COMPLETE"
        )

        print(
            "=" * 70
        )

        print()

        print(
            "MODEL"
        )

        print(
            f"Model             : "
            f"{self.best_model_name}"
        )

        print(
            f"Features          : "
            f"{len(self.selected_features)}"
        )

        print()

        print(
            "VALIDATION RESULTS"
        )

        print(
            "-" * 70
        )

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
            f"Recall/Sensitivity: "
            f"{metrics['recall']:.4f}"
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

        print()

        print(
            "CONFUSION MATRIX"
        )

        print(
            "-" * 70
        )

        print(
            "                Predicted"
        )

        print(
            "                HC    PD"
        )

        print(
            f"Actual HC       "
            f"{metrics['tn']:4d}  "
            f"{metrics['fp']:4d}"
        )

        print(
            f"Actual PD       "
            f"{metrics['fn']:4d}  "
            f"{metrics['tp']:4d}"
        )

        print()

        print(
            "ERROR ANALYSIS"
        )

        print(
            "-" * 70
        )

        print(
            f"Total errors    : "
            f"{len(errors)}"
        )

        if not errors.empty:

            false_positives = int(
                (
                    errors[
                        "ErrorType"
                    ]
                    ==
                    "False Positive"
                ).sum()
            )

            false_negatives = int(
                (
                    errors[
                        "ErrorType"
                    ]
                    ==
                    "False Negative"
                ).sum()
            )

            print(
                f"False positives : "
                f"{false_positives}"
            )

            print(
                f"False negatives : "
                f"{false_negatives}"
            )

        print()

        print(
            "CONFIDENCE"
        )

        print(
            "-" * 70
        )

        print(
            f"Mean confidence       : "
            f"{confidence['mean_confidence']:.4f}"
        )

        print(
            f"Incorrect confidence  : "
            f"{confidence['incorrect_mean_confidence']:.4f}"
        )

        print(
            f"High-confidence errors: "
            f"{confidence['high_confidence_errors']}"
        )

        print()

        print(
            "22 vs 12 FEATURES"
        )

        print(
            "-" * 70
        )

        print(
            f"22-feature accuracy : "
            f"{baseline['accuracy']:.4f}"
        )

        print(
            f"12-feature accuracy : "
            f"{metrics['accuracy']:.4f}"
        )

        print(
            f"22-feature ROC-AUC : "
            f"{baseline['roc_auc']:.4f}"
        )

        print(
            f"12-feature ROC-AUC : "
            f"{metrics['roc_auc']:.4f}"
        )

        print()

        print(
            "LEAKAGE CHECK"
        )

        print(
            "-" * 70
        )

        print(
            leakage[
                "message"
            ]
        )

        print()

        print(
            "PRODUCTION MODEL"
        )

        print(
            "-" * 70
        )

        print(
            "model.pkl was NOT changed."
        )

        print()

        print(
            "Reports saved to:"
        )

        print(
            self.output_directory.resolve()
        )

        print()

        print(
            "=" * 70
        )

    # ======================================================
    # Main Run
    # ======================================================

    def run(
        self,
    ) -> Dict:

        # --------------------------------------------------
        # Load
        # --------------------------------------------------

        self.load_dataset()

        self.load_selected_features()

        self.load_model_configuration()

        # --------------------------------------------------
        # Validate
        # --------------------------------------------------

        print()

        print(
            "=" * 70
        )

        print(
            "STEP 7 - ROBUST FINAL VALIDATION"
        )

        print(
            "=" * 70
        )

        print()

        print(
            f"Dataset: "
            f"{len(self.dataframe)} recordings"
        )

        print(
            f"Model: "
            f"{self.best_model_name}"
        )

        print(
            f"Features: "
            f"{len(self.selected_features)}"
        )

        print()

        self.validate_dataset()

        # --------------------------------------------------
        # Repeated CV
        # --------------------------------------------------

        (
            fold_dataframe,
            oof_dataframe,
        ) = self.repeated_validation()

        # --------------------------------------------------
        # Metrics
        # --------------------------------------------------

        metrics = (
            self.overall_oof_metrics(
                oof_dataframe
            )
        )

        # --------------------------------------------------
        # Errors
        # --------------------------------------------------

        errors = (
            self.error_analysis(
                oof_dataframe
            )
        )

        # --------------------------------------------------
        # Confidence
        # --------------------------------------------------

        confidence = (
            self.confidence_analysis(
                oof_dataframe
            )
        )

        # --------------------------------------------------
        # Leakage
        # --------------------------------------------------

        leakage = (
            self.inspect_participant_columns()
        )

        # --------------------------------------------------
        # Baseline
        # --------------------------------------------------

        baseline = (
            self.baseline_comparison()
        )

        # --------------------------------------------------
        # Save
        # --------------------------------------------------

        self.save_oof(
            oof_dataframe
        )

        self.save_fold_results(
            fold_dataframe
        )

        self.save_errors(
            errors
        )

        self.save_report(
            metrics,
            confidence,
            leakage,
            baseline,
            errors,
            fold_dataframe,
        )

        # --------------------------------------------------
        # Print
        # --------------------------------------------------

        self.print_summary(
            metrics,
            confidence,
            leakage,
            baseline,
            errors,
            fold_dataframe,
        )

        return {
            "metrics":
                metrics,

            "confidence":
                confidence,

            "errors":
                errors,

            "leakage":
                leakage,

            "baseline":
                baseline,
        }


# ==========================================================
# Standalone Execution
# ==========================================================

if __name__ == "__main__":

    validator = FinalValidator(
        csv_path=(
            "models/audio_training_features.csv"
        ),
        selected_features_path=(
            "models/selected_features.json"
        ),
        best_model_path=(
            "models/best_model_configuration.json"
        ),
        output_directory=(
            "models"
        ),
        random_state=42,
        folds=5,
        repeats=10,
    )

    try:

        validator.run()

    except Exception as exc:

        print()

        print(
            "=" * 70
        )

        print(
            "FINAL VALIDATION FAILED"
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
