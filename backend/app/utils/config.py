"""
Application Configuration

Centralized configuration management for the
Parkinson Disease Detection System.
"""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# ==========================================================
# Base Paths
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

MODEL_DIR = BASE_DIR / "models"

DATASET_DIR = BASE_DIR / "datasets"

REPORT_DIR = BASE_DIR / "reports"

LOG_DIR = BASE_DIR / "logs"


# ==========================================================
# Settings
# ==========================================================

class Settings(BaseSettings):
    """
    Application settings.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ======================================================
    # Application
    # ======================================================

    APP_NAME: str = "Parkinson Disease Detection API"

    APP_VERSION: str = "1.0.0"

    APP_DESCRIPTION: str = (
        "AI-powered Parkinson Disease Detection System"
    )

    DEBUG: bool = False

    ENVIRONMENT: str = "development"

    # ======================================================
    # API
    # ======================================================

    API_PREFIX: str = "/api/v1"

    # ======================================================
    # Database
    # ======================================================

    DATABASE_URL: str = Field(
        default="sqlite:///./parkinson.db"
    )

    # ======================================================
    # JWT
    # ======================================================

    SECRET_KEY: str = Field(
        default="CHANGE_THIS_SECRET_KEY"
    )

    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ======================================================
    # Machine Learning
    # ======================================================

    MODEL_PATH: Path = MODEL_DIR / "model.pkl"

    SCALER_PATH: Path = MODEL_DIR / "scaler.pkl"

    # ======================================================
    # Reports
    # ======================================================

    REPORT_DIRECTORY: Path = REPORT_DIR

    # ======================================================
    # Logging
    # ======================================================

    LOG_LEVEL: str = "INFO"

    LOG_FILE: Path = LOG_DIR / "application.log"

    # ======================================================
    # Uploads
    # ======================================================

    MAX_UPLOAD_SIZE_MB: int = 10

    ALLOWED_EXTENSIONS: list[str] = [
        "csv",
        "xlsx",
        "json",
    ]

    # ======================================================
    # CORS
    # ======================================================

    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:8501",
        "http://localhost:8000",
    ]

    # ======================================================
    # Email (Optional)
    # ======================================================

    SMTP_SERVER: str = ""

    SMTP_PORT: int = 587

    SMTP_USERNAME: str = ""

    SMTP_PASSWORD: str = ""

    # ======================================================
    # AI Assistant
    # ======================================================

    ENABLE_AI_ASSISTANT: bool = True

    MAX_CHAT_HISTORY: int = 20


# ==========================================================
# Cached Settings
# ==========================================================

@lru_cache
def get_settings() -> Settings:
    """
    Return cached application settings.
    """

    return Settings()


settings = get_settings()
