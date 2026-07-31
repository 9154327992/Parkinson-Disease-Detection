"""
API Routes Package

This package contains all FastAPI route modules for the
Parkinson Disease Detection Agent.
"""

from .auth import router as auth_router
from .prediction import router as prediction_router
from .patient import router as patient_router
from .analytics import router as analytics_router
from .recommendation import router as recommendation_router
from .exercise import router as exercise_router
from .medication import router as medication_router
from .reports import router as reports_router
from .chatbot import router as chatbot_router

__all__ = [
    "auth_router",
    "prediction_router",
    "patient_router",
    "analytics_router",
    "recommendation_router",
    "exercise_router",
    "medication_router",
    "reports_router",
    "chatbot_router",
]
