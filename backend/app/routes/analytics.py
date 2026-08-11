from fastapi import (
    APIRouter,
    Depends,
    status,
)

from app.dependencies import get_current_user

from app.schemas.analytics import (
    DashboardAnalytics,
    PredictionAnalytics,
    PatientAnalytics,
)

from app.services.analytics_service import (
    AnalyticsService,
)


router = APIRouter(
    tags=["Analytics"],
)


analytics_service = AnalyticsService()


# ==========================================================
# Dashboard
# ==========================================================

@router.get(
    "/dashboard",
    response_model=DashboardAnalytics,
    status_code=status.HTTP_200_OK,
)
def dashboard_analytics(
    current_user=Depends(
        get_current_user
    ),
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
    status_code=status.HTTP_200_OK,
)
def prediction_analytics(
    current_user=Depends(
        get_current_user
    ),
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
    status_code=status.HTTP_200_OK,
)
def patient_analytics(
    current_user=Depends(
        get_current_user
    ),
):
    """
    Return patient statistics.
    """

    return analytics_service.patient_statistics()


# ==========================================================
# Monthly Trend
# ==========================================================

@router.get(
    "/monthly-trend",
)
def monthly_trend(
    current_user=Depends(
        get_current_user
    ),
):
    """
    Return monthly prediction trend.
    """

    return analytics_service.monthly_trend()


# ==========================================================
# Age Distribution
# ==========================================================

@router.get(
    "/age-distribution",
)
def age_distribution(
    current_user=Depends(
        get_current_user
    ),
):
    """
    Return patient age distribution.
    """

    return analytics_service.age_distribution()


# ==========================================================
# Gender Distribution
# ==========================================================

@router.get(
    "/gender-distribution",
)
def gender_distribution(
    current_user=Depends(
        get_current_user
    ),
):
    """
    Return gender distribution.
    """

    return analytics_service.gender_distribution()


# ==========================================================
# Risk Distribution
# ==========================================================

@router.get(
    "/risk-distribution",
)
def risk_distribution(
    current_user=Depends(
        get_current_user
    ),
):
    """
    Return risk distribution.
    """

    return analytics_service.risk_distribution()


# ==========================================================
# Disease Distribution
# ==========================================================

@router.get(
    "/disease-distribution",
)
def disease_distribution(
    current_user=Depends(
        get_current_user
    ),
):
    """
    Return disease distribution.
    """

    return analytics_service.disease_distribution()


# ==========================================================
# Complete Summary
# ==========================================================

@router.get(
    "/summary",
)
def summary(
    current_user=Depends(
        get_current_user
    ),
):
    """
    Return complete analytics summary.
    """

    return analytics_service.analytics_summary()


# ==========================================================
# Frontend Convenience Endpoint
# ==========================================================

@router.get(
    "",
)
def analytics_root(
    current_user=Depends(
        get_current_user
    ),
):
    """
    Return complete analytics summary.

    This allows the frontend to call:

        GET /analytics

    instead of requiring multiple API requests.
    """

    return analytics_service.analytics_summary()
