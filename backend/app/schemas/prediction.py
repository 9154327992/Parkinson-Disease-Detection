from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ==========================================================
# Constants
# ==========================================================

TOTAL_FEATURES = 22


# ==========================================================
# Patient Information
# ==========================================================

class PatientInfo(BaseModel):
    """
    Basic patient information.
    """

    patient_name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Patient full name"
    )

    age: int = Field(
        ...,
        ge=1,
        le=120,
        description="Patient age"
    )

    gender: str = Field(
        ...,
        description="Patient gender"
    )

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, value: str):
        allowed = {"Male", "Female", "Other"}

        if value not in allowed:
            raise ValueError(
                f"Gender must be one of {allowed}"
            )

        return value


# ==========================================================
# Prediction Request
# ==========================================================

class PredictionRequest(PatientInfo):
    """
    Request model for Parkinson prediction.
    """

    features: List[float] = Field(
        ...,
        description="22 Parkinson voice features"
    )

    @field_validator("features")
    @classmethod
    def validate_features(cls, value):

        if len(value) != TOTAL_FEATURES:

            raise ValueError(
                f"Exactly {TOTAL_FEATURES} voice features are required."
            )

        return value


# ==========================================================
# Prediction Result
# ==========================================================

class PredictionResult(BaseModel):
    """
    Prediction output.
    """

    prediction: str

    prediction_value: int

    confidence: float = Field(
        ...,
        ge=0,
        le=100
    )

    risk_score: float = Field(
        ...,
        ge=0,
        le=100
    )

    risk_level: str

    recommendation: str


# ==========================================================
# Prediction Response
# ==========================================================

class PredictionResponse(PredictionResult):
    """
    Complete API response.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    prediction_id: Optional[int] = None

    patient_id: Optional[int] = None

    model_name: str

    model_version: str

    created_at: datetime


# ==========================================================
# Prediction History
# ==========================================================

class PredictionHistory(BaseModel):

    prediction_id: int

    patient_id: int

    patient_name: str

    age: int

    gender: str

    prediction: str

    confidence: float

    risk_score: float

    risk_level: str

    created_at: datetime

# ==========================================================
# Prediction Statistics
# ==========================================================

class PredictionStatistics(BaseModel):
    """
    Prediction statistics.
    """

    total_predictions: int

    healthy_cases: int

    parkinson_cases: int

    average_confidence: float

    high_risk_cases: int

    medium_risk_cases: int

    low_risk_cases: int


# ==========================================================
# Model Information
# ==========================================================

class ModelInformation(BaseModel):
    """
    Machine learning model information.
    """

    model_name: str

    model_version: str

    algorithm: str

    total_features: int

    accuracy: float

    precision: float

    recall: float

    f1_score: float

    status: str
