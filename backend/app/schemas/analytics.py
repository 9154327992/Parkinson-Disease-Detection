"""
Analytics Schemas
"""

from typing import List

from pydantic import BaseModel, Field


# ==========================================================
# Dashboard Metrics
# ==========================================================

class DashboardAnalytics(BaseModel):
    """
    Dashboard summary statistics.
    """

    total_patients: int = Field(
        ...,
        ge=0,
    )

    total_predictions: int = Field(
        ...,
        ge=0,
    )

    total_reports: int = Field(
        ...,
        ge=0,
    )

    healthy_cases: int = Field(
        ...,
        ge=0,
    )

    parkinson_cases: int = Field(
        ...,
        ge=0,
    )

    high_risk_cases: int = Field(
        ...,
        ge=0,
    )

    medium_risk_cases: int = Field(
        ...,
        ge=0,
    )

    low_risk_cases: int = Field(
        ...,
        ge=0,
    )


# ==========================================================
# Prediction Statistics
# ==========================================================

class PredictionAnalytics(BaseModel):
    """
    Prediction analytics.
    """

    total_predictions: int

    healthy_predictions: int

    parkinson_predictions: int

    average_confidence: float

    average_risk_score: float


# ==========================================================
# Patient Statistics
# ==========================================================

class PatientAnalytics(BaseModel):
    """
    Patient analytics.
    """

    total_patients: int

    male_patients: int

    female_patients: int

    other_patients: int

    average_age: float


# ==========================================================
# Monthly Trend
# ==========================================================

class MonthlyTrend(BaseModel):
    """
    Monthly prediction trend.
    """

    month: str

    predictions: int


# ==========================================================
# Age Distribution
# ==========================================================

class AgeDistribution(BaseModel):
    """
    Age group distribution.
    """

    age_group: str

    count: int


# ==========================================================
# Gender Distribution
# ==========================================================

class GenderDistribution(BaseModel):
    """
    Gender distribution.
    """

    gender: str

    count: int


# ==========================================================
# Risk Distribution
# ==========================================================

class RiskDistribution(BaseModel):
    """
    Risk level distribution.
    """

    risk_level: str

    count: int


# ==========================================================
# Disease Distribution
# ==========================================================

class DiseaseDistribution(BaseModel):
    """
    Healthy vs Parkinson distribution.
    """

    label: str

    count: int


# ==========================================================
# Recent Prediction
# ==========================================================

class RecentPrediction(BaseModel):
    """
    Recent prediction record.
    """

    prediction_id: int

    patient_name: str

    prediction: str

    confidence: float

    risk_level: str

    created_at: str


# ==========================================================
# Analytics Summary
# ==========================================================

class AnalyticsSummary(BaseModel):
    """
    Complete analytics response.
    """

    dashboard: DashboardAnalytics

    prediction: PredictionAnalytics

    patient: PatientAnalytics

    monthly_trend: List[MonthlyTrend]

    age_distribution: List[AgeDistribution]

    gender_distribution: List[GenderDistribution]

    risk_distribution: List[RiskDistribution]

    disease_distribution: List[DiseaseDistribution]

    recent_predictions: List[RecentPrediction]
