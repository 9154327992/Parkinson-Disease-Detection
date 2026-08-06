from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.auth import router as auth_router
from app.routes.prediction import router as prediction_router
from app.routes.patient import router as patient_router
from app.routes.analytics import router as analytics_router
from app.routes.recommendation import router as recommendation_router
from app.routes.reports import router as reports_router
from app.routes.chatbot import router as chatbot_router


app = FastAPI(
    title="Parkinson Disease Detection API",
    description="Backend API for Parkinson Disease Detection System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routers
app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"],
)

app.include_router(
    prediction_router,
    prefix="/prediction",
    tags=["Prediction"]
)

app.include_router(
    patient_router,
    tags=["Patients"]
)

app.include_router(
    analytics_router,
    prefix="/analytics",
    tags=["Analytics"],
)

app.include_router(
    recommendation_router,
    prefix="/recommendations",
    tags=["Recommendations"],
)

app.include_router(
    reports_router,
    prefix="/reports",
    tags=["Reports"],
)

app.include_router(
    chatbot_router,
    prefix="/chatbot",
    tags=["AI Chatbot"],
)


@app.get("/", tags=["Root"])
async def root():
    return {
        "status": "success",
        "message": "Parkinson Disease Detection API is running",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health"])
async def health():
    return {
        "status": "healthy",
        "service": "Parkinson Disease Detection API",
    }
