"""
frontend/utils/api_client.py

Central API client for the Parkinson Disease Detection
Streamlit frontend.

This module provides:
    - Authentication
    - Generic GET / POST / PUT / DELETE
    - Prediction
    - Patient history
    - Patients
    - Reports
    - Analytics
    - Admin dashboard
    - User management
    - Settings
    - Password changes
    - AI Health Assistant

All functions fail safely and return None / [] / False
instead of crashing the Streamlit application.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import requests
import streamlit as st


# ==========================================================
# Configuration
# ==========================================================

DEFAULT_API_URL = (
    "https://parkinson-disease-detection-wced.onrender.com"
)

BASE_URL = os.getenv(
    "API_URL",
    DEFAULT_API_URL,
).rstrip("/")

REQUEST_TIMEOUT = 60


# ==========================================================
# Session Helpers
# ==========================================================

def _get_token() -> Optional[str]:
    """
    Get authentication token from Streamlit session.
    """

    token = st.session_state.get("access_token")

    if token:
        return str(token)

    token = st.session_state.get("token")

    if token:
        return str(token)

    return None


def _headers() -> Dict[str, str]:
    """
    Build HTTP headers.
    """

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    token = _get_token()

    if token:
        headers["Authorization"] = (
            f"Bearer {token}"
        )

    return headers


# ==========================================================
# Response Helpers
# ==========================================================

def _json_response(
    response: requests.Response,
) -> Any:
    """
    Safely decode an HTTP response.

    JSON responses are returned as Python objects.
    Plain text responses are returned as strings.
    """

    try:
        return response.json()

    except ValueError:

        text = response.text

        if text:
            return text

        return None


def _request_error(
    response: requests.Response,
) -> None:
    """
    Store useful API error information in session state.

    Do not expose sensitive server details to users.
    """

    try:
        detail = response.json()

        if isinstance(detail, dict):
            detail = (
                detail.get("detail")
                or detail.get("message")
                or detail.get("error")
            )

        if detail:
            st.session_state["last_api_error"] = str(
                detail
            )

        else:
            st.session_state["last_api_error"] = (
                f"HTTP {response.status_code}"
            )

    except Exception:

        st.session_state["last_api_error"] = (
            f"HTTP {response.status_code}"
        )


# ==========================================================
# Generic GET
# ==========================================================

def get(
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Perform GET request against FastAPI.
    """

    url = (
        f"{BASE_URL.rstrip('/')}"
        f"/{endpoint.lstrip('/')}"
    )

    try:

        response = requests.get(
            url,
            params=params,
            headers=_headers(),
            timeout=REQUEST_TIMEOUT,
        )

        if not response.ok:
            _request_error(response)
            return None

        return _json_response(response)

    except requests.RequestException as exc:

        st.session_state["last_api_error"] = str(exc)

        return None

    except Exception as exc:

        st.session_state["last_api_error"] = str(exc)

        return None


# ==========================================================
# Generic POST
# ==========================================================

def post(
    endpoint: str,
    data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Perform POST request against FastAPI.
    """

    url = (
        f"{BASE_URL.rstrip('/')}"
        f"/{endpoint.lstrip('/')}"
    )

    try:

        response = requests.post(
            url,
            json=data or {},
            params=params,
            headers=_headers(),
            timeout=REQUEST_TIMEOUT,
        )

        if not response.ok:
            _request_error(response)
            return None

        return _json_response(response)

    except requests.RequestException as exc:

        st.session_state["last_api_error"] = str(exc)

        return None

    except Exception as exc:

        st.session_state["last_api_error"] = str(exc)

        return None


# ==========================================================
# Generic PUT
# ==========================================================

def put(
    endpoint: str,
    data: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Perform PUT request against FastAPI.
    """

    url = (
        f"{BASE_URL.rstrip('/')}"
        f"/{endpoint.lstrip('/')}"
    )

    try:

        response = requests.put(
            url,
            json=data or {},
            headers=_headers(),
            timeout=REQUEST_TIMEOUT,
        )

        if not response.ok:
            _request_error(response)
            return None

        return _json_response(response)

    except requests.RequestException as exc:

        st.session_state["last_api_error"] = str(exc)

        return None

    except Exception as exc:

        st.session_state["last_api_error"] = str(exc)

        return None


# ==========================================================
# Generic DELETE
# ==========================================================

def delete(
    endpoint: str,
) -> Any:
    """
    Perform DELETE request against FastAPI.
    """

    url = (
        f"{BASE_URL.rstrip('/')}"
        f"/{endpoint.lstrip('/')}"
    )

    try:

        response = requests.delete(
            url,
            headers=_headers(),
            timeout=REQUEST_TIMEOUT,
        )

        if not response.ok:
            _request_error(response)
            return None

        return _json_response(response)

    except requests.RequestException as exc:

        st.session_state["last_api_error"] = str(exc)

        return None

    except Exception as exc:

        st.session_state["last_api_error"] = str(exc)

        return None


# ==========================================================
# Authentication
# ==========================================================

def login_user(
    username: str,
    password: str,
):
    """
    Login user through FastAPI.

    Supports common FastAPI login response formats.
    """

    username = str(username).strip()

    if not username or not password:
        return None

    # ------------------------------------------------------
    # Primary JSON login
    # ------------------------------------------------------

    payload = {
        "username": username,
        "password": password,
    }

    result = post(
        "/auth/login",
        payload,
    )

    # ------------------------------------------------------
    # Alternative endpoint
    # ------------------------------------------------------

    if result is None:

        result = post(
            "/login",
            payload,
        )

    if result is None:

        result = post(
            "/users/login",
            payload,
        )

    if result is None:
        return None

    # ------------------------------------------------------
    # Save authentication
    # ------------------------------------------------------

    if isinstance(result, dict):

        token = (
            result.get("access_token")
            or result.get("token")
        )

        if token:

            st.session_state["access_token"] = str(
                token
            )

            st.session_state["token"] = str(
                token
            )

        user = result.get("user")

        if isinstance(user, dict):

            st.session_state["user"] = user

            if user.get("id") is not None:
                st.session_state["user_id"] = user.get(
                    "id"
                )

            if user.get("username"):
                st.session_state["username"] = user.get(
                    "username"
                )

            if user.get("role"):
                st.session_state["role"] = user.get(
                    "role"
                )

        if result.get("user_id") is not None:
            st.session_state["user_id"] = result.get(
                "user_id"
            )

        if result.get("username"):
            st.session_state["username"] = result.get(
                "username"
            )

        if result.get("role"):
            st.session_state["role"] = result.get(
                "role"
            )

        st.session_state["logged_in"] = True

    return result


def logout_user():
    """
    Clear frontend authentication state.
    """

    keys = [
        "access_token",
        "token",
        "user",
        "user_id",
        "username",
        "role",
        "logged_in",
    ]

    for key in keys:

        if key in st.session_state:
            del st.session_state[key]

    return True


# ==========================================================
# Prediction
# ==========================================================

def predict_patient(
    patient_name: str,
    patient_age: int,
    patient_gender: str,
    values: List[float],
):
    """
    Submit Parkinson prediction.

    The backend may expect either:
        - features
        - measurements
        - voice_features

    The primary payload uses features.
    """

    if not patient_name:
        return None

    if not isinstance(values, list):
        return None

    if len(values) != 22:
        return None

    payload = {
        "patient_name": patient_name,
        "age": patient_age,
        "gender": patient_gender,
        "features": values,
    }

    result = post(
        "/prediction/predict",
        payload,
    )

    if result is None:

        payload["voice_features"] = values

        result = post(
            "/predict",
            payload,
        )

    return result


# ==========================================================
# Prediction History
# ==========================================================

def get_patient_history():
    """
    Get patient/prediction history.
    """

    result = get(
        "/prediction/history"
    )

    if result is None:
        return None

    if isinstance(result, list):
        return result

    if isinstance(result, dict):

        return (
            result.get("history")
            or result.get("patients")
            or result.get("predictions")
            or result.get("records")
            or []
        )

    return []


# Compatibility alias

def get_prediction_history():
    return get_patient_history()


# ==========================================================
# Patients
# ==========================================================

def get_patients():
    """
    Get all patients.
    """

    result = get(
        "/patients"
    )

    if isinstance(result, list):
        return result

    if isinstance(result, dict):

        return (
            result.get("patients")
            or result.get("data")
            or result.get("records")
            or []
        )

    return []


def get_patient(
    patient_id: int,
):
    """
    Get one patient.
    """

    return get(
        f"/patients/{patient_id}"
    )


def delete_patient(
    patient_id: int,
) -> bool:
    """
    Delete a patient.
    """

    result = delete(
        f"/patients/{patient_id}"
    )

    return result is not None


# ==========================================================
# Reports
# ==========================================================

def get_reports():
    """
    Get reports.
    """

    result = get(
        "/reports"
    )

    if isinstance(result, list):
        return result

    if isinstance(result, dict):

        return (
            result.get("reports")
            or result.get("data")
            or result.get("records")
            or []
        )

    return []


def get_report(
    report_id: int,
):
    """
    Get a single report.
    """

    return get(
        f"/reports/{report_id}"
    )


def delete_report(
    report_id: int,
) -> bool:
    """
    Delete a report.
    """

    result = delete(
        f"/reports/{report_id}"
    )

    return result is not None


# ==========================================================
# Analytics
# ==========================================================

def get_analytics():
    """
    Get analytics dashboard data.
    """

    result = get(
        "/analytics"
    )

    if result is None:

        result = get(
            "/analytics/dashboard"
        )

    if isinstance(result, dict):
        return result

    return None


# ==========================================================
# Admin Dashboard
# ==========================================================

def get_admin_dashboard():
    """
    Get administrator dashboard.
    """

    result = get(
        "/admin/dashboard"
    )

    if isinstance(result, dict):
        return result

    return None


def get_users():
    """
    Get all users.
    """

    result = get(
        "/users"
    )

    if isinstance(result, list):
        return result

    if isinstance(result, dict):

        return (
            result.get("users")
            or result.get("data")
            or result.get("records")
            or []
        )

    return []


def get_user(
    user_id: int,
):
    """
    Get a single user.
    """

    return get(
        f"/users/{user_id}"
    )


def delete_user(
    user_id: int,
) -> bool:
    """
    Delete a user.
    """

    result = delete(
        f"/users/{user_id}"
    )

    return result is not None


# ==========================================================
# User Settings
# ==========================================================

def get_user_settings():
    """
    Get current user's settings/profile.
    """

    result = get(
        "/users/me"
    )

    if result is None:

        result = get(
            "/users/settings"
        )

    if result is None:

        result = get(
            "/settings"
        )

    if isinstance(result, dict):
        return result

    return None


def update_user_settings(
    settings: Dict[str, Any],
):
    """
    Update current user's settings/profile.
    """

    if not isinstance(settings, dict):
        return None

    result = put(
        "/users/me",
        settings,
    )

    if result is None:

        result = put(
            "/users/settings",
            settings,
        )

    if result is None:

        result = put(
            "/settings",
            settings,
        )

    return result


def change_password(
    current_password: str,
    new_password: str,
) -> bool:
    """
    Change current user's password.
    """

    if not current_password or not new_password:
        return False

    payload = {
        "current_password": current_password,
        "new_password": new_password,
    }

    result = post(
        "/auth/change-password",
        payload,
    )

    if result is None:

        result = post(
            "/users/change-password",
            payload,
        )

    if result is None:

        result = post(
            "/change-password",
            payload,
        )

    return result is not None


# ==========================================================
# AI Health Assistant
# ==========================================================

def ask_ai_assistant(
    question: str,
):
    """
    Send a question to the FastAPI AI Assistant.

    Always normalizes a plain string response into:

        {
            "response": "..."
        }

    This prevents:
        AttributeError:
        'str' object has no attribute 'get'
    """

    if question is None:
        return None

    question = str(
        question
    ).strip()

    if not question:
        return {
            "response": ""
        }

    payload = {
        "question": question,
        "message": question,
    }

    # ------------------------------------------------------
    # Primary endpoint
    # ------------------------------------------------------

    result = post(
        "/chatbot",
        payload,
    )

    # ------------------------------------------------------
    # Alternative endpoint
    # ------------------------------------------------------

    if result is None:

        result = post(
            "/chatbot/",
            payload,
        )

    # ------------------------------------------------------
    # Alternative AI endpoint
    # ------------------------------------------------------

    if result is None:

        result = post(
            "/ai/assistant",
            payload,
        )

    if result is None:
        return None

    # ------------------------------------------------------
    # Plain text response
    # ------------------------------------------------------

    if isinstance(result, str):

        return {
            "response": result
        }

    # ------------------------------------------------------
    # JSON response
    # ------------------------------------------------------

    if isinstance(result, dict):

        answer = (
            result.get("response")
            or result.get("answer")
            or result.get("message")
            or result.get("reply")
        )

        if answer is not None:

            return {
                **result,
                "response": str(answer),
            }

        return {
            **result,
            "response": str(result),
        }

    # ------------------------------------------------------
    # Other response types
    # ------------------------------------------------------

    return {
        "response": str(result)
    }


def get_chatbot_suggestions():
    """
    Get suggested questions for the AI Assistant.

    Uses the backend when available and falls back
    to local suggestions.
    """

    fallback = [
        "What is Parkinson's Disease?",
        "What are the early symptoms of Parkinson's?",
        "What causes hand tremors?",
        "How is Parkinson's diagnosed?",
        "Is Parkinson's disease curable?",
        "Which exercises are beneficial?",
        "What foods are recommended?",
        "How can stress be reduced?",
        "What is Bradykinesia?",
        "What are common voice disorders in Parkinson's?",
    ]

    result = get(
        "/chatbot/suggestions"
    )

    if isinstance(result, list):

        return result

    if isinstance(result, dict):

        suggestions = (
            result.get("suggestions")
            or result.get("questions")
            or result.get("data")
        )

        if isinstance(suggestions, list):
            return suggestions

    return fallback


# ==========================================================
# Backend Health
# ==========================================================

def check_backend_health() -> bool:
    """
    Check whether the FastAPI backend is reachable.
    """

    result = get(
        "/health"
    )

    if result is not None:
        return True

    result = get(
        "/"
    )

    return result is not None


# Compatibility alias

def health_check():
    return check_backend_health()


# ==========================================================
# Utility
# ==========================================================

def get_api_url() -> str:
    """
    Return configured API URL.
    """

    return BASE_URL


def get_last_api_error() -> Optional[str]:
    """
    Return last API error stored in session.
    """

    return st.session_state.get(
        "last_api_error"
    )


# ==========================================================
# Public API
# ==========================================================

__all__ = [
    # Generic
    "get",
    "post",
    "put",
    "delete",

    # Authentication
    "login_user",
    "logout_user",

    # Prediction
    "predict_patient",
    "get_patient_history",
    "get_prediction_history",

    # Patients
    "get_patients",
    "get_patient",
    "delete_patient",

    # Reports
    "get_reports",
    "get_report",
    "delete_report",

    # Analytics
    "get_analytics",

    # Admin
    "get_admin_dashboard",
    "get_users",
    "get_user",
    "delete_user",

    # Settings
    "get_user_settings",
    "update_user_settings",
    "change_password",

    # AI
    "ask_ai_assistant",
    "get_chatbot_suggestions",

    # Health
    "check_backend_health",
    "health_check",

    # Utility
    "get_api_url",
    "get_last_api_error",
]
