from pathlib import Path
from typing import Dict, List, Tuple

import json
import warnings

import joblib
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
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from sklearn.model_selection import (
    StratifiedKFold,
    cross_val_score,
    train_test_split,
)

from sklearn.pipeline import Pipeline

from sklearn.preprocessing import StandardScaler


from app.ml.audio_feature_service import (
    AudioFeatureService,
)

from app.ml.feature_engineering import (
    FeatureEngineering,
)


# ==========================================================
# Warnings
# ==========================================================

warnings.filterwarnings(
    "ignore",
    category=UserWarning,
)


# ==========================================================
# Constants
# ==========================================================

HEALTHY = 0

PARKINSON = 1

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
# Model Trainer
# ==========================================================

class ModelTrainer:
    """
    Train the Parkinson audio model from WAV files.
    """

    # ======================================================
    # Initialization
    # ======================================================

    def __init__(
        self,
        dataset_path: str = "datasets/audio",
        model_path: str = "models/model.pkl",
        scaler_path: str = "models/scaler.pkl",
        feature_csv_path: str = (
            "models/audio_training_features.csv"
        ),
        report_path: str = (
            "models/audio_training_report.json"
        ),
    ):

        self.dataset_path = Path(
            dataset_path
        )

        self.model_path = Path(
            model_path
        )

        self.scaler_path = Path(
            scaler_path
        )

        self.feature_csv_path = Path(
            feature_csv_path
        )

        self.report_path = Path(
            report_path
        )

        # --------------------------------------------------
        # Feature services
        # --------------------------------------------------

        self.audio_feature_service = (
            AudioFeatureService()
        )

        self.feature_engineering = (
            FeatureEngineering()
        )

        # --------------------------------------------------
        # Verify feature contract
        # --------------------------------------------------

        self._validate_feature_contract()

        # --------------------------------------------------
        # Model
        # --------------------------------------------------

        self.base_model = (
            self._create_model()
        )

        # --------------------------------------------------
        # Complete training pipeline
        #
        # IMPORTANT:
        # The pipeline contains:
        #
        #   imputer
        #       ↓
        #   scaler
        #       ↓
        #   classifier
        #
        # This prevents preprocessing leakage.
        # --------------------------------------------------

        self.pipeline = Pipeline(
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
                    self.base_model,
                ),
            ]
        )

        # --------------------------------------------------
        # Runtime state
        # --------------------------------------------------

        self.training_dataframe = None

        self.successful_files = []

        self.failed_files = []

        self.metrics = {}

    # ======================================================
    # Feature Contract
    # ======================================================

    def _validate_feature_contract(
        self,
    ) -> None:
        """
        Make sure audio extraction,
        feature engineering and training
        all use exactly the same 22 features.
        """

        audio_names = (
            self.audio_feature_service
            .get_feature_names()
        )

        engineering_names = (
            self.feature_engineering
            .get_feature_names()
        )

        if list(audio_names) != (
            FEATURE_NAMES
        ):

            raise RuntimeError(
                "AudioFeatureService feature order "
                "does not match the 22-feature "
                "training schema.\n\n"
                f"Expected:\n{FEATURE_NAMES}\n\n"
                f"Received:\n{audio_names}"
            )

        if list(engineering_names) != (
            FEATURE_NAMES
        ):

            raise RuntimeError(
                "FeatureEngineering feature order "
                "does not match the 22-feature "
                "training schema.\n\n"
                f"Expected:\n{FEATURE_NAMES}\n\n"
                f"Received:\n{engineering_names}"
            )

        if len(
            FEATURE_NAMES
        ) != TOTAL_FEATURES:

            raise RuntimeError(
                "Internal feature schema error."
            )

    # ======================================================
    # Create Model
    # ======================================================

    def _create_model(self):
        """
        Create a balanced ensemble classifier.
        """

        random_forest = (
            RandomForestClassifier(
                n_estimators=500,
                random_state=42,
                class_weight="balanced",
                max_features="sqrt",
                n_jobs=-1,
            )
        )

        extra_trees = (
            ExtraTreesClassifier(
                n_estimators=500,
                random_state=42,
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
    # Find WAV Files
    # ======================================================

    def find_audio_files(
        self,
    ) -> List[
        Tuple[
            Path,
            int,
            str,
        ]
    ]:
        """
        Find all WAV files in PD and HC folders.
        """

        if not self.dataset_path.exists():

            raise FileNotFoundError(
                "Audio dataset directory not found:\n"
                f"{self.dataset_path.resolve()}"
            )

        pd_directory = (
            self.dataset_path
            / "PD"
        )

        hc_directory = (
            self.dataset_path
            / "HC"
        )

        if not pd_directory.exists():

            raise FileNotFoundError(
                "PD directory not found:\n"
                f"{pd_directory.resolve()}"
            )

        if not hc_directory.exists():

            raise FileNotFoundError(
                "HC directory not found:\n"
                f"{hc_directory.resolve()}"
            )

        files = []

        # --------------------------------------------------
        # PD
        # --------------------------------------------------

        for path in pd_directory.rglob(
            "*"
        ):

            if (
                path.is_file()
                and path.suffix.lower()
                == ".wav"
            ):

                files.append(
                    (
                        path,
                        PARKINSON,
                        "PD",
                    )
                )

        # --------------------------------------------------
        # HC
        # --------------------------------------------------

        for path in hc_directory.rglob(
            "*"
        ):

            if (
                path.is_file()
                and path.suffix.lower()
                == ".wav"
            ):

                files.append(
                    (
                        path,
                        HEALTHY,
                        "HC",
                    )
                )

        # --------------------------------------------------
        # Sort
        # --------------------------------------------------

        files.sort(
            key=lambda item: str(
                item[0]
            ).lower()
        )

        if not files:

            raise RuntimeError(
                "No WAV files were found."
            )

        return files

    # ======================================================
    # Dataset Summary
    # ======================================================

    def dataset_summary(
        self,
        files,
    ) -> Dict:

        pd_count = sum(
            1
            for _, label, _
            in files
            if label == PARKINSON
        )

        hc_count = sum(
            1
            for _, label, _
            in files
            if label == HEALTHY
        )

        return {
            "total":
                len(files),

            "pd":
                pd_count,

            "hc":
                hc_count,
        }

    # ======================================================
    # Extract One WAV
    # ======================================================

    def extract_one(
        self,
        path: Path,
        label: int,
        class_name: str,
    ) -> Dict:
        """
        Extract the 22 features from one WAV file.
        """

        # --------------------------------------------------
        # Extract dictionary
        # --------------------------------------------------

        features = (
            self.audio_feature_service
            .extract_features_from_file(
                str(path)
            )
        )

        if not isinstance(
            features,
            dict,
        ):

            raise ValueError(
                "AudioFeatureService did not "
                "return a feature dictionary."
            )

        # --------------------------------------------------
        # Validate dictionary
        # --------------------------------------------------

        self.audio_feature_service.validate_feature_dictionary(
            features
        )

        # --------------------------------------------------
        # Ordered vector
        # --------------------------------------------------

        vector = (
            self.audio_feature_service
            .to_feature_vector(
                features
            )
        )

        if len(vector) != (
            TOTAL_FEATURES
        ):

            raise ValueError(
                "Expected "
                f"{TOTAL_FEATURES} features, "
                f"received {len(vector)}."
            )

        # --------------------------------------------------
        # Create row
        # --------------------------------------------------

        row = {}

        for name, value in zip(
            FEATURE_NAMES,
            vector,
        ):

            numeric_value = float(
                value
            )

            if not np.isfinite(
                numeric_value
            ):

                raise ValueError(
                    f"Feature '{name}' "
                    "is not finite."
                )

            row[name] = (
                numeric_value
            )

        # --------------------------------------------------
        # Metadata
        # --------------------------------------------------

        row["status"] = int(
            label
        )

        row["class_name"] = (
            class_name
        )

        row["audio_file"] = (
            path.name
        )

        row["audio_path"] = (
            str(path)
        )

        return row

    # ======================================================
    # Extract Complete Dataset
    # ======================================================

    def extract_dataset(
        self,
    ) -> pd.DataFrame:
        """
        Extract features from every WAV recording.
        """

        files = (
            self.find_audio_files()
        )

        summary = (
            self.dataset_summary(
                files
            )
        )

        print()
        print(
            "=" * 70
        )
        print(
            "PARKINSON AUDIO DATASET"
        )
        print(
            "=" * 70
        )
        print(
            f"Total recordings : "
            f"{summary['total']}"
        )
        print(
            f"PD recordings    : "
            f"{summary['pd']}"
        )
        print(
            f"HC recordings    : "
            f"{summary['hc']}"
        )
        print(
            "=" * 70
        )
        print()

        if summary["pd"] < 2:

            raise RuntimeError(
                "At least two PD recordings are required."
            )

        if summary["hc"] < 2:

            raise RuntimeError(
                "At least two HC recordings are required."
            )

        rows = []

        self.successful_files = []

        self.failed_files = []

        # --------------------------------------------------
        # Process every recording
        # --------------------------------------------------

        for index, (
            path,
            label,
            class_name,
        ) in enumerate(
            files,
            start=1,
        ):

            print(
                f"[{index:03d}/{len(files):03d}] "
                f"{class_name:<3} "
                f"{path.name}"
            )

            try:

                row = self.extract_one(
                    path,
                    label,
                    class_name,
                )

                rows.append(
                    row
                )

                self.successful_files.append(
                    str(path)
                )

                print(
                    "       OK"
                )

            except Exception as exc:

                self.failed_files.append(
                    {
                        "file":
                            str(path),

                        "class":
                            class_name,

                        "error":
                            str(exc),
                    }
                )

                print(
                    "       FAILED: "
                    f"{exc}"
                )

        if not rows:

            raise RuntimeError(
                "No WAV recordings could be "
                "successfully processed."
            )

        dataframe = pd.DataFrame(
            rows
        )

        # --------------------------------------------------
        # Ensure columns exist
        # --------------------------------------------------

        missing = [
            feature
            for feature in FEATURE_NAMES
            if feature not in dataframe.columns
        ]

        if missing:

            raise RuntimeError(
                "Extracted dataset is missing "
                f"features: {missing}"
            )

        # --------------------------------------------------
        # Numeric conversion
        # --------------------------------------------------

        for feature in (
            FEATURE_NAMES
        ):

            dataframe[feature] = pd.to_numeric(
                dataframe[feature],
                errors="coerce",
            )

        # --------------------------------------------------
        # Remove invalid rows
        # --------------------------------------------------

        invalid_mask = (
            ~np.isfinite(
                dataframe[
                    FEATURE_NAMES
                ].to_numpy(
                    dtype=float
                )
            ).all(
                axis=1
            )
        )

        if invalid_mask.any():

            invalid_rows = dataframe[
                invalid_mask
            ]

            for _, row in (
                invalid_rows.iterrows()
            ):

                self.failed_files.append(
                    {
                        "file":
                            row[
                                "audio_path"
                            ],

                        "class":
                            row[
                                "class_name"
                            ],

                        "error":
                            "Non-finite extracted feature.",
                    }
                )

            dataframe = dataframe[
                ~invalid_mask
            ].copy()

        # --------------------------------------------------
        # Require both classes
        # --------------------------------------------------

        if dataframe[
            "status"
        ].nunique() < 2:

            raise RuntimeError(
                "Only one class remains after "
                "audio feature extraction."
            )

        # --------------------------------------------------
        # Save extracted features
        # --------------------------------------------------

        self.feature_csv_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        dataframe.to_csv(
            self.feature_csv_path,
            index=False,
        )

        self.training_dataframe = (
            dataframe
        )

        # --------------------------------------------------
        # Final summary
        # --------------------------------------------------

        successful_pd = int(
            (
                dataframe["status"]
                == PARKINSON
            ).sum()
        )

        successful_hc = int(
            (
                dataframe["status"]
                == HEALTHY
            ).sum()
        )

        print()
        print(
            "=" * 70
        )
        print(
            "FEATURE EXTRACTION COMPLETE"
        )
        print(
            "=" * 70
        )
        print(
            f"Successful : "
            f"{len(dataframe)}"
        )
        print(
            f"PD         : "
            f"{successful_pd}"
        )
        print(
            f"HC         : "
            f"{successful_hc}"
        )
        print(
            f"Failed     : "
            f"{len(self.failed_files)}"
        )
        print(
            f"CSV        : "
            f"{self.feature_csv_path}"
        )
        print(
            "=" * 70
        )
        print()

        return dataframe

    # ======================================================
    # Prepare Training Data
    # ======================================================

    def prepare_training_data(
        self,
        dataframe: pd.DataFrame,
    ):

        if dataframe is None:

            raise ValueError(
                "Training dataframe is required."
            )

        X, y = (
            self.feature_engineering
            .prepare_training_data(
                dataframe,
                target_column="status",
            )
        )

        # --------------------------------------------------
        # Numeric
        # --------------------------------------------------

        for feature in (
            FEATURE_NAMES
        ):

            X[feature] = pd.to_numeric(
                X[feature],
                errors="coerce",
            )

        # --------------------------------------------------
        # Labels
        # --------------------------------------------------

        y = pd.to_numeric(
            y,
            errors="coerce",
        )

        if y.isnull().any():

            raise ValueError(
                "Training labels contain "
                "missing values."
            )

        y = y.astype(
            int
        )

        # --------------------------------------------------
        # Check classes
        # --------------------------------------------------

        labels = sorted(
            y.unique().tolist()
        )

        if labels != [
            HEALTHY,
            PARKINSON,
        ]:

            raise ValueError(
                "Training data must contain "
                "both classes 0 and 1. "
                f"Found: {labels}"
            )

        return X, y

    # ======================================================
    # Split Data
    # ======================================================

    def split_data(
        self,
        X: pd.DataFrame,
        y: pd.Series,
    ):

        return train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=42,
            stratify=y,
        )

    # ======================================================
    # Cross Validation
    # ======================================================

    def cross_validate(
        self,
        X: pd.DataFrame,
        y: pd.Series,
    ) -> Dict:
        """
        Perform stratified cross-validation.

        The preprocessing pipeline is fitted separately
        within each fold.
        """

        class_counts = (
            y.value_counts()
        )

        minimum_class_count = int(
            class_counts.min()
        )

        folds = min(
            5,
            minimum_class_count,
        )

        if folds < 2:

            return {
                "folds":
                    0,

                "accuracy_mean":
                    None,

                "accuracy_std":
                    None,

                "scores":
                    [],
            }

        cv = StratifiedKFold(
            n_splits=folds,
            shuffle=True,
            random_state=42,
        )

        scores = cross_val_score(
            self.pipeline,
            X,
            y,
            cv=cv,
            scoring="accuracy",
            n_jobs=1,
        )

        return {
            "folds":
                int(folds),

            "accuracy_mean":
                float(
                    np.mean(scores)
                ),

            "accuracy_std":
                float(
                    np.std(scores)
                ),

            "scores":
                [
                    float(value)
                    for value in scores
                ],
        }

    # ======================================================
    # Calculate Metrics
    # ======================================================

    def calculate_metrics(
        self,
        y_true,
        predictions,
        probabilities=None,
    ) -> Dict:
        """
        Calculate complete binary classification metrics.

        0 = Healthy
        1 = Parkinson
        """

        matrix = confusion_matrix(
            y_true,
            predictions,
            labels=[
                HEALTHY,
                PARKINSON,
            ],
        )

        tn, fp, fn, tp = (
            matrix.ravel()
        )

        accuracy = (
            accuracy_score(
                y_true,
                predictions,
            )
        )

        precision = (
            precision_score(
                y_true,
                predictions,
                pos_label=PARKINSON,
                zero_division=0,
            )
        )

        sensitivity = (
            recall_score(
                y_true,
                predictions,
                pos_label=PARKINSON,
                zero_division=0,
            )
        )

        specificity = (
            tn
            / (
                tn + fp
            )
            if (
                tn + fp
            ) > 0
            else 0.0
        )

        f1 = (
            f1_score(
                y_true,
                predictions,
                pos_label=PARKINSON,
                zero_division=0,
            )
        )

        balanced_accuracy = (
            sensitivity
            + specificity
        ) / 2.0

        metrics = {
            "accuracy":
                float(
                    accuracy
                ),

            "precision":
                float(
                    precision
                ),

            "sensitivity":
                float(
                    sensitivity
                ),

            "recall":
                float(
                    sensitivity
                ),

            "specificity":
                float(
                    specificity
                ),

            "f1":
                float(
                    f1
                ),

            "balanced_accuracy":
                float(
                    balanced_accuracy
                ),

            "true_negative":
                int(tn),

            "false_positive":
                int(fp),

            "false_negative":
                int(fn),

            "true_positive":
                int(tp),

            "confusion_matrix":
                matrix.tolist(),

            "classification_report":
                classification_report(
                    y_true,
                    predictions,
                    output_dict=True,
                    zero_division=0,
                ),
        }

        # --------------------------------------------------
        # ROC-AUC
        # --------------------------------------------------

        if probabilities is not None:

            try:

                metrics[
                    "roc_auc"
                ] = float(
                    roc_auc_score(
                        y_true,
                        probabilities,
                    )
                )

            except Exception:

                metrics[
                    "roc_auc"
                ] = None

        else:

            metrics[
                "roc_auc"
            ] = None

        return metrics

    # ======================================================
    # Train
    # ======================================================

    def train(
        self,
        dataframe=None,
    ) -> Dict:
        """
        Train the model.
        """

        if dataframe is None:

            if (
                self.training_dataframe
                is None
            ):

                dataframe = (
                    self.extract_dataset()
                )

            else:

                dataframe = (
                    self.training_dataframe
                )

        self.training_dataframe = (
            dataframe
        )

        X, y = (
            self.prepare_training_data(
                dataframe
            )
        )

        print()
        print(
            "=" * 70
        )
        print(
            "TRAINING DATA"
        )
        print(
            "=" * 70
        )
        print(
            f"Total : {len(X)}"
        )
        print(
            f"HC    : "
            f"{int((y == HEALTHY).sum())}"
        )
        print(
            f"PD    : "
            f"{int((y == PARKINSON).sum())}"
        )
        print(
            "=" * 70
        )
        print()

        # --------------------------------------------------
        # Cross-validation
        # --------------------------------------------------

        print(
            "Running stratified cross-validation..."
        )

        cv_metrics = (
            self.cross_validate(
                X,
                y,
            )
        )

        if (
            cv_metrics[
                "accuracy_mean"
            ]
            is not None
        ):

            print(
                "Cross-validation accuracy: "
                f"{cv_metrics['accuracy_mean']:.4f}"
            )

            print(
                "Cross-validation std: "
                f"{cv_metrics['accuracy_std']:.4f}"
            )

        # --------------------------------------------------
        # Holdout split
        # --------------------------------------------------

        (
            X_train,
            X_test,
            y_train,
            y_test,
        ) = self.split_data(
            X,
            y,
        )

        print()
        print(
            f"Training samples: "
            f"{len(X_train)}"
        )

        print(
            f"Testing samples: "
            f"{len(X_test)}"
        )

        # --------------------------------------------------
        # Fit
        # --------------------------------------------------

        print()
        print(
            "Training ensemble model..."
        )

        self.pipeline.fit(
            X_train,
            y_train,
        )

        print(
            "Training complete."
        )

        # --------------------------------------------------
        # Predictions
        # --------------------------------------------------

        predictions = (
            self.pipeline.predict(
                X_test
            )
        )

        # --------------------------------------------------
        # Probabilities
        # --------------------------------------------------

        probabilities = None

        if hasattr(
            self.pipeline,
            "predict_proba",
        ):

            try:

                probabilities = (
                    self.pipeline
                    .predict_proba(
                        X_test
                    )[:, 1]
                )

            except Exception:

                probabilities = None

        # --------------------------------------------------
        # Metrics
        # --------------------------------------------------

        metrics = (
            self.calculate_metrics(
                y_test,
                predictions,
                probabilities,
            )
        )

        metrics[
            "cross_validation"
        ] = cv_metrics

        metrics[
            "training_samples"
        ] = int(
            len(X_train)
        )

        metrics[
            "test_samples"
        ] = int(
            len(X_test)
        )

        metrics[
            "total_samples"
        ] = int(
            len(X)
        )

        metrics[
            "successful_audio_files"
        ] = int(
            len(
                self.successful_files
            )
        )

        metrics[
            "failed_audio_files"
        ] = int(
            len(
                self.failed_files
            )
        )

        self.metrics = metrics

        self.print_metrics(
            metrics
        )

        return metrics

    # ======================================================
    # Print Metrics
    # ======================================================

    def print_metrics(
        self,
        metrics: Dict,
    ) -> None:

        print()
        print(
            "=" * 70
        )
        print(
            "MODEL RESULTS"
        )
        print(
            "=" * 70
        )

        print(
            f"Accuracy            : "
            f"{metrics['accuracy']:.4f}"
        )

        print(
            f"Sensitivity / Recall: "
            f"{metrics['sensitivity']:.4f}"
        )

        print(
            f"Specificity         : "
            f"{metrics['specificity']:.4f}"
        )

        print(
            f"Precision           : "
            f"{metrics['precision']:.4f}"
        )

        print(
            f"F1 Score            : "
            f"{metrics['f1']:.4f}"
        )

        print(
            f"Balanced Accuracy   : "
            f"{metrics['balanced_accuracy']:.4f}"
        )

        if (
            metrics.get(
                "roc_auc"
            )
            is not None
        ):

            print(
                f"ROC-AUC             : "
                f"{metrics['roc_auc']:.4f}"
            )

        print()
        print(
            "Confusion Matrix"
        )

        print(
            "Rows = Actual"
        )

        print(
            "Columns = Predicted"
        )

        print(
            "       HC    PD"
        )

        matrix = np.asarray(
            metrics[
                "confusion_matrix"
            ]
        )

        print(
            f"HC     "
            f"{matrix[0][0]:<5}"
            f"{matrix[0][1]:<5}"
        )

        print(
            f"PD     "
            f"{matrix[1][0]:<5}"
            f"{matrix[1][1]:<5}"
        )

        print()
        print(
            "Class convention:"
        )

        print(
            "    0 = Healthy Control"
        )

        print(
            "    1 = Parkinson's Disease"
        )

        print(
            "=" * 70
        )
        print()

    # ======================================================
    # Feature Importance
    # ======================================================

    def feature_importance(
        self,
    ) -> pd.DataFrame:
        """
        Return feature importance from the trained model.
        """

        if self.pipeline is None:

            raise RuntimeError(
                "Model has not been trained."
            )

        return (
            self.feature_engineering
            .feature_importance(
                self.pipeline
            )
        )

    # ======================================================
    # Save Model
    # ======================================================

    def save(
        self,
    ) -> None:
        """
        Save the complete trained pipeline
        and the scaler separately.

        model.pkl:
            Complete pipeline:
                imputer
                scaler
                classifier

        scaler.pkl:
            Standalone StandardScaler for
            compatibility with older application code.
        """

        if self.pipeline is None:

            raise RuntimeError(
                "Nothing to save. "
                "Train the model first."
            )

        # --------------------------------------------------
        # Create directories
        # --------------------------------------------------

        self.model_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.scaler_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.feature_csv_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.report_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # --------------------------------------------------
        # Save complete pipeline
        # --------------------------------------------------

        joblib.dump(
            self.pipeline,
            self.model_path,
        )

        # --------------------------------------------------
        # Extract scaler
        # --------------------------------------------------

        scaler = (
            self.pipeline
            .named_steps
            .get(
                "scaler"
            )
        )

        if scaler is None:

            raise RuntimeError(
                "Trained pipeline does not contain "
                "a scaler."
            )

        joblib.dump(
            scaler,
            self.scaler_path,
        )

        # --------------------------------------------------
        # Save report
        # --------------------------------------------------

        report = {
            "dataset_path":
                str(
                    self.dataset_path.resolve()
                ),

            "model_path":
                str(
                    self.model_path.resolve()
                ),

            "scaler_path":
                str(
                    self.scaler_path.resolve()
                ),

            "feature_csv":
                str(
                    self.feature_csv_path.resolve()
                ),

            "feature_count":
                TOTAL_FEATURES,

            "feature_names":
                FEATURE_NAMES,

            "class_labels":
                {
                    "0":
                        "Healthy Control",

                    "1":
                        "Parkinson's Disease",
                },

            "successful_files":
                self.successful_files,

            "failed_files":
                self.failed_files,

            "metrics":
                self.metrics,
        }

        with open(
            self.report_path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                report,
                file,
                indent=4,
                default=str,
            )

        print()
        print(
            "=" * 70
        )
        print(
            "MODEL ARTIFACTS SAVED"
        )
        print(
            "=" * 70
        )

        print(
            f"Model : "
            f"{self.model_path.resolve()}"
        )

        print(
            f"Scaler: "
            f"{self.scaler_path.resolve()}"
        )

        print(
            f"CSV   : "
            f"{self.feature_csv_path.resolve()}"
        )

        print(
            f"Report: "
            f"{self.report_path.resolve()}"
        )

        print(
            "=" * 70
        )
        print()

    # ======================================================
    # Train + Save
    # ======================================================

    def train_and_save(
        self,
    ) -> Dict:

        dataframe = (
            self.extract_dataset()
        )

        metrics = (
            self.train(
                dataframe
            )
        )

        self.save()

        return metrics

    # ======================================================
    # Model Information
    # ======================================================

    def model_information(
        self,
    ) -> Dict:

        return {
            "algorithm":
                self.pipeline
                .named_steps[
                    "model"
                ].__class__.__name__,

            "dataset":
                str(
                    self.dataset_path
                ),

            "model_path":
                str(
                    self.model_path
                ),

            "scaler_path":
                str(
                    self.scaler_path
                ),

            "feature_csv":
                str(
                    self.feature_csv_path
                ),

            "feature_count":
                TOTAL_FEATURES,

            "features":
                FEATURE_NAMES.copy(),

            "successful_files":
                len(
                    self.successful_files
                ),

            "failed_files":
                len(
                    self.failed_files
                ),
        }


# ==========================================================
# Standalone Training
# ==========================================================

if __name__ == "__main__":

    trainer = ModelTrainer(
        dataset_path="datasets/audio",
        model_path="models/model.pkl",
        scaler_path="models/scaler.pkl",
        feature_csv_path=(
            "models/audio_training_features.csv"
        ),
        report_path=(
            "models/audio_training_report.json"
        ),
    )

    try:

        metrics = (
            trainer.train_and_save()
        )

        print()
        print(
            "=" * 70
        )
        print(
            "AUDIO MODEL TRAINING COMPLETE"
        )
        print(
            "=" * 70
        )

        print(
            f"Accuracy     : "
            f"{metrics['accuracy']:.4f}"
        )

        print(
            f"Sensitivity  : "
            f"{metrics['sensitivity']:.4f}"
        )

        print(
            f"Specificity  : "
            f"{metrics['specificity']:.4f}"
        )

        print(
            f"Precision    : "
            f"{metrics['precision']:.4f}"
        )

        print(
            f"F1           : "
            f"{metrics['f1']:.4f}"
        )

        if (
            metrics.get(
                "roc_auc"
            )
            is not None
        ):

            print(
                f"ROC-AUC      : "
                f"{metrics['roc_auc']:.4f}"
            )

        print()
        print(
            "Model saved successfully."
        )

        print(
            "=" * 70
        )

    except Exception as exc:

        print()
        print(
            "=" * 70
        )
        print(
            "TRAINING FAILED"
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
