"""
Pydantic Schemas Package

This package contains all request and response models
used throughout the Parkinson Disease Detection API.
"""

# ==========================================================
# Authentication
# ==========================================================

from .auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    UserResponse,
)

# ==========================================================
# Prediction
# ==========================================================

from .prediction import (
    PredictionRequest,
    PredictionResponse,
)

# ==========================================================
# Patient
# ==========================================================

from .patient import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
)

# ==========================================================
# Analytics
# ==========================================================

from .analytics import (
    DashboardAnalytics,
    PredictionAnalytics,
    PatientAnalytics,
)

# ==========================================================
# Recommendation
# ==========================================================

from .recommendation import (
    RecommendationRequest,
    RecommendationResponse,
)

# ==========================================================
# Report
# ==========================================================

from .report import (
    ReportRequest,
    ReportResponse,
)

# ==========================================================
# Chatbot
# ==========================================================

from .chatbot import (
    ChatRequest,
    ChatResponse,
)

# ==========================================================
# Exported Schemas
# ==========================================================

__all__ = [

    # Authentication
    "LoginRequest",
    "LoginResponse",
    "RegisterRequest",
    "UserResponse",

    # Prediction
    "PredictionRequest",
    "PredictionResponse",

    # Patient
    "PatientCreate",
    "PatientUpdate",
    "PatientResponse",

    # Analytics
    "DashboardAnalytics",
    "PredictionAnalytics",
    "PatientAnalytics",

    # Recommendation
    "RecommendationRequest",
    "RecommendationResponse",

    # Report
    "ReportRequest",
    "ReportResponse",

    # Chatbot
    "ChatRequest",
    "ChatResponse",
]
