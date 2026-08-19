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


def _get_api_url() -> str:
    """
    Get backend URL from Streamlit secrets/environment.

    Priority:
        1. Streamlit secrets
        2. Environment variable
        3. Default Render backend
    """

    try:
        url = st.secrets.get(
            "API_URL",
            None,
        )
    except Exception:
        url = None

    if not url:

        url = os.getenv(
            "API_URL"
        )

    if not url:

        url = os.getenv(
            "BACKEND_URL"
        )

    if not url:

        url = DEFAULT_API_URL

    return str(
        url
    ).rstrip("/")


BASE_URL = _get_api_url()


# ==========================================================
# Session Helpers
# ==========================================================

def _get_token() -> Optional[str]:
    """
    Return the JWT/access token stored in Streamlit session.
    """

    token = st.session_state.get(
        "access_token"
    )

    if not token:

        token = st.session_state.get(
            "token"
        )

    if not token:

        token = st.session_state.get(
            "jwt_token"
        )

    return token


def _headers(
    extra_headers: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
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


    if extra_headers:

        headers.update(
            extra_headers
        )

    return headers


# ==========================================================
# Request Helpers
# ==========================================================

def _handle_response(
    response: requests.Response,
) -> Any:
    """
    Safely convert an HTTP response into Python data.
    """

    if response.status_code == 204:

        return True


    try:

        data = response.json()

    except ValueError:

        data = None


    if response.ok:

        if data is None:

            return True

        return data


    # ------------------------------------------------------
    # Authentication errors
    # ------------------------------------------------------

    if response.status_code == 401:

        return None


    # ------------------------------------------------------
    # Authorization errors
    # ------------------------------------------------------

    if response.status_code == 403:

        return None


    return None


def _request(
    method: str,
    endpoint: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    json: Optional[Dict[str, Any]] = None,
    data: Any = None,
    timeout: int = 30,
    show_error: bool = False,
) -> Any:
    """
    Centralized HTTP request function.
    """

    endpoint = str(
        endpoint
    )

    if not endpoint.startswith("/"):
        endpoint = "/" + endpoint


    url = (
        f"{BASE_URL}"
        f"{endpoint}"
    )


    try:

        response = requests.request(
            method=method.upper(),
            url=url,
            headers=_headers(),
            params=params,
            json=json,
            data=data,
            timeout=timeout,
        )


        if (
            response.status_code == 401
            and st.session_state.get(
                "logged_in",
                False,
            )
        ):

            # Do not force logout here.
            # Pages can decide how to handle authentication.

            pass


        result = _handle_response(
            response
        )


        if result is None and show_error:

            detail = ""

            try:

                error_data = response.json()

                if isinstance(
                    error_data,
                    dict,
                ):

                    detail = (
                        error_data.get(
                            "detail"
                        )
                        or ""
                    )

            except Exception:

                detail = ""


            if detail:

                st.error(
                    str(detail)
                )

            else:

                st.error(
                    f"Backend request failed "
                    f"({response.status_code})."
                )


        return result


    except requests.RequestException as exc:

        if show_error:

            st.error(
                f"Unable to connect to backend: {exc}"
            )

        return None


# ==========================================================
# Public GET / POST / PUT / DELETE
# ==========================================================

def get(
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    timeout: int = 30,
) -> Any:

    return _request(
        "GET",
        endpoint,
        params=params,
        timeout=timeout,
    )


def post(
    endpoint: str,
    json: Optional[Dict[str, Any]] = None,
    timeout: int = 60,
) -> Any:

    return _request(
        "POST",
        endpoint,
        json=json,
        timeout=timeout,
    )


def put(
    endpoint: str,
    json: Optional[Dict[str, Any]] = None,
    timeout: int = 30,
) -> Any:

    return _request(
        "PUT",
        endpoint,
        json=json,
        timeout=timeout,
    )


def delete(
    endpoint: str,
    timeout: int = 30,
) -> Any:

    return _request(
        "DELETE",
        endpoint,
        timeout=timeout,
    )


# ==========================================================
# Delete Prediction
# ==========================================================

def delete_prediction(
    prediction_id: int,
) -> Any:
    """
    Delete a prediction by ID.
    """

    return delete(
        f"/prediction/{int(prediction_id)}"
    )


# ==========================================================
# Generic List Normalizer
# ==========================================================

def _extract_list(
    result: Any,
    keys: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Convert common API response formats into a list.
    """

    if result is None:

        return []


    if isinstance(
        result,
        list,
    ):

        return result


    if isinstance(
        result,
        dict,
    ):

        search_keys = (
            keys
            or [
                "data",
                "items",
                "records",
                "results",
            ]
        )


        for key in search_keys:

            value = result.get(
                key
            )

            if isinstance(
                value,
                list,
            ):

                return value


    return []


# ==========================================================
# Authentication
# ==========================================================

def login_user(
    username: str,
    password: str,
) -> Optional[Dict[str, Any]]:
    """
    Login against the FastAPI authentication endpoint.

    Supports common token response formats.
    """

    username = str(
        username
    ).strip()

    password = str(
        password
    )


    if not username or not password:

        return None


    # ------------------------------------------------------
    # Primary login endpoint
    # ------------------------------------------------------

    result = _request(
        "POST",
        "/auth/login",
        json={
            "username": username,
            "password": password,
        },
        timeout=30,
    )


    if result is None:

        return None


    if not isinstance(
        result,
        dict,
    ):

        return None


    # ------------------------------------------------------
    # Extract token
    # ------------------------------------------------------

    token = (
        result.get(
            "access_token"
        )
        or result.get(
            "token"
        )
        or result.get(
            "jwt"
        )
    )


    if token:

        st.session_state[
            "access_token"
        ] = token

        st.session_state[
            "token"
        ] = token


    # ------------------------------------------------------
    # Extract user
    # ------------------------------------------------------

    user = result.get(
        "user"
    )


    if not isinstance(
        user,
        dict,
    ):

        user = {}


    # Some backends return user fields at top level.

    if not user:

        user = {
            key: result.get(key)
            for key in [
                "id",
                "user_id",
                "username",
                "email",
                "full_name",
                "role",
                "is_active",
            ]
            if result.get(key) is not None
        }


    if token:

        user[
            "access_token"
        ] = token


    # ------------------------------------------------------
    # Save session information
    # ------------------------------------------------------

    if user:

        if user.get(
            "id"
        ) is not None:

            st.session_state[
                "user_id"
            ] = user.get(
                "id"
            )

        elif user.get(
            "user_id"
        ) is not None:

            st.session_state[
                "user_id"
            ] = user.get(
                "user_id"
            )


        if user.get(
            "username"
        ):

            st.session_state[
                "username"
            ] = user.get(
                "username"
            )


        if user.get(
            "role"
        ):

            st.session_state[
                "role"
            ] = user.get(
                "role"
            )


    return user


def logout_user() -> None:
    """
    Clear local authentication state.
    """

    for key in [
        "access_token",
        "token",
        "jwt_token",
        "user_id",
        "username",
        "role",
        "logged_in",
    ]:

        if key in st.session_state:

            del st.session_state[
                key
            ]


# ==========================================================
# Current User
# ==========================================================

def get_current_user() -> Optional[Dict[str, Any]]:
    """
    Retrieve the currently authenticated user.

    The FastAPI /auth/me endpoint requires user_id
    as a query parameter.
    """

    token = _get_token()

    if not token:

        st.warning(
            "No authentication token found in the current session."
        )

        return None


    user_id = st.session_state.get(
        "user_id"
    )

    if user_id is None:

        st.warning(
            "No user ID found in the current session."
        )

        return None


    endpoint = (
        f"{BASE_URL}/auth/me"
    )


    params = {
        "user_id": int(user_id),
    }


    headers = {
        "Accept": "application/json",
        "Authorization": (
            f"Bearer {token}"
        ),
    }


    try:

        response = requests.get(
            endpoint,
            params=params,
            headers=headers,
            timeout=30,
        )


        # --------------------------------------------------
        # Handle HTTP errors
        # --------------------------------------------------

        if not response.ok:

            st.error(
                "Current-user request failed "
                f"(HTTP {response.status_code})."
            )

            try:

                st.json(
                    response.json()
                )

            except ValueError:

                st.code(
                    response.text
                )

            return None


        # --------------------------------------------------
        # Parse JSON
        # --------------------------------------------------

        try:

            result = response.json()

        except ValueError:

            st.error(
                "The FastAPI backend returned "
                "an invalid JSON response."
            )

            st.code(
                response.text
            )

            return None


        # --------------------------------------------------
        # Nested user object
        # --------------------------------------------------

        if isinstance(
            result,
            dict,
        ):

            user = result.get(
                "user"
            )

            if isinstance(
                user,
                dict,
            ):

                return user


            # ------------------------------------------------
            # Direct user object
            # ------------------------------------------------

            return result


        return None


    except requests.RequestException as exc:

        st.error(
            "Unable to connect to FastAPI backend: "
            f"{exc}"
        )

        return None
        
# ==========================================================
# User Settings
# ==========================================================

def get_user_settings() -> Optional[Dict[str, Any]]:
    """
    Get the current user's account information.

    Uses /auth/me first because account information
    belongs to the authenticated user.
    """

    result = get_current_user()


    if isinstance(
        result,
        dict,
    ):

        return result


    # Fallback for projects that expose /users/me.

    result = get(
        "/users/me"
    )


    if isinstance(
        result,
        dict,
    ):

        return result


    return None


def update_user_settings(
    settings: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """
    Update current user profile.

    Tries common backend endpoints without executing
    anything at module import time.
    """

    if not isinstance(
        settings,
        dict,
    ):

        return None


    # ------------------------------------------------------
    # Preferred endpoint
    # ------------------------------------------------------

    result = put(
        "/auth/me",
        json=settings,
    )


    if isinstance(
        result,
        dict,
    ):

        return result


    # ------------------------------------------------------
    # Fallback
    # ------------------------------------------------------

    result = put(
        "/users/me",
        json=settings,
    )


    if isinstance(
        result,
        dict,
    ):

        return result


    return None


# ==========================================================
# Change Password
# ==========================================================

def change_password(
    current_password: str,
    new_password: str,
) -> bool:
    """
    Change the logged-in user's password.
    """

    if not current_password:

        return False

    if not new_password:

        return False


    try:

        response = requests.post(
            f"{BASE_URL}/auth/change-password",
            params={
                "old_password":
                    current_password,

                "new_password":
                    new_password,
            },
            headers=_headers(),
            timeout=30,
        )


        if response.status_code == 200:

            return True


        # --------------------------------------------------
        # Display backend error
        # --------------------------------------------------

        try:

            error = response.json()

        except ValueError:

            error = None


        if isinstance(
            error,
            dict,
        ):

            detail = error.get(
                "detail"
            )

            if isinstance(
                detail,
                list,
            ):

                for item in detail:

                    if isinstance(
                        item,
                        dict,
                    ):

                        st.error(
                            item.get(
                                "msg",
                                "Validation error.",
                            )
                        )

                    else:

                        st.error(
                            str(item)
                        )

            elif detail:

                st.error(
                    str(detail)
                )

            else:

                st.error(
                    f"Password update failed "
                    f"(HTTP {response.status_code})."
                )

        else:

            st.error(
                f"Password update failed "
                f"(HTTP {response.status_code})."
            )


        return False


    except requests.RequestException as exc:

        st.error(
            f"Password request failed: {exc}"
        )

        return False

# ==========================================================
# Prediction
# ==========================================================

def predict_patient(
    patient_name: str,
    patient_age: int,
    patient_gender: str,
    values: List[float],
) -> Optional[Dict[str, Any]]:
    """
    Submit a patient prediction.

    Expected frontend signature:

        predict_patient(
            patient_name,
            patient_age,
            patient_gender,
            values,
        )

    where values contains exactly 22 ML features.
    """

    if not patient_name:

        return None


    if not isinstance(
        values,
        list,
    ):

        return None


    if len(values) != 22:

        return None


    try:

        numeric_values = [
            float(value)
            for value in values
        ]

    except (
        TypeError,
        ValueError,
    ):

        return None


    payload = {
        "patient_name":
            str(
                patient_name
            ).strip(),

        "age":
            int(
                patient_age
            ),

        "gender":
            str(
                patient_gender
            ),

        "features":
            numeric_values,
    }


    # ------------------------------------------------------
    # Primary prediction endpoint
    # ------------------------------------------------------

    result = post(
        "/prediction/predict",
        json=payload,
        timeout=120,
    )


    if isinstance(
        result,
        dict,
    ):

        return result


    # ------------------------------------------------------
    # Compatibility fallback
    # ------------------------------------------------------

    result = post(
        "/prediction",
        json=payload,
        timeout=120,
    )


    if isinstance(
        result,
        dict,
    ):

        return result


    return None

# ==========================================================
# Predict From Audio File
# ==========================================================

def predict_audio(
    patient_name: str,
    age: int,
    gender: str,
    audio_file,
) -> Optional[Dict[str, Any]]:
    """
    Upload a WAV audio file and run voice-based prediction.

    The backend automatically extracts the 22 voice features
    before running the prediction model.
    """

    endpoint = (
        f"{BASE_URL}/prediction/predict-audio"
    )

    params = {
        "patient_name": str(
            patient_name
        ).strip(),

        "age": int(
            age
        ),

        "gender": str(
            gender
        ),
    }

    files = {
        "file": (
            audio_file.name,
            audio_file.getvalue(),
            "audio/wav",
        )
    }

    headers = {
        "Accept": "application/json",
    }

    token = _get_token()

    if token:

        headers[
            "Authorization"
        ] = f"Bearer {token}"

    try:

        response = requests.post(
            endpoint,
            params=params,
            files=files,
            headers=headers,
            timeout=60,
        )

        # --------------------------------------------------
        # HTTP Error
        # --------------------------------------------------

        if not response.ok:

            st.error(
                "Audio prediction failed "
                f"(HTTP {response.status_code})."
            )

            try:

                error_data = response.json()

                st.json(
                    error_data
                )

            except ValueError:

                st.code(
                    response.text
                )

            return None

        # --------------------------------------------------
        # Parse Response
        # --------------------------------------------------

        result = _handle_response(
            response
        )

        if not isinstance(
            result,
            dict,
        ):

            st.error(
                "Invalid response received "
                "from the audio prediction endpoint."
            )

            return None

        # --------------------------------------------------
        # Backend response structure:
        #
        # {
        #     "prediction": {
        #         ...
        #     },
        #     "features": {
        #         ...
        #     },
        #     "feature_count": 22
        # }
        #
        # Return only the prediction object because
        # the existing Prediction page expects the
        # prediction fields at the top level.
        # --------------------------------------------------

        prediction_result = result.get(
            "prediction"
        )

        if isinstance(
            prediction_result,
            dict,
        ):

            return prediction_result

        # --------------------------------------------------
        # Fallback
        # --------------------------------------------------

        return result

    except requests.RequestException as exc:

        st.error(
            "Audio prediction request failed: "
            f"{exc}"
        )

        return None


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
            result.get("history")
            or result.get("patients")
            or result.get("predictions")
            or result.get("records")
            or result.get("data")
            or []
        )


    return []

# ==========================================================
# Patients
# ==========================================================

def get_patients():
    """
    Get normal patient records.

    Backend route:
        GET /patients/
    """

    result = get(
        "/patients/"
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
            result.get("patients")
            or result.get("data")
            or result.get("records")
            or []
        )


    return []


def get_patient(
    patient_id: Any,
):
    """
    Get one patient.
    """

    if patient_id is None:

        return None


    result = get(
        f"/patients/{patient_id}"
    )


    return (
        result
        if isinstance(
            result,
            dict,
        )
        else None
    )


# ==========================================================
# Analytics
# ==========================================================

def get_analytics():
    """
    Get analytics summary.

    Backend:
        GET /analytics
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
# Reports
# ==========================================================

def get_reports():
    """
    Get report list.

    Backend:
        GET /reports/
    """

    result = get(
        "/reports/"
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
            result.get("reports")
            or result.get("data")
            or result.get("records")
            or []
        )


    return []


def get_report(
    report_id: Any,
):
    """
    Get one report.
    """

    if report_id is None:

        return None


    result = get(
        f"/reports/{report_id}"
    )


    if isinstance(
        result,
        dict,
    ):

        return result


    return None


def download_report(
    report_id: Any,
):
    """
    Download a generated report.

    Returns:
        bytes for PDF
        dict for metadata
        None on failure
    """

    if report_id is None:

        return None


    endpoint = (
        f"/reports/{report_id}/download"
    )


    url = (
        f"{BASE_URL}"
        f"{endpoint}"
    )


    try:

        response = requests.get(
            url,
            headers=_headers(),
            timeout=60,
        )


        if not response.ok:

            return None


        content_type = (
            response.headers.get(
                "content-type",
                "",
            )
            .lower()
        )


        if (
            "application/pdf"
            in content_type
        ):

            return response.content


        try:

            return response.json()

        except ValueError:

            return response.content


    except requests.RequestException:

        return None


# ==========================================================
# Admin Dashboard
# ==========================================================

def get_admin_dashboard():
    """
    Get administrator dashboard.

    IMPORTANT:
        The backend route is /admin/dashboard.
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


# ==========================================================
# Admin Users
# ==========================================================

def get_users():
    """
    Get all users for administrator.

    IMPORTANT:
        The backend route is /admin/users,
        not /users.
    """

    result = get(
        "/admin/users"
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
            result.get("users")
            or result.get("data")
            or result.get("records")
            or []
        )


    return []


# ==========================================================
# Admin Patients
# ==========================================================

def get_admin_patients():
    """
    Get all patients for administrator.

    IMPORTANT:
        The backend route is /admin/patients.
    """

    result = get(
        "/admin/patients"
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
            result.get("patients")
            or result.get("data")
            or result.get("records")
            or []
        )


    return []


# ==========================================================
# Delete User
# ==========================================================

def delete_user(
    user_id: Any,
) -> bool:
    """
    Delete an administrator-managed user.
    """

    if user_id is None:

        return False


    result = delete(
        f"/admin/users/{user_id}"
    )


    return result is not None


# ==========================================================
# Delete Patient
# ==========================================================

def delete_patient(
    patient_id: Any,
) -> bool:
    """
    Delete an administrator-managed patient.
    """

    if patient_id is None:

        return False


    result = delete(
        f"/admin/patients/{patient_id}"
    )


    return result is not None


# ==========================================================
# AI Health Assistant
# ==========================================================

def ask_ai_assistant(
    question: str,
) -> Optional[Dict[str, Any]]:
    """
    Ask the FastAPI AI Health Assistant.

    Backend endpoint:

        POST /chatbot/

    Backend request field:

        message

    Backend response contains:

        response
        conversation_id
        sources
        suggestions
        timestamp
    """

    question = str(
        question
    ).strip()


    if not question:

        return None


    payload = {
        "message":
            question,
    }


    # ------------------------------------------------------
    # FastAPI Chatbot Endpoint
    # ------------------------------------------------------

    result = post(
        "/chatbot/",
        json=payload,
        timeout=120,
    )


    # ------------------------------------------------------
    # Return Backend Response
    # ------------------------------------------------------

    if isinstance(
        result,
        dict,
    ):

        # --------------------------------------------------
        # Normalize backend "response" into "answer"
        # so the Streamlit page can use it.
        # --------------------------------------------------

        if (
            "answer" not in result
            and "response" in result
        ):

            result["answer"] = (
                result.get(
                    "response"
                )
            )


        return result


    return None


# ==========================================================
# Health Check
# ==========================================================

def health_check() -> bool:
    """
    Check whether the FastAPI backend is reachable.
    """

    result = get(
        "/health",
        timeout=10,
    )


    return result is not None


# ==========================================================
# Backend URL
# ==========================================================

def get_api_url() -> str:
    """
    Return the configured API URL.
    """

    return BASE_URL
