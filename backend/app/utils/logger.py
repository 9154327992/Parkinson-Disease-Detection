"""
Application Logger

Centralized logging configuration for the
Parkinson Disease Detection System.
"""

import logging
import logging.handlers
from pathlib import Path

from app.utils.config import settings


# ==========================================================
# Create Log Directory
# ==========================================================

LOG_FILE = Path(settings.LOG_FILE)

LOG_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)


# ==========================================================
# Log Formatter
# ==========================================================

LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)-8s | "
    "%(name)s | "
    "%(filename)s:%(lineno)d | "
    "%(message)s"
)

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

formatter = logging.Formatter(
    LOG_FORMAT,
    DATE_FORMAT,
)


# ==========================================================
# Logger Factory
# ==========================================================

def get_logger(name: str) -> logging.Logger:
    """
    Return configured logger.
    """

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(settings.LOG_LEVEL)

    # ------------------------------------------------------
    # Console Handler
    # ------------------------------------------------------

    console_handler = logging.StreamHandler()

    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    # ------------------------------------------------------
    # Rotating File Handler
    # ------------------------------------------------------

    file_handler = logging.handlers.RotatingFileHandler(

        filename=LOG_FILE,

        maxBytes=5 * 1024 * 1024,

        backupCount=5,

        encoding="utf-8",

    )

    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    logger.propagate = False

    return logger


# ==========================================================
# Default Logger
# ==========================================================

logger = get_logger("parkinson")


# ==========================================================
# Convenience Methods
# ==========================================================

def log_info(message: str):

    logger.info(message)


def log_warning(message: str):

    logger.warning(message)


def log_error(message: str):

    logger.error(message)


def log_debug(message: str):

    logger.debug(message)


def log_exception(message: str):

    logger.exception(message)


# ==========================================================
# Startup Logs
# ==========================================================

def startup_log():

    logger.info("=" * 60)

    logger.info(settings.APP_NAME)

    logger.info(f"Version : {settings.APP_VERSION}")

    logger.info(f"Environment : {settings.ENVIRONMENT}")

    logger.info("=" * 60)


# ==========================================================
# Shutdown Logs
# ==========================================================

def shutdown_log():

    logger.info("Application shutdown.")


# ==========================================================
# API Logging
# ==========================================================

def log_request(
    method: str,
    path: str,
):

    logger.info(
        f"{method} {path}"
    )


def log_response(
    status_code: int,
):

    logger.info(
        f"Response Status : {status_code}"
    )


# ==========================================================
# Authentication Logging
# ==========================================================

def log_login(username: str):

    logger.info(
        f"User logged in : {username}"
    )


def log_logout(username: str):

    logger.info(
        f"User logged out : {username}"
    )


# ==========================================================
# Prediction Logging
# ==========================================================

def log_prediction(

    patient_id: int,

    prediction: str,

):

    logger.info(

        f"Prediction generated "

        f"[Patient={patient_id}] "

        f"{prediction}"

    )


# ==========================================================
# Report Logging
# ==========================================================

def log_report(

    patient_id: int,

    filename: str,

):

    logger.info(

        f"Report generated "

        f"[Patient={patient_id}] "

        f"{filename}"

    )


# ==========================================================
# AI Assistant Logging
# ==========================================================

def log_chat(

    patient_id: int,

):

    logger.info(

        f"AI chat "

        f"[Patient={patient_id}]"

    )


# ==========================================================
# Database Logging
# ==========================================================

def log_database(message: str):

    logger.info(

        f"Database : {message}"

    )


# ==========================================================
# ML Logging
# ==========================================================

def log_model(message: str):

    logger.info(

        f"ML Model : {message}"

    )


# ==========================================================
# Health Check
# ==========================================================

def logger_status():

    return {

        "status": "Online",

        "level": settings.LOG_LEVEL,

        "log_file": str(LOG_FILE),

    }
