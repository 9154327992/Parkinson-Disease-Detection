from pathlib import Path
from typing import Dict, Optional

import json
import warnings

import joblib
import numpy as np
import pandas as pd

from scipy.stats import (
    mannwhitneyu,
)

from sklearn.inspection import permutation_importance

from app.ml.feature_engineering import (
    FeatureEngineering,
)


warnings.filterwarnings(
    "ignore",
)


# ==========================================================
# Constants
# ==========================================================

HEALTHY = 0

PARKINSON = 1

TARGET_COLUMN = "status"

CLASS_COLUMN = "class_name"

AUDIO_FILE_COLUMN = "audio_file"

AUDIO_PATH_COLUMN = "audio_path"


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
# Feature Analyzer
# ==========================================================

class FeatureAnalyzer:
    """
    Analyze the 22 extracted Parkinson voice features.
    """

    # ======================================================
    # Initialization
    # ======================================================

    def __init__(
        self,
        csv_path: str = (
            "models/audio_training_features.csv"
        ),
        model_path: str = (
            "models/model.pkl"
        ),
        output_directory: str = (
            "models"
        ),
    ):

        self.csv_path = Path(
            csv_path
        )

        self.model_path = Path(
            model_path
        )

        self.output_directory = Path(
            output_directory
        )

        self.feature_engineering = (
            FeatureEngineering()
        )

        self.dataframe = None

        self.results = {}

    # ======================================================
    # Load Dataset
    # ======================================================

    def load_dataset(
        self,
    ) -> pd.DataFrame:
        """
        Load the extracted feature CSV.
        """

        if not self.csv_path.exists():

            raise FileNotFoundError(
                "Feature dataset not found:\n"
                f"{self.csv_path.resolve()}"
            )

        dataframe = pd.read_csv(
            self.csv_path
        )

        if dataframe.empty:

            raise ValueError(
                "Feature dataset is empty."
            )

        self.dataframe = dataframe

        return dataframe

    # ======================================================
    # Validate Dataset
    # ======================================================

    def validate_dataset(
        self,
        dataframe: Optional[
            pd.DataFrame
        ] = None,
    ) -> Dict:

        if dataframe is None:

            dataframe = self.dataframe

        if dataframe is None:

            raise ValueError(
                "Dataset has not been loaded."
            )

        required = [
            *FEATURE_NAMES,
            TARGET_COLUMN,
        ]

        missing = [
            column
            for column in required
            if column not in dataframe.columns
        ]

        if missing:

            raise ValueError(
                "Dataset is missing required "
                f"columns: {missing}"
            )

        labels = pd.to_numeric(
            dataframe[
                TARGET_COLUMN
            ],
            errors="coerce",
        )

        invalid_labels = (
            labels.dropna()
            .unique()
            .tolist()
        )

        invalid_labels = [
            value
            for value in invalid_labels
            if value not in [
                HEALTHY,
                PARKINSON,
            ]
        ]

        if invalid_labels:

            raise ValueError(
                "Invalid target labels: "
                f"{invalid_labels}"
            )

        return {
            "valid":
                True,

            "rows":
                int(
                    len(dataframe)
                ),

            "columns":
                int(
                    len(dataframe.columns)
                ),

            "feature_count":
                len(FEATURE_NAMES),

            "missing_columns":
                missing,

            "labels":
                sorted(
                    int(value)
                    for value in labels
                    .dropna()
                    .unique()
                ),
        }

    # ======================================================
    # Dataset Summary
    # ======================================================

    def dataset_summary(
        self,
        dataframe: Optional[
            pd.DataFrame
        ] = None,
    ) -> Dict:

        if dataframe is None:

            dataframe = self.dataframe

        if dataframe is None:

            raise ValueError(
                "Dataset has not been loaded."
            )

        labels = pd.to_numeric(
            dataframe[
                TARGET_COLUMN
            ],
            errors="coerce",
        )

        healthy = int(
            (
                labels
                == HEALTHY
            ).sum()
        )

        parkinson = int(
            (
                labels
                == PARKINSON
            ).sum()
        )

        return {
            "total":
                int(
                    len(dataframe)
                ),

            "healthy":
                healthy,

            "parkinson":
                parkinson,

            "feature_count":
                len(FEATURE_NAMES),

            "healthy_percentage":
                (
                    healthy
                    / len(dataframe)
                    * 100
                ),

            "parkinson_percentage":
                (
                    parkinson
                    / len(dataframe)
                    * 100
                ),
        }

    # ======================================================
    # Missing Values
    # ======================================================

    def missing_value_analysis(
        self,
        dataframe: Optional[
            pd.DataFrame
        ] = None,
    ) -> pd.DataFrame:

        if dataframe is None:

            dataframe = self.dataframe

        rows = []

        for feature in FEATURE_NAMES:

            missing = int(
                dataframe[
                    feature
                ].isna().sum()
            )

            rows.append(
                {
                    "Feature":
                        feature,

                    "Missing":
                        missing,

                    "MissingPercentage":
                        (
                            missing
                            / len(dataframe)
                            * 100
                        ),
                }
            )

        return pd.DataFrame(
            rows
        ).sort_values(
            by="Missing",
            ascending=False,
        ).reset_index(
            drop=True
        )

    # ======================================================
    # Numeric Validation
    # ======================================================

    def numeric_validation(
        self,
        dataframe: Optional[
            pd.DataFrame
        ] = None,
    ) -> pd.DataFrame:

        if dataframe is None:

            dataframe = self.dataframe

        rows = []

        for feature in FEATURE_NAMES:

            values = pd.to_numeric(
                dataframe[
                    feature
                ],
                errors="coerce",
            )

            invalid = int(
                values.isna().sum()
                - dataframe[
                    feature
                ].isna().sum()
            )

            infinite = int(
                np.isinf(
                    values
                    .dropna()
                    .to_numpy(
                        dtype=float
                    )
                ).sum()
            )

            rows.append(
                {
                    "Feature":
                        feature,

                    "InvalidNumeric":
                        invalid,

                    "Infinite":
                        infinite,

                    "Valid":
                        int(
                            len(dataframe)
                            - invalid
                            - infinite
                        ),
                }
            )

        return pd.DataFrame(
            rows
        )

    # ======================================================
    # Descriptive Statistics
    # ======================================================

    def descriptive_statistics(
        self,
        dataframe: Optional[
            pd.DataFrame
        ] = None,
    ) -> pd.DataFrame:

        if dataframe is None:

            dataframe = self.dataframe

        rows = []

        for feature in FEATURE_NAMES:

            values = pd.to_numeric(
                dataframe[
                    feature
                ],
                errors="coerce",
            )

            rows.append(
                {
                    "Feature":
                        feature,

                    "Count":
                        int(
                            values.count()
                        ),

                    "Mean":
                        float(
                            values.mean()
                        ),

                    "Median":
                        float(
                            values.median()
                        ),

                    "Std":
                        float(
                            values.std()
                        ),

                    "Min":
                        float(
                            values.min()
                        ),

                    "Max":
                        float(
                            values.max()
                        ),

                    "Q1":
                        float(
                            values.quantile(
                                0.25
                            )
                        ),

                    "Q3":
                        float(
                            values.quantile(
                                0.75
                            )
                        ),
                }
            )

        return pd.DataFrame(
            rows
        )

    # ======================================================
    # Outlier Analysis
    # ======================================================

    def outlier_analysis(
        self,
        dataframe: Optional[
            pd.DataFrame
        ] = None,
    ) -> pd.DataFrame:

        if dataframe is None:

            dataframe = self.dataframe

        rows = []

        for feature in FEATURE_NAMES:

            values = pd.to_numeric(
                dataframe[
                    feature
                ],
                errors="coerce",
            ).dropna()

            if values.empty:

                continue

            q1 = values.quantile(
                0.25
            )

            q3 = values.quantile(
                0.75
            )

            iqr = q3 - q1

            lower = (
                q1
                - 1.5 * iqr
            )

            upper = (
                q3
                + 1.5 * iqr
            )

            outlier_mask = (
                (values < lower)
                | (values > upper)
            )

            count = int(
                outlier_mask.sum()
            )

            rows.append(
                {
                    "Feature":
                        feature,

                    "Q1":
                        float(q1),

                    "Q3":
                        float(q3),

                    "IQR":
                        float(iqr),

                    "LowerBound":
                        float(lower),

                    "UpperBound":
                        float(upper),

                    "Outliers":
                        count,

                    "OutlierPercentage":
                        (
                            count
                            / len(values)
                            * 100
                        ),
                }
            )

        return pd.DataFrame(
            rows
        ).sort_values(
            by="Outliers",
            ascending=False,
        ).reset_index(
            drop=True
        )

    # ======================================================
    # PD vs HC Statistics
    # ======================================================

    def group_statistics(
        self,
        dataframe: Optional[
            pd.DataFrame
        ] = None,
    ) -> pd.DataFrame:

        if dataframe is None:

            dataframe = self.dataframe

        labels = pd.to_numeric(
            dataframe[
                TARGET_COLUMN
            ],
            errors="coerce",
        )

        healthy = dataframe[
            labels == HEALTHY
        ]

        parkinson = dataframe[
            labels == PARKINSON
        ]

        rows = []

        for feature in FEATURE_NAMES:

            hc_values = pd.to_numeric(
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

            hc_mean = (
                float(
                    hc_values.mean()
                )
                if len(hc_values)
                else np.nan
            )

            pd_mean = (
                float(
                    pd_values.mean()
                )
                if len(pd_values)
                else np.nan
            )

            hc_median = (
                float(
                    hc_values.median()
                )
                if len(hc_values)
                else np.nan
            )

            pd_median = (
                float(
                    pd_values.median()
                )
                if len(pd_values)
                else np.nan
            )

            # --------------------------------------------------
            # Cohen-style standardized difference
            # --------------------------------------------------

            pooled_std = np.sqrt(
                (
                    (
                        len(hc_values)
                        - 1
                    )
                    * hc_values.var()
                    +
                    (
                        len(pd_values)
                        - 1
                    )
                    * pd_values.var()
                )
                /
                max(
                    (
                        len(hc_values)
                        + len(pd_values)
                        - 2
                    ),
                    1,
                )
            )

            if (
                pooled_std
                and np.isfinite(
                    pooled_std
                )
            ):

                effect_size = (
                    pd_mean
                    - hc_mean
                ) / pooled_std

            else:

                effect_size = 0.0

            # --------------------------------------------------
            # Mann-Whitney U test
            # --------------------------------------------------

            p_value = np.nan

            if (
                len(hc_values) >= 2
                and len(pd_values) >= 2
            ):

                try:

                    _, p_value = (
                        mannwhitneyu(
                            hc_values,
                            pd_values,
                            alternative="two-sided",
                        )
                    )

                    p_value = float(
                        p_value
                    )

                except Exception:

                    p_value = np.nan

            rows.append(
                {
                    "Feature":
                        feature,

                    "HC_Mean":
                        hc_mean,

                    "PD_Mean":
                        pd_mean,

                    "HC_Median":
                        hc_median,

                    "PD_Median":
                        pd_median,

                    "MeanDifference":
                        (
                            pd_mean
                            - hc_mean
                        ),

                    "AbsoluteMeanDifference":
                        abs(
                            pd_mean
                            - hc_mean
                        ),

                    "EffectSize":
                        float(
                            effect_size
                        ),

                    "AbsoluteEffectSize":
                        abs(
                            float(
                                effect_size
                            )
                        ),

                    "PValue":
                        p_value,
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
    # Correlation Analysis
    # ======================================================

    def correlation_analysis(
        self,
        dataframe: Optional[
            pd.DataFrame
        ] = None,
    ) -> pd.DataFrame:

        if dataframe is None:

            dataframe = self.dataframe

        features = dataframe[
            FEATURE_NAMES
        ].apply(
            pd.to_numeric,
            errors="coerce",
        )

        return features.corr()

    # ======================================================
    # Highly Correlated Pairs
    # ======================================================

    def correlated_pairs(
        self,
        dataframe: Optional[
            pd.DataFrame
        ] = None,
        threshold: float = 0.90,
    ) -> pd.DataFrame:

        if dataframe is None:

            dataframe = self.dataframe

        correlation = (
            self.correlation_analysis(
                dataframe
            )
        )

        rows = []

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
                    >= threshold
                ):

                    rows.append(
                        {
                            "FeatureA":
                                feature_a,

                            "FeatureB":
                                feature_b,

                            "Correlation":
                                float(value),

                            "AbsoluteCorrelation":
                                abs(
                                    float(value)
                                ),
                        }
                    )

        if not rows:

            return pd.DataFrame(
                columns=[
                    "FeatureA",
                    "FeatureB",
                    "Correlation",
                    "AbsoluteCorrelation",
                ]
            )

        return pd.DataFrame(
            rows
        ).sort_values(
            by="AbsoluteCorrelation",
            ascending=False,
        ).reset_index(
            drop=True
        )

    # ======================================================
    # Load Model
    # ======================================================

    def load_model(
        self,
    ):
        """
        Load the already-trained model.
        """

        if not self.model_path.exists():

            return None

        return joblib.load(
            self.model_path
        )

    # ======================================================
    # Model Importance
    # ======================================================

    def model_importance(
        self,
    ) -> pd.DataFrame:

        model = self.load_model()

        if model is None:

            return pd.DataFrame(
                columns=[
                    "Feature",
                    "Importance",
                ]
            )

        try:

            return (
                self.feature_engineering
                .feature_importance(
                    model
                )
            )

        except Exception:

            return pd.DataFrame(
                columns=[
                    "Feature",
                    "Importance",
                ]
            )

    # ======================================================
    # Combined Ranking
    # ======================================================

    def combined_feature_ranking(
        self,
        group_statistics: pd.DataFrame,
        model_importance: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Combine statistical separation and model
        importance.

        IMPORTANT:
        This is a ranking aid, not a final feature
        selection decision.
        """

        ranking = group_statistics[
            [
                "Feature",
                "AbsoluteEffectSize",
                "PValue",
            ]
        ].copy()

        if (
            model_importance is not None
            and not model_importance.empty
        ):

            ranking = ranking.merge(
                model_importance[
                    [
                        "Feature",
                        "Importance",
                    ]
                ],
                on="Feature",
                how="left",
            )

        else:

            ranking[
                "Importance"
            ] = np.nan

        ranking[
            "Importance"
        ] = ranking[
            "Importance"
        ].fillna(
            0.0
        )

        # --------------------------------------------------
        # Rank each measure
        # --------------------------------------------------

        ranking[
            "EffectRank"
        ] = ranking[
            "AbsoluteEffectSize"
        ].rank(
            ascending=False,
            method="min",
        )

        ranking[
            "ImportanceRank"
        ] = ranking[
            "Importance"
        ].rank(
            ascending=False,
            method="min",
        )

        ranking[
            "PValueRank"
        ] = ranking[
            "PValue"
        ].rank(
            ascending=True,
            method="min",
        )

        ranking[
            "CombinedRank"
        ] = (
            ranking[
                "EffectRank"
            ]
            +
            ranking[
                "ImportanceRank"
            ]
            +
            ranking[
                "PValueRank"
            ]
        )

        return ranking.sort_values(
            by=[
                "CombinedRank",
                "EffectRank",
            ],
            ascending=[
                True,
                True,
            ],
        ).reset_index(
            drop=True
        )

    # ======================================================
    # Run Complete Analysis
    # ======================================================

    def analyze(
        self,
    ) -> Dict:

        dataframe = (
            self.load_dataset()
        )

        validation = (
            self.validate_dataset(
                dataframe
            )
        )

        summary = (
            self.dataset_summary(
                dataframe
            )
        )

        missing = (
            self.missing_value_analysis(
                dataframe
            )
        )

        numeric = (
            self.numeric_validation(
                dataframe
            )
        )

        descriptive = (
            self.descriptive_statistics(
                dataframe
            )
        )

        outliers = (
            self.outlier_analysis(
                dataframe
            )
        )

        group_stats = (
            self.group_statistics(
                dataframe
            )
        )

        correlation = (
            self.correlation_analysis(
                dataframe
            )
        )

        correlated = (
            self.correlated_pairs(
                dataframe
            )
        )

        importance = (
            self.model_importance()
        )

        ranking = (
            self.combined_feature_ranking(
                group_stats,
                importance,
            )
        )

        self.results = {
            "validation":
                validation,

            "summary":
                summary,

            "missing":
                missing,

            "numeric":
                numeric,

            "descriptive":
                descriptive,

            "outliers":
                outliers,

            "group_statistics":
                group_stats,

            "correlation":
                correlation,

            "correlated_pairs":
                correlated,

            "model_importance":
                importance,

            "ranking":
                ranking,
        }

        return self.results

    # ======================================================
    # Save Reports
    # ======================================================

    def save_reports(
        self,
    ) -> None:

        if not self.results:

            raise RuntimeError(
                "Run analyze() before saving reports."
            )

        self.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        # --------------------------------------------------
        # CSV files
        # --------------------------------------------------

        self.results[
            "missing"
        ].to_csv(
            self.output_directory
            / "feature_missing_values.csv",
            index=False,
        )

        self.results[
            "numeric"
        ].to_csv(
            self.output_directory
            / "feature_numeric_validation.csv",
            index=False,
        )

        self.results[
            "descriptive"
        ].to_csv(
            self.output_directory
            / "feature_descriptive_statistics.csv",
            index=False,
        )

        self.results[
            "outliers"
        ].to_csv(
            self.output_directory
            / "feature_outliers.csv",
            index=False,
        )

        self.results[
            "group_statistics"
        ].to_csv(
            self.output_directory
            / "feature_group_statistics.csv",
            index=False,
        )

        self.results[
            "correlation"
        ].to_csv(
            self.output_directory
            / "feature_correlation.csv",
        )

        self.results[
            "correlated_pairs"
        ].to_csv(
            self.output_directory
            / "feature_correlated_pairs.csv",
            index=False,
        )

        self.results[
            "model_importance"
        ].to_csv(
            self.output_directory
            / "feature_model_importance.csv",
            index=False,
        )

        self.results[
            "ranking"
        ].to_csv(
            self.output_directory
            / "feature_analysis.csv",
            index=False,
        )

        # --------------------------------------------------
        # JSON report
        # --------------------------------------------------

        json_report = {
            "validation":
                self.results[
                    "validation"
                ],

            "summary":
                self.results[
                    "summary"
                ],

            "top_features":
                self.results[
                    "ranking"
                ].head(10).to_dict(
                    orient="records"
                ),

            "highly_correlated_pairs":
                self.results[
                    "correlated_pairs"
                ].to_dict(
                    orient="records"
                ),
        }

        with open(
            self.output_directory
            / "feature_analysis_report.json",
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                json_report,
                file,
                indent=4,
                default=str,
            )

        # --------------------------------------------------
        # Human-readable report
        # --------------------------------------------------

        self.write_text_report()

    # ======================================================
    # Text Report
    # ======================================================

    def write_text_report(
        self,
    ) -> None:

        if not self.results:

            raise RuntimeError(
                "Run analyze() first."
            )

        summary = (
            self.results[
                "summary"
            ]
        )

        ranking = (
            self.results[
                "ranking"
            ]
        )

        outliers = (
            self.results[
                "outliers"
            ]
        )

        correlated = (
            self.results[
                "correlated_pairs"
            ]
        )

        group_stats = (
            self.results[
                "group_statistics"
            ]
        )

        lines = []

        lines.append(
            "=" * 70
        )

        lines.append(
            "PARKINSON VOICE FEATURE ANALYSIS"
        )

        lines.append(
            "=" * 70
        )

        lines.append("")

        lines.append(
            "DATASET SUMMARY"
        )

        lines.append(
            "-" * 70
        )

        lines.append(
            f"Total recordings : "
            f"{summary['total']}"
        )

        lines.append(
            f"Healthy          : "
            f"{summary['healthy']}"
        )

        lines.append(
            f"Parkinson        : "
            f"{summary['parkinson']}"
        )

        lines.append(
            f"Features         : "
            f"{summary['feature_count']}"
        )

        lines.append("")

        lines.append(
            "TOP FEATURES"
        )

        lines.append(
            "-" * 70
        )

        for index, row in (
            ranking.head(10)
            .iterrows()
        ):

            p_value = row[
                "PValue"
            ]

            p_text = (
                f"{p_value:.6g}"
                if pd.notna(
                    p_value
                )
                else "N/A"
            )

            lines.append(
                f"{index + 1:02d}. "
                f"{row['Feature']}"
            )

            lines.append(
                f"    Effect size : "
                f"{row['AbsoluteEffectSize']:.4f}"
            )

            lines.append(
                f"    P-value     : "
                f"{p_text}"
            )

            lines.append(
                f"    Importance  : "
                f"{row['Importance']:.6f}"
            )

        lines.append("")

        lines.append(
            "OUTLIER SUMMARY"
        )

        lines.append(
            "-" * 70
        )

        for _, row in (
            outliers.head(10)
            .iterrows()
        ):

            lines.append(
                f"{row['Feature']}: "
                f"{int(row['Outliers'])} "
                f"outliers "
                f"({row['OutlierPercentage']:.2f}%)"
            )

        lines.append("")

        lines.append(
            "HIGHLY CORRELATED FEATURES"
        )

        lines.append(
            "-" * 70
        )

        if correlated.empty:

            lines.append(
                "No feature pairs exceeded "
                "the 0.90 correlation threshold."
            )

        else:

            for _, row in (
                correlated.iterrows()
            ):

                lines.append(
                    f"{row['FeatureA']} <-> "
                    f"{row['FeatureB']} : "
                    f"{row['Correlation']:.4f}"
                )

        lines.append("")

        lines.append(
            "PD vs HC FEATURE SEPARATION"
        )

        lines.append(
            "-" * 70
        )

        for _, row in (
            group_stats.head(10)
            .iterrows()
        ):

            lines.append(
                f"{row['Feature']}: "
                f"HC mean="
                f"{row['HC_Mean']:.6f}, "
                f"PD mean="
                f"{row['PD_Mean']:.6f}, "
                f"effect="
                f"{row['EffectSize']:.4f}, "
                f"p="
                f"{row['PValue']:.6g}"
            )

        lines.append("")

        lines.append(
            "=" * 70
        )

        lines.append(
            "END OF FEATURE ANALYSIS"
        )

        lines.append(
            "=" * 70
        )

        report_path = (
            self.output_directory
            / "feature_analysis_report.txt"
        )

        with open(
            report_path,
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
    ) -> None:

        if not self.results:

            raise RuntimeError(
                "Run analyze() first."
            )

        summary = (
            self.results[
                "summary"
            ]
        )

        ranking = (
            self.results[
                "ranking"
            ]
        )

        outliers = (
            self.results[
                "outliers"
            ]
        )

        correlated = (
            self.results[
                "correlated_pairs"
            ]
        )

        print()

        print(
            "=" * 70
        )

        print(
            "STEP 4 - FEATURE ANALYSIS"
        )

        print(
            "=" * 70
        )

        print()

        print(
            "DATASET"
        )

        print(
            f"Total recordings : "
            f"{summary['total']}"
        )

        print(
            f"Healthy          : "
            f"{summary['healthy']}"
        )

        print(
            f"Parkinson        : "
            f"{summary['parkinson']}"
        )

        print(
            f"Features         : "
            f"{summary['feature_count']}"
        )

        print()

        print(
            "TOP 10 FEATURES"
        )

        print(
            "-" * 70
        )

        for index, row in (
            ranking.head(10)
            .iterrows()
        ):

            print(
                f"{index + 1:02d}. "
                f"{row['Feature']:<22} "
                f"Effect="
                f"{row['AbsoluteEffectSize']:.4f} "
                f"Importance="
                f"{row['Importance']:.6f}"
            )

        print()

        print(
            "TOP OUTLIERS"
        )

        print(
            "-" * 70
        )

        for _, row in (
            outliers.head(5)
            .iterrows()
        ):

            print(
                f"{row['Feature']:<22} "
                f"{int(row['Outliers'])} "
                f"outliers "
                f"({row['OutlierPercentage']:.2f}%)"
            )

        print()

        print(
            "HIGH CORRELATION PAIRS"
        )

        print(
            "-" * 70
        )

        if correlated.empty:

            print(
                "None above 0.90."
            )

        else:

            for _, row in (
                correlated.head(10)
                .iterrows()
            ):

                print(
                    f"{row['FeatureA']} <-> "
                    f"{row['FeatureB']} : "
                    f"{row['Correlation']:.4f}"
                )

        print()

        print(
            "=" * 70
        )

        print(
            "Analysis complete."
        )

        print(
            "=" * 70
        )

    # ======================================================
    # Run All
    # ======================================================

    def run(
        self,
    ) -> Dict:

        self.analyze()

        self.save_reports()

        self.print_results()

        return self.results


# ==========================================================
# Standalone Execution
# ==========================================================

if __name__ == "__main__":

    analyzer = FeatureAnalyzer(
        csv_path=(
            "models/audio_training_features.csv"
        ),
        model_path=(
            "models/model.pkl"
        ),
        output_directory=(
            "models"
        ),
    )

    try:

        analyzer.run()

        print()

        print(
            "Reports created in:"
        )

        print(
            Path("models").resolve()
        )

        print()

    except Exception as exc:

        print()

        print(
            "=" * 70
        )

        print(
            "FEATURE ANALYSIS FAILED"
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
