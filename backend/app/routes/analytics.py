"""
Analytics API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_current_user

from app.schemas.analytics import (
    DashboardAnalytics,
    PredictionAnalytics,
    PatientAnalytics,
)

from app.services.analytics_service import AnalyticsService


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)

analytics_service = AnalyticsService()


# ==========================================================
# Dashboard Analytics
# ==========================================================

@router.get(
    "/dashboard",
    response_model=DashboardAnalytics,
    status_code=status.HTTP_200_OK
)
def dashboard_analytics(
    current_user=Depends(get_current_user)
):
    """
    Return dashboard statistics.
    """

    return analytics_service.dashboard()


# ==========================================================
# Prediction Analytics
# ==========================================================

@router.get(
    "/predictions",
    response_model=PredictionAnalytics,
    status_code=status.HTTP_200_OK
)
def prediction_analytics(
    current_user=Depends(get_current_user)
):
    """
    Return prediction statistics.
    """

    return analytics_service.prediction_statistics()


# ==========================================================
# Patient Analytics
# ==========================================================

@router.get(
    "/patients",
    response_model=PatientAnalytics,
    status_code=status.HTTP_200_OK
)
def patient_analytics(
    current_user=Depends(get_current_user)
):
    """
    Return patient statistics.
    """

    return analytics_service.patient_statistics()


# ==========================================================
# Monthly Trend
# ==========================================================

@router.get("/monthly-trend")
def monthly_trend(
    current_user=Depends(get_current_user)
):
    """
    Monthly prediction trend.
    """

    return analytics_service.monthly_trend()


# ==========================================================
# Age Distribution
# ==========================================================

@router.get("/age-distribution")
def age_distribution(
    current_user=Depends(get_current_user)
):
    """
    Patient age distribution.
    """

    return analytics_service.age_distribution()


# ==========================================================
# Gender Distribution
# ==========================================================

@router.get("/gender-distribution")
def gender_distribution(
    current_user=Depends(get_current_user)
):
    """
    Gender distribution.
    """

    return analytics_service.gender_distribution()


# ==========================================================
# Risk Distribution
# ==========================================================

@router.get("/risk-distribution")
def risk_distribution(
    current_user=Depends(get_current_user)
):
    """
    Low, Medium and High risk distribution.
    """

    return analytics_service.risk_distribution()


# ==========================================================
# System Summary
# ==========================================================

@router.get("/summary")
def summary(
    current_user=Depends(get_current_user)
):
    """
    Overall analytics summary.
    """

    return analytics_service.summary()
