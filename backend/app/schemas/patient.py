"""
Patient Schemas
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# ==========================================================
# Base Patient Schema
# ==========================================================

class PatientBase(BaseModel):
    """
    Common patient fields.
    """

    first_name: str = Field(
        ...,
        min_length=2,
        max_length=50
    )

    last_name: str = Field(
        ...,
        min_length=2,
        max_length=50
    )

    age: int = Field(
        ...,
        ge=1,
        le=120
    )

    gender: str

    phone: Optional[str] = None

    email: Optional[EmailStr] = None

    address: Optional[str] = None

    emergency_contact: Optional[str] = None

    medical_history: Optional[str] = None

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, value):

        allowed = {"Male", "Female", "Other"}

        if value not in allowed:
            raise ValueError(
                f"Gender must be one of {allowed}"
            )

        return value


# ==========================================================
# Create Patient
# ==========================================================

class PatientCreate(PatientBase):
    """
    Create patient request.
    """

    pass


# ==========================================================
# Update Patient
# ==========================================================

class PatientUpdate(BaseModel):
    """
    Update patient request.
    """

    first_name: Optional[str] = None

    last_name: Optional[str] = None

    age: Optional[int] = Field(
        default=None,
        ge=1,
        le=120
    )

    gender: Optional[str] = None

    phone: Optional[str] = None

    email: Optional[EmailStr] = None

    address: Optional[str] = None

    emergency_contact: Optional[str] = None

    medical_history: Optional[str] = None

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, value):

        if value is None:
            return value

        allowed = {"Male", "Female", "Other"}

        if value not in allowed:
            raise ValueError(
                f"Gender must be one of {allowed}"
            )

        return value


# ==========================================================
# Patient Response
# ==========================================================

class PatientResponse(PatientBase):
    """
    Patient information returned by API.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    full_name: str

    created_by: int

    created_at: datetime

    updated_at: Optional[datetime] = None


# ==========================================================
# Patient Summary
# ==========================================================

class PatientSummary(BaseModel):
    """
    Lightweight patient information.
    """

    id: int

    full_name: str

    age: int

    gender: str


# ==========================================================
# Patient Search
# ==========================================================

class PatientSearch(BaseModel):
    """
    Search parameters.
    """

    keyword: Optional[str] = None

    gender: Optional[str] = None

    min_age: Optional[int] = None

    max_age: Optional[int] = None


# ==========================================================
# Patient Statistics
# ==========================================================

class PatientStatistics(BaseModel):
    """
    Patient statistics.
    """

    total_patients: int

    male_patients: int

    female_patients: int

    other_patients: int

    average_age: float


# ==========================================================
# Patient History
# ==========================================================

class PatientHistory(BaseModel):
    """
    Patient prediction history.
    """

    patient_id: int

    prediction_id: int

    prediction: str

    confidence: float

    risk_level: str

    prediction_date: datetime
