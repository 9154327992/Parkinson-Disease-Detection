import os
import time
from typing import Any, Dict, List, Optional

import requests
import streamlit as st

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# ==========================================================
# Configuration
# ==========================================================

DEFAULT_API_URL = (
    "https://parkinson-disease-detection-wced.onrender.com"
)

CONNECT_TIMEOUT = 15

DEFAULT_READ_TIMEOUT = 60

RETRY_TOTAL = 3

RETRY_BACKOFF_FACTOR = 1


# ==========================================================
# API URL
# ==========================================================

def _get_api_url() -> str:
    """
    Get backend URL from Streamlit secrets or environment.

    Priority:
        1. Streamlit secrets
        2. API_URL environment variable
        3. BACKEND_URL environment variable
        4. Default Render backend
    """

    url = None

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
    ).strip().rstrip(
        "/"
    )


BASE_URL = _get_api_url()


# ==========================================================
# HTTP Session
# ==========================================================

@st.cache_resource
def _get_http_session() -> requests.Session:
    """
    Create a reusable HTTP session.

    The session automatically retries temporary backend
    failures such as 502, 503 and 504.
    """

    session = requests.Session()


    retry = Retry(
        total=RETRY_TOTAL,

        connect=RETRY_TOTAL,

        read=RETRY_TOTAL,

        status=RETRY_TOTAL,

        backoff_factor=RETRY_BACKOFF_FACTOR,

        status_forcelist=(
            429,
            500,
            502,
            503,
            504,
        ),

        allowed_methods=frozenset(
            [
                "GET",
                "POST",
                "PUT",
                "DELETE",
                "PATCH",
                "HEAD",
            ]
        ),

        raise_on_status=False,
    )


    adapter = HTTPAdapter(
        max_retries=retry,

        pool_connections=10,

        pool_maxsize=20,

        pool_block=False,
    )


    session.mount(
        "https://",
        adapter,
    )


    session.mount(
        "http://",
        adapter,
    )


    return session


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
    extra_headers: Optional[
        Dict[str, str]
    ] = None,
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
# Backend Wake-Up
# ==========================================================

def _wake_backend(
    max_attempts: int = 3,
) -> bool:
    """
    Check and wake the backend.

    This is useful when the hosting platform temporarily
    stops, restarts or cold-starts the API service.
    """

    session = _get_http_session()


    health_url = (
        f"{BASE_URL}/health"
    )


    for attempt in range(
        max_attempts
    ):

        try:

            response = session.get(
                health_url,

                headers={
                    "Accept":
                        "application/json",
                },

                timeout=(
                    CONNECT_TIMEOUT,
                    30,
                ),
            )


            if response.ok:

                return True


        except requests.RequestException:

            pass


        if attempt < (
            max_attempts - 1
        ):

            time.sleep(
                2 * (attempt + 1)
            )


    return False


# ==========================================================
# Response Handler
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


# ==========================================================
# Central Request Function
# ==========================================================

def _request(
    method: str,
    endpoint: str,
    *,
    params: Optional[
        Dict[str, Any]
    ] = None,
    json: Optional[
        Dict[str, Any]
    ] = None,
    data: Any = None,
    files: Any = None,
    timeout: int = DEFAULT_READ_TIMEOUT,
    show_error: bool = False,
) -> Any:
    """
    Centralized HTTP request function.

    Features:
        - Reusable HTTP connection
        - Automatic retries
        - Backend wake-up
        - Timeout recovery
        - Render restart recovery
    """

    endpoint = str(
        endpoint
    )


    if not endpoint.startswith(
        "/"
    ):

        endpoint = (
            "/"
            + endpoint
        )


    url = (
        f"{BASE_URL}"
        f"{endpoint}"
    )


    session = _get_http_session()


    max_attempts = 2


    for attempt in range(
        max_attempts
    ):

        try:

            request_headers = _headers()


            # --------------------------------------------------
            # Multipart file requests should not manually set
            # Content-Type because requests creates the boundary.
            # --------------------------------------------------

            if files:

                request_headers.pop(
                    "Content-Type",
                    None,
                )


            response = session.request(
                method=method.upper(),

                url=url,

                headers=request_headers,

                params=params,

                json=json,

                data=data,

                files=files,

                timeout=(
                    CONNECT_TIMEOUT,
                    timeout,
                ),
            )


            # --------------------------------------------------
            # Temporary server failure
            # --------------------------------------------------

            if (
                response.status_code
                in (
                    502,
                    503,
                    504,
                )
                and attempt < (
                    max_attempts - 1
                )
            ):

                _wake_backend()

                time.sleep(2)

                continue


            result = _handle_response(
                response
            )


            # --------------------------------------------------
            # Show error when requested
            # --------------------------------------------------

            if (
                result is None
                and show_error
            ):

                detail = ""


                try:

                    error_data = (
                        response.json()
                    )


                    if isinstance(
                        error_data,
                        dict,
                    ):

                        detail = (
                            error_data.get(
                                "detail"
                            )
                            or error_data.get(
                                "message"
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
                        "Backend request failed "
                        f"(HTTP {response.status_code})."
                    )


            return result


        # ------------------------------------------------------
        # Connection / Timeout Recovery
        # ------------------------------------------------------

        except (
            requests.ConnectionError,
            requests.Timeout,
        ):

            if attempt < (
                max_attempts - 1
            ):

                _wake_backend()

                time.sleep(2)

                continue


            if show_error:

                st.error(
                    "Unable to connect to the backend. "
                    "The server may be restarting. "
                    "Please try again."
                )


            return None


        except requests.RequestException as exc:

            if show_error:

                st.error(
                    f"Backend request failed: {exc}"
                )


            return None


    return None


# ==========================================================
# Public GET / POST / PUT / DELETE
# ==========================================================

def get(
    endpoint: str,
    params: Optional[
        Dict[str, Any]
    ] = None,
    timeout: int = DEFAULT_READ_TIMEOUT,
) -> Any:

    return _request(
        "GET",

        endpoint,

        params=params,

        timeout=timeout,
    )


def post(
    endpoint: str,
    json: Optional[
        Dict[str, Any]
    ] = None,
    timeout: int = 120,
) -> Any:

    return _request(
        "POST",

        endpoint,

        json=json,

        timeout=timeout,
    )


def put(
    endpoint: str,
    json: Optional[
        Dict[str, Any]
    ] = None,
    timeout: int = DEFAULT_READ_TIMEOUT,
) -> Any:

    return _request(
        "PUT",

        endpoint,

        json=json,

        timeout=timeout,
    )


def delete(
    endpoint: str,
    timeout: int = DEFAULT_READ_TIMEOUT,
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

    return delete(
        f"/prediction/{int(prediction_id)}"
    )


# ==========================================================
# Generic List Normalizer
# ==========================================================

def _extract_list(
    result: Any,
    keys: Optional[
        List[str]
    ] = None,
) -> List[
    Dict[str, Any]
]:

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
) -> Optional[
    Dict[str, Any]
]:

    username = str(
        username
    ).strip()

    password = str(
        password
    )


    if not username:

        return None


    if not password:

        return None


    result = post(
        "/auth/login",

        json={
            "username":
                username,

            "password":
                password,
        },

        timeout=60,
    )


    if not isinstance(
        result,
        dict,
    ):

        return None


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


    user = result.get(
        "user"
    )


    if not isinstance(
        user,
        dict,
    ):

        user = {}


    if not user:

        user = {
            key:
                result.get(key)
            for key in [
                "id",
                "user_id",
                "username",
                "email",
                "full_name",
                "role",
                "is_active",
            ]
            if result.get(key)
            is not None
        }


    if token:

        user[
            "access_token"
        ] = token


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

    for key in [
        "access_token",
        "token",
        "jwt_token",
        "user_id",
        "username",
        "role",
        "logged_in",
        "chat_conversation_id",
    ]:

        if key in st.session_state:

            del st.session_state[
                key
            ]


# ==========================================================
# Current User
# ==========================================================

def get_current_user() -> Optional[
    Dict[str, Any]
]:

    token = _get_token()


    if not token:

        return None


    user_id = st.session_state.get(
        "user_id"
    )


    if user_id is None:

        return None


    result = get(
        "/auth/me",

        params={
            "user_id":
                int(user_id),
        },

        timeout=60,
    )


    if not isinstance(
        result,
        dict,
    ):

        return None


    user = result.get(
        "user"
    )


    if isinstance(
        user,
        dict,
    ):

        return user


    return result


# ==========================================================
# User Settings
# ==========================================================

def get_user_settings() -> Optional[
    Dict[str, Any]
]:

    result = get_current_user()


    if isinstance(
        result,
        dict,
    ):

        return result


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
) -> Optional[
    Dict[str, Any]
]:

    if not isinstance(
        settings,
        dict,
    ):

        return None


    result = put(
        "/auth/me",

        json=settings,
    )


    if isinstance(
        result,
        dict,
    ):

        return result


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

    if not current_password:

        return False


    if not new_password:

        return False


    result = _request(
        "POST",

        "/auth/change-password",

        params={
            "old_password":
                current_password,

            "new_password":
                new_password,
        },

        timeout=60,

        show_error=True,
    )


    return result is not None


# ==========================================================
# Prediction
# ==========================================================

def predict_patient(
    patient_name: str,
    patient_age: int,
    patient_gender: str,
    values: List[float],
) -> Optional[
    Dict[str, Any]
]:

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
# Audio Prediction
# ==========================================================

def predict_audio(
    patient_name: str,
    age: int,
    gender: str,
    audio_file,
) -> Optional[
    Dict[str, Any]
]:

    if audio_file is None:

        return None


    try:

        audio_bytes = (
            audio_file.getvalue()
        )


    except Exception:

        return None


    filename = getattr(
        audio_file,
        "name",
        "audio.wav",
    )


    files = {
        "file": (
            filename,
            audio_bytes,
            "audio/wav",
        )
    }


    params = {
        "patient_name":
            str(
                patient_name
            ).strip(),

        "age":
            int(age),

        "gender":
            str(gender),
    }


    # Wake backend first if needed.

    _wake_backend(
        max_attempts=3
    )


    result = _request(
        "POST",

        "/prediction/predict-audio",

        params=params,

        files=files,

        timeout=180,

        show_error=True,
    )


    if not isinstance(
        result,
        dict,
    ):

        return None


    prediction_result = (
        result.get(
            "prediction"
        )
    )


    if isinstance(
        prediction_result,
        dict,
    ):

        return prediction_result


    return result


# ==========================================================
# Prediction History
# ==========================================================

def get_patient_history():

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

    if patient_id is None:

        return None


    result = get(
        f"/patients/{patient_id}"
    )


    if isinstance(
        result,
        dict,
    ):

        return result


    return None


# ==========================================================
# Analytics
# ==========================================================

def get_analytics():

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

    if report_id is None:

        return None


    endpoint = (
        f"/reports/{report_id}/download"
    )


    url = (
        f"{BASE_URL}{endpoint}"
    )


    session = _get_http_session()


    for attempt in range(2):

        try:

            response = session.get(
                url,

                headers=_headers(),

                timeout=(
                    CONNECT_TIMEOUT,
                    120,
                ),
            )


            if (
                response.status_code
                in (
                    502,
                    503,
                    504,
                )
                and attempt == 0
            ):

                _wake_backend()

                continue


            if not response.ok:

                return None


            content_type = (
                response.headers.get(
                    "content-type",
                    "",
                ).lower()
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

            if attempt == 0:

                _wake_backend()

                continue


            return None


    return None


# ==========================================================
# Admin Dashboard
# ==========================================================

def get_admin_dashboard():

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
    conversation_id: Optional[
        str
    ] = None,
) -> Optional[
    Dict[str, Any]
]:

    question = str(
        question
    ).strip()


    if not question:

        return None


    if conversation_id is None:

        conversation_id = (
            st.session_state.get(
                "chat_conversation_id"
            )
        )


    payload = {
        "message":
            question,
    }


    if conversation_id:

        payload[
            "conversation_id"
        ] = conversation_id


    result = post(
        "/chatbot/",

        json=payload,

        timeout=180,
    )


    if not isinstance(
        result,
        dict,
    ):

        return None


    returned_conversation_id = (
        result.get(
            "conversation_id"
        )
    )


    if returned_conversation_id:

        st.session_state[
            "chat_conversation_id"
        ] = returned_conversation_id


    if (
        "answer"
        not in result
        and "response"
        in result
    ):

        result[
            "answer"
        ] = result.get(
            "response"
        )


    return result


# ==========================================================
# Health Check
# ==========================================================

def health_check() -> bool:
    """
    Check whether the FastAPI backend is reachable.
    """

    result = get(
        "/health",

        timeout=30,
    )


    return result is not None


# ==========================================================
# Backend URL
# ==========================================================

def get_api_url() -> str:
    """
    Return the configured backend URL.
    """

    return BASE_URL
