from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import create_tables
from app.database.seed import DatabaseSeeder

from app.routes.admin import router as admin_router
from app.routes.auth import router as auth_router
from app.routes.prediction import router as prediction_router
from app.routes.patient import router as patient_router
from app.routes.analytics import router as analytics_router
from app.routes.recommendation import router as recommendation_router
from app.routes.reports import router as reports_router
from app.routes.chatbot import router as chatbot_router


# ==========================================================
# Database Startup
# ==========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initialize database tables and default development
    data when the FastAPI application starts.
    """

    print(
        "=================================================="
    )

    print(
        "Starting Parkinson Disease Detection API..."
    )

    print(
        "=================================================="
    )

    # ------------------------------------------------------
    # Create Database Tables
    # ------------------------------------------------------

    try:

        print(
            "Initializing database tables..."
        )

        create_tables()

        print(
            "Database tables initialized successfully."
        )

    except Exception as exc:

        print(
            f"Database initialization failed: {exc}"
        )

        raise


    # ------------------------------------------------------
    # Seed Default Development Data
    # ------------------------------------------------------

    try:

        print(
            "Checking default database users..."
        )

        seeder = DatabaseSeeder()

        try:

            seeder.seed()

        finally:

            seeder.close()


        print(
            "Database seed completed successfully."
        )

    except Exception as exc:

        print(
            f"Database seeding failed: {exc}"
        )

        raise


    print(
        "=================================================="
    )

    print(
        "Parkinson Disease Detection API is ready."
    )

    print(
        "=================================================="
    )


    # Application is running
    yield


    # ------------------------------------------------------
    # Shutdown
    # ------------------------------------------------------

    print(
        "=================================================="
    )

    print(
        "Parkinson Disease Detection API shutting down."
    )

    print(
        "=================================================="
    )


# ==========================================================
# FastAPI Application
# ==========================================================

app = FastAPI(
    title="Parkinson Disease Detection API",

    description=(
        "Backend API for Parkinson Disease "
        "Detection System"
    ),

    version="1.0.0",

    docs_url="/docs",

    redoc_url="/redoc",

    lifespan=lifespan,
)


# ==========================================================
# CORS
# ==========================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "*"
    ],

    allow_credentials=True,

    allow_methods=[
        "*"
    ],

    allow_headers=[
        "*"
    ],
)


# ==========================================================
# Admin Router
# ==========================================================

app.include_router(
    admin_router,

    prefix="/admin",

    tags=[
        "Admin"
    ],
)


# ==========================================================
# Authentication Router
# ==========================================================

app.include_router(
    auth_router,

    prefix="/auth",

    tags=[
        "Authentication"
    ],
)


# ==========================================================
# Prediction Router
# ==========================================================

app.include_router(
    prediction_router,

    prefix="/prediction",

    tags=[
        "Prediction"
    ],
)


# ==========================================================
# Patient Router
# ==========================================================

app.include_router(
    patient_router,

    tags=[
        "Patients"
    ],
)


# ==========================================================
# Analytics Router
# ==========================================================

app.include_router(
    analytics_router,

    prefix="/analytics",

    tags=[
        "Analytics"
    ],
)


# ==========================================================
# Recommendation Router
# ==========================================================

app.include_router(
    recommendation_router,

    prefix="/recommendations",

    tags=[
        "Recommendations"
    ],
)


# ==========================================================
# Reports Router
# ==========================================================

app.include_router(
    reports_router,

    prefix="/reports",

    tags=[
        "Reports"
    ],
)


# ==========================================================
# AI Chatbot Router
# ==========================================================

app.include_router(
    chatbot_router,

    tags=[
        "AI Chatbot"
    ],
)


# ==========================================================
# Root Endpoint
# ==========================================================

@app.get(
    "/",
    tags=[
        "Root"
    ],
)
async def root():

    return {
        "status": "success",

        "message": (
            "Parkinson Disease Detection "
            "API is running"
        ),

        "version": "1.0.0",
    }


# ==========================================================
# Health Check
# ==========================================================

@app.get(
    "/health",
    tags=[
        "Health"
    ],
)
async def health_check():

    return {
        "status": "healthy",

        "service": (
            "Parkinson Disease Detection API"
        ),
    }
