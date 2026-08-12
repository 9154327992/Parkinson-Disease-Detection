import requests
import streamlit as st

from typing import Optional, Dict, List, Any


# ==========================================================
# Backend Configuration
# ==========================================================

BASE_URL = (
    "https://parkinson-disease-detection-wced.onrender.com"
)

TIMEOUT = 30


# ==========================================================
# Authentication Token
# ==========================================================

def _get_token() -> Optional[str]:
    """
    Get JWT token from Streamlit session state.
    """

    for key in (
        "access_token",
        "token",
        "jwt_token",
    ):

        token = st.session_state.get(
            key
        )

        if token:
            return str(token)

    return None


def _headers() -> Dict[str, str]:
    """
    Build request headers.
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
    Safely convert response to JSON.
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
    params: Optional[
        Dict[str, Any]
    ] = None,
):
    """
    Generic GET request.
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
    data: Optional[
        Dict[str, Any]
    ] = None,
):
    """
    Generic POST request.
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
    data: Optional[
        Dict[str, Any]
    ] = None,
):
    """
    Generic PUT request.
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
    data: Optional[
        Dict[str, Any]
    ] = None,
):
    """
    Generic PATCH request.
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

        if response.status_code == 401:

            return None

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
    Generic DELETE request.
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

        if response.status_code == 401:

            return False

        response.raise_for_status()

        return True

    except requests.RequestException:

        return False


# ==========================================================
# LOGIN
# ==========================================================

def login(
    username: str,
    password: str,
):
    """
    Login against FastAPI /auth/login.

    Attempts JSON first, then OAuth2 form data.
    """

    url = (
        f"{BASE_URL}/auth/login"
    )


    # ------------------------------------------------------
    # JSON Login
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
    # OAuth2 Form Login
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
# LOGIN USER
# ==========================================================

def login_user(
    username: str,
    password: str,
):
    """
    Compatibility wrapper used by frontend.py.
    """

    return login(
        username,
        password,
    )


# ==========================================================
# LOGOUT
# ==========================================================

def logout():
    """
    Clear authentication information.
    """

    for key in (
        "access_token",
        "token",
        "jwt_token",
        "username",
        "user_id",
        "role",
    ):

        st.session_state.pop(
            key,
            None,
        )

    return True


# ==========================================================
# Prediction
# ==========================================================

def predict_patient(
    patient_name: str,
    age: int,
    gender: str,
    features: List[float],
):
    """
    Submit patient information and 22 ML features.
    """

    if len(features) != 22:

        return None


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
    Get prediction history.
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
    Get all patients.
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
    Get all reports.
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
    Download report.
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
    Get analytics.
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
    Ask AI assistant.
    """

    question = (
        question
        .strip()
    )


    if not question:

        return None


    # Primary endpoint
    result = post(
        "/chatbot/",
        {
            "message": question,
        },
    )


    if result is not None:

        return result


    # Compatibility endpoint
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
    Get current user's settings.
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
    Update current user's settings.
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


    result = post(
        "/change-password",
        {
            "current_password": current_password,
            "new_password": new_password,
        },
    )


    return result is not None


# ==========================================================
# Backend Health
# ==========================================================

def check_backend():
    """
    Check whether FastAPI backend is online.
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
# API URL
# ==========================================================

def get_api_url():
    """
    Return backend URL.
    """

    return BASE_URL


# ==========================================================
# API Status
# ==========================================================

def get_api_status():
    """
    Return backend status.
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
