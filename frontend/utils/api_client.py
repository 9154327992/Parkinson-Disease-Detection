import requests
from typing import Optional, Dict, List
import streamlit as st

# ==========================================================
# Backend Configuration
# ==========================================================

BASE_URL = "https://parkinson-disease-detection-wced.onrender.com"

TIMEOUT = 30


# ==========================================================
# Generic Request Functions
# ==========================================================

def get(endpoint: str):

    url = f"{BASE_URL}{endpoint}"

    try:

        response = requests.get(
            url,
            timeout=TIMEOUT
        )

        st.write("URL:", url)
        st.write("Status Code:", response.status_code)
        st.write("Response:", response.text)

        response.raise_for_status()

        return response.json()

    except Exception as e:
        st.error(f"Error: {e}")
        return None


import requests
import streamlit as st

def post(endpoint: str, data: dict):

    url = f"{BASE_URL}{endpoint}"

    try:
        response = requests.post(
            url,
            json=data,
            timeout=30
        )

        st.write("URL:", url)
        st.write("Status Code:", response.status_code)
        st.write("Response:", response.text)

        response.raise_for_status()

        return response.json()

    except Exception as e:
        st.error(f"Error: {e}")
        return None


def put(endpoint: str, data: Dict):

    try:

        response = requests.put(
            f"{BASE_URL}{endpoint}",
            json=data,
            timeout=TIMEOUT
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException:

        return None


def delete(endpoint: str):

    try:

        response = requests.delete(
            f"{BASE_URL}{endpoint}",
            timeout=TIMEOUT
        )

        response.raise_for_status()

        return True

    except requests.RequestException:

        return False


# ==========================================================
# Prediction
# ==========================================================

def predict_patient(
    patient_name: str,
    age: int,
    gender: str,
    features: List[float]
) -> Optional[Dict]:

    payload = {
        "patient_name": patient_name,
        "age": age,
        "gender": gender,
        "features": features
    }

    return post(
        "/prediction/predict",
        payload
    )


# ==========================================================
# Patient History
# ==========================================================

def get_patient_history():

    return get("/prediction/history")


def get_patients():

    return get("/prediction/history")


def delete_patient(patient_id: int):

    return delete(
        f"/patients/{patient_id}"
    )


# ==========================================================
# Reports
# ==========================================================

def get_reports():

    return get("/reports")


def download_report(report_id):

    try:

        response = requests.get(
            f"{BASE_URL}/reports/{report_id}/download",
            timeout=TIMEOUT
        )

        response.raise_for_status()

        return response.content

    except requests.RequestException:

        return None


# ==========================================================
# Analytics
# ==========================================================

def get_analytics():

    return get("/analytics")


# ==========================================================
# AI Assistant
# ==========================================================

def ask_ai_assistant(question: str):

    payload = {
        "question": question
    }

    return post(
        "/chatbot",
        payload
    )


# ==========================================================
# Admin
# ==========================================================

def get_admin_dashboard():

    return get("/admin/dashboard")


def get_users():

    return get("/users")


def delete_user(user_id):

    return delete(
        f"/users/{user_id}"
    )


# ==========================================================
# Settings
# ==========================================================

def get_user_settings():

    return get("/settings")


def update_user_settings(data):

    return put(
        "/settings",
        data
    )


def change_password(current_password, new_password):

    payload = {
        "current_password": current_password,
        "new_password": new_password
    }

    return post(
        "/change-password",
        payload
    )


# ==========================================================
# Health Check
# ==========================================================

def check_backend():

    try:

        response = requests.get(
            f"{BASE_URL}/health",
            timeout=5
        )

        return response.status_code == 200

    except requests.RequestException:

        return False
