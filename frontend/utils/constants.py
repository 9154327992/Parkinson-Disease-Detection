"""
Application Constants
Parkinson Disease Detection Agent
"""

# ==========================================================
# Application
# ==========================================================

APP_NAME = "Parkinson Disease Detection Agent"

APP_VERSION = "1.0.0"

APP_DESCRIPTION = (
    "AI-powered Parkinson Disease Detection System"
)

# ==========================================================
# Backend
# ==========================================================

BASE_URL = "https://parkinson-disease-detection-wced.onrender.com"

API_TIMEOUT = 30

# ==========================================================
# Authentication
# ==========================================================

TOKEN_KEY = "access_token"

USER_ROLES = [
    "Admin",
    "Doctor",
    "User"
]

# ==========================================================
# Languages
# ==========================================================

LANGUAGES = [
    "English",
    "Hindi"
]

# ==========================================================
# Themes
# ==========================================================

THEMES = [
    "Light",
    "Dark"
]

# ==========================================================
# Risk Levels
# ==========================================================

LOW_RISK = "Low Risk"

MEDIUM_RISK = "Medium Risk"

HIGH_RISK = "High Risk"

RISK_LEVELS = [
    LOW_RISK,
    MEDIUM_RISK,
    HIGH_RISK
]

# ==========================================================
# Prediction Labels
# ==========================================================

HEALTHY = "Healthy"

PARKINSON = "Parkinson Detected"

PREDICTION_LABELS = [
    HEALTHY,
    PARKINSON
]

# ==========================================================
# Patient Gender
# ==========================================================

GENDERS = [
    "Male",
    "Female",
    "Other"
]

# ==========================================================
# Parkinson Dataset Features
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
    "PPE"
]

TOTAL_FEATURES = len(VOICE_FEATURES)

# ==========================================================
# Navigation Pages
# ==========================================================

PAGES = [
    "Home",
    "Prediction",
    "Patient History",
    "AI Health Assistant",
    "Reports",
    "Analytics",
    "Admin Dashboard",
    "Settings"
]

# ==========================================================
# Chart Colors
# ==========================================================

PRIMARY_COLOR = "#2563EB"

SUCCESS_COLOR = "#16A34A"

WARNING_COLOR = "#F59E0B"

DANGER_COLOR = "#DC2626"

INFO_COLOR = "#0891B2"

# ==========================================================
# Status
# ==========================================================

ONLINE = "Online"

OFFLINE = "Offline"

# ==========================================================
# HTTP Status
# ==========================================================

HTTP_OK = 200

HTTP_CREATED = 201

HTTP_BAD_REQUEST = 400

HTTP_UNAUTHORIZED = 401

HTTP_FORBIDDEN = 403

HTTP_NOT_FOUND = 404

HTTP_SERVER_ERROR = 500
