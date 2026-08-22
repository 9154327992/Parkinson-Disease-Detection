from pathlib import Path
from typing import Dict, List, Tuple

import json
import warnings

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import (
    RandomForestClassifier,
    ExtraTreesClassifier,
    VotingClassifier,
)
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)
from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    cross_val_score,
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
# Labels
# ==========================================================

LABEL_PD = 1
LABEL_HC = 0


# ==========================================================
# Model Trainer
# ==========================================================

class ModelTrainer:
    """
    Train the Parkinson voice model directly from WAV files.

    PD = 1
    HC = 0

    The audio feature extractor used here must be the same
    extractor used by the prediction service.
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
        # Feature extraction
        # --------------------------------------------------

        self.audio_feature_service = (
            AudioFeatureService()
        )

        # --------------------------------------------------
        # Shared feature schema
        # --------------------------------------------------

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

        self.model = self._create_model()

        # --------------------------------------------------
        # Pipeline
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
                    self.model,
                ),
            ]
        )

        # --------------------------------------------------
        # Training information
        # --------------------------------------------------

        self.training_dataframe = None

        self.training_files = []

        self.failed_files = []

        self.metrics = {}

    # ======================================================
    # Feature Contract
    # ======================================================

    def _validate_feature_contract(
        self,
    ) -> None:

        audio_names = (
            self.audio_feature_service
            .get_feature_names()
        )

        engineering_names = (
            self.feature_engineering
            .get_feature_names()
        )

        if audio_names != FEATURE_NAMES:

            raise RuntimeError(
                "AudioFeatureService feature order "
                "does not match the training feature order."
            )

        if engineering_names != FEATURE_NAMES:

            raise RuntimeError(
                "FeatureEngineering feature order "
                "does not match the training feature order."
            )

        if len(audio_names) != TOTAL_FEATURES:

            raise RuntimeError(
                "Audio feature count must be exactly 22."
            )

    # ======================================================
    # Create Model
    # ======================================================

    def _create_model(self):

        random_forest = (
            RandomForestClassifier(
                n_estimators=500,
                max_depth=None,
                min_samples_split=2,
                min_samples_leaf=1,
                max_features="sqrt",
                class_weight="balanced",
                random_state=42,
                n_jobs=-1,
            )
        )

        extra_trees = (
            ExtraTreesClassifier(
                n_estimators=500,
                max_depth=None,
                min_samples_split=2,
                min_samples_leaf=1,
                max_features="sqrt",
                class_weight="balanced",
                random_state=42,
                n_jobs=-1,
            )
        )

        model = VotingClassifier(
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

        return model

    # ======================================================
    # Find WAV Files
    # ======================================================

    def find_audio_files(
        self,
    ) -> List[Tuple[Path, int, str]]:

        if not self.dataset_path.exists():

            raise FileNotFoundError(
                "Audio dataset directory not found: "
                f"{self.dataset_path}"
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
                "PD directory not found: "
                f"{pd_directory}"
            )

        if not hc_directory.exists():

            raise FileNotFoundError(
                "HC directory not found: "
                f"{hc_directory}"
            )

        files = []

        # --------------------------------------------------
        # Parkinson
        # --------------------------------------------------

        for path in sorted(
            pd_directory.rglob("*.wav")
        ):

            if path.is_file():

                files.append(
                    (
                        path,
                        LABEL_PD,
                        "PD",
                    )
                )

        # --------------------------------------------------
        # Healthy
        # --------------------------------------------------

        for path in sorted(
            hc_directory.rglob("*.wav")
        ):

            if path.is_file():

                files.append(
                    (
                        path,
                        LABEL_HC,
                        "HC",
                    )
                )

        # --------------------------------------------------
        # Case-insensitive extensions
        # --------------------------------------------------

        for directory, label, name in [
            (
                pd_directory,
                LABEL_PD,
                "PD",
            ),
            (
                hc_directory,
                LABEL_HC,
                "HC",
            ),
        ]:

            for path in sorted(
                directory.rglob("*")
            ):

                if (
                    path.is_file()
                    and path.suffix.lower()
                    == ".wav"
                ):

                    entry = (
                        path,
                        label,
                        name,
                    )

                    if entry not in files:

                        files.append(
                            entry
                        )

        # --------------------------------------------------
        # Remove duplicate paths
        # --------------------------------------------------

        unique = {}

        for path, label, name in files:

            unique[
                str(path.resolve())
            ] = (
                path,
                label,
                name,
            )

        files = list(
            unique.values()
        )

        files.sort(
            key=lambda item: str(
                item[0]
            )
        )

        if not files:

            raise RuntimeError(
                "No WAV recordings were found."
            )

        return files

    # ======================================================
    # Dataset Summary
    # ======================================================

    def dataset_summary(
        self,
        files: List[
            Tuple[Path, int, str]
        ],
    ) -> Dict:

        pd_count = sum(
            1
            for _, label, _
            in files
            if label == LABEL_PD
        )

        hc_count = sum(
            1
            for _, label, _
            in files
            if label == LABEL_HC
        )

        return {
            "total": len(files),
            "pd": pd_count,
            "hc": hc_count,
        }

    # ======================================================
    # Extract One Recording
    # ======================================================

    def extract_one(
        self,
        path: Path,
        label: int,
        class_name: str,
    ) -> Dict:

        features = (
            self.audio_feature_service
            .extract_features_from_file(
                str(path)
            )
        )

        # --------------------------------------------------
        # Validate exact feature set
        # --------------------------------------------------

        self.audio_feature_service.validate_feature_dictionary(
            features
        )

        # --------------------------------------------------
        # Convert to ordered vector
        # --------------------------------------------------

        vector = (
            self.audio_feature_service
            .to_feature_vector(
                features
            )
        )

        if len(vector) != TOTAL_FEATURES:

            raise ValueError(
                "Audio feature vector must contain "
                f"{TOTAL_FEATURES} values."
            )

        # --------------------------------------------------
        # Build row
        # --------------------------------------------------

        row = {}

        for name, value in zip(
            FEATURE_NAMES,
            vector,
        ):

            row[name] = float(
                value
            )

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

        files = (
            self.find_audio_files()
        )

        summary = (
            self.dataset_summary(
                files
            )
        )

        print(
            "\n========================================"
        )

        print(
            "Audio Dataset"
        )

        print(
            "========================================"
        )

        print(
            f"Total recordings : "
            f"{summary['total']}"
        )

        print(
            f"Parkinson (PD)   : "
            f"{summary['pd']}"
        )

        print(
            f"Healthy (HC)     : "
            f"{summary['hc']}"
        )

        print(
            "========================================\n"
        )

        if summary["pd"] < 2:

            raise RuntimeError(
                "At least 2 PD recordings are required."
            )

        if summary["hc"] < 2:

            raise RuntimeError(
                "At least 2 HC recordings are required."
            )

        rows = []

        self.training_files = []

        self.failed_files = []

        for index, (
            path,
            label,
            class_name,
        ) in enumerate(
            files,
            start=1,
        ):

            print(
                f"[{index}/{len(files)}] "
                f"{class_name}: "
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

                self.training_files.append(
                    str(path)
                )

                print(
                    "    ✓ features extracted"
                )

            except Exception as exc:

                error = {
                    "file":
                        str(path),

                    "class":
                        class_name,

                    "error":
                        str(exc),
                }

                self.failed_files.append(
                    error
                )

                print(
                    "    ✗ failed: "
                    f"{exc}"
                )

        if not rows:

            raise RuntimeError(
                "No recordings could be processed."
            )

        dataframe = pd.DataFrame(
            rows
        )

        # --------------------------------------------------
        # Verify feature columns
        # --------------------------------------------------

        missing = [
            name
            for name in FEATURE_NAMES
            if name not in dataframe.columns
        ]

        if missing:

            raise RuntimeError(
                "Missing extracted features: "
                f"{missing}"
            )

        # --------------------------------------------------
        # Numeric conversion
        # --------------------------------------------------

        for name in FEATURE_NAMES:

            dataframe[name] = pd.to_numeric(
                dataframe[name],
                errors="coerce",
            )

        # --------------------------------------------------
        # Remove invalid feature rows
        # --------------------------------------------------

        invalid_mask = (
            ~np.isfinite(
                dataframe[
                    FEATURE_NAMES
                ].to_numpy(
                    dtype=np.float64
                )
            ).all(
                axis=1
            )
        )

        invalid_rows = (
            dataframe[
                invalid_mask
            ]
        )

        if len(invalid_rows) > 0:

            for _, row in invalid_rows.iterrows():

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
                            "Non-finite feature value.",
                    }
                )

            dataframe = dataframe[
                ~invalid_mask
            ].copy()

        # --------------------------------------------------
        # Require both classes
        # --------------------------------------------------

        if (
            dataframe["status"]
            .nunique()
            < 2
        ):

            raise RuntimeError(
                "After feature extraction, "
                "only one class remains."
            )

        # --------------------------------------------------
        # Save extracted dataset
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

        print(
            "\n========================================"
        )

        print(
            "Feature extraction complete"
        )

        print(
            f"Successful recordings : "
            f"{len(dataframe)}"
        )

        print(
            f"Failed recordings     : "
            f"{len(self.failed_files)}"
        )

        print(
            f"Feature CSV           : "
            f"{self.feature_csv_path}"
        )

        print(
            "========================================\n"
        )

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

        if len(dataframe) < 10:

            raise ValueError(
                "Not enough recordings for training."
            )

        # --------------------------------------------------
        # Use existing FeatureEngineering
        # --------------------------------------------------

        X, y = (
            self.feature_engineering
            .prepare_training_data(
                dataframe,
                target_column="status",
            )
        )

        X = X.copy()

        y = y.copy()

        # --------------------------------------------------
        # Force numeric
        # --------------------------------------------------

        for name in FEATURE_NAMES:

            X[name] = pd.to_numeric(
                X[name],
                errors="coerce",
            )

        # --------------------------------------------------
        # Validate labels
        # --------------------------------------------------

        if y.isnull().any():

            raise ValueError(
                "Training labels contain missing values."
            )

        y = y.astype(
            int
        )

        unique_labels = sorted(
            y.unique().tolist()
        )

        if unique_labels != [
            LABEL_HC,
            LABEL_PD,
        ]:

            raise ValueError(
                "Training labels must contain "
                "both 0 (HC) and 1 (PD). "
                f"Found: {unique_labels}"
            )

        return (
            X,
            y,
        )

    # ======================================================
    # Train/Test Split
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
    # Calculate Metrics
    # ======================================================

    def calculate_metrics(
        self,
        y_true,
        predictions,
        probabilities=None,
    ) -> Dict:

        matrix = confusion_matrix(
            y_true,
            predictions,
            labels=[
                LABEL_HC,
                LABEL_PD,
            ],
        )

        tn, fp, fn, tp = (
            matrix.ravel()
        )

        accuracy = accuracy_score(
            y_true,
            predictions,
        )

        precision = precision_score(
            y_true,
            predictions,
            pos_label=LABEL_PD,
            zero_division=0,
        )

        recall = recall_score(
            y_true,
            predictions,
            pos_label=LABEL_PD,
            zero_division=0,
        )

        f1 = f1_score(
            y_true,
            predictions,
            pos_label=LABEL_PD,
            zero_division=0,
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

        balanced_accuracy = (
            recall
            + specificity
        ) / 2.0

        metrics = {

            "accuracy":
                float(accuracy),

            "precision":
                float(precision),

            "sensitivity":
                float(recall),

            "recall":
                float(recall),

            "specificity":
                float(specificity),

            "f1":
                float(f1),

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

                metrics["roc_auc"] = float(
                    roc_auc_score(
                        y_true,
                        probabilities,
                    )
                )

            except Exception:

                metrics["roc_auc"] = None

        else:

            metrics["roc_auc"] = None

        return metrics

    # ======================================================
    # Cross Validation
    # ======================================================

    def cross_validate(
        self,
        X: pd.DataFrame,
        y: pd.Series,
    ) -> Dict:

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
                "cv_folds": 0,
                "accuracy_mean": None,
                "accuracy_std": None,
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

            "cv_folds":
                int(folds),

            "accuracy_mean":
                float(
                    np.mean(scores)
                ),

            "accuracy_std":
                float(
                    np.std(scores)
                ),

            "accuracy_scores":
                [
                    float(x)
                    for x in scores
                ],
        }

    # ======================================================
    # Train
    # ======================================================

    def train(
        self,
        dataframe: pd.DataFrame = None,
    ) -> Dict:

        if dataframe is None:

            if self.training_dataframe is None:

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

        # --------------------------------------------------
        # Print class distribution
        # --------------------------------------------------

        print(
            "\n========================================"
        )

        print(
            "Training Dataset"
        )

        print(
            "========================================"
        )

        print(
            f"Total samples : {len(X)}"
        )

        print(
            f"Healthy       : "
            f"{int((y == LABEL_HC).sum())}"
        )

        print(
            f"Parkinson     : "
            f"{int((y == LABEL_PD).sum())}"
        )

        print(
            "========================================\n"
        )

        # --------------------------------------------------
        # Cross-validation
        # --------------------------------------------------

        print(
            "Running cross-validation..."
        )

        cv_metrics = (
            self.cross_validate(
                X,
                y,
            )
        )

        print(
            "Cross-validation accuracy: "
            f"{cv_metrics['accuracy_mean']}"
        )

        # --------------------------------------------------
        # Hold-out split
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

        print(
            "\nTraining samples: "
            f"{len(X_train)}"
        )

        print(
            "Testing samples: "
            f"{len(X_test)}"
        )

        # --------------------------------------------------
        # Train
        # --------------------------------------------------

        print(
            "\nTraining model..."
        )

        self.pipeline.fit(
            X_train,
            y_train,
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
            "failed_audio_files"
        ] = int(
            len(self.failed_files)
        )

        self.metrics = (
            metrics
        )

        # --------------------------------------------------
        # Print results
        # --------------------------------------------------

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

        print(
            "\n========================================"
        )

        print(
            "MODEL RESULTS"
        )

        print(
            "========================================"
        )

        print(
            f"Accuracy          : "
            f"{metrics['accuracy']:.4f}"
        )

        print(
            f"Sensitivity / Recall: "
            f"{metrics['sensitivity']:.4f}"
        )

        print(
            f"Specificity       : "
            f"{metrics['specificity']:.4f}"
        )

        print(
            f"Precision         : "
            f"{metrics['precision']:.4f}"
        )

        print(
            f"F1 Score          : "
            f"{metrics['f1']:.4f}"
        )

        print(
            f"Balanced Accuracy : "
            f"{metrics['balanced_accuracy']:.4f}"
        )

        if metrics.get(
            "roc_auc"
        ) is not None:

            print(
                f"ROC-AUC           : "
                f"{metrics['roc_auc']:.4f}"
            )

        print(
            "\nConfusion Matrix:"
        )

        print(
            np.asarray(
                metrics[
                    "confusion_matrix"
                ]
            )
        )

        print(
            "\nInterpretation:"
        )

        print(
            "  0 = Healthy Control"
        )

        print(
            "  1 = Parkinson's Disease"
        )

        print(
            "========================================\n"
        )

    # ======================================================
    # Feature Importance
    # ======================================================

    def feature_importance(
        self,
    ) -> pd.DataFrame:

        if self.pipeline is None:

            raise RuntimeError(
                "Model has not been trained."
            )

        model = (
            self.pipeline
            .named_steps
            .get(
                "model"
            )
        )

        if model is None:

            raise RuntimeError(
                "Trained model not found."
            )

        # --------------------------------------------------
        # Voting classifier
        # --------------------------------------------------

        importances = []

        for estimator in (
            model.estimators_
        ):

            if hasattr(
                estimator,
                "feature_importances_",
            ):

                importances.append(
                    estimator.feature_importances_
                )

        if not importances:

            return pd.DataFrame(
                columns=[
                    "Feature",
                    "Importance",
                ]
            )

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
                    FEATURE_NAMES,

                "Importance":
                    mean_importance,
            }
        ).sort_values(
            by="Importance",
            ascending=False,
        ).reset_index(
            drop=True
        )

    # ======================================================
    # Save Artifacts
    # ======================================================

    def save(
        self,
    ) -> None:

        self.model_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.scaler_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.report_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # --------------------------------------------------
        # Save model pipeline
        # --------------------------------------------------

        joblib.dump(
            self.pipeline,
            self.model_path,
        )

        # --------------------------------------------------
        # Save scaler separately
        #
        # Existing prediction code expects scaler.pkl.
        # The scaler is taken from the trained pipeline.
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
                "Scaler was not found in trained pipeline."
            )

        joblib.dump(
            scaler,
            self.scaler_path,
        )

        # --------------------------------------------------
        # Save training report
        # --------------------------------------------------

        report = {
            "dataset_path":
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

            "feature_names":
                FEATURE_NAMES,

            "successful_files":
                len(
                    self.training_files
                ),

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
            )

        print(
            "\nArtifacts saved:"
        )

        print(
            f"Model  : {self.model_path}"
        )

        print(
            f"Scaler : {self.scaler_path}"
        )

        print(
            f"Report : {self.report_path}"
        )

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

            "features":
                TOTAL_FEATURES,

            "feature_names":
                FEATURE_NAMES,

            "successful_files":
                len(
                    self.training_files
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
    )

    metrics = (
        trainer.train_and_save()
    )

    print(
        "\n========================================"
    )

    print(
        "Audio Model Training Complete"
    )

    print(
        "========================================"
    )

    print(
        f"Accuracy: "
        f"{metrics['accuracy']:.4f}"
    )

    print(
        f"Sensitivity: "
        f"{metrics['sensitivity']:.4f}"
    )

    print(
        f"Specificity: "
        f"{metrics['specificity']:.4f}"
    )

    print(
        f"F1: "
        f"{metrics['f1']:.4f}"
    )

    if metrics.get(
        "roc_auc"
    ) is not None:

        print(
            f"ROC-AUC: "
            f"{metrics['roc_auc']:.4f}"
        )

    print(
        "\nModel saved successfully."
    )
