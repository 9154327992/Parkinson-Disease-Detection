from pathlib import Path
from typing import Dict, List, Tuple

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

# ----------------------------------------------------------
# Threshold range
# ----------------------------------------------------------

THRESHOLDS = [
    0.20,
    0.25,
    0.30,
    0.35,
    0.40,
    0.45,
    0.50,
    0.55,
    0.60,
    0.65,
    0.70,
    0.75,
    0.80,
]


# ==========================================================
# Threshold Optimizer
# ==========================================================

class ThresholdOptimizer:
    """
    Step 8 threshold optimization and error analysis.
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

        self.folds = folds

        self.repeats = repeats

        self.dataframe = None

        self.selected_features = []

        self.best_model_name = (
            "HistGradientBoosting"
        )

        self.prediction_dataframe = None

        self.threshold_dataframe = None

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
                "Run Step 3 / Step 4 first."
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
                "Selected feature file not found:\n"
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

        # --------------------------------------------------
        # Support several possible Step-5 JSON structures.
        # --------------------------------------------------

        if features is None:

            selected = data.get(
                "selected_features"
            )

            if isinstance(
                selected,
                list,
            ):

                features = selected

        if features is None:

            result = data.get(
                "selected_feature_set"
            )

            if isinstance(
                result,
                dict,
            ):

                features = result.get(
                    "features"
                )

        if not isinstance(
            features,
            list,
        ):

            raise ValueError(
                "Could not find a valid "
                "selected feature list in:\n"
                f"{self.selected_features_path}"
            )

        missing = [
            feature
            for feature in features
            if feature not in self.dataframe.columns
        ]

        if missing:

            raise ValueError(
                "Selected features missing "
                f"from dataset: {missing}"
            )

        self.selected_features = (
            features
        )

        return features

    # ======================================================
    # Load Model Configuration
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
                "best_model_configuration.json "
                "was not found."
            )

            print(
                "Using HistGradientBoosting "
                "from Step 6."
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
    # Create Model
    # ======================================================

    def create_model(
        self,
    ):

        """
        Recreate the Step-6 HistGradientBoosting model.

        This is intentionally recreated inside each
        validation fold to prevent preprocessing leakage.
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
    # Generate OOF Probabilities
    # ======================================================

    def generate_oof_predictions(
        self,
    ) -> pd.DataFrame:

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
            self.folds,
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

        # --------------------------------------------------
        # Accumulate probabilities from every repetition.
        # --------------------------------------------------

        probability_sum = np.zeros(
            len(y),
            dtype=float,
        )

        probability_count = np.zeros(
            len(y),
            dtype=float,
        )

        print()

        print(
            "GENERATING OUT-OF-FOLD "
            "PROBABILITIES"
        )

        print(
            "-" * 70
        )

        split_number = 0

        for (
            train_indices,
            test_indices,
        ) in cv.split(
            X,
            y,
        ):

            split_number += 1

            model = (
                self.create_model()
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

            model.fit(
                X_train,
                y_train,
            )

            probabilities = (
                model.predict_proba(
                    X_test
                )[:, 1]
            )

            probability_sum[
                test_indices
            ] += probabilities

            probability_count[
                test_indices
            ] += 1

            print(
                f"Split "
                f"{split_number:02d}/"
                f"{folds * self.repeats:02d}"
            )

        average_probabilities = (
            probability_sum
            /
            np.maximum(
                probability_count,
                1,
            )
        )

        prediction_dataframe = (
            pd.DataFrame(
                {
                    "Index":
                        np.arange(
                            len(y)
                        ),

                    "Actual":
                        y.values,

                    "Probability_PD":
                        average_probabilities,
                }
            )
        )

        prediction_dataframe[
            "Probability_HC"
        ] = (
            1.0
            -
            prediction_dataframe[
                "Probability_PD"
            ]
        )

        self.prediction_dataframe = (
            prediction_dataframe
        )

        return prediction_dataframe

    # ======================================================
    # Calculate Threshold Metrics
    # ======================================================

    @staticmethod
    def calculate_threshold_metrics(
        y_true,
        probabilities,
        threshold,
    ) -> Dict:

        predictions = (
            probabilities
            >= threshold
        ).astype(
            int
        )

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

        # --------------------------------------------------
        # Clinical-style cost.
        #
        # False negative is weighted more heavily because
        # missing a PD recording is more undesirable for
        # a screening-oriented system.
        #
        # This is NOT a clinical decision rule.
        # --------------------------------------------------

        cost = (
            (5 * fn)
            +
            (1 * fp)
        )

        youden = (
            recall
            +
            specificity
            -
            1.0
        )

        return {
            "Threshold":
                float(
                    threshold
                ),

            "Accuracy":
                float(
                    accuracy
                ),

            "BalancedAccuracy":
                float(
                    balanced
                ),

            "Precision":
                float(
                    precision
                ),

            "Recall":
                float(
                    recall
                ),

            "Sensitivity":
                float(
                    recall
                ),

            "Specificity":
                float(
                    specificity
                ),

            "F1":
                float(
                    f1
                ),

            "ROCAUC":
                float(
                    auc
                ),

            "TN":
                tn,

            "FP":
                fp,

            "FN":
                fn,

            "TP":
                tp,

            "FalseNegativeCost":
                int(
                    cost
                ),

            "YoudenJ":
                float(
                    youden
                ),
        }

    # ======================================================
    # Evaluate All Thresholds
    # ======================================================

    def evaluate_thresholds(
        self,
    ) -> pd.DataFrame:

        if self.prediction_dataframe is None:

            raise RuntimeError(
                "OOF predictions have not "
                "been generated."
            )

        y_true = (
            self.prediction_dataframe[
                "Actual"
            ].values
        )

        probabilities = (
            self.prediction_dataframe[
                "Probability_PD"
            ].values
        )

        rows = []

        print()

        print(
            "THRESHOLD ANALYSIS"
        )

        print(
            "-" * 90
        )

        print(
            "Threshold | Accuracy | Balanced | "
            "Precision | Recall | Specificity | "
            "F1 | FN | FP"
        )

        for threshold in THRESHOLDS:

            metrics = (
                self.calculate_threshold_metrics(
                    y_true,
                    probabilities,
                    threshold,
                )
            )

            rows.append(
                metrics
            )

            print(
                f"{threshold:8.2f} | "
                f"{metrics['Accuracy']:.4f} | "
                f"{metrics['BalancedAccuracy']:.4f} | "
                f"{metrics['Precision']:.4f} | "
                f"{metrics['Recall']:.4f} | "
                f"{metrics['Specificity']:.4f} | "
                f"{metrics['F1']:.4f} | "
                f"{metrics['FN']:2d} | "
                f"{metrics['FP']:2d}"
            )

        dataframe = pd.DataFrame(
            rows
        )

        self.threshold_dataframe = (
            dataframe
        )

        return dataframe

    # ======================================================
    # Select Best Threshold
    # ======================================================

    def select_threshold(
        self,
        dataframe: pd.DataFrame,
    ) -> Dict:

        # --------------------------------------------------
        # Candidate 1:
        # Highest F1
        # --------------------------------------------------

        best_f1_row = (
            dataframe.loc[
                dataframe[
                    "F1"
                ].idxmax()
            ]
        )

        # --------------------------------------------------
        # Candidate 2:
        # Highest balanced accuracy
        # --------------------------------------------------

        best_balanced_row = (
            dataframe.loc[
                dataframe[
                    "BalancedAccuracy"
                ].idxmax()
            ]
        )

        # --------------------------------------------------
        # Candidate 3:
        # Highest Youden J
        # --------------------------------------------------

        best_youden_row = (
            dataframe.loc[
                dataframe[
                    "YoudenJ"
                ].idxmax()
            ]
        )

        # --------------------------------------------------
        # Screening-oriented candidates.
        #
        # We prefer sensitivity >= 70%.
        # If possible, retain specificity >= 70%.
        # --------------------------------------------------

        screening_candidates = (
            dataframe[
                (
                    dataframe[
                        "Sensitivity"
                    ]
                    >= 0.70
                )
                &
                (
                    dataframe[
                        "Specificity"
                    ]
                    >= 0.70
                )
            ]
        )

        if (
            not screening_candidates.empty
        ):

            best_screening_row = (
                screening_candidates
                .sort_values(
                    [
                        "F1",
                        "Sensitivity",
                        "BalancedAccuracy",
                    ],
                    ascending=False,
                )
                .iloc[0]
            )

        else:

            # ----------------------------------------------
            # If no threshold reaches both targets,
            # maximize sensitivity first.
            # ----------------------------------------------

            best_screening_row = (
                dataframe
                .sort_values(
                    [
                        "Sensitivity",
                        "F1",
                        "Specificity",
                    ],
                    ascending=False,
                )
                .iloc[0]
            )

        # --------------------------------------------------
        # Cost-based threshold.
        # --------------------------------------------------

        best_cost_row = (
            dataframe.loc[
                dataframe[
                    "FalseNegativeCost"
                ].idxmin()
            ]
        )

        # --------------------------------------------------
        # Recommended threshold.
        #
        # For a Parkinson screening model, prioritize
        # balanced performance while preventing excessive
        # false negatives.
        # --------------------------------------------------

        recommended = (
            best_screening_row
        )

        recommendation = {
            "threshold":
                float(
                    recommended[
                        "Threshold"
                    ]
                ),

            "accuracy":
                float(
                    recommended[
                        "Accuracy"
                    ]
                ),

            "balanced_accuracy":
                float(
                    recommended[
                        "BalancedAccuracy"
                    ]
                ),

            "precision":
                float(
                    recommended[
                        "Precision"
                    ]
                ),

            "sensitivity":
                float(
                    recommended[
                        "Sensitivity"
                    ]
                ),

            "specificity":
                float(
                    recommended[
                        "Specificity"
                    ]
                ),

            "f1":
                float(
                    recommended[
                        "F1"
                    ]
                ),

            "roc_auc":
                float(
                    recommended[
                        "ROCAUC"
                    ]
                ),

            "false_negatives":
                int(
                    recommended[
                        "FN"
                    ]
                ),

            "false_positives":
                int(
                    recommended[
                        "FP"
                    ]
                ),

            "selection_rule":
                (
                    "Highest F1 among thresholds "
                    "with sensitivity >= 0.70 and "
                    "specificity >= 0.70. If no threshold "
                    "satisfies both conditions, maximize "
                    "sensitivity first."
                ),
        }

        return {
            "recommended":
                recommendation,

            "best_f1":
                self.row_to_dict(
                    best_f1_row
                ),

            "best_balanced_accuracy":
                self.row_to_dict(
                    best_balanced_row
                ),

            "best_youden":
                self.row_to_dict(
                    best_youden_row
                ),

            "best_false_negative_cost":
                self.row_to_dict(
                    best_cost_row
                ),
        }

    # ======================================================
    # Convert Row
    # ======================================================

    @staticmethod
    def row_to_dict(
        row,
    ) -> Dict:

        result = {}

        for key, value in (
            row.to_dict().items()
        ):

            if isinstance(
                value,
                np.integer,
            ):

                value = int(
                    value
                )

            elif isinstance(
                value,
                np.floating,
            ):

                value = float(
                    value
                )

            result[
                key
            ] = value

        return result

    # ======================================================
    # Apply Recommended Threshold
    # ======================================================

    def apply_recommended_threshold(
        self,
        recommendation: Dict,
    ) -> pd.DataFrame:

        threshold = (
            recommendation[
                "threshold"
            ]
        )

        dataframe = (
            self.prediction_dataframe
            .copy()
        )

        dataframe[
            "Prediction"
        ] = (
            dataframe[
                "Probability_PD"
            ]
            >= threshold
        ).astype(
            int
        )

        dataframe[
            "Correct"
        ] = (
            dataframe[
                "Actual"
            ]
            ==
            dataframe[
                "Prediction"
            ]
        )

        dataframe[
            "ActualClass"
        ] = dataframe[
            "Actual"
        ].map(
            {
                0: "HC",
                1: "PD",
            }
        )

        dataframe[
            "PredictedClass"
        ] = dataframe[
            "Prediction"
        ].map(
            {
                0: "HC",
                1: "PD",
            }
        )

        dataframe[
            "ErrorType"
        ] = "Correct"

        dataframe.loc[
            (
                (
                    dataframe[
                        "Actual"
                    ]
                    == 0
                )
                &
                (
                    dataframe[
                        "Prediction"
                    ]
                    == 1
                )
            ),
            "ErrorType",
        ] = "False Positive"

        dataframe.loc[
            (
                (
                    dataframe[
                        "Actual"
                    ]
                    == 1
                )
                &
                (
                    dataframe[
                        "Prediction"
                    ]
                    == 0
                )
            ),
            "ErrorType",
        ] = "False Negative"

        dataframe[
            "Confidence"
        ] = np.maximum(
            dataframe[
                "Probability_PD"
            ],
            dataframe[
                "Probability_HC"
            ],
        )

        # --------------------------------------------------
        # Add filename if available.
        # --------------------------------------------------

        possible_columns = [
            "filename",
            "file",
            "audio_file",
            "recording",
            "name",
            "patient_name",
        ]

        for column in possible_columns:

            if column in (
                self.dataframe.columns
            ):

                dataframe[
                    "Recording"
                ] = (
                    self.dataframe[
                        column
                    ]
                    .astype(
                        str
                    )
                    .values
                )

                break

        if "Recording" not in (
            dataframe.columns
        ):

            dataframe[
                "Recording"
            ] = dataframe[
                "Index"
            ].apply(
                lambda value:
                f"recording_{int(value):03d}"
            )

        return dataframe

    # ======================================================
    # Error Analysis
    # ======================================================

    def analyze_errors(
        self,
        prediction_dataframe: pd.DataFrame,
    ) -> pd.DataFrame:

        errors = (
            prediction_dataframe[
                prediction_dataframe[
                    "ErrorType"
                ]
                != "Correct"
            ]
            .copy()
        )

        if errors.empty:

            return errors

        return errors[
            [
                "Index",
                "Recording",
                "ActualClass",
                "PredictedClass",
                "ErrorType",
                "Probability_PD",
                "Probability_HC",
                "Confidence",
            ]
        ].sort_values(
            by="Confidence",
            ascending=False,
        )

    # ======================================================
    # Confidence Analysis
    # ======================================================

    def confidence_analysis(
        self,
        prediction_dataframe: pd.DataFrame,
    ) -> Dict:

        confidence = (
            prediction_dataframe[
                "Confidence"
            ]
        )

        correct = (
            prediction_dataframe[
                "Correct"
            ]
        )

        errors = (
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
                ),

            "incorrect_mean_confidence":
                float(
                    confidence[
                        errors
                    ].mean()
                ),

            "high_confidence_threshold":
                0.80,

            "high_confidence_predictions":
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
                        errors
                    ).sum()
                ),

            "low_confidence_predictions":
                int(
                    (
                        confidence
                        < 0.60
                    ).sum()
                ),

            "low_confidence_errors":
                int(
                    (
                        (
                            confidence
                            < 0.60
                        )
                        &
                        errors
                    ).sum()
                ),
        }

    # ======================================================
    # Threshold Stability
    # ======================================================

    def threshold_stability(
        self,
        dataframe: pd.DataFrame,
    ) -> Dict:

        # --------------------------------------------------
        # Identify thresholds that satisfy useful ranges.
        # --------------------------------------------------

        acceptable = dataframe[
            (
                dataframe[
                    "Sensitivity"
                ]
                >= 0.70
            )
            &
            (
                dataframe[
                    "Specificity"
                ]
                >= 0.70
            )
        ]

        if acceptable.empty:

            return {
                "stable_range_found":
                    False,

                "thresholds":
                    [],

                "message":
                    (
                        "No tested threshold achieved "
                        "both sensitivity >= 70% and "
                        "specificity >= 70%."
                    ),
            }

        values = (
            acceptable[
                "Threshold"
            ]
            .tolist()
        )

        return {
            "stable_range_found":
                True,

            "thresholds":
                values,

            "minimum_threshold":
                float(
                    min(
                        values
                    )
                ),

            "maximum_threshold":
                float(
                    max(
                        values
                    )
                ),

            "message":
                (
                    "These thresholds achieved at least "
                    "70% sensitivity and 70% specificity "
                    "on the current out-of-fold dataset."
                ),
        }

    # ======================================================
    # Save Reports
    # ======================================================

    def save_reports(
        self,
        threshold_dataframe: pd.DataFrame,
        prediction_dataframe: pd.DataFrame,
        error_dataframe: pd.DataFrame,
        report: Dict,
    ) -> None:

        self.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        threshold_dataframe.to_csv(
            self.output_directory
            / "threshold_analysis.csv",
            index=False,
        )

        prediction_dataframe.to_csv(
            self.output_directory
            / "threshold_oof_predictions.csv",
            index=False,
        )

        error_dataframe.to_csv(
            self.output_directory
            / "threshold_errors.csv",
            index=False,
        )

        with open(
            self.output_directory
            / "threshold_optimization_report.json",
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
            error_dataframe,
        )

    # ======================================================
    # Text Report
    # ======================================================

    def write_text_report(
        self,
        report: Dict,
        errors: pd.DataFrame,
    ) -> None:

        recommendation = (
            report[
                "recommendation"
            ][
                "recommended"
            ]
        )

        lines = []

        lines.append(
            "=" * 70
        )

        lines.append(
            "STEP 8 - THRESHOLD OPTIMIZATION"
        )

        lines.append(
            "=" * 70
        )

        lines.append("")

        lines.append(
            "MODEL"
        )

        lines.append(
            f"Model    : "
            f"{report['model']}"
        )

        lines.append(
            f"Features : "
            f"{report['feature_count']}"
        )

        lines.append(
            f"Samples  : "
            f"{report['recordings']}"
        )

        lines.append("")

        lines.append(
            "RECOMMENDED THRESHOLD"
        )

        lines.append(
            "-" * 70
        )

        lines.append(
            f"Threshold          : "
            f"{recommendation['threshold']:.2f}"
        )

        lines.append(
            f"Accuracy           : "
            f"{recommendation['accuracy']:.4f}"
        )

        lines.append(
            f"Balanced Accuracy  : "
            f"{recommendation['balanced_accuracy']:.4f}"
        )

        lines.append(
            f"Precision          : "
            f"{recommendation['precision']:.4f}"
        )

        lines.append(
            f"Sensitivity        : "
            f"{recommendation['sensitivity']:.4f}"
        )

        lines.append(
            f"Specificity        : "
            f"{recommendation['specificity']:.4f}"
        )

        lines.append(
            f"F1                 : "
            f"{recommendation['f1']:.4f}"
        )

        lines.append(
            f"ROC-AUC            : "
            f"{recommendation['roc_auc']:.4f}"
        )

        lines.append(
            f"False negatives    : "
            f"{recommendation['false_negatives']}"
        )

        lines.append(
            f"False positives    : "
            f"{recommendation['false_positives']}"
        )

        lines.append("")

        lines.append(
            "THRESHOLD RANGE"
        )

        lines.append(
            "-" * 70
        )

        stability = (
            report[
                "threshold_stability"
            ]
        )

        lines.append(
            stability[
                "message"
            ]
        )

        if stability.get(
            "stable_range_found"
        ):

            lines.append(
                f"Minimum threshold: "
                f"{stability['minimum_threshold']:.2f}"
            )

            lines.append(
                f"Maximum threshold: "
                f"{stability['maximum_threshold']:.2f}"
            )

        lines.append("")

        lines.append(
            "ERROR ANALYSIS"
        )

        lines.append(
            "-" * 70
        )

        lines.append(
            f"Total errors: "
            f"{len(errors)}"
        )

        if not errors.empty:

            fp = int(
                (
                    errors[
                        "ErrorType"
                    ]
                    ==
                    "False Positive"
                ).sum()
            )

            fn = int(
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
                f"{fp}"
            )

            lines.append(
                f"False negatives: "
                f"{fn}"
            )

            lines.append("")

            lines.append(
                "ERRORS"
            )

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

        confidence = (
            report[
                "confidence"
            ]
        )

        lines.append(
            f"Mean confidence: "
            f"{confidence['mean_confidence']:.4f}"
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
            "IMPORTANT"
        )

        lines.append(
            "-" * 70
        )

        lines.append(
            "model.pkl was NOT changed."
        )

        lines.append(
            "The recommended threshold is a "
            "validation candidate only."
        )

        lines.append(
            "It must be validated again before "
            "being used in production."
        )

        lines.append("")

        lines.append(
            "=" * 70
        )

        with open(
            self.output_directory
            / "threshold_optimization_report.txt",
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
        threshold_dataframe: pd.DataFrame,
        recommendation: Dict,
        confidence: Dict,
        errors: pd.DataFrame,
    ) -> None:

        recommended = (
            recommendation[
                "recommended"
            ]
        )

        print()

        print(
            "=" * 70
        )

        print(
            "STEP 8 - THRESHOLD OPTIMIZATION COMPLETE"
        )

        print(
            "=" * 70
        )

        print()

        print(
            "RECOMMENDED THRESHOLD"
        )

        print(
            "-" * 70
        )

        print(
            f"Threshold          : "
            f"{recommended['threshold']:.2f}"
        )

        print(
            f"Accuracy           : "
            f"{recommended['accuracy']:.4f}"
        )

        print(
            f"Balanced Accuracy  : "
            f"{recommended['balanced_accuracy']:.4f}"
        )

        print(
            f"Precision          : "
            f"{recommended['precision']:.4f}"
        )

        print(
            f"Sensitivity        : "
            f"{recommended['sensitivity']:.4f}"
        )

        print(
            f"Specificity        : "
            f"{recommended['specificity']:.4f}"
        )

        print(
            f"F1                 : "
            f"{recommended['f1']:.4f}"
        )

        print(
            f"ROC-AUC            : "
            f"{recommended['roc_auc']:.4f}"
        )

        print()

        print(
            "THRESHOLD COMPARISON"
        )

        print(
            "-" * 70
        )

        print(
            threshold_dataframe[
                [
                    "Threshold",
                    "Accuracy",
                    "BalancedAccuracy",
                    "Sensitivity",
                    "Specificity",
                    "F1",
                    "FN",
                    "FP",
                ]
            ].to_string(
                index=False
            )
        )

        print()

        print(
            "ERROR ANALYSIS"
        )

        print(
            "-" * 70
        )

        print(
            f"Total errors     : "
            f"{len(errors)}"
        )

        if not errors.empty:

            fp = int(
                (
                    errors[
                        "ErrorType"
                    ]
                    ==
                    "False Positive"
                ).sum()
            )

            fn = int(
                (
                    errors[
                        "ErrorType"
                    ]
                    ==
                    "False Negative"
                ).sum()
            )

            print(
                f"False positives  : "
                f"{fp}"
            )

            print(
                f"False negatives  : "
                f"{fn}"
            )

        print()

        print(
            "CONFIDENCE"
        )

        print(
            "-" * 70
        )

        print(
            f"Mean confidence:"
            f" {confidence['mean_confidence']:.4f}"
        )

        print(
            f"Incorrect confidence:"
            f" {confidence['incorrect_mean_confidence']:.4f}"
        )

        print(
            f"High-confidence errors:"
            f" {confidence['high_confidence_errors']}"
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
        # Load everything
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
            "STEP 8 - THRESHOLD OPTIMIZATION"
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
            f"Features: "
            f"{len(self.selected_features)}"
        )

        print(
            f"Model   : "
            f"{self.best_model_name}"
        )

        print()

        print(
            "Selected features:"
        )

        for index, feature in enumerate(
            self.selected_features,
            start=1,
        ):

            print(
                f"    {index:02d}. "
                f"{feature}"
            )

        # --------------------------------------------------
        # Generate probabilities
        # --------------------------------------------------

        self.generate_oof_predictions()

        # --------------------------------------------------
        # Evaluate thresholds
        # --------------------------------------------------

        threshold_dataframe = (
            self.evaluate_thresholds()
        )

        # --------------------------------------------------
        # Select threshold
        # --------------------------------------------------

        recommendation = (
            self.select_threshold(
                threshold_dataframe
            )
        )

        recommended = (
            recommendation[
                "recommended"
            ]
        )

        # --------------------------------------------------
        # Apply threshold
        # --------------------------------------------------

        prediction_dataframe = (
            self.apply_recommended_threshold(
                recommended
            )
        )

        # --------------------------------------------------
        # Error analysis
        # --------------------------------------------------

        errors = (
            self.analyze_errors(
                prediction_dataframe
            )
        )

        # --------------------------------------------------
        # Confidence
        # --------------------------------------------------

        confidence = (
            self.confidence_analysis(
                prediction_dataframe
            )
        )

        # --------------------------------------------------
        # Stability
        # --------------------------------------------------

        stability = (
            self.threshold_stability(
                threshold_dataframe
            )
        )

        # --------------------------------------------------
        # Build report
        # --------------------------------------------------

        report = {
            "step":
                8,

            "model":
                self.best_model_name,

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

            "thresholds_tested":
                THRESHOLDS,

            "recommendation":
                recommendation,

            "threshold_stability":
                stability,

            "confidence":
                confidence,

            "error_count":
                int(
                    len(
                        errors
                    )
                ),

            "false_positive_count":
                int(
                    (
                        errors[
                            "ErrorType"
                        ]
                        ==
                        "False Positive"
                    ).sum()
                )
                if not errors.empty
                else 0,

            "false_negative_count":
                int(
                    (
                        errors[
                            "ErrorType"
                        ]
                        ==
                        "False Negative"
                    ).sum()
                )
                if not errors.empty
                else 0,

            "production_model_changed":
                False,

            "warning":
                (
                    "Threshold was optimized using "
                    "out-of-fold validation predictions. "
                    "This threshold is not a clinical "
                    "diagnostic threshold."
                ),
        }

        # --------------------------------------------------
        # Save
        # --------------------------------------------------

        self.save_reports(
            threshold_dataframe,
            prediction_dataframe,
            errors,
            report,
        )

        # --------------------------------------------------
        # Print
        # --------------------------------------------------

        self.print_summary(
            threshold_dataframe,
            recommendation,
            confidence,
            errors,
        )

        return report


# ==========================================================
# Standalone Execution
# ==========================================================

if __name__ == "__main__":

    optimizer = (
        ThresholdOptimizer(
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
    )

    try:

        optimizer.run()

    except Exception as exc:

        print()

        print(
            "=" * 70
        )

        print(
            "THRESHOLD OPTIMIZATION FAILED"
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
