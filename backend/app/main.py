"""
Main entry point for the
Parkinson Disease Detection Agent API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ==========================================================
# Import Routers
# ==========================================================

from app.routes.predict import router as predict_router
from app.routes.patients import router as patient_router
from app.routes.reports import router as report_router
from app.routes.analytics import router as analytics_router
from app.routes.chatbot import router as chatbot_router
from app.routes.admin import router as admin_router
from app.routes.users import router as user_router
from app.routes.settings import router as settings_router

# ==========================================================
# FastAPI App
# ==========================================================

app = FastAPI(
    title="Parkinson Disease Detection API",
    description="Backend API for Parkinson Disease Detection Agent",
    version="1.0.0"
)

# ==========================================================
# CORS
# ==========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================================
# Include Routers
# ==========================================================

app.include_router(
    predict_router,
    prefix="/predict",
    tags=["Prediction"]
)

app.include_router(
    patient_router,
    prefix="/patients",
    tags=["Patients"]
)

app.include_router(
    report_router,
    prefix="/reports",
    tags=["Reports"]
)

app.include_router(
    analytics_router,
    prefix="/analytics",
    tags=["Analytics"]
)

app.include_router(
    chatbot_router,
    prefix="/chatbot",
    tags=["AI Assistant"]
)

app.include_router(
    admin_router,
    prefix="/admin",
    tags=["Admin"]
)

app.include_router(
    user_router,
    prefix="/users",
    tags=["Users"]
)

app.include_router(
    settings_router,
    prefix="/settings",
    tags=["Settings"]
)

# ==========================================================
# Root Endpoint
# ==========================================================

@app.get("/")
def root():
    return {
        "message": "Parkinson Disease Detection API",
        "version": "1.0.0",
        "status": "Running"
    }

# ==========================================================
# Health Check
# ==========================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "api": "running"
    }
