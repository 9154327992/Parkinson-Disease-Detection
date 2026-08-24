from pathlib import Path
from typing import Dict, List, Tuple

import json
import warnings

import numpy as np
import pandas as pd

from sklearn.ensemble import (
    RandomForestClassifier,
    ExtraTreesClassifier,
    GradientBoostingClassifier,
    HistGradientBoostingClassifier,
    RandomForestClassifier,
    VotingClassifier,
    StackingClassifier,
    AdaBoostClassifier,
)

from sklearn.impute import SimpleImputer

from sklearn.linear_model import (
    LogisticRegression,
)

from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from sklearn.model_selection import (
    StratifiedKFold,
    cross_validate,
)

from sklearn.pipeline import Pipeline

from sklearn.preprocessing import (
    StandardScaler,
)

from sklearn.svm import (
    SVC,
)

from sklearn.neighbors import (
    KNeighborsClassifier,
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

DEFAULT_OUTPUT_DIRECTORY = (
    "models"
)


# ==========================================================
# Model Optimizer
# ==========================================================

class ModelOptimizer:
    """
    Optimize machine-learning models using the
    feature set selected in Step 5.
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
        output_directory: str = (
            DEFAULT_OUTPUT_DIRECTORY
        ),
        random_state: int = RANDOM_STATE,
    ):

        self.csv_path = Path(
            csv_path
        )

        self.selected_features_path = (
            Path(
                selected_features_path
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

        self.dataframe = None

        self.selected_features = []

        self.results = []

    # ======================================================
    # Load Dataset
    # ======================================================

    def load_dataset(
        self,
    ) -> pd.DataFrame:

        if not self.csv_path.exists():

            raise FileNotFoundError(
                "Training feature dataset not found:\n"
                f"{self.csv_path.resolve()}\n\n"
                "Run:\n"
                "python -m app.ml.train_model"
            )

        dataframe = pd.read_csv(
            self.csv_path
        )

        if dataframe.empty:

            raise ValueError(
                "Training feature dataset is empty."
            )

        if TARGET_COLUMN not in (
            dataframe.columns
        ):

            raise ValueError(
                "Dataset does not contain "
                "'status' target column."
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
                "Run Step 5 first:\n"
                "python -m app.ml.feature_selection"
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
                "selected_features.json does not "
                "contain a valid 'features' list."
            )

        if len(features) < 2:

            raise ValueError(
                "At least two features are "
                "required for model training."
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
    # Validate Dataset
    # ======================================================

    def validate_dataset(
        self,
    ) -> None:

        if self.dataframe is None:

            raise RuntimeError(
                "Dataset has not been loaded."
            )

        if not self.selected_features:

            raise RuntimeError(
                "Selected features have not "
                "been loaded."
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
                "missing or invalid values."
            )

        labels = labels.astype(
            int
        )

        unique = sorted(
            labels.unique().tolist()
        )

        if unique != [
            HEALTHY,
            PARKINSON,
        ]:

            raise ValueError(
                "Expected target labels "
                "[0, 1]. Found: "
                f"{unique}"
            )

        if (
            len(self.dataframe)
            < 20
        ):

            raise ValueError(
                "Dataset is too small for "
                "the optimization experiment."
            )

    # ======================================================
    # Create Model Pipeline
    # ======================================================

    def pipeline(
        self,
        estimator,
        scaling: bool = True,
    ):

        steps = [
            (
                "imputer",
                SimpleImputer(
                    strategy="median"
                ),
            )
        ]

        if scaling:

            steps.append(
                (
                    "scaler",
                    StandardScaler(),
                )
            )

        steps.append(
            (
                "model",
                estimator,
            )
        )

        return Pipeline(
            steps=steps
        )

    # ======================================================
    # Candidate Models
    # ======================================================

    def candidate_models(
        self,
    ) -> Dict:

        models = {}

        # --------------------------------------------------
        # Logistic Regression
        # --------------------------------------------------

        models[
            "LogisticRegression"
        ] = self.pipeline(
            LogisticRegression(
                C=1.0,
                max_iter=5000,
                class_weight="balanced",
                random_state=self.random_state,
            )
        )

        models[
            "LogisticRegression_C01"
        ] = self.pipeline(
            LogisticRegression(
                C=0.1,
                max_iter=5000,
                class_weight="balanced",
                random_state=self.random_state,
            )
        )

        models[
            "LogisticRegression_C10"
        ] = self.pipeline(
            LogisticRegression(
                C=10.0,
                max_iter=5000,
                class_weight="balanced",
                random_state=self.random_state,
            )
        )

        # --------------------------------------------------
        # Random Forest
        # --------------------------------------------------

        models[
            "RandomForest_300"
        ] = self.pipeline(
            RandomForestClassifier(
                n_estimators=300,
                max_depth=None,
                min_samples_leaf=1,
                max_features="sqrt",
                class_weight="balanced",
                random_state=self.random_state,
                n_jobs=-1,
            ),
            scaling=False,
        )

        models[
            "RandomForest_500"
        ] = self.pipeline(
            RandomForestClassifier(
                n_estimators=500,
                max_depth=None,
                min_samples_leaf=1,
                max_features="sqrt",
                class_weight="balanced",
                random_state=self.random_state,
                n_jobs=-1,
            ),
            scaling=False,
        )

        models[
            "RandomForest_depth8"
        ] = self.pipeline(
            RandomForestClassifier(
                n_estimators=500,
                max_depth=8,
                min_samples_leaf=1,
                max_features="sqrt",
                class_weight="balanced",
                random_state=self.random_state,
                n_jobs=-1,
            ),
            scaling=False,
        )

        models[
            "RandomForest_leaf2"
        ] = self.pipeline(
            RandomForestClassifier(
                n_estimators=500,
                max_depth=None,
                min_samples_leaf=2,
                max_features="sqrt",
                class_weight="balanced",
                random_state=self.random_state,
                n_jobs=-1,
            ),
            scaling=False,
        )

        # --------------------------------------------------
        # Extra Trees
        # --------------------------------------------------

        models[
            "ExtraTrees_300"
        ] = self.pipeline(
            ExtraTreesClassifier(
                n_estimators=300,
                max_depth=None,
                min_samples_leaf=1,
                max_features="sqrt",
                class_weight="balanced",
                random_state=self.random_state,
                n_jobs=-1,
            ),
            scaling=False,
        )

        models[
            "ExtraTrees_500"
        ] = self.pipeline(
            ExtraTreesClassifier(
                n_estimators=500,
                max_depth=None,
                min_samples_leaf=1,
                max_features="sqrt",
                class_weight="balanced",
                random_state=self.random_state,
                n_jobs=-1,
            ),
            scaling=False,
        )

        models[
            "ExtraTrees_depth8"
        ] = self.pipeline(
            ExtraTreesClassifier(
                n_estimators=500,
                max_depth=8,
                min_samples_leaf=1,
                max_features="sqrt",
                class_weight="balanced",
                random_state=self.random_state,
                n_jobs=-1,
            ),
            scaling=False,
        )

        models[
            "ExtraTrees_leaf2"
        ] = self.pipeline(
            ExtraTreesClassifier(
                n_estimators=500,
                max_depth=None,
                min_samples_leaf=2,
                max_features="sqrt",
                class_weight="balanced",
                random_state=self.random_state,
                n_jobs=-1,
            ),
            scaling=False,
        )

        # --------------------------------------------------
        # Gradient Boosting
        # --------------------------------------------------

        models[
            "GradientBoosting"
        ] = self.pipeline(
            GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.05,
                max_depth=2,
                random_state=self.random_state,
            ),
            scaling=False,
        )

        models[
            "GradientBoosting_deeper"
        ] = self.pipeline(
            GradientBoostingClassifier(
                n_estimators=150,
                learning_rate=0.05,
                max_depth=3,
                random_state=self.random_state,
            ),
            scaling=False,
        )

        models[
            "GradientBoosting_fast"
        ] = self.pipeline(
            GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=2,
                random_state=self.random_state,
            ),
            scaling=False,
        )

        # --------------------------------------------------
        # HistGradientBoosting
        # --------------------------------------------------

        models[
            "HistGradientBoosting"
        ] = self.pipeline(
            HistGradientBoostingClassifier(
                max_iter=150,
                learning_rate=0.05,
                max_leaf_nodes=15,
                l2_regularization=1.0,
                random_state=self.random_state,
            ),
            scaling=False,
        )

        models[
            "HistGradientBoosting_fast"
        ] = self.pipeline(
            HistGradientBoostingClassifier(
                max_iter=100,
                learning_rate=0.1,
                max_leaf_nodes=15,
                l2_regularization=1.0,
                random_state=self.random_state,
            ),
            scaling=False,
        )

        # --------------------------------------------------
        # SVM
        # --------------------------------------------------

        models[
            "SVM_RBF"
        ] = self.pipeline(
            SVC(
                C=1.0,
                kernel="rbf",
                gamma="scale",
                probability=True,
                class_weight="balanced",
                random_state=self.random_state,
            )
        )

        models[
            "SVM_RBF_C10"
        ] = self.pipeline(
            SVC(
                C=10.0,
                kernel="rbf",
                gamma="scale",
                probability=True,
                class_weight="balanced",
                random_state=self.random_state,
            )
        )

        models[
            "SVM_Linear"
        ] = self.pipeline(
            SVC(
                C=1.0,
                kernel="linear",
                probability=True,
                class_weight="balanced",
                random_state=self.random_state,
            )
        )

        # --------------------------------------------------
        # KNN
        # --------------------------------------------------

        models[
            "KNN_5"
        ] = self.pipeline(
            KNeighborsClassifier(
                n_neighbors=5,
                weights="distance",
            )
        )

        models[
            "KNN_7"
        ] = self.pipeline(
            KNeighborsClassifier(
                n_neighbors=7,
                weights="distance",
            )
        )

        return models

    # ======================================================
    # Cross Validation
    # ======================================================

    def evaluate_model(
        self,
        name: str,
        model,
        X: pd.DataFrame,
        y: pd.Series,
    ) -> Dict:

        class_counts = (
            y.value_counts()
        )

        minimum_class = int(
            class_counts.min()
        )

        folds = min(
            5,
            minimum_class,
        )

        if folds < 2:

            raise ValueError(
                "Insufficient samples for "
                "stratified cross-validation."
            )

        cv = StratifiedKFold(
            n_splits=folds,
            shuffle=True,
            random_state=self.random_state,
        )

        scoring = {
            "accuracy":
                "accuracy",

            "balanced_accuracy":
                "balanced_accuracy",

            "precision":
                "precision",

            "recall":
                "recall",

            "f1":
                "f1",

            "roc_auc":
                "roc_auc",
        }

        scores = cross_validate(
            model,
            X,
            y,
            cv=cv,
            scoring=scoring,
            n_jobs=1,
            return_train_score=False,
            error_score="raise",
        )

        return {
            "Model":
                name,

            "AccuracyMean":
                float(
                    np.mean(
                        scores[
                            "test_accuracy"
                        ]
                    )
                ),

            "AccuracyStd":
                float(
                    np.std(
                        scores[
                            "test_accuracy"
                        ]
                    )
                ),

            "BalancedAccuracyMean":
                float(
                    np.mean(
                        scores[
                            "test_balanced_accuracy"
                        ]
                    )
                ),

            "PrecisionMean":
                float(
                    np.mean(
                        scores[
                            "test_precision"
                        ]
                    )
                ),

            "RecallMean":
                float(
                    np.mean(
                        scores[
                            "test_recall"
                        ]
                    )
                ),

            "F1Mean":
                float(
                    np.mean(
                        scores[
                            "test_f1"
                        ]
                    )
                ),

            "ROCAUCMean":
                float(
                    np.mean(
                        scores[
                            "test_roc_auc"
                        ]
                    )
                ),

            "ROCAUCStd":
                float(
                    np.std(
                        scores[
                            "test_roc_auc"
                        ]
                    )
                ),
        }

    # ======================================================
    # Run Optimization
    # ======================================================

    def run_optimization(
        self,
    ) -> pd.DataFrame:

        dataframe = (
            self.load_dataset()
        )

        self.load_selected_features()

        self.validate_dataset()

        X = dataframe[
            self.selected_features
        ].copy()

        y = dataframe[
            TARGET_COLUMN
        ].astype(
            int
        )

        models = (
            self.candidate_models()
        )

        print()

        print(
            "=" * 70
        )

        print(
            "STEP 6 - MODEL OPTIMIZATION"
        )

        print(
            "=" * 70
        )

        print()

        print(
            f"Dataset        : "
            f"{len(dataframe)} recordings"
        )

        print(
            f"Selected       : "
            f"{len(self.selected_features)} features"
        )

        print(
            "Features:"
        )

        for index, feature in enumerate(
            self.selected_features,
            start=1,
        ):

            print(
                f"    {index:02d}. "
                f"{feature}"
            )

        print()

        print(
            f"Models tested  : "
            f"{len(models)}"
        )

        print()

        results = []

        total = len(
            models
        )

        for index, (
            name,
            model,
        ) in enumerate(
            models.items(),
            start=1,
        ):

            print(
                f"[{index:02d}/{total:02d}] "
                f"{name}"
            )

            try:

                result = (
                    self.evaluate_model(
                        name,
                        model,
                        X,
                        y,
                    )
                )

                results.append(
                    result
                )

                print(
                    f"    Accuracy : "
                    f"{result['AccuracyMean']:.4f}"
                )

                print(
                    f"    Balanced : "
                    f"{result['BalancedAccuracyMean']:.4f}"
                )

                print(
                    f"    Precision: "
                    f"{result['PrecisionMean']:.4f}"
                )

                print(
                    f"    Recall   : "
                    f"{result['RecallMean']:.4f}"
                )

                print(
                    f"    F1       : "
                    f"{result['F1Mean']:.4f}"
                )

                print(
                    f"    ROC-AUC  : "
                    f"{result['ROCAUCMean']:.4f}"
                )

            except Exception as exc:

                print(
                    f"    FAILED: "
                    f"{exc}"
                )

            print()

        if not results:

            raise RuntimeError(
                "All model optimization experiments failed."
            )

        result_dataframe = (
            pd.DataFrame(
                results
            )
        )

        # --------------------------------------------------
        # Rank models
        #
        # Primary:
        #     balanced accuracy
        #
        # Secondary:
        #     ROC-AUC
        #     F1
        #     accuracy
        # --------------------------------------------------

        result_dataframe = (
            result_dataframe
            .sort_values(
                by=[
                    "BalancedAccuracyMean",
                    "ROCAUCMean",
                    "F1Mean",
                    "AccuracyMean",
                ],
                ascending=[
                    False,
                    False,
                    False,
                    False,
                ],
            )
            .reset_index(
                drop=True
            )
        )

        result_dataframe[
            "Rank"
        ] = (
            result_dataframe.index
            + 1
        )

        self.results = (
            result_dataframe
        )

        return result_dataframe

    # ======================================================
    # Select Best Model
    # ======================================================

    def select_best_model(
        self,
        results: pd.DataFrame,
    ) -> Dict:

        if results.empty:

            raise ValueError(
                "No optimization results."
            )

        best = results.iloc[
            0
        ]

        return {
            "model":
                best[
                    "Model"
                ],

            "accuracy":
                float(
                    best[
                        "AccuracyMean"
                    ]
                ),

            "accuracy_std":
                float(
                    best[
                        "AccuracyStd"
                    ]
                ),

            "balanced_accuracy":
                float(
                    best[
                        "BalancedAccuracyMean"
                    ]
                ),

            "precision":
                float(
                    best[
                        "PrecisionMean"
                    ]
                ),

            "recall":
                float(
                    best[
                        "RecallMean"
                    ]
                ),

            "f1":
                float(
                    best[
                        "F1Mean"
                    ]
                ),

            "roc_auc":
                float(
                    best[
                        "ROCAUCMean"
                    ]
                ),

            "roc_auc_std":
                float(
                    best[
                        "ROCAUCStd"
                    ]
                ),

            "features":
                self.selected_features.copy(),
        }

    # ======================================================
    # Save Results
    # ======================================================

    def save_results(
        self,
        results: pd.DataFrame,
        winner: Dict,
    ) -> None:

        self.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        # --------------------------------------------------
        # CSV
        # --------------------------------------------------

        results.to_csv(
            self.output_directory
            / "model_optimization_results.csv",
            index=False,
        )

        # --------------------------------------------------
        # Best model configuration
        # --------------------------------------------------

        configuration = {
            "step":
                6,

            "selected_feature_count":
                len(
                    self.selected_features
                ),

            "selected_features":
                self.selected_features,

            "best_model":
                winner[
                    "model"
                ],

            "cross_validation":
                {
                    "accuracy":
                        winner[
                            "accuracy"
                        ],

                    "accuracy_std":
                        winner[
                            "accuracy_std"
                        ],

                    "balanced_accuracy":
                        winner[
                            "balanced_accuracy"
                        ],

                    "precision":
                        winner[
                            "precision"
                        ],

                    "recall":
                        winner[
                            "recall"
                        ],

                    "f1":
                        winner[
                            "f1"
                        ],

                    "roc_auc":
                        winner[
                            "roc_auc"
                        ],

                    "roc_auc_std":
                        winner[
                            "roc_auc_std"
                        ],
                },

            "model_replaced":
                False,

            "note":
                "Candidate model only. "
                "Existing model.pkl was not "
                "overwritten.",
        }

        with open(
            self.output_directory
            / "best_model_configuration.json",
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                configuration,
                file,
                indent=4,
            )

        # --------------------------------------------------
        # Complete report
        # --------------------------------------------------

        report = {
            "step":
                6,

            "dataset":
                str(
                    self.csv_path.resolve()
                ),

            "selected_features_file":
                str(
                    self.selected_features_path.resolve()
                ),

            "selected_features":
                self.selected_features,

            "best_model":
                winner,

            "all_models":
                results.to_dict(
                    orient="records"
                ),

            "baseline_from_step_5":
                {
                    "accuracy":
                        0.7390,

                    "roc_auc":
                        0.7812,
                },

            "production_model_changed":
                False,
        }

        with open(
            self.output_directory
            / "model_optimization_report.json",
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                report,
                file,
                indent=4,
            )

        # --------------------------------------------------
        # Text report
        # --------------------------------------------------

        self.write_text_report(
            results,
            winner,
        )

    # ======================================================
    # Text Report
    # ======================================================

    def write_text_report(
        self,
        results: pd.DataFrame,
        winner: Dict,
    ) -> None:

        lines = []

        lines.append(
            "=" * 70
        )

        lines.append(
            "STEP 6 - MODEL OPTIMIZATION REPORT"
        )

        lines.append(
            "=" * 70
        )

        lines.append("")

        lines.append(
            "SELECTED FEATURES"
        )

        lines.append(
            "-" * 70
        )

        for index, feature in enumerate(
            self.selected_features,
            start=1,
        ):

            lines.append(
                f"{index:02d}. {feature}"
            )

        lines.append("")

        lines.append(
            "MODEL COMPARISON"
        )

        lines.append(
            "-" * 70
        )

        for _, row in (
            results.iterrows()
        ):

            lines.append(
                f"Rank {int(row['Rank'])}: "
                f"{row['Model']}"
            )

            lines.append(
                f"    Accuracy : "
                f"{row['AccuracyMean']:.4f} "
                f"+/- "
                f"{row['AccuracyStd']:.4f}"
            )

            lines.append(
                f"    Balanced : "
                f"{row['BalancedAccuracyMean']:.4f}"
            )

            lines.append(
                f"    Precision: "
                f"{row['PrecisionMean']:.4f}"
            )

            lines.append(
                f"    Recall   : "
                f"{row['RecallMean']:.4f}"
            )

            lines.append(
                f"    F1       : "
                f"{row['F1Mean']:.4f}"
            )

            lines.append(
                f"    ROC-AUC  : "
                f"{row['ROCAUCMean']:.4f}"
            )

            lines.append("")

        lines.append(
            "=" * 70
        )

        lines.append(
            "BEST MODEL"
        )

        lines.append(
            "=" * 70
        )

        lines.append(
            f"Model: "
            f"{winner['model']}"
        )

        lines.append(
            f"Accuracy: "
            f"{winner['accuracy']:.4f}"
        )

        lines.append(
            f"Balanced Accuracy: "
            f"{winner['balanced_accuracy']:.4f}"
        )

        lines.append(
            f"Precision: "
            f"{winner['precision']:.4f}"
        )

        lines.append(
            f"Recall: "
            f"{winner['recall']:.4f}"
        )

        lines.append(
            f"F1: "
            f"{winner['f1']:.4f}"
        )

        lines.append(
            f"ROC-AUC: "
            f"{winner['roc_auc']:.4f}"
        )

        lines.append("")

        lines.append(
            "IMPORTANT"
        )

        lines.append(
            "The production model.pkl was NOT "
            "replaced."
        )

        lines.append(
            "The selected model must undergo "
            "final validation before deployment."
        )

        lines.append(
            "=" * 70
        )

        with open(
            self.output_directory
            / "model_optimization_report.txt",
            "w",
            encoding="utf-8",
        ) as file:

            file.write(
                "\n".join(
                    lines
                )
            )

    # ======================================================
    # Print Results
    # ======================================================

    def print_results(
        self,
        results: pd.DataFrame,
        winner: Dict,
    ) -> None:

        print()

        print(
            "=" * 70
        )

        print(
            "STEP 6 - MODEL OPTIMIZATION COMPLETE"
        )

        print(
            "=" * 70
        )

        print()

        print(
            "MODEL RESULTS"
        )

        print(
            "-" * 70
        )

        for _, row in (
            results.iterrows()
        ):

            print(
                f"{int(row['Rank']):02d}. "
                f"{row['Model']:<30} "
                f"Accuracy="
                f"{row['AccuracyMean']:.4f} "
                f"F1="
                f"{row['F1Mean']:.4f} "
                f"AUC="
                f"{row['ROCAUCMean']:.4f}"
            )

        print()

        print(
            "=" * 70
        )

        print(
            "BEST MODEL"
        )

        print(
            "=" * 70
        )

        print(
            f"Model             : "
            f"{winner['model']}"
        )

        print(
            f"Accuracy          : "
            f"{winner['accuracy']:.4f}"
        )

        print(
            f"Accuracy Std      : "
            f"{winner['accuracy_std']:.4f}"
        )

        print(
            f"Balanced Accuracy : "
            f"{winner['balanced_accuracy']:.4f}"
        )

        print(
            f"Precision         : "
            f"{winner['precision']:.4f}"
        )

        print(
            f"Recall            : "
            f"{winner['recall']:.4f}"
        )

        print(
            f"F1                : "
            f"{winner['f1']:.4f}"
        )

        print(
            f"ROC-AUC           : "
            f"{winner['roc_auc']:.4f}"
        )

        print(
            f"ROC-AUC Std       : "
            f"{winner['roc_auc_std']:.4f}"
        )

        print()

        print(
            "Production model:"
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

        print(
            "=" * 70
        )

    # ======================================================
    # Run
    # ======================================================

    def run(
        self,
    ) -> Tuple[
        pd.DataFrame,
        Dict,
    ]:

        results = (
            self.run_optimization()
        )

        winner = (
            self.select_best_model(
                results
            )
        )

        self.save_results(
            results,
            winner,
        )

        self.print_results(
            results,
            winner,
        )

        return (
            results,
            winner,
        )


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    optimizer = ModelOptimizer(
        csv_path=(
            "models/audio_training_features.csv"
        ),
        selected_features_path=(
            "models/selected_features.json"
        ),
        output_directory=(
            "models"
        ),
        random_state=42,
    )

    try:

        optimizer.run()

    except Exception as exc:

        print()

        print(
            "=" * 70
        )

        print(
            "MODEL OPTIMIZATION FAILED"
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
