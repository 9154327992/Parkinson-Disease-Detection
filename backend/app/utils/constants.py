"""
Application Constants

Centralized constants for the
Parkinson Disease Detection System.
"""

# ==========================================================
# APPLICATION
# ==========================================================

APP_NAME = "Parkinson Disease Detection System"

APP_VERSION = "1.0.0"

API_VERSION = "v1"


# ==========================================================
# USER ROLES
# ==========================================================

ROLE_ADMIN = "admin"

ROLE_DOCTOR = "doctor"

ROLE_USER = "user"

USER_ROLES = [
    ROLE_ADMIN,
    ROLE_DOCTOR,
    ROLE_USER,
]


# ==========================================================
# GENDER
# ==========================================================

GENDER_MALE = "Male"

GENDER_FEMALE = "Female"

GENDER_OTHER = "Other"

GENDERS = [
    GENDER_MALE,
    GENDER_FEMALE,
    GENDER_OTHER,
]


# ==========================================================
# PREDICTION LABELS
# ==========================================================

PREDICTION_POSITIVE = "Parkinson Detected"

PREDICTION_NEGATIVE = "Healthy"

PREDICTION_LABELS = [
    PREDICTION_NEGATIVE,
    PREDICTION_POSITIVE,
]


# ==========================================================
# RISK LEVELS
# ==========================================================

MINIMAL_RISK = "Minimal Risk"

LOW_RISK = "Low Risk"

MODERATE_RISK = "Moderate Risk"

HIGH_RISK = "High Risk"

RISK_LEVELS = [
    MINIMAL_RISK,
    LOW_RISK,
    MODERATE_RISK,
    HIGH_RISK,
]


# ==========================================================
# MODEL STATUS
# ==========================================================

MODEL_READY = "Ready"

MODEL_LOADING = "Loading"

MODEL_NOT_FOUND = "Not Found"

MODEL_ERROR = "Error"


# ==========================================================
# FEATURE NAMES
# ==========================================================

VOICE_FEATURES = [

    "MDVP:Fo(Hz)",
    "MDVP:Fhi(Hz)",
    "MDVP:Flo(Hz)",

    "MDVP:Jitter(%)",
    "MDVP:Jitter(Abs)",
    "MDVP:RAP",
    "MDVP:PPQ",
    "Jitter:DDP",

    "MDVP:Shimmer",
    "MDVP:Shimmer(dB)",
    "Shimmer:APQ3",
    "Shimmer:APQ5",
    "MDVP:APQ",
    "Shimmer:DDA",

    "NHR",
    "HNR",

    "RPDE",
    "DFA",

    "spread1",
    "spread2",

    "D2",

    "PPE",
]

TOTAL_FEATURES = len(VOICE_FEATURES)


# ==========================================================
# FILE TYPES
# ==========================================================

SUPPORTED_UPLOADS = [
    ".csv",
    ".xlsx",
    ".json",
]

MODEL_EXTENSION = ".pkl"

PDF_EXTENSION = ".pdf"


# ==========================================================
# CHATBOT
# ==========================================================

MAX_CHAT_HISTORY = 20

DEFAULT_LANGUAGE = "English"

AI_ASSISTANT_NAME = "Parkinson Health Assistant"


# ==========================================================
# REPORTS
# ==========================================================

REPORT_TITLE = "Parkinson Disease Detection Report"

REPORT_AUTHOR = "Parkinson AI System"


# ==========================================================
# EXERCISE CATEGORIES
# ==========================================================

EXERCISE_TYPES = [

    "Walking",

    "Balance",

    "Strength",

    "Flexibility",

    "Speech",

    "Breathing",
]


# ==========================================================
# MEDICATION
# ==========================================================

REMINDER_PENDING = "Pending"

REMINDER_COMPLETED = "Completed"

REMINDER_MISSED = "Missed"


# ==========================================================
# API RESPONSES
# ==========================================================

SUCCESS = "Success"

FAILED = "Failed"

CREATED = "Created"

UPDATED = "Updated"

DELETED = "Deleted"


# ==========================================================
# ERROR MESSAGES
# ==========================================================

USER_NOT_FOUND = "User not found."

PATIENT_NOT_FOUND = "Patient not found."

PREDICTION_NOT_FOUND = "Prediction not found."

REPORT_NOT_FOUND = "Report not found."

INVALID_CREDENTIALS = "Invalid username or password."

UNAUTHORIZED = "Unauthorized."

FORBIDDEN = "Access denied."

MODEL_NOT_LOADED = "Machine learning model is unavailable."

INVALID_FEATURE_COUNT = (
    f"Exactly {TOTAL_FEATURES} features are required."
)


# ==========================================================
# SUCCESS MESSAGES
# ==========================================================

LOGIN_SUCCESS = "Login successful."

REGISTER_SUCCESS = "Registration successful."

PREDICTION_SUCCESS = "Prediction completed successfully."

REPORT_SUCCESS = "Report generated successfully."

PATIENT_CREATED = "Patient created successfully."

PATIENT_UPDATED = "Patient updated successfully."

PATIENT_DELETED = "Patient deleted successfully."


# ==========================================================
# DATABASE TABLES
# ==========================================================

TABLE_USERS = "users"

TABLE_PATIENTS = "patients"

TABLE_PREDICTIONS = "predictions"

TABLE_REPORTS = "reports"

TABLE_CHAT_HISTORY = "chat_history"

TABLE_REMINDERS = "medication_reminders"


# ==========================================================
# DATE FORMATS
# ==========================================================

DATE_FORMAT = "%Y-%m-%d"

TIME_FORMAT = "%H:%M"

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


# ==========================================================
# SECURITY
# ==========================================================

JWT_ALGORITHM = "HS256"

TOKEN_TYPE = "Bearer"
