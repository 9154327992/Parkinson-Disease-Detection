"""
Feature Engineering Module

Handles feature validation, selection, engineering,
and statistical analysis for Parkinson Disease Detection.
"""

from typing import List

import numpy as np
import pandas as pd


class FeatureEngineering:
    """
    Feature engineering for Parkinson dataset.
    """

    # =====================================================
    # Original Features
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
    # Validate Features
    # =====================================================

    def validate_dataframe(
        self,
        dataframe: pd.DataFrame,
    ) -> bool:
        """
        Validate dataframe columns.
        """

        missing = set(self.FEATURE_NAMES) - set(dataframe.columns)

        if missing:
            raise ValueError(
                f"Missing features: {missing}"
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
        Select model features.
        """

        self.validate_dataframe(dataframe)

        return dataframe[self.FEATURE_NAMES]

    # =====================================================
    # Correlation Matrix
    # =====================================================

    def correlation_matrix(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Compute feature correlation matrix.
        """

        features = self.select_features(dataframe)

        return features.corr()

    # =====================================================
    # Feature Statistics
    # =====================================================

    def feature_statistics(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Generate descriptive statistics.
        """

        features = self.select_features(dataframe)

        return features.describe()

    # =====================================================
    # Missing Values
    # =====================================================

    def missing_values(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.Series:
        """
        Count missing values.
        """

        return dataframe.isnull().sum()

    # =====================================================
    # Remove Missing
    # =====================================================

    def remove_missing(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Remove rows containing missing values.
        """

        return dataframe.dropna()

    # =====================================================
    # Fill Missing
    # =====================================================

    def fill_missing(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Fill missing values using column means.
        """

        return dataframe.fillna(
            dataframe.mean(numeric_only=True)
        )

    # =====================================================
    # Detect Outliers
    # =====================================================

    def detect_outliers(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Detect outliers using IQR.
        """

        features = self.select_features(dataframe)

        outliers = {}

        for column in features.columns:

            q1 = features[column].quantile(0.25)
            q3 = features[column].quantile(0.75)

            iqr = q3 - q1

            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr

            outliers[column] = (
                (features[column] < lower)
                | (features[column] > upper)
            ).sum()

        return pd.DataFrame(
            outliers.items(),
            columns=["Feature", "Outliers"],
        )

    # =====================================================
    # Normalize Features
    # =====================================================

    def normalize(
        self,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Min-Max normalization.
        """

        features = self.select_features(dataframe)

        return (
            features - features.min()
        ) / (
            features.max() - features.min()
        )

    # =====================================================
    # Feature Importance
    # =====================================================

    def feature_importance(
        self,
        model,
        dataframe: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Return feature importance.

        Model must expose feature_importances_.
        """

        importance = model.feature_importances_

        return pd.DataFrame(
            {
                "Feature": self.FEATURE_NAMES,
                "Importance": importance,
            }
        ).sort_values(
            by="Importance",
            ascending=False,
        )

    # =====================================================
    # Prepare Training Data
    # =====================================================

    def prepare_training_data(
        self,
        dataframe: pd.DataFrame,
        target_column: str = "status",
    ):
        """
        Split features and target.
        """

        self.validate_dataframe(dataframe)

        X = dataframe[self.FEATURE_NAMES]

        y = dataframe[target_column]

        return X, y

    # =====================================================
    # Feature Count
    # =====================================================

    def total_features(self) -> int:
        """
        Return number of features.
        """

        return len(self.FEATURE_NAMES)

    # =====================================================
    # Feature Names
    # =====================================================

    def get_feature_names(self) -> List[str]:
        """
        Return feature names.
        """

        return self.FEATURE_NAMES.copy()
