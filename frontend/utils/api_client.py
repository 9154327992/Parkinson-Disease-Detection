from typing import Any, Dict, List, Optional

import requests
import streamlit as st


# ==========================================================
# Configuration
# ==========================================================

BASE_URL = (
    "https://parkinson-disease-detection-wced.onrender.com"
)

TIMEOUT = 60


# ==========================================================
# Authentication
# ==========================================================

def _get_token() -> Optional[str]:
    """
    Get JWT token from Streamlit session.
    """

    token = st.session_state.get(
        "access_token"
    )

    if token:
        return str(token)

    token = st.session_state.get(
        "token"
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
# Response
# ==========================================================

def _read_response(
    response: requests.Response,
):
    """
    Safely read JSON or text response.
    """

    try:
        return response.json()

    except ValueError:

        if response.text:
            return response.text

        return None


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

        if not response.ok:

            st.session_state[
                "last_api_status"
            ] = response.status_code

            return None

        return _read_response(
            response
        )

    except requests.RequestException as exc:

        st.session_state[
            "last_api_error"
        ] = str(exc)

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

        if not response.ok:

            st.session_state[
                "last_api_status"
            ] = response.status_code

            return None

        return _read_response(
            response
        )

    except requests.RequestException as exc:

        st.session_state[
            "last_api_error"
        ] = str(exc)

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

        if not response.ok:
            return None

        return _read_response(
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

        if not response.ok:
            return False

        # Some DELETE endpoints return no body.
        if not response.content:
            return True

        result = _read_response(
            response
        )

        return (
            result
            if isinstance(result, bool)
            else True
        )

    except requests.RequestException:

        return False


# ==========================================================
# LOGIN
# ==========================================================

def login_user(
    username: str,
    password: str,
):
    """
    Login user.

    Supports JSON login and OAuth-style form login.
    """

    username = str(
        username
    ).strip()

    if not username or not password:
        return None


    url = (
        f"{BASE_URL}/auth/login"
    )


    # ------------------------------------------------------
    # JSON request
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

        if response.ok:

            result = _read_response(
                response
            )

            _store_login(
                result
            )

            return result

    except requests.RequestException:
        pass


    # ------------------------------------------------------
    # OAuth2 form request
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

        if response.ok:

            result = _read_response(
                response
            )

            _store_login(
                result
            )

            return result

    except requests.RequestException:
        pass


    return None


def _store_login(
    result,
):
    """
    Store authentication information.
    """

    if not isinstance(
        result,
        dict,
    ):
        return


    token = (
        result.get(
            "access_token"
        )
        or result.get(
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


    user = result.get(
        "user"
    )


    if isinstance(
        user,
        dict,
    ):

        st.session_state[
            "user"
        ] = user


        if user.get("id") is not None:

            st.session_state[
                "user_id"
            ] = user.get("id")


        if user.get("username"):

            st.session_state[
                "username"
            ] = user.get(
                "username"
            )


        if user.get("role"):

            st.session_state[
                "role"
            ] = user.get(
                "role"
            )


    if result.get(
        "username"
    ):

        st.session_state[
            "username"
        ] = result.get(
            "username"
        )


    if result.get(
        "role"
    ):

        st.session_state[
            "role"
        ] = result.get(
            "role"
        )


    st.session_state[
        "logged_in"
    ] = True


def logout_user():
    """
    Clear login state.
    """

    for key in [
        "access_token",
        "token",
        "user",
        "user_id",
        "username",
        "role",
        "logged_in",
    ]:

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
    Submit a Parkinson prediction.
    """

    if not patient_name:
        return None

    if not isinstance(
        features,
        list,
    ):
        return None

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


def get_prediction_history():
    """
    Compatibility alias.
    """

    return get_patient_history()


def delete_prediction(
    prediction_id: int,
):
    """
    Delete prediction.
    """

    return delete(
        f"/prediction/{prediction_id}"
    )


# ==========================================================
# Patients
# ==========================================================

def get_patients():
    """
    Get patients.
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


def delete_patient(
    patient_id: int,
):
    """
    Delete patient.
    """

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


def download_report(
    report_id: int,
):
    """
    Download report PDF.
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

        if not response.ok:
            return None

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

    result = get(
        "/analytics"
    )


    if isinstance(
        result,
        dict,
    ):
        return result


    return None


# ==========================================================
# AI Assistant
# ==========================================================

def ask_ai_assistant(
    question: str,
):
    """
    Ask the AI Health Assistant.
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


    result = post(
        "/chatbot/",
        payload,
    )


    if result is None:

        result = post(
            "/chatbot",
            payload,
        )


    if result is None:
        return None


    # Backend returned plain text.
    if isinstance(
        result,
        str,
    ):

        return {
            "response": result
        }


    # Backend returned JSON.
    if isinstance(
        result,
        dict,
    ):

        answer = (
            result.get(
                "response"
            )
            or result.get(
                "answer"
            )
            or result.get(
                "message"
            )
            or result.get(
                "reply"
            )
        )


        if answer is not None:

            return {
                **result,
                "response": str(
                    answer
                ),
            }


        return {
            **result,
            "response": str(
                result
            ),
        }


    return {
        "response": str(
            result
        )
    }


def get_chatbot_suggestions():
    """
    Get AI Assistant suggested questions.
    """

    fallback = [
        "What is Parkinson's Disease?",
        "What are the early symptoms?",
        "What causes hand tremors?",
        "How is Parkinson's diagnosed?",
        "Is Parkinson's curable?",
        "Which exercises are beneficial?",
        "What foods are recommended?",
        "How can stress be reduced?",
        "What is Bradykinesia?",
        "What are voice disorders?",
    ]


    result = get(
        "/chatbot/suggestions"
    )


    if isinstance(
        result,
        list,
    ):

        return result


    if isinstance(
        result,
        dict,
    ):

        suggestions = (
            result.get(
                "suggestions"
            )
            or result.get(
                "questions"
            )
            or result.get(
                "data"
            )
        )


        if isinstance(
            suggestions,
            list,
        ):

            return suggestions


    return fallback


# ==========================================================
# Admin
# ==========================================================

def get_admin_dashboard():
    """
    Get administrator dashboard.
    """

    result = get(
        "/admin/dashboard"
    )


    if isinstance(
        result,
        dict,
    ):

        return result


    return None


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


def delete_user(
    user_id: int,
):
    """
    Delete user.
    """

    return delete(
        f"/users/{user_id}"
    )


# ==========================================================
# Settings
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


    return None


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


def change_password(
    current_password: str,
    new_password: str,
):
    """
    Change password.
    """

    if not current_password:
        return False

    if not new_password:
        return False


    payload = {
        "current_password":
            current_password,

        "new_password":
            new_password,
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
    Check FastAPI backend.
    """

    try:

        response = requests.get(
            f"{BASE_URL}/health",
            timeout=15,
        )

        return (
            response.status_code
            == 200
        )

    except requests.RequestException:

        return False


def get_api_url():
    """
    Return backend URL.
    """

    return BASE_URL
