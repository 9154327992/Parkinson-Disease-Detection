from typing import List, Optional

import numpy as np
import pandas as pd


class FeatureEngineering:
    """
    Feature engineering for the Parkinson voice dataset.

    The application uses the following 22 features:

        1.  MDVP:Fo(Hz)
        2.  MDVP:Fhi(Hz)
        3.  MDVP:Flo(Hz)
        4.  MDVP:Jitter(%)
        5.  MDVP:Jitter(Abs)
        6.  MDVP:RAP
        7.  MDVP:PPQ
        8.  Jitter:DDP
        9.  MDVP:Shimmer
        10. MDVP:Shimmer(dB)
        11. Shimmer:APQ3
        12. Shimmer:APQ5
        13. MDVP:APQ
        14. Shimmer:DDA
        15. NHR
        16. HNR
        17. RPDE
        18. DFA
        19. spread1
        20. spread2
        21. D2
        22. PPE

    Important:
        This module contains ONLY feature-engineering logic.

        Model training belongs in:
            backend/app/ml/train_model.py

        Prediction belongs in:
            backend/app/ml/predictor.py
    """

    # =====================================================
    # Feature Names
    # =====================================================

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

    # =====================================================
    # Constants
    # =====================================================

    TOTAL_FEATURES = 22

    TARGET_COLUMN = "status"

    HEALTHY_LABEL = 0

    PARKINSON_LABEL = 1

    # =====================================================
    # Initialization
    # =====================================================

    def __init__(
        self,
        feature_names: Optional[
            List[str]
        ] = None,
    ):
        """
        Initialize FeatureEngineering.

        Parameters
        ----------
        feature_names:
            Optional custom feature list.

        By default the application's official
        22-feature list is used.
        """

        if feature_names is None:

            self.FEATURE_NAMES = (
                [
                    *self.__class__.FEATURE_NAMES
                ]
            )

        else:

            self.FEATURE_NAMES = list(
                feature_names
            )

        if len(
            self.FEATURE_NAMES
        ) != self.TOTAL_FEATURES:

            raise ValueError(
                "FeatureEngineering requires "
                f"{self.TOTAL_FEATURES} features. "
                f"Received "
                f"{len(self.FEATURE_NAMES)}."
            )

    # =====================================================
    # Validate DataFrame
    # =====================================================

    def validate_dataframe(
        self,
        dataframe: pd.DataFrame,
    ) -> bool:
        """
        Validate that a dataframe contains
        all required model features.
        """

        if not isinstance(
            dataframe,
            pd.DataFrame,
        ):

            raise TypeError(
                "Expected a pandas DataFrame."
            )

        missing = [
            feature
            for feature in self.FEATURE_NAMES
            if feature not in dataframe.columns
        ]

        if missing:

            raise ValueError(
                "Missing features: "
                + ", ".join(missing)
            )

        return True

    # =====================================================
    # Validate Target
    # =====================================================

    def validate_target(
        self,
        dataframe: pd.DataFrame,
        target_column: str = TARGET_COLUMN,
    ) -> bool:
        """
        Validate that the target column exists.
        """

        if target_column not in (
            dataframe.columns
        ):

            raise ValueError(
                f"Target column "
                f"'{target_column}' "
                "not found in dataframe."
            )

        return True

    # =====================================================
    # Select Features
    # =====================================================

    def select_features(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Select the 22 model features in
        exactly the required order.
        """

        self.validate_dataframe(
            dataframe
        )

        return dataframe[
            self.FEATURE_NAMES
        ].copy()

    # =====================================================
    # Select Target
    # =====================================================

    def select_target(
        self,
        dataframe: pd.DataFrame,
        target_column: str = TARGET_COLUMN,
    ) -> pd.Series:
        """
        Select the target column.
        """

        self.validate_target(
            dataframe,
            target_column,
        )

        return dataframe[
            target_column
        ].copy()

    # =====================================================
    # Prepare Training Data
    # =====================================================

    def prepare_training_data(
        self,
        dataframe: pd.DataFrame,
        target_column: str = TARGET_COLUMN,
    ):
        """
        Prepare X and y for model training.

        Returns
        -------
        X : pandas.DataFrame
            22 model features.

        y : pandas.Series
            Target labels.
        """

        self.validate_dataframe(
            dataframe
        )

        self.validate_target(
            dataframe,
            target_column,
        )

        X = self.select_features(
            dataframe
        )

        y = self.select_target(
            dataframe,
            target_column,
        )

        # -------------------------------------------------
        # Convert features to numeric
        # -------------------------------------------------

        for feature in (
            self.FEATURE_NAMES
        ):

            X[feature] = pd.to_numeric(
                X[feature],
                errors="coerce",
            )

        # -------------------------------------------------
        # Convert target to numeric
        # -------------------------------------------------

        y = pd.to_numeric(
            y,
            errors="coerce",
        )

        # -------------------------------------------------
        # Validate target
        # -------------------------------------------------

        if y.isnull().any():

            raise ValueError(
                "Target column contains "
                "missing or non-numeric values."
            )

        y = y.astype(
            int
        )

        # -------------------------------------------------
        # Validate labels
        # -------------------------------------------------

        unique_labels = sorted(
            y.unique().tolist()
        )

        allowed_labels = [
            self.HEALTHY_LABEL,
            self.PARKINSON_LABEL,
        ]

        invalid_labels = [
            value
            for value in unique_labels
            if value not in allowed_labels
        ]

        if invalid_labels:

            raise ValueError(
                "Invalid target labels: "
                f"{invalid_labels}. "
                "Expected 0 = Healthy and "
                "1 = Parkinson's."
            )

        return X, y

    # =====================================================
    # Feature Vector → DataFrame
    # =====================================================

    def vector_to_dataframe(
        self,
        features: List[float],
    ) -> pd.DataFrame:
        """
        Convert a 22-value feature vector into
        a one-row DataFrame.

        This is useful for prediction.
        """

        self.validate_feature_vector(
            features
        )

        values = []

        for value in features:

            values.append(
                float(value)
            )

        return pd.DataFrame(
            [
                values
            ],
            columns=self.FEATURE_NAMES,
        )

    # =====================================================
    # DataFrame → Feature Vector
    # =====================================================

    def dataframe_to_vector(
        self,
        dataframe: pd.DataFrame,
    ) -> List[float]:
        """
        Convert one-row dataframe into
        an ordered feature vector.
        """

        selected = self.select_features(
            dataframe
        )

        if len(selected) != 1:

            raise ValueError(
                "Expected exactly one row."
            )

        values = selected.iloc[
            0
        ].tolist()

        self.validate_feature_vector(
            values
        )

        return [
            float(value)
            for value in values
        ]

    # =====================================================
    # Validate Feature Vector
    # =====================================================

    def validate_feature_vector(
        self,
        features,
    ) -> bool:
        """
        Validate an individual 22-feature vector.
        """

        if features is None:

            raise ValueError(
                "Feature vector is required."
            )

        try:

            count = len(
                features
            )

        except TypeError:

            raise ValueError(
                "Feature vector must be a "
                "list-like object."
            )

        if count != self.TOTAL_FEATURES:

            raise ValueError(
                "Exactly "
                f"{self.TOTAL_FEATURES} "
                "features are required. "
                f"Received {count}."
            )

        for index, value in enumerate(
            features
        ):

            try:

                numeric_value = float(
                    value
                )

            except (
                TypeError,
                ValueError,
            ):

                raise ValueError(
                    f"Feature {index + 1} "
                    "must be numeric."
                )

            if not np.isfinite(
                numeric_value
            ):

                raise ValueError(
                    f"Feature {index + 1} "
                    "must be finite."
                )

        return True

    # =====================================================
    # Correlation Matrix
    # =====================================================

    def correlation_matrix(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Compute the feature correlation matrix.
        """

        features = self.select_features(
            dataframe
        )

        features = features.apply(
            pd.to_numeric,
            errors="coerce",
        )

        return features.corr()

    # =====================================================
    # Feature Statistics
    # =====================================================

    def feature_statistics(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Generate descriptive statistics
        for all 22 features.
        """

        features = self.select_features(
            dataframe
        )

        features = features.apply(
            pd.to_numeric,
            errors="coerce",
        )

        return features.describe()

    # =====================================================
    # Missing Values
    # =====================================================

    def missing_values(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.Series:
        """
        Count missing values in every dataframe column.
        """

        return dataframe.isnull().sum()

    # =====================================================
    # Feature Missing Values
    # =====================================================

    def feature_missing_values(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.Series:
        """
        Count missing values only for model features.
        """

        features = self.select_features(
            dataframe
        )

        return features.isnull().sum()

    # =====================================================
    # Remove Missing Rows
    # =====================================================

    def remove_missing(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Remove rows containing missing values
        in the 22 model features.
        """

        features = self.select_features(
            dataframe
        )

        valid_mask = (
            ~features.isnull().any(
                axis=1
            )
        )

        return dataframe.loc[
            valid_mask
        ].copy()

    # =====================================================
    # Fill Missing
    # =====================================================

    def fill_missing(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Fill missing numeric values.

        Model feature columns are filled using
        their column mean.

        Other dataframe columns are preserved.
        """

        result = dataframe.copy()

        self.validate_dataframe(
            result
        )

        for feature in (
            self.FEATURE_NAMES
        ):

            result[feature] = pd.to_numeric(
                result[feature],
                errors="coerce",
            )

            mean_value = result[
                feature
            ].mean()

            if pd.isfinite(
                mean_value
            ):

                result[
                    feature
                ] = result[
                    feature
                ].fillna(
                    mean_value
                )

        return result

    # =====================================================
    # Fill Missing With Median
    # =====================================================

    def fill_missing_median(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Fill missing model features using
        column medians.
        """

        result = dataframe.copy()

        self.validate_dataframe(
            result
        )

        for feature in (
            self.FEATURE_NAMES
        ):

            result[feature] = pd.to_numeric(
                result[feature],
                errors="coerce",
            )

            median_value = result[
                feature
            ].median()

            if pd.isfinite(
                median_value
            ):

                result[
                    feature
                ] = result[
                    feature
                ].fillna(
                    median_value
                )

        return result

    # =====================================================
    # Detect Outliers
    # =====================================================

    def detect_outliers(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Detect feature outliers using IQR.

        Returns a dataframe containing:

            Feature
            Outliers
            LowerBound
            UpperBound
        """

        features = self.select_features(
            dataframe
        )

        results = []

        for column in (
            self.FEATURE_NAMES
        ):

            values = pd.to_numeric(
                features[column],
                errors="coerce",
            )

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

            count = int(
                (
                    (values < lower)
                    | (values > upper)
                ).sum()
            )

            results.append(
                {
                    "Feature":
                        column,

                    "Outliers":
                        count,

                    "LowerBound":
                        float(lower),

                    "UpperBound":
                        float(upper),
                }
            )

        return pd.DataFrame(
            results
        )

    # =====================================================
    # Remove Outliers
    # =====================================================

    def remove_outliers(
        self,
        dataframe: pd.DataFrame,
        multiplier: float = 1.5,
    ) -> pd.DataFrame:
        """
        Remove rows containing IQR outliers.

        Parameters
        ----------
        multiplier:
            IQR multiplier. Default is 1.5.
        """

        if multiplier <= 0:

            raise ValueError(
                "Multiplier must be greater than zero."
            )

        features = self.select_features(
            dataframe
        )

        mask = pd.Series(
            True,
            index=dataframe.index,
        )

        for column in (
            self.FEATURE_NAMES
        ):

            values = pd.to_numeric(
                features[column],
                errors="coerce",
            )

            q1 = values.quantile(
                0.25
            )

            q3 = values.quantile(
                0.75
            )

            iqr = q3 - q1

            lower = (
                q1
                - multiplier * iqr
            )

            upper = (
                q3
                + multiplier * iqr
            )

            column_mask = (
                values >= lower
            ) & (
                values <= upper
            )

            column_mask = (
                column_mask.fillna(
                    False
                )
            )

            mask &= column_mask

        return dataframe.loc[
            mask
        ].copy()

    # =====================================================
    # Normalize Features
    # =====================================================

    def normalize(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Perform Min-Max normalization.

        This method is intended for analysis.

        The production model should use the fitted
        scaler saved by the preprocessing pipeline.
        """

        features = self.select_features(
            dataframe
        )

        features = features.apply(
            pd.to_numeric,
            errors="coerce",
        )

        minimum = features.min()

        maximum = features.max()

        denominator = (
            maximum
            - minimum
        )

        # Prevent division by zero
        denominator = denominator.replace(
            0,
            1.0,
        )

        normalized = (
            features
            - minimum
        ) / denominator

        return normalized

    # =====================================================
    # Standardize Statistics
    # =====================================================

    def standardize_statistics(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Return mean and standard deviation
        for each model feature.
        """

        features = self.select_features(
            dataframe
        )

        features = features.apply(
            pd.to_numeric,
            errors="coerce",
        )

        return pd.DataFrame(
            {
                "Feature":
                    self.FEATURE_NAMES,

                "Mean":
                    [
                        features[
                            name
                        ].mean()
                        for name
                        in self.FEATURE_NAMES
                    ],

                "Std":
                    [
                        features[
                            name
                        ].std()
                        for name
                        in self.FEATURE_NAMES
                    ],
            }
        )

    # =====================================================
    # Feature Importance
    # =====================================================

    def feature_importance(
        self,
        model,
        dataframe: Optional[
            pd.DataFrame
        ] = None,
    ) -> pd.DataFrame:
        """
        Return model feature importance.

        Supports:

            - RandomForestClassifier
            - ExtraTreesClassifier
            - Pipeline
            - VotingClassifier
            - other estimators exposing
              feature_importances_
        """

        # -------------------------------------------------
        # Direct feature_importances_
        # -------------------------------------------------

        if hasattr(
            model,
            "feature_importances_",
        ):

            importance = np.asarray(
                model.feature_importances_,
                dtype=float,
            )

            if len(
                importance
            ) != self.TOTAL_FEATURES:

                raise ValueError(
                    "Model feature importance contains "
                    f"{len(importance)} values, "
                    f"expected {self.TOTAL_FEATURES}."
                )

            return pd.DataFrame(
                {
                    "Feature":
                        self.FEATURE_NAMES,

                    "Importance":
                        importance,
                }
            ).sort_values(
                by="Importance",
                ascending=False,
            ).reset_index(
                drop=True
            )

        # -------------------------------------------------
        # Pipeline
        # -------------------------------------------------

        if hasattr(
            model,
            "named_steps",
        ):

            underlying_model = (
                model.named_steps.get(
                    "model"
                )
            )

            if underlying_model is not None:

                return self.feature_importance(
                    underlying_model,
                    dataframe,
                )

        # -------------------------------------------------
        # VotingClassifier
        # -------------------------------------------------

        if hasattr(
            model,
            "estimators_",
        ):

            importances = []

            for estimator in (
                model.estimators_
            ):

                if hasattr(
                    estimator,
                    "feature_importances_",
                ):

                    values = np.asarray(
                        estimator.feature_importances_,
                        dtype=float,
                    )

                    if len(
                        values
                    ) == self.TOTAL_FEATURES:

                        importances.append(
                            values
                        )

            if importances:

                mean_importance = (
                    np.mean(
                        np.asarray(
                            importances
                        ),
                        axis=0,
                    )
                )

                return pd.DataFrame(
                    {
                        "Feature":
                            self.FEATURE_NAMES,

                        "Importance":
                            mean_importance,
                    }
                ).sort_values(
                    by="Importance",
                    ascending=False,
                ).reset_index(
                    drop=True
                )

        raise ValueError(
            "The supplied model does not expose "
            "feature_importances_."
        )

    # =====================================================
    # Feature Count
    # =====================================================

    def total_features(
        self,
    ) -> int:
        """
        Return total number of model features.
        """

        return self.TOTAL_FEATURES

    # =====================================================
    # Feature Names
    # =====================================================

    def get_feature_names(
        self,
    ) -> List[str]:
        """
        Return a copy of the feature names.
        """

        return self.FEATURE_NAMES.copy()

    # =====================================================
    # Feature Index
    # =====================================================

    def feature_index(
        self,
        feature_name: str,
    ) -> int:
        """
        Return the zero-based index of a feature.
        """

        if feature_name not in (
            self.FEATURE_NAMES
        ):

            raise ValueError(
                f"Unknown feature: "
                f"{feature_name}"
            )

        return self.FEATURE_NAMES.index(
            feature_name
        )

    # =====================================================
    # Check Feature Names
    # =====================================================

    def validate_feature_names(
        self,
        names: List[str],
    ) -> bool:
        """
        Validate a feature-name list against
        the official 22-feature order.
        """

        if list(names) != (
            self.FEATURE_NAMES
        ):

            raise ValueError(
                "Feature names or order do not "
                "match the application's 22-feature schema."
            )

        return True

    # =====================================================
    # Dataset Shape
    # =====================================================

    def dataset_shape(
        self,
        dataframe: pd.DataFrame,
    ) -> dict:
        """
        Return useful dataset shape information.
        """

        self.validate_dataframe(
            dataframe
        )

        return {
            "rows":
                int(
                    len(dataframe)
                ),

            "columns":
                int(
                    len(dataframe.columns)
                ),

            "features":
                self.TOTAL_FEATURES,

            "feature_columns":
                self.FEATURE_NAMES.copy(),
        }

    # =====================================================
    # Class Distribution
    # =====================================================

    def class_distribution(
        self,
        dataframe: pd.DataFrame,
        target_column: str = TARGET_COLUMN,
    ) -> dict:
        """
        Return class counts.

        0 = Healthy
        1 = Parkinson's
        """

        self.validate_target(
            dataframe,
            target_column,
        )

        values = pd.to_numeric(
            dataframe[
                target_column
            ],
            errors="coerce",
        )

        return {
            "healthy":
                int(
                    (
                        values
                        == self.HEALTHY_LABEL
                    ).sum()
                ),

            "parkinson":
                int(
                    (
                        values
                        == self.PARKINSON_LABEL
                    ).sum()
                ),

            "total":
                int(
                    values.notna().sum()
                ),
        }

    # =====================================================
    # Summary
    # =====================================================

    def summary(
        self,
        dataframe: pd.DataFrame,
        target_column: str = TARGET_COLUMN,
    ) -> dict:
        """
        Return a complete feature-engineering summary.
        """

        self.validate_dataframe(
            dataframe
        )

        summary = {
            "rows":
                int(
                    len(dataframe)
                ),

            "total_features":
                self.TOTAL_FEATURES,

            "feature_names":
                self.FEATURE_NAMES.copy(),

            "missing_values":
                {
                    key:
                        int(value)
                    for key, value
                    in self.feature_missing_values(
                        dataframe
                    ).items()
                },
        }

        if target_column in (
            dataframe.columns
        ):

            summary[
                "class_distribution"
            ] = self.class_distribution(
                dataframe,
                target_column,
            )

        return summary


# ==========================================================
# Module-Level Convenience
# ==========================================================

FEATURE_ENGINEERING = FeatureEngineering()


def get_feature_names() -> List[str]:
    """
    Return the application's 22 feature names.
    """

    return FEATURE_ENGINEERING.get_feature_names()


def total_features() -> int:
    """
    Return the application's feature count.
    """

    return FEATURE_ENGINEERING.total_features()
