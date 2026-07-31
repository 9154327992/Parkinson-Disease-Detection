"""
Report Schemas
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ==========================================================
# Report Request
# ==========================================================

class ReportRequest(BaseModel):
    """
    Request for generating a patient report.
    """

    patient_id: int = Field(..., gt=0)

    prediction_id: int = Field(..., gt=0)

    include_recommendations: bool = True

    include_exercises: bool = True

    include_medication: bool = True

    include_follow_up: bool = True

    doctor_notes: Optional[str] = None


# ==========================================================
# Report Metadata
# ==========================================================

class ReportMetadata(BaseModel):
    """
    Report metadata.
    """

    report_id: int

    report_name: str

    report_type: str

    generated_by: str

    generated_at: datetime

    version: str


# ==========================================================
# Patient Information
# ==========================================================

class ReportPatient(BaseModel):
    """
    Patient information included in report.
    """

    patient_id: int

    full_name: str

    age: int

    gender: str

    medical_history: Optional[str] = None


# ==========================================================
# Prediction Summary
# ==========================================================

class PredictionSummary(BaseModel):
    """
    Prediction summary.
    """

    prediction: str

    confidence: float

    risk_score: float

    risk_level: str

    recommendation: str


# ==========================================================
# Recommendation Item
# ==========================================================

class RecommendationItem(BaseModel):
    """
    Recommendation section.
    """

    title: str

    description: str


# ==========================================================
# Exercise Item
# ==========================================================

class ExerciseItem(BaseModel):
    """
    Exercise recommendation.
    """

    name: str

    duration: str

    frequency: str

    description: str


# ==========================================================
# Medication Item
# ==========================================================

class MedicationItem(BaseModel):
    """
    Medication guidance.
    """

    title: str

    description: str


# ==========================================================
# Follow-up Plan
# ==========================================================

class FollowUpPlan(BaseModel):
    """
    Follow-up recommendation.
    """

    next_visit: str

    specialist: str

    notes: str


# ==========================================================
# Report Response
# ==========================================================

class ReportResponse(BaseModel):
    """
    Complete patient report.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    metadata: ReportMetadata

    patient: ReportPatient

    prediction: PredictionSummary

    recommendations: List[RecommendationItem]

    exercises: List[ExerciseItem]

    medication: List[MedicationItem]

    follow_up: FollowUpPlan

    doctor_notes: Optional[str] = None


# ==========================================================
# Report Summary
# ==========================================================

class ReportSummary(BaseModel):
    """
    Lightweight report information.
    """

    report_id: int

    patient_id: int

    patient_name: str

    report_name: str

    generated_at: datetime


# ==========================================================
# Report Download
# ==========================================================

class ReportDownload(BaseModel):
    """
    Downloadable report information.
    """

    report_id: int

    filename: str

    download_url: str

    file_type: str = "pdf"

    file_size: Optional[str] = None


# ==========================================================
# Report List
# ==========================================================

class ReportList(BaseModel):
    """
    Collection of reports.
    """

    total_reports: int

    reports: List[ReportSummary]


# ==========================================================
# Delete Report Response
# ==========================================================

class DeleteReportResponse(BaseModel):
    """
    Response after deleting a report.
    """

    message: str
