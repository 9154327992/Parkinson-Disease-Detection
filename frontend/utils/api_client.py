import requests
from typing import Optional, Dict, List

import streamlit as st


# ==========================================================
# Backend Configuration
# ==========================================================

BASE_URL = "https://parkinson-disease-detection-wced.onrender.com"

TIMEOUT = 30


# ==========================================================
# Authentication Headers
# ==========================================================

def _headers() -> Dict[str, str]:
    """
    Return Authorization headers when the user is logged in.
    """

    headers = {
        "Content-Type": "application/json",
    }

    token = st.session_state.get(
        "token"
    )

    if token:

        headers["Authorization"] = (
            f"Bearer {token}"
        )

    return headers


# ==========================================================
# Generic GET Request
# ==========================================================

def get(endpoint: str):

    url = f"{BASE_URL}{endpoint}"

    try:

        response = requests.get(
            url,
            headers=_headers(),
            timeout=TIMEOUT,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:

        st.error(
            f"API Error: {e}"
        )

        return None


# ==========================================================
# Generic POST Request
# ==========================================================

def post(
    endpoint: str,
    data: dict,
):

    url = f"{BASE_URL}{endpoint}"

    try:

        response = requests.post(
            url,
            json=data,
            headers=_headers(),
            timeout=TIMEOUT,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:

        st.error(
            f"API Error: {e}"
        )

        return None


# ==========================================================
# Login
# ==========================================================

def login_user(
    username: str,
    password: str,
) -> Optional[Dict]:

    url = f"{BASE_URL}/auth/login"

    payload = {
        "username": username,
        "password": password,
    }

    try:

        response = requests.post(
            url,
            json=payload,
            timeout=TIMEOUT,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:

        try:

            detail = response.json().get(
                "detail",
                str(e),
            )

        except Exception:

            detail = str(e)

        st.error(
            f"Login failed: {detail}"
        )

        return None


# ==========================================================
# Generic PUT Request
# ==========================================================

def put(
    endpoint: str,
    data: Dict,
):

    try:

        response = requests.put(
            f"{BASE_URL}{endpoint}",
            json=data,
            headers=_headers(),
            timeout=TIMEOUT,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:

        st.error(
            f"API Error: {e}"
        )

        return None


# ==========================================================
# Generic DELETE Request
# ==========================================================

def delete(
    endpoint: str,
):

    try:

        response = requests.delete(
            f"{BASE_URL}{endpoint}",
            headers=_headers(),
            timeout=TIMEOUT,
        )

        response.raise_for_status()

        return True

    except requests.RequestException as e:

        st.error(
            f"API Error: {e}"
        )

        return False


# ==========================================================
# Prediction
# ==========================================================

def predict_patient(
    patient_name: str,
    age: int,
    gender: str,
    features: List[float],
) -> Optional[Dict]:

    payload = {
        "patient_name": patient_name,
        "age": age,
        "gender": gender,
        "features": features,
    }

    return post(
        "/prediction/predict",
        payload,
    )


# ==========================================================
# Prediction History
# ==========================================================

def get_prediction_history():

    return get(
        "/prediction/history"
    )


def delete_prediction(
    prediction_id: int,
):

    return delete(
        f"/prediction/{prediction_id}"
    )


# ==========================================================
# Patients
# ==========================================================

def get_patient_history():

    return get(
        "/prediction/history"
    )


def get_patients():

    return get(
        "/patients"
    )


def delete_patient(
    patient_id: int,
):

    return delete(
        f"/patients/{patient_id}"
    )


# ==========================================================
# Reports
# ==========================================================

def get_reports():

    return get(
        "/reports"
    )


def download_report(
    report_id,
):

    try:

        response = requests.get(
            f"{BASE_URL}/reports/{report_id}/download",
            headers=_headers(),
            timeout=TIMEOUT,
        )

        response.raise_for_status()

        return response.content

    except requests.RequestException as e:

        st.error(
            f"Download failed: {e}"
        )

        return None


# ==========================================================
# Analytics
# ==========================================================

def get_analytics():

    return get(
        "/analytics"
    )


# ==========================================================
# AI Assistant
# ==========================================================

def ask_ai_assistant(
    question: str,
):

    payload = {
        "message": question,
    }

    return post(
        "/chatbot/",
        payload,
    )


# ==========================================================
# Admin
# ==========================================================

def get_admin_dashboard():

    return get(
        "/admin/dashboard"
    )


def get_users():

    return get(
        "/users"
    )


def delete_user(
    user_id,
):

    return delete(
        f"/users/{user_id}"
    )


# ==========================================================
# Settings
# ==========================================================

def get_user_settings():

    return get(
        "/settings"
    )


def update_user_settings(
    data,
):

    return put(
        "/settings",
        data,
    )


def change_password(
    current_password,
    new_password,
):

    payload = {
        "current_password": current_password,
        "new_password": new_password,
    }

    return post(
        "/change-password",
        payload,
    )


# ==========================================================
# Health Check
# ==========================================================

def check_backend():

    try:

        response = requests.get(
            f"{BASE_URL}/health",
            timeout=5,
        )

        return response.status_code == 200

    except requests.RequestException:

        return False
