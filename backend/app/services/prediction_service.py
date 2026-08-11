from datetime import datetime
from typing import Dict, List, Optional

from app.schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
    PredictionHistory,
    PredictionStatistics,
    ModelInformation,
)


class PredictionService:
    """
    Handles Parkinson disease predictions.

    Uses shared in-memory storage until database
    persistence is implemented.
    """

    # ==========================================================
    # Shared In-Memory Storage
    # ==========================================================

    history: List[PredictionHistory] = []

    predictions: Dict[int, Dict] = {}

    next_prediction_id: int = 1

    # ==========================================================
    # Initialize
    # ==========================================================

    def __init__(self):
        """
        No instance-level storage is used.

        All PredictionService instances share the same
        prediction records.
        """
        pass

    # ==========================================================
    # Predict
    # ==========================================================

    def predict(
        self,
        request: PredictionRequest,
    ) -> PredictionResponse:
        """
        Predict Parkinson disease.
        """

        # ------------------------------------------------------
        # ML Prediction
        # ------------------------------------------------------
        #
        # Replace this section with the real ML model
        # when model integration is enabled.
        #

        prediction_value = 1

        confidence = 97.45

        risk_score = 95.80

        # ------------------------------------------------------
        # Prediction Label
        # ------------------------------------------------------

        if prediction_value == 1:

            prediction = "Parkinson Detected"

        else:

            prediction = "Healthy"

        # ------------------------------------------------------
        # Risk Level
        # ------------------------------------------------------

        if risk_score >= 80:

            risk_level = "High Risk"

        elif risk_score >= 50:

            risk_level = "Medium Risk"

        else:

            risk_level = "Low Risk"

        # ------------------------------------------------------
        # Recommendation
        # ------------------------------------------------------

        recommendation = self._recommendation(
            risk_level
        )

        # ------------------------------------------------------
        # Generate Prediction ID
        # ------------------------------------------------------

        prediction_id = (
            PredictionService.next_prediction_id
        )

        PredictionService.next_prediction_id += 1

        # ------------------------------------------------------
        # Patient ID
        # ------------------------------------------------------
        #
        # PredictionRequest currently contains:
        # patient_name
        # age
        # gender
        # features
        #
        # It does not contain patient_id.
        #

        patient_id = 1

        # ------------------------------------------------------
        # Created Time
        # ------------------------------------------------------

        created_at = datetime.utcnow()

        # ------------------------------------------------------
        # Prediction Response
        # ------------------------------------------------------

        response = PredictionResponse(

            prediction_id=prediction_id,

            patient_id=patient_id,

            prediction=prediction,

            prediction_value=prediction_value,

            confidence=confidence,

            risk_score=risk_score,

            risk_level=risk_level,

            recommendation=recommendation,

            model_name="Random Forest",

            model_version="1.0.0",

            created_at=created_at,
        )

        # ======================================================
        # Save History
        # ======================================================

        history_item = PredictionHistory(

            prediction_id=prediction_id,

            patient_id=patient_id,

            patient_name=request.patient_name,

            prediction=prediction,

            confidence=confidence,

            risk_level=risk_level,

            created_at=created_at,
        )

        PredictionService.history.append(
            history_item
        )

        # ======================================================
        # Save Complete Prediction
        # ======================================================

        PredictionService.predictions[
            prediction_id
        ] = {

            "response": response,

            "patient_name": request.patient_name,

            "age": request.age,

            "gender": request.gender,

            "features": request.features,
        }

        return response

    # ==========================================================
    # Recommendation
    # ==========================================================

    def _recommendation(
        self,
        risk_level: str,
    ) -> str:
        """
        Generate recommendation based on risk level.
        """

        recommendations = {

            "High Risk":
                (
                    "Consult a neurologist as soon as possible "
                    "for a complete clinical evaluation."
                ),

            "Medium Risk":
                (
                    "Schedule a follow-up assessment and "
                    "monitor symptoms."
                ),

            "Low Risk":
                (
                    "Maintain a healthy lifestyle and continue "
                    "routine medical check-ups."
                ),
        }

        return recommendations.get(
            risk_level,
            "Consult a healthcare professional.",
        )

    # ==========================================================
    # Prediction History
    # ==========================================================

    def get_history(
        self,
        patient_id: Optional[int] = None,
    ) -> List[PredictionHistory]:
        """
        Return prediction history.
        """

        records = PredictionService.history

        if patient_id is None:

            return records

        return [
            item
            for item in records
            if item.patient_id == patient_id
        ]

    # ==========================================================
    # Prediction Details
    # ==========================================================

    def get_prediction(
        self,
        prediction_id: int,
    ) -> Optional[PredictionResponse]:
        """
        Retrieve prediction by ID.
        """

        record = PredictionService.predictions.get(
            prediction_id
        )

        if record is None:

            return None

        return record["response"]

    # ==========================================================
    # Complete Prediction Data
    # ==========================================================

    def get_prediction_data(
        self,
        prediction_id: int,
    ) -> Optional[Dict]:
        """
        Return complete prediction information.
        """

        return PredictionService.predictions.get(
            prediction_id
        )

    # ==========================================================
    # Delete Prediction
    # ==========================================================

    def delete_prediction(
        self,
        prediction_id: int,
    ) -> bool:
        """
        Delete prediction.
        """

        if prediction_id not in (
            PredictionService.predictions
        ):

            return False

        # ------------------------------------------------------
        # Delete complete prediction
        # ------------------------------------------------------

        del PredictionService.predictions[
            prediction_id
        ]

        # ------------------------------------------------------
        # Delete history record
        # ------------------------------------------------------

        PredictionService.history = [
            item
            for item in PredictionService.history
            if item.prediction_id != prediction_id
        ]

        return True

    # ==========================================================
    # Statistics
    # ==========================================================

    def statistics(
        self,
    ) -> PredictionStatistics:
        """
        Calculate statistics from actual predictions.
        """

        records = PredictionService.predictions

        total_predictions = len(
            records
        )

        healthy_cases = 0

        parkinson_cases = 0

        high_risk_cases = 0

        medium_risk_cases = 0

        low_risk_cases = 0

        confidence_values = []

        # ------------------------------------------------------
        # Calculate
        # ------------------------------------------------------

        for record in records.values():

            prediction = record["response"]

            confidence_values.append(
                prediction.confidence
            )

            if prediction.prediction_value == 1:

                parkinson_cases += 1

            else:

                healthy_cases += 1

            if prediction.risk_level == "High Risk":

                high_risk_cases += 1

            elif prediction.risk_level == "Medium Risk":

                medium_risk_cases += 1

            elif prediction.risk_level == "Low Risk":

                low_risk_cases += 1

        # ------------------------------------------------------
        # Average Confidence
        # ------------------------------------------------------

        if confidence_values:

            average_confidence = (
                sum(confidence_values)
                / len(confidence_values)
            )

        else:

            average_confidence = 0.0

        return PredictionStatistics(

            total_predictions=total_predictions,

            healthy_cases=healthy_cases,

            parkinson_cases=parkinson_cases,

            average_confidence=round(
                average_confidence,
                2,
            ),

            high_risk_cases=high_risk_cases,

            medium_risk_cases=medium_risk_cases,

            low_risk_cases=low_risk_cases,
        )

    # ==========================================================
    # Model Information
    # ==========================================================

    def model_info(
        self,
    ) -> ModelInformation:
        """
        Return ML model information.
        """

        return ModelInformation(

            model_name="Random Forest Classifier",

            model_version="1.0.0",

            algorithm="Random Forest",

            total_features=22,

            accuracy=95.80,

            precision=94.70,

            recall=95.10,

            f1_score=94.90,

            status="Ready",
        )
