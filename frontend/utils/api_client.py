import requests
import streamlit as st

from typing import (
    Optional,
    Dict,
    List,
    Any,
)


# ==========================================================
# Backend Configuration
# ==========================================================

BASE_URL = (
    "https://parkinson-disease-detection-wced.onrender.com"
)

TIMEOUT = 30


# ==========================================================
# Session / Authentication Helpers
# ==========================================================

def _get_token() -> Optional[str]:
    """
    Get JWT token from Streamlit session state.
    """

    possible_keys = [
        "access_token",
        "token",
        "jwt_token",
    ]

    for key in possible_keys:

        value = st.session_state.get(
            key
        )

        if value:

            return str(
                value
            )

    return None


def _headers() -> Dict[str, str]:
    """
    Build authenticated request headers.
    """

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    token = _get_token()

    if token:

        headers[
            "Authorization"
        ] = f"Bearer {token}"

    return headers


# ==========================================================
# Response Helper
# ==========================================================

def _json_response(
    response: requests.Response,
) -> Any:
    """
    Safely decode JSON response.
    """

    try:

        return response.json()

    except ValueError:

        return {
            "detail": response.text
        }


# ==========================================================
# Generic GET
# ==========================================================

def get(
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
):
    """
    Generic authenticated GET request.
    """

    url = (
        f"{BASE_URL.rstrip('/')}"
        f"/{endpoint.lstrip('/')}"
    )

    try:

        response = requests.get(
            url,
            headers=_headers(),
            params=params,
            timeout=TIMEOUT,
        )

        if response.status_code == 401:

            st.session_state.pop(
                "access_token",
                None,
            )

            st.session_state.pop(
                "token",
                None,
            )

            return None


        response.raise_for_status()

        return _json_response(
            response
        )

    except requests.RequestException:

        return None


# ==========================================================
# Generic POST
# ==========================================================

def post(
    endpoint: str,
    data: Optional[Dict[str, Any]] = None,
):
    """
    Generic authenticated POST request.
    """

    url = (
        f"{BASE_URL.rstrip('/')}"
        f"/{endpoint.lstrip('/')}"
    )

    try:

        response = requests.post(
            url,
            json=data or {},
            headers=_headers(),
            timeout=TIMEOUT,
        )

        if response.status_code == 401:

            return None


        response.raise_for_status()

        return _json_response(
            response
        )

    except requests.RequestException:

        return None


# ==========================================================
# Generic PUT
# ==========================================================

def put(
    endpoint: str,
    data: Optional[Dict[str, Any]] = None,
):
    """
    Generic authenticated PUT request.
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
            timeout=TIMEOUT,
        )

        if response.status_code == 401:

            return None


        response.raise_for_status()

        return _json_response(
            response
        )

    except requests.RequestException:

        return None


# ==========================================================
# Generic PATCH
# ==========================================================

def patch(
    endpoint: str,
    data: Optional[Dict[str, Any]] = None,
):
    """
    Generic authenticated PATCH request.
    """

    url = (
        f"{BASE_URL.rstrip('/')}"
        f"/{endpoint.lstrip('/')}"
    )

    try:

        response = requests.patch(
            url,
            json=data or {},
            headers=_headers(),
            timeout=TIMEOUT,
        )

        response.raise_for_status()

        return _json_response(
            response
        )

    except requests.RequestException:

        return None


# ==========================================================
# Generic DELETE
# ==========================================================

def delete(
    endpoint: str,
):
    """
    Generic authenticated DELETE request.
    """

    url = (
        f"{BASE_URL.rstrip('/')}"
        f"/{endpoint.lstrip('/')}"
    )

    try:

        response = requests.delete(
            url,
            headers=_headers(),
            timeout=TIMEOUT,
        )

        response.raise_for_status()

        return True

    except requests.RequestException:

        return False


# ==========================================================
# Authentication
# ==========================================================

def login(
    username: str,
    password: str,
):
    """
    Login using the FastAPI authentication endpoint.

    Supports both JSON and OAuth2 form-style login.
    """

    url = (
        f"{BASE_URL}/auth/login"
    )


    # ------------------------------------------------------
    # First attempt: JSON
    # ------------------------------------------------------

    try:

        response = requests.post(
            url,
            json={
                "username": username,
                "password": password,
            },
            timeout=TIMEOUT,
        )


        if response.status_code < 400:

            data = _json_response(
                response
            )

            if isinstance(
                data,
                dict,
            ):

                token = (
                    data.get(
                        "access_token"
                    )
                    or data.get(
                        "token"
                    )
                )

                if token:

                    st.session_state[
                        "access_token"
                    ] = token

                    st.session_state[
                        "token"
                    ] = token


                return data

    except requests.RequestException:

        pass


    # ------------------------------------------------------
    # Second attempt: OAuth2 form
    # ------------------------------------------------------

    try:

        response = requests.post(
            url,
            data={
                "username": username,
                "password": password,
            },
            timeout=TIMEOUT,
        )


        if response.status_code < 400:

            data = _json_response(
                response
            )

            if isinstance(
                data,
                dict,
            ):

                token = (
                    data.get(
                        "access_token"
                    )
                    or data.get(
                        "token"
                    )
                )

                if token:

                    st.session_state[
                        "access_token"
                    ] = token

                    st.session_state[
                        "token"
                    ] = token


                return data


    except requests.RequestException:

        pass


    return None


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
        "age": int(age),
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
    """
    Get all prediction history.
    """

    result = get(
        "/prediction/history"
    )


    if result is None:

        return None


    if isinstance(
        result,
        list,
    ):

        return result


    if isinstance(
        result,
        dict,
    ):

        return (
            result.get(
                "history"
            )
            or result.get(
                "predictions"
            )
            or result.get(
                "records"
            )
            or result.get(
                "data"
            )
            or []
        )


    return []


# ==========================================================
# Patient History
# ==========================================================

def get_patient_history():
    """
    Get patient/prediction history.

    The Patient History page expects a list.
    The backend may return either a list or a
    dictionary containing the records.
    """

    result = get(
        "/prediction/history"
    )


    if result is None:

        return None


    if isinstance(
        result,
        list,
    ):

        return result


    if isinstance(
        result,
        dict,
    ):

        return (
            result.get(
                "history"
            )
            or result.get(
                "patients"
            )
            or result.get(
                "predictions"
            )
            or result.get(
                "records"
            )
            or result.get(
                "data"
            )
            or []
        )


    return []


# ==========================================================
# Delete Prediction
# ==========================================================

def delete_prediction(
    prediction_id: int,
):

    return delete(
        f"/prediction/{prediction_id}"
    )


# ==========================================================
# Patients
# ==========================================================

def get_patients():
    """
    Get patient records.
    """

    result = get(
        "/patients"
    )


    if result is None:

        return None


    if isinstance(
        result,
        list,
    ):

        return result


    if isinstance(
        result,
        dict,
    ):

        return (
            result.get(
                "patients"
            )
            or result.get(
                "data"
            )
            or result.get(
                "records"
            )
            or []
        )


    return []


# ==========================================================
# Delete Patient
# ==========================================================

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
    """
    Get reports.
    """

    result = get(
        "/reports"
    )


    if result is None:

        return None


    if isinstance(
        result,
        list,
    ):

        return result


    if isinstance(
        result,
        dict,
    ):

        return (
            result.get(
                "reports"
            )
            or result.get(
                "data"
            )
            or result.get(
                "records"
            )
            or []
        )


    return []


# ==========================================================
# Download Report
# ==========================================================

def download_report(
    report_id,
):
    """
    Download report as bytes.
    """

    url = (
        f"{BASE_URL}"
        f"/reports/{report_id}/download"
    )


    try:

        response = requests.get(
            url,
            headers=_headers(),
            timeout=TIMEOUT,
        )

        response.raise_for_status()

        return response.content

    except requests.RequestException:

        return None


# ==========================================================
# Analytics
# ==========================================================

def get_analytics():
    """
    Get analytics information.
    """

    return get(
        "/analytics"
    )


# ==========================================================
# AI Assistant
# ==========================================================

def ask_ai_assistant(
    question: str,
):
    """
    Ask the backend AI assistant.

    The primary endpoint is /chatbot/.
    """

    question = (
        question
        .strip()
    )


    if not question:

        return None


    # ------------------------------------------------------
    # Primary chatbot request
    # ------------------------------------------------------

    result = post(
        "/chatbot/",
        {
            "message": question,
        },
    )


    if result is not None:

        return result


    # ------------------------------------------------------
    # Compatibility fallback
    # ------------------------------------------------------

    return post(
        "/chatbot",
        {
            "question": question,
        },
    )


# ==========================================================
# Admin Dashboard
# ==========================================================

def get_admin_dashboard():
    """
    Get administrator dashboard.
    """

    return get(
        "/admin/dashboard"
    )


# ==========================================================
# Admin Users
# ==========================================================

def get_users():
    """
    Get all users.
    """

    result = get(
        "/users"
    )


    if result is None:

        return None


    if isinstance(
        result,
        list,
    ):

        return result


    if isinstance(
        result,
        dict,
    ):

        return (
            result.get(
                "users"
            )
            or result.get(
                "data"
            )
            or result.get(
                "records"
            )
            or []
        )


    return []


# ==========================================================
# Delete User
# ==========================================================

def delete_user(
    user_id: int,
):

    return delete(
        f"/users/{user_id}"
    )


# ==========================================================
# User Settings
# ==========================================================

def get_user_settings():
    """
    Get current user settings.
    """

    result = get(
        "/settings"
    )


    if isinstance(
        result,
        dict,
    ):

        return result


    return {}


# ==========================================================
# Update User Settings
# ==========================================================

def update_user_settings(
    data: Dict[str, Any],
):
    """
    Update current user settings.
    """

    if not isinstance(
        data,
        dict,
    ):

        return None


    return put(
        "/settings",
        data,
    )


# ==========================================================
# Change Password
# ==========================================================

def change_password(
    current_password: str,
    new_password: str,
):
    """
    Change current user's password.
    """

    if not current_password:

        return False


    if not new_password:

        return False


    payload = {
        "current_password": current_password,
        "new_password": new_password,
    }


    result = post(
        "/change-password",
        payload,
    )


    return result is not None


# ==========================================================
# Backend Health
# ==========================================================

def check_backend():
    """
    Check FastAPI backend health.
    """

    try:

        response = requests.get(
            f"{BASE_URL}/health",
            timeout=10,
        )


        return (
            response.status_code
            == 200
        )

    except requests.RequestException:

        return False


# ==========================================================
# API Information
# ==========================================================

def get_api_url():
    """
    Return configured backend URL.
    """

    return BASE_URL


# ==========================================================
# API Status
# ==========================================================

def get_api_status():
    """
    Return simple API status information.
    """

    online = check_backend()


    return {
        "online": online,
        "status": (
            "Connected"
            if online
            else "Unavailable"
        ),
        "url": BASE_URL,
    }
