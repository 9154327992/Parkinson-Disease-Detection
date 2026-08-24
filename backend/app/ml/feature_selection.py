from pathlib import Path
from typing import Dict, List, Tuple

import json
import warnings

import numpy as np
import pandas as pd

from sklearn.ensemble import (
    ExtraTreesClassifier,
    RandomForestClassifier,
    VotingClassifier,
)

from sklearn.impute import SimpleImputer

from sklearn.metrics import (
    accuracy_score,
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

from sklearn.preprocessing import StandardScaler

from app.ml.feature_engineering import (
    FeatureEngineering,
)


warnings.filterwarnings(
    "ignore"
)


# ==========================================================
# Constants
# ==========================================================

HEALTHY = 0

PARKINSON = 1

TARGET_COLUMN = "status"

TOTAL_FEATURES = 22


FEATURE_NAMES = [
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


# ==========================================================
# Feature Selection
# ==========================================================

class FeatureSelector:
    """
    Evaluate candidate feature subsets using
    stratified cross-validation.
    """

    # ======================================================
    # Initialization
    # ======================================================

    def __init__(
        self,
        csv_path: str = (
            "models/audio_training_features.csv"
        ),
        output_directory: str = (
            "models"
        ),
        correlation_threshold: float = 0.95,
        random_state: int = 42,
    ):

        self.csv_path = Path(
            csv_path
        )

        self.output_directory = Path(
            output_directory
        )

        self.correlation_threshold = (
            correlation_threshold
        )

        self.random_state = (
            random_state
        )

        self.feature_engineering = (
            FeatureEngineering()
        )

        self.dataframe = None

        self.results = []

    # ======================================================
    # Load Dataset
    # ======================================================

    def load_dataset(
        self,
    ) -> pd.DataFrame:
        """
        Load the extracted 22-feature dataset.
        """

        if not self.csv_path.exists():

            raise FileNotFoundError(
                "Feature dataset not found:\n"
                f"{self.csv_path.resolve()}\n\n"
                "Run this first:\n"
                "python -m app.ml.train_model"
            )

        dataframe = pd.read_csv(
            self.csv_path
        )

        if dataframe.empty:

            raise ValueError(
                "Feature dataset is empty."
            )

        missing = [
            feature
            for feature in FEATURE_NAMES
            if feature not in dataframe.columns
        ]

        if missing:

            raise ValueError(
                "Dataset is missing features: "
                f"{missing}"
            )

        if TARGET_COLUMN not in (
            dataframe.columns
        ):

            raise ValueError(
                "Dataset is missing the "
                "'status' target column."
            )

        self.dataframe = dataframe

        return dataframe

    # ======================================================
    # Validate Dataset
    # ======================================================

    def validate_dataset(
        self,
        dataframe: pd.DataFrame,
    ) -> None:
        """
        Validate the dataset before experiments.
        """

        if len(dataframe) < 10:

            raise ValueError(
                "Dataset contains too few recordings."
            )

        labels = pd.to_numeric(
            dataframe[
                TARGET_COLUMN
            ],
            errors="coerce",
        )

        if labels.isna().any():

            raise ValueError(
                "Target column contains "
                "missing or invalid labels."
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
                "Expected both classes "
                "0 and 1. Found: "
                f"{unique_labels}"
            )

        for feature in FEATURE_NAMES:

            dataframe[
                feature
            ] = pd.to_numeric(
                dataframe[
                    feature
                ],
                errors="coerce",
            )

    # ======================================================
    # Create Base Classifier
    # ======================================================

    def create_classifier(
        self,
    ):
        """
        Create the same general ensemble family
        used by the current training pipeline.
        """

        random_forest = (
            RandomForestClassifier(
                n_estimators=500,
                random_state=self.random_state,
                class_weight="balanced",
                max_features="sqrt",
                n_jobs=-1,
            )
        )

        extra_trees = (
            ExtraTreesClassifier(
                n_estimators=500,
                random_state=self.random_state,
                class_weight="balanced",
                max_features="sqrt",
                n_jobs=-1,
            )
        )

        return VotingClassifier(
            estimators=[
                (
                    "random_forest",
                    random_forest,
                ),
                (
                    "extra_trees",
                    extra_trees,
                ),
            ],
            voting="soft",
            weights=[
                1,
                1,
            ],
        )

    # ======================================================
    # Create Pipeline
    # ======================================================

    def create_pipeline(
        self,
    ):

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
                    self.create_classifier(),
                ),
            ]
        )

    # ======================================================
    # Correlation Matrix
    # ======================================================

    def correlation_matrix(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:

        return dataframe[
            FEATURE_NAMES
        ].corr()

    # ======================================================
    # Remove Highly Correlated Features
    # ======================================================

    def reduce_correlated_features(
        self,
        dataframe: pd.DataFrame,
    ) -> List[str]:
        """
        Automatically create a reduced feature set.

        If two features have absolute correlation
        >= correlation_threshold, one is removed.

        The feature removed is the one that has
        lower standalone model importance from
        a quick Random Forest ranking.

        This is only a candidate set.

        Cross-validation determines whether
        it is actually useful.
        """

        correlation = (
            self.correlation_matrix(
                dataframe
            )
        )

        # --------------------------------------------------
        # Quick importance estimate
        # --------------------------------------------------

        X = dataframe[
            FEATURE_NAMES
        ]

        y = dataframe[
            TARGET_COLUMN
        ].astype(
            int
        )

        imputer = SimpleImputer(
            strategy="median"
        )

        X_imputed = (
            imputer.fit_transform(
                X
            )
        )

        model = (
            ExtraTreesClassifier(
                n_estimators=300,
                random_state=self.random_state,
                class_weight="balanced",
                n_jobs=-1,
            )
        )

        model.fit(
            X_imputed,
            y,
        )

        importance = dict(
            zip(
                FEATURE_NAMES,
                model.feature_importances_,
            )
        )

        selected = list(
            FEATURE_NAMES
        )

        # --------------------------------------------------
        # Process correlation pairs
        # --------------------------------------------------

        pairs = []

        for i, feature_a in enumerate(
            FEATURE_NAMES
        ):

            for feature_b in (
                FEATURE_NAMES[
                    i + 1:
                ]
            ):

                value = correlation.loc[
                    feature_a,
                    feature_b,
                ]

                if (
                    abs(value)
                    >= self.correlation_threshold
                ):

                    pairs.append(
                        (
                            feature_a,
                            feature_b,
                            abs(float(value)),
                        )
                    )

        pairs.sort(
            key=lambda item: item[2],
            reverse=True,
        )

        # --------------------------------------------------
        # Remove lower-importance feature
        # --------------------------------------------------

        for (
            feature_a,
            feature_b,
            _,
        ) in pairs:

            if (
                feature_a not in selected
                or feature_b not in selected
            ):

                continue

            if (
                importance[
                    feature_a
                ]
                >=
                importance[
                    feature_b
                ]
            ):

                selected.remove(
                    feature_b
                )

            else:

                selected.remove(
                    feature_a
                )

        return selected

    # ======================================================
    # Candidate Sets
    # ======================================================

    def create_candidate_sets(
        self,
        dataframe: pd.DataFrame,
    ) -> Dict[
        str,
        List[str],
    ]:
        """
        Create several candidate feature sets.

        Set 1:
            All 22 features.

        Set 2:
            Remove highly redundant features.

        Set 3:
            Jitter-focused reduction.

        Set 4:
            Shimmer-focused reduction.

        Set 5:
            Nonlinear-focused reduction.

        Set 6:
            Hybrid feature set.
        """

        candidates = {}

        # --------------------------------------------------
        # A - Full baseline
        # --------------------------------------------------

        candidates[
            "A_full_22"
        ] = list(
            FEATURE_NAMES
        )

        # --------------------------------------------------
        # B - Correlation reduction
        # --------------------------------------------------

        candidates[
            "B_correlation_reduced"
        ] = (
            self.reduce_correlated_features(
                dataframe
            )
        )

        # --------------------------------------------------
        # C - Jitter reduction
        # --------------------------------------------------

        jitter_set = [
            "MDVP:Fo(Hz)",
            "MDVP:Fhi(Hz)",
            "MDVP:Flo(Hz)",
            "MDVP:Jitter(%)",
            "MDVP:Jitter(Abs)",
            "MDVP:RAP",
            "MDVP:Shimmer",
            "MDVP:Shimmer(dB)",
            "MDVP:APQ",
            "NHR",
            "HNR",
            "RPDE",
            "DFA",
            "spread1",
            "spread2",
            "D2",
            "PPE",
        ]

        candidates[
            "C_jitter_reduced"
        ] = jitter_set

        # --------------------------------------------------
        # D - Shimmer reduction
        # --------------------------------------------------

        shimmer_set = [
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
            "MDVP:APQ",
            "NHR",
            "HNR",
            "RPDE",
            "DFA",
            "spread1",
            "spread2",
            "D2",
            "PPE",
        ]

        candidates[
            "D_shimmer_reduced"
        ] = shimmer_set

        # --------------------------------------------------
        # E - Compact statistical set
        # --------------------------------------------------

        statistical_set = [
            "MDVP:Fo(Hz)",
            "MDVP:Fhi(Hz)",
            "MDVP:Flo(Hz)",
            "MDVP:Jitter(%)",
            "MDVP:Shimmer(dB)",
            "MDVP:APQ",
            "NHR",
            "HNR",
            "RPDE",
            "DFA",
            "spread1",
            "D2",
            "PPE",
        ]

        candidates[
            "E_compact_statistical"
        ] = statistical_set

        # --------------------------------------------------
        # F - Strong importance features
        # --------------------------------------------------

        importance_features = (
            self.quick_feature_importance(
                dataframe
            )
        )

        top_12 = (
            importance_features
            .head(12)
            [
                "Feature"
            ]
            .tolist()
        )

        candidates[
            "F_top_12_importance"
        ] = top_12

        # --------------------------------------------------
        # G - Hybrid
        # --------------------------------------------------

        group_stats = (
            self.group_statistics(
                dataframe
            )
        )

        top_effect = (
            group_stats
            .sort_values(
                by="AbsoluteEffectSize",
                ascending=False,
            )
            .head(12)
            [
                "Feature"
            ]
            .tolist()
        )

        hybrid = []

        for feature in (
            importance_features[
                "Feature"
            ].tolist()
        ):

            if feature in top_effect:

                hybrid.append(
                    feature
                )

        # Add important features until
        # we have a reasonable subset.

        for feature in top_effect:

            if feature not in hybrid:

                hybrid.append(
                    feature
                )

        hybrid = hybrid[
            :15
        ]

        candidates[
            "G_hybrid"
        ] = hybrid

        # --------------------------------------------------
        # Remove duplicates while preserving order
        # --------------------------------------------------

        cleaned = {}

        for name, features in (
            candidates.items()
        ):

            ordered = []

            for feature in features:

                if (
                    feature in FEATURE_NAMES
                    and feature not in ordered
                ):

                    ordered.append(
                        feature
                    )

            if len(ordered) >= 2:

                cleaned[
                    name
                ] = ordered

        return cleaned

    # ======================================================
    # Quick Feature Importance
    # ======================================================

    def quick_feature_importance(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:

        X = dataframe[
            FEATURE_NAMES
        ]

        y = dataframe[
            TARGET_COLUMN
        ].astype(
            int
        )

        imputer = SimpleImputer(
            strategy="median"
        )

        X_imputed = (
            imputer.fit_transform(
                X
            )
        )

        model = (
            ExtraTreesClassifier(
                n_estimators=500,
                random_state=self.random_state,
                class_weight="balanced",
                n_jobs=-1,
            )
        )

        model.fit(
            X_imputed,
            y,
        )

        return pd.DataFrame(
            {
                "Feature":
                    FEATURE_NAMES,

                "Importance":
                    model.feature_importances_,
            }
        ).sort_values(
            by="Importance",
            ascending=False,
        ).reset_index(
            drop=True
        )

    # ======================================================
    # Group Statistics
    # ======================================================

    def group_statistics(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Calculate PD/HC separation using standardized
        mean differences.
        """

        healthy = dataframe[
            dataframe[
                TARGET_COLUMN
            ]
            == HEALTHY
        ]

        parkinson = dataframe[
            dataframe[
                TARGET_COLUMN
            ]
            == PARKINSON
        ]

        rows = []

        for feature in FEATURE_NAMES:

            hc = pd.to_numeric(
                healthy[
                    feature
                ],
                errors="coerce",
            ).dropna()

            pd_values = pd.to_numeric(
                parkinson[
                    feature
                ],
                errors="coerce",
            ).dropna()

            if (
                len(hc) < 2
                or len(pd_values) < 2
            ):

                effect = 0.0

            else:

                pooled = np.sqrt(
                    (
                        (
                            len(hc) - 1
                        )
                        * hc.var()
                        +
                        (
                            len(pd_values) - 1
                        )
                        * pd_values.var()
                    )
                    /
                    (
                        len(hc)
                        + len(pd_values)
                        - 2
                    )
                )

                if (
                    pooled > 0
                    and np.isfinite(
                        pooled
                    )
                ):

                    effect = (
                        pd_values.mean()
                        - hc.mean()
                    ) / pooled

                else:

                    effect = 0.0

            rows.append(
                {
                    "Feature":
                        feature,

                    "EffectSize":
                        float(
                            effect
                        ),

                    "AbsoluteEffectSize":
                        abs(
                            float(
                                effect
                            )
                        ),
                }
            )

        return pd.DataFrame(
            rows
        ).sort_values(
            by="AbsoluteEffectSize",
            ascending=False,
        ).reset_index(
            drop=True
        )

    # ======================================================
    # Cross Validation
    # ======================================================

    def evaluate_feature_set(
        self,
        dataframe: pd.DataFrame,
        feature_set_name: str,
        features: List[str],
    ) -> Dict:
        """
        Evaluate one feature subset.

        Uses the same 5-fold stratified CV structure
        for every candidate.
        """

        X = dataframe[
            features
        ].copy()

        y = dataframe[
            TARGET_COLUMN
        ].astype(
            int
        )

        # --------------------------------------------------
        # Determine folds
        # --------------------------------------------------

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
                "Not enough samples per class "
                "for cross-validation."
            )

        cv = StratifiedKFold(
            n_splits=folds,
            shuffle=True,
            random_state=self.random_state,
        )

        pipeline = (
            self.create_pipeline()
        )

        scoring = {
            "accuracy":
                "accuracy",

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
            pipeline,
            X,
            y,
            cv=cv,
            scoring=scoring,
            n_jobs=1,
            return_train_score=False,
        )

        result = {
            "FeatureSet":
                feature_set_name,

            "FeatureCount":
                len(features),

            "Features":
                ", ".join(
                    features
                ),

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

        return result

    # ======================================================
    # Run Experiments
    # ======================================================

    def run_experiments(
        self,
    ) -> pd.DataFrame:

        dataframe = (
            self.load_dataset()
        )

        self.validate_dataset(
            dataframe
        )

        candidates = (
            self.create_candidate_sets(
                dataframe
            )
        )

        print()

        print(
            "=" * 70
        )

        print(
            "STEP 5 - FEATURE SELECTION"
        )

        print(
            "=" * 70
        )

        print()

        print(
            f"Dataset : "
            f"{len(dataframe)} recordings"
        )

        print(
            f"Features: "
            f"{len(FEATURE_NAMES)}"
        )

        print()

        results = []

        # --------------------------------------------------
        # Evaluate every candidate
        # --------------------------------------------------

        for index, (
            name,
            features,
        ) in enumerate(
            candidates.items(),
            start=1,
        ):

            print(
                f"[{index}/{len(candidates)}] "
                f"{name}"
            )

            print(
                f"    Features: "
                f"{len(features)}"
            )

            print(
                f"    {', '.join(features)}"
            )

            result = (
                self.evaluate_feature_set(
                    dataframe,
                    name,
                    features,
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

            print()

        self.results = results

        dataframe_results = pd.DataFrame(
            results
        )

        # --------------------------------------------------
        # Rank candidates
        #
        # Accuracy is primary.
        # F1 and ROC-AUC are secondary.
        # --------------------------------------------------

        dataframe_results = (
            dataframe_results
            .sort_values(
                by=[
                    "AccuracyMean",
                    "F1Mean",
                    "ROCAUCMean",
                ],
                ascending=[
                    False,
                    False,
                    False,
                ],
            )
            .reset_index(
                drop=True
            )
        )

        dataframe_results[
            "Rank"
        ] = (
            dataframe_results.index
            + 1
        )

        self.results = (
            dataframe_results
        )

        return dataframe_results

    # ======================================================
    # Select Winner
    # ======================================================

    def select_winner(
        self,
        results: pd.DataFrame,
    ) -> Dict:
        """
        Select the best candidate.

        Important:
        This does NOT retrain or overwrite the model.
        """

        if results.empty:

            raise ValueError(
                "No feature-selection results."
            )

        winner = results.iloc[
            0
        ]

        features = [
            feature.strip()
            for feature in (
                winner[
                    "Features"
                ].split(",")
            )
            if feature.strip()
        ]

        return {
            "feature_set":
                winner[
                    "FeatureSet"
                ],

            "feature_count":
                int(
                    winner[
                        "FeatureCount"
                    ]
                ),

            "features":
                features,

            "accuracy":
                float(
                    winner[
                        "AccuracyMean"
                    ]
                ),

            "accuracy_std":
                float(
                    winner[
                        "AccuracyStd"
                    ]
                ),

            "precision":
                float(
                    winner[
                        "PrecisionMean"
                    ]
                ),

            "recall":
                float(
                    winner[
                        "RecallMean"
                    ]
                ),

            "f1":
                float(
                    winner[
                        "F1Mean"
                    ]
                ),

            "roc_auc":
                float(
                    winner[
                        "ROCAUCMean"
                    ]
                ),
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
            / "feature_selection_results.csv",
            index=False,
        )

        # --------------------------------------------------
        # Selected features
        # --------------------------------------------------

        selected = {
            "step":
                5,

            "description":
                "Best feature subset from "
                "stratified cross-validation.",

            "feature_set":
                winner[
                    "feature_set"
                ],

            "feature_count":
                winner[
                    "feature_count"
                ],

            "features":
                winner[
                    "features"
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
                },

            "warning":
                "This feature set has not yet "
                "been used to replace the "
                "production model.",
        }

        with open(
            self.output_directory
            / "selected_features.json",
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                selected,
                file,
                indent=4,
            )

        # --------------------------------------------------
        # Complete report
        # --------------------------------------------------

        report = {
            "step":
                5,

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

            "baseline":
                {
                    "feature_count":
                        22,

                    "feature_set":
                        "A_full_22",
                },

            "winner":
                selected,

            "all_results":
                results.to_dict(
                    orient="records"
                ),

            "important_note":
                "Feature selection uses "
                "cross-validation only. "
                "The existing model.pkl "
                "was not overwritten.",
        }

        with open(
            self.output_directory
            / "feature_selection_report.json",
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
            "STEP 5 - FEATURE SELECTION REPORT"
        )

        lines.append(
            "=" * 70
        )

        lines.append("")

        lines.append(
            "DATASET"
        )

        lines.append(
            f"Recordings: "
            f"{len(self.dataframe)}"
        )

        lines.append(
            f"Features tested: "
            f"{len(FEATURE_NAMES)}"
        )

        lines.append("")

        lines.append(
            "FEATURE SET COMPARISON"
        )

        lines.append(
            "-" * 70
        )

        for _, row in (
            results.iterrows()
        ):

            lines.append(
                f"Rank {int(row['Rank'])}: "
                f"{row['FeatureSet']}"
            )

            lines.append(
                f"    Features : "
                f"{int(row['FeatureCount'])}"
            )

            lines.append(
                f"    Accuracy : "
                f"{row['AccuracyMean']:.4f} "
                f"+/- "
                f"{row['AccuracyStd']:.4f}"
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
            "SELECTED FEATURE SET"
        )

        lines.append(
            "=" * 70
        )

        lines.append(
            f"Name: "
            f"{winner['feature_set']}"
        )

        lines.append(
            f"Count: "
            f"{winner['feature_count']}"
        )

        lines.append("")

        for index, feature in enumerate(
            winner[
                "features"
            ],
            start=1,
        ):

            lines.append(
                f"{index:02d}. {feature}"
            )

        lines.append("")

        lines.append(
            "CROSS-VALIDATION"
        )

        lines.append(
            f"Accuracy : "
            f"{winner['accuracy']:.4f}"
        )

        lines.append(
            f"Std      : "
            f"{winner['accuracy_std']:.4f}"
        )

        lines.append(
            f"Precision: "
            f"{winner['precision']:.4f}"
        )

        lines.append(
            f"Recall   : "
            f"{winner['recall']:.4f}"
        )

        lines.append(
            f"F1       : "
            f"{winner['f1']:.4f}"
        )

        lines.append(
            f"ROC-AUC  : "
            f"{winner['roc_auc']:.4f}"
        )

        lines.append("")

        lines.append(
            "IMPORTANT"
        )

        lines.append(
            "The existing model.pkl was NOT "
            "overwritten."
        )

        lines.append(
            "The selected feature set must "
            "be validated again before deployment."
        )

        lines.append(
            "=" * 70
        )

        with open(
            self.output_directory
            / "feature_selection_report.txt",
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
            "STEP 5 - FEATURE SELECTION COMPLETE"
        )

        print(
            "=" * 70
        )

        print()

        print(
            "FEATURE SET RESULTS"
        )

        print(
            "-" * 70
        )

        for _, row in (
            results.iterrows()
        ):

            print(
                f"{int(row['Rank']):02d}. "
                f"{row['FeatureSet']:<28} "
                f"{int(row['FeatureCount']):02d} features "
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
            "SELECTED FEATURE SET"
        )

        print(
            "=" * 70
        )

        print(
            f"Name       : "
            f"{winner['feature_set']}"
        )

        print(
            f"Feature count: "
            f"{winner['feature_count']}"
        )

        print()

        for index, feature in enumerate(
            winner[
                "features"
            ],
            start=1,
        ):

            print(
                f"{index:02d}. {feature}"
            )

        print()

        print(
            "CROSS-VALIDATION"
        )

        print(
            f"Accuracy   : "
            f"{winner['accuracy']:.4f}"
        )

        print(
            f"Std        : "
            f"{winner['accuracy_std']:.4f}"
        )

        print(
            f"Precision  : "
            f"{winner['precision']:.4f}"
        )

        print(
            f"Recall     : "
            f"{winner['recall']:.4f}"
        )

        print(
            f"F1         : "
            f"{winner['f1']:.4f}"
        )

        print(
            f"ROC-AUC    : "
            f"{winner['roc_auc']:.4f}"
        )

        print()

        print(
            "IMPORTANT:"
        )

        print(
            "model.pkl was NOT replaced."
        )

        print(
            "The selected feature set is a "
            "candidate for Step 6."
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
            self.run_experiments()
        )

        winner = (
            self.select_winner(
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

    selector = FeatureSelector(
        csv_path=(
            "models/audio_training_features.csv"
        ),
        output_directory=(
            "models"
        ),
        correlation_threshold=0.95,
        random_state=42,
    )

    try:

        selector.run()

    except Exception as exc:

        print()

        print(
            "=" * 70
        )

        print(
            "FEATURE SELECTION FAILED"
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
