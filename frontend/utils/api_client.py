from typing import Any, Dict, List, Optional
import requests
import streamlit as st


# ==========================================================
# Backend Configuration
# ==========================================================

BASE_URL = (
    "https://parkinson-disease-detection-wced.onrender.com"
)

TIMEOUT = 30


# ==========================================================
# Internal Helpers
# ==========================================================

def _clean_endpoint(endpoint: str) -> str:
    """
    Ensure endpoint starts with /.
    """

    if not endpoint:
        return ""

    if not endpoint.startswith("/"):
        endpoint = "/" + endpoint

    return endpoint


def _get_token() -> Optional[str]:
    """
    Get JWT token from Streamlit session.
    """

    try:
        return st.session_state.get(
            "token"
        )
    except Exception:
        return None


def _headers(
    authenticated: bool = True,
) -> Dict[str, str]:
    """
    Build request headers.

    Adds Bearer token when available.
    """

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    if authenticated:

        token = _get_token()

        if token:

            headers["Authorization"] = (
                f"Bearer {token}"
            )

    return headers


def _parse_response(
    response: requests.Response,
) -> Any:
    """
    Safely parse a FastAPI response.
    """

    try:

        return response.json()

    except ValueError:

        return response.text


def _error_message(
    response: Optional[requests.Response],
) -> str:
    """
    Extract useful API error information.
    """

    if response is None:
        return "Unable to connect to backend."

    try:

        data = response.json()

        if isinstance(data, dict):

            detail = data.get(
                "detail"
            )

            if detail:

                if isinstance(
                    detail,
                    list,
                ):

                    return "; ".join(
                        str(item)
                        for item in detail
                    )

                return str(detail)

            message = data.get(
                "message"
            )

            if message:
                return str(message)

    except Exception:
        pass

    if response.text:
        return response.text

    return (
        f"Request failed "
        f"with status {response.status_code}."
    )


# ==========================================================
# Generic GET
# ==========================================================

def get(
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    timeout: int = TIMEOUT,
    authenticated: bool = True,
) -> Any:
    """
    Generic GET request.
    """

    endpoint = _clean_endpoint(
        endpoint
    )

    url = (
        f"{BASE_URL}"
        f"{endpoint}"
    )

    try:

        response = requests.get(
            url,
            params=params,
            headers=_headers(
                authenticated
            ),
            timeout=timeout,
        )

        response.raise_for_status()

        return _parse_response(
            response
        )

    except requests.RequestException as exc:

        print(
            f"GET {url} failed: {exc}"
        )

        return None

    except Exception as exc:

        print(
            f"GET {url} unexpected error: {exc}"
        )

        return None


# ==========================================================
# Generic POST
# ==========================================================

def post(
    endpoint: str,
    data: Optional[Dict[str, Any]] = None,
    timeout: int = TIMEOUT,
    authenticated: bool = True,
) -> Any:
    """
    Generic POST request.
    """

    endpoint = _clean_endpoint(
        endpoint
    )

    url = (
        f"{BASE_URL}"
        f"{endpoint}"
    )

    if data is None:
        data = {}

    try:

        response = requests.post(
            url,
            json=data,
            headers=_headers(
                authenticated
            ),
            timeout=timeout,
        )

        response.raise_for_status()

        return _parse_response(
            response
        )

    except requests.RequestException as exc:

        print(
            f"POST {url} failed: {exc}"
        )

        return None

    except Exception as exc:

        print(
            f"POST {url} unexpected error: {exc}"
        )

        return None


# ==========================================================
# Generic PUT
# ==========================================================

def put(
    endpoint: str,
    data: Optional[Dict[str, Any]] = None,
    timeout: int = TIMEOUT,
    authenticated: bool = True,
) -> Any:
    """
    Generic PUT request.
    """

    endpoint = _clean_endpoint(
        endpoint
    )

    url = (
        f"{BASE_URL}"
        f"{endpoint}"
    )

    if data is None:
        data = {}

    try:

        response = requests.put(
            url,
            json=data,
            headers=_headers(
                authenticated
            ),
            timeout=timeout,
        )

        response.raise_for_status()

        return _parse_response(
            response
        )

    except requests.RequestException as exc:

        print(
            f"PUT {url} failed: {exc}"
        )

        return None

    except Exception as exc:

        print(
            f"PUT {url} unexpected error: {exc}"
        )

        return None


# ==========================================================
# Generic DELETE
# ==========================================================

def delete(
    endpoint: str,
    timeout: int = TIMEOUT,
    authenticated: bool = True,
) -> bool:
    """
    Generic DELETE request.
    """

    endpoint = _clean_endpoint(
        endpoint
    )

    url = (
        f"{BASE_URL}"
        f"{endpoint}"
    )

    try:

        response = requests.delete(
            url,
            headers=_headers(
                authenticated
            ),
            timeout=timeout,
        )

        response.raise_for_status()

        return True

    except requests.RequestException as exc:

        print(
            f"DELETE {url} failed: {exc}"
        )

        return False

    except Exception as exc:

        print(
            f"DELETE {url} unexpected error: {exc}"
        )

        return False


# ==========================================================
# Authentication
# ==========================================================

def login_user(
    username: str,
    password: str,
) -> Optional[Dict[str, Any]]:
    """
    Login user.

    Backend:
        POST /auth/login
    """

    if not username or not password:
        return None

    payload = {
        "username": username,
        "password": password,
    }

    result = post(
        "/auth/login",
        payload,
        timeout=30,
        authenticated=False,
    )

    if not isinstance(
        result,
        dict,
    ):
        return None

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

        user = {
            "id": result.get(
                "user_id"
            ),
            "username": result.get(
                "username",
                username,
            ),
            "full_name": result.get(
                "full_name",
                "",
            ),
            "email": result.get(
                "email",
                "",
            ),
            "role": result.get(
                "role",
                "User",
            ),
            "is_active": result.get(
                "is_active",
                True,
            ),
        }

    token = (
        result.get(
            "access_token"
        )
        or result.get(
            "token"
        )
    )

    # ------------------------------------------------------
    # Normalize role
    # ------------------------------------------------------

    role = (
        user.get(
            "role"
        )
        or result.get(
            "role"
        )
        or "User"
    )

    if isinstance(
        role,
        str,
    ):

        if role.lower() == "admin":
            role = "Admin"

        elif role.lower() == "doctor":
            role = "Doctor"

        elif role.lower() == "user":
            role = "User"

    # ------------------------------------------------------
    # Return normalized response
    # ------------------------------------------------------

    return {
        "success": True,
        "access_token": token,
        "token": token,
        "token_type": result.get(
            "token_type",
            "bearer",
        ),
        "expires_in": result.get(
            "expires_in"
        ),
        "user": user,
        "id": user.get(
            "id"
        ),
        "user_id": user.get(
            "id"
        ),
        "username": user.get(
            "username",
            username,
        ),
        "full_name": user.get(
            "full_name",
            "",
        ),
        "email": user.get(
            "email",
            "",
        ),
        "role": role,
        "is_active": user.get(
            "is_active",
            True,
        ),
    }


def login(
    username: str,
    password: str,
) -> Optional[Dict[str, Any]]:
    """
    Compatibility alias for login_user().
    """

    return login_user(
        username,
        password,
    )


def register_user(
    username: str,
    password: str,
    confirm_password: str,
    full_name: str = "",
    email: str = "",
    role: str = "User",
) -> Optional[Dict[str, Any]]:
    """
    Register a new user.

    Backend:
        POST /auth/register
    """

    payload = {
        "username": username,
        "password": password,
        "confirm_password": (
            confirm_password
        ),
        "full_name": full_name,
        "email": email,
        "role": role,
    }

    return post(
        "/auth/register",
        payload,
        timeout=30,
        authenticated=False,
    )


def register(
    username: str,
    password: str,
    confirm_password: str,
    full_name: str = "",
    email: str = "",
    role: str = "User",
) -> Optional[Dict[str, Any]]:
    """
    Compatibility alias.
    """

    return register_user(
        username=username,
        password=password,
        confirm_password=confirm_password,
        full_name=full_name,
        email=email,
        role=role,
    )


def get_current_user(
    user_id: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    """
    Get current authenticated user.

    Backend currently exposes:
        GET /auth/me

    The current backend schema expects user_id
    as a query parameter.
    """

    params = None

    if user_id is None:

        try:

            user_id = st.session_state.get(
                "user_id"
            )

        except Exception:

            user_id = None

    if user_id is not None:

        params = {
            "user_id": user_id
        }

    return get(
        "/auth/me",
        params=params,
    )


def logout_user() -> bool:
    """
    Logout user.

    Backend:
        POST /auth/logout
    """

    result = post(
        "/auth/logout",
        {},
    )

    return result is not None


def logout() -> bool:
    """
    Compatibility alias.
    """

    return logout_user()


# ==========================================================
# Prediction
# ==========================================================

def predict_patient(
    patient_name: str,
    age: int,
    gender: str,
    features: List[float],
) -> Optional[Dict[str, Any]]:
    """
    Predict Parkinson disease.

    Backend:
        POST /prediction/predict
    """

    payload = {
        "patient_name": patient_name,
        "age": age,
        "gender": gender,
        "features": features,
    }

    return post(
        "/prediction/predict",
        payload,
        timeout=60,
    )


def predict(
    patient_name: str,
    age: int,
    gender: str,
    features: List[float],
) -> Optional[Dict[str, Any]]:
    """
    Compatibility alias.
    """

    return predict_patient(
        patient_name,
        age,
        gender,
        features,
    )


# ==========================================================
# Prediction History
# ==========================================================

def get_prediction_history():
    """
    Get prediction history.

    Backend:
        GET /prediction/history
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
            or []
        )

    return []


def delete_prediction(
    prediction_id: int,
) -> bool:
    """
    Delete prediction.

    Backend:
        DELETE /prediction/{prediction_id}
    """

    return delete(
        f"/prediction/{prediction_id}"
    )


def get_prediction(
    prediction_id: int,
):
    """
    Get a single prediction.
    """

    return get(
        f"/prediction/{prediction_id}"
    )


# ==========================================================
# Patient History
# ==========================================================

def get_patient_history():
    """
    Get patient/prediction history.

    Primary endpoint:
        /prediction/history

    The prediction history contains patient_name,
    diagnosis/prediction, confidence, risk level,
    and timestamps.
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
            or []
        )

    return []


# ==========================================================
# Patients
# ==========================================================

def get_patients(
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
):
    """
    Get all patients.

    Backend:
        GET /patients/
    """

    params = {
        "skip": skip,
        "limit": limit,
    }

    if search:
        params["search"] = search

    result = get(
        "/patients/",
        params=params,
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
                "records"
            )
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


def create_patient(
    data: Dict[str, Any],
):
    """
    Create patient.
    """

    return post(
        "/patients/",
        data,
    )


def update_patient(
    patient_id: int,
    data: Dict[str, Any],
):
    """
    Update patient.
    """

    return put(
        f"/patients/{patient_id}",
        data,
    )


def delete_patient(
    patient_id: int,
) -> bool:
    """
    Delete patient.

    Backend:
        DELETE /patients/{patient_id}
    """

    return delete(
        f"/patients/{patient_id}"
    )


def get_patient_predictions(
    patient_id: int,
):
    """
    Get predictions belonging to a patient.
    """

    result = get(
        f"/patients/{patient_id}/predictions"
    )

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

        return (
            result.get(
                "predictions"
            )
            or result.get(
                "history"
            )
            or result.get(
                "records"
            )
            or []
        )

    return []


def get_patient_reports(
    patient_id: int,
):
    """
    Get reports belonging to a patient.
    """

    result = get(
        f"/patients/{patient_id}/reports"
    )

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

        return (
            result.get(
                "reports"
            )
            or result.get(
                "records"
            )
            or []
        )

    return []


# ==========================================================
# Reports
# ==========================================================

def get_reports():
    """
    Get all reports.

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
            result.get(
                "reports"
            )
            or result.get(
                "records"
            )
            or []
        )

    return []


def get_report(
    report_id: int,
):
    """
    Get report details.
    """

    return get(
        f"/reports/{report_id}"
    )


def generate_report(
    data: Dict[str, Any],
):
    """
    Generate a patient report.
    """

    return post(
        "/reports/",
        data,
    )


def download_report(
    report_id: int,
):
    """
    Download report content.

    Returns raw bytes when backend provides
    a binary response.
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

        content_type = (
            response.headers.get(
                "content-type",
                "",
            )
            .lower()
        )

        if (
            "application/json"
            in content_type
        ):

            return _parse_response(
                response
            )

        return response.content

    except requests.RequestException as exc:

        print(
            f"Report download failed: {exc}"
        )

        return None


def delete_report(
    report_id: int,
) -> bool:
    """
    Delete report.
    """

    return delete(
        f"/reports/{report_id}"
    )


# ==========================================================
# Analytics
# ==========================================================

def get_analytics():
    """
    Get analytics dashboard.

    Backend:
        GET /analytics/dashboard

    The old frontend used /analytics, but the
    FastAPI router exposes /analytics/dashboard.
    """

    result = get(
        "/analytics/dashboard"
    )

    if result is None:
        return None

    if isinstance(
        result,
        dict,
    ):
        return result

    return {}


def get_prediction_analytics():
    """
    Get prediction analytics.
    """

    return get(
        "/analytics/predictions"
    )


def get_patient_analytics():
    """
    Get patient analytics.
    """

    return get(
        "/analytics/patients"
    )


def get_monthly_trend():
    """
    Get monthly prediction trend.
    """

    return get(
        "/analytics/monthly-trend"
    )


def get_age_distribution():
    """
    Get age distribution.
    """

    return get(
        "/analytics/age-distribution"
    )


def get_gender_distribution():
    """
    Get gender distribution.
    """

    return get(
        "/analytics/gender-distribution"
    )


def get_risk_distribution():
    """
    Get risk distribution.
    """

    return get(
        "/analytics/risk-distribution"
    )


def get_analytics_summary():
    """
    Get analytics summary.
    """

    return get(
        "/analytics/summary"
    )


# ==========================================================
# AI Health Assistant
# ==========================================================

def ask_ai_assistant(
    question: str,
):
    """
    Send a question to the AI Health Assistant.

    Backend endpoint:
        POST /chatbot/chatbot/

    Request:
        {
            "message": "..."
        }

    Response:
        {
            "conversation_id": "...",
            "response": "...",
            "sources": [...],
            "suggestions": [...],
            "timestamp": "..."
        }
    """

    if not question:
        return {
            "success": False,
            "answer": "Please enter a question.",
            "response": "",
            "sources": [],
            "suggestions": [],
        }

    question = str(
        question
    ).strip()

    if not question:

        return {
            "success": False,
            "answer": "Please enter a question.",
            "response": "",
            "sources": [],
            "suggestions": [],
        }

    payload = {
        "message": question,
    }

    result = post(
        "/chatbot/chatbot/",
        payload,
        timeout=60,
    )

    # ------------------------------------------------------
    # Backend unavailable
    # ------------------------------------------------------

    if result is None:

        return {
            "success": False,
            "answer": (
                "The AI Health Assistant "
                "is temporarily unavailable. "
                "Please try again."
            ),
            "response": "",
            "sources": [],
            "suggestions": [],
        }

    # ------------------------------------------------------
    # Dictionary response
    # ------------------------------------------------------

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
            or ""
        )

        sources = (
            result.get(
                "sources"
            )
            or []
        )

        suggestions = (
            result.get(
                "suggestions"
            )
            or []
        )

        return {
            "success": True,
            "answer": str(
                answer
            ),
            "response": str(
                answer
            ),
            "conversation_id":
                result.get(
                    "conversation_id"
                ),
            "sources": sources,
            "suggestions":
                suggestions,
            "timestamp":
                result.get(
                    "timestamp"
                ),
        }

    # ------------------------------------------------------
    # Plain text response
    # ------------------------------------------------------

    if isinstance(
        result,
        str,
    ):

        return {
            "success": True,
            "answer": result,
            "response": result,
            "sources": [],
            "suggestions": [],
        }

    # ------------------------------------------------------
    # Unexpected response
    # ------------------------------------------------------

    return {
        "success": False,
        "answer": (
            "The AI Assistant returned "
            "an unexpected response."
        ),
        "response": "",
        "sources": [],
        "suggestions": [],
    }


def ask_question(
    question: str,
):
    """
    Compatibility alias.

    Some versions of the AI page use
    ask_question() instead of
    ask_ai_assistant().
    """

    return ask_ai_assistant(
        question
    )


def ask_chatbot(
    question: str,
):
    """
    Compatibility alias.
    """

    return ask_ai_assistant(
        question
    )


def get_chatbot_suggestions():
    """
    Get suggested questions.

    Backend:
        GET /chatbot/chatbot/suggestions
    """

    result = get(
        "/chatbot/chatbot/suggestions"
    )

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

        return (
            result.get(
                "suggestions"
            )
            or result.get(
                "questions"
            )
            or []
        )

    return []


def get_chatbot_faq():
    """
    Get chatbot FAQs.
    """

    result = get(
        "/chatbot/chatbot/faq"
    )

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

        return (
            result.get(
                "faq"
            )
            or result.get(
                "faqs"
            )
            or []
        )

    return []


def get_parkinson_information():
    """
    Get educational Parkinson information.
    """

    return get(
        "/chatbot/chatbot/parkinson"
    )


# ==========================================================
# Recommendations
# ==========================================================

def get_recommendations():
    """
    Get recommendations.

    Kept flexible because recommendation routes
    may evolve.
    """

    result = get(
        "/recommendations/"
    )

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

        return (
            result.get(
                "recommendations"
            )
            or result.get(
                "items"
            )
            or result.get(
                "records"
            )
            or []
        )

    return []


def create_recommendation(
    data: Dict[str, Any],
):
    """
    Create recommendation.
    """

    return post(
        "/recommendations/",
        data,
    )


# ==========================================================
# Admin Dashboard
# ==========================================================

def get_admin_dashboard():
    """
    Get administrator dashboard.

    Backend:
        GET /admin/dashboard
    """

    return get(
        "/admin/dashboard"
    )


def get_users():
    """
    Get users for admin dashboard.

    The admin frontend expects a list.
    """

    result = get(
        "/users"
    )

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

        return (
            result.get(
                "users"
            )
            or result.get(
                "records"
            )
            or []
        )

    return []


def get_admin_users():
    """
    Compatibility alias.
    """

    return get_users()


def delete_user(
    user_id: int,
) -> bool:
    """
    Delete a user.
    """

    return delete(
        f"/users/{user_id}"
    )


# ==========================================================
# Settings
# ==========================================================

def get_user_settings():
    """
    Get user settings.

    If the backend settings endpoint is unavailable,
    return safe frontend defaults rather than crashing
    the Settings page.
    """

    result = get(
        "/settings"
    )

    if isinstance(
        result,
        dict,
    ):

        return result

    # Safe frontend defaults.
    return {
        "username": st.session_state.get(
            "username",
            "",
        ),
        "email": st.session_state.get(
            "email",
            "",
        ),
        "full_name": st.session_state.get(
            "full_name",
            "",
        ),
        "theme": st.session_state.get(
            "theme",
            "Light",
        ),
        "language": st.session_state.get(
            "language",
            "English",
        ),
        "api_url": BASE_URL,
    }


def update_user_settings(
    data: Dict[str, Any],
):
    """
    Update user settings.
    """

    result = put(
        "/settings",
        data,
    )

    # Update local session for frontend
    # preferences that don't require backend
    # support.
    try:

        if "theme" in data:

            st.session_state.theme = (
                data["theme"]
            )

        if "language" in data:

            st.session_state.language = (
                data["language"]
            )

        if "username" in data:

            st.session_state.username = (
                data["username"]
            )

        if "email" in data:

            st.session_state.email = (
                data["email"]
            )

    except Exception:
        pass

    return result


def change_password(
    current_password: str,
    new_password: str,
):
    """
    Change current user's password.

    Backend:
        POST /auth/change-password

    The backend currently defines old_password
    and new_password as parameters.
    """

    payload = {
        "old_password": current_password,
        "new_password": new_password,
    }

    result = post(
        "/auth/change-password",
        payload,
    )

    return result


# ==========================================================
# Backend Health
# ==========================================================

def check_backend() -> bool:
    """
    Check FastAPI backend.
    """

    result = get(
        "/health",
        timeout=10,
        authenticated=False,
    )

    return isinstance(
        result,
        dict,
    ) and (
        result.get(
            "status"
        )
        in (
            "healthy",
            "success",
        )
    )


def backend_health():
    """
    Return full backend health response.
    """

    return get(
        "/health",
        timeout=10,
        authenticated=False,
    )


# ==========================================================
# Model Health
# ==========================================================

def get_model_info():
    """
    Get ML model information.
    """

    return get(
        "/prediction/model-info"
    )


def get_prediction_statistics():
    """
    Get prediction statistics.
    """

    return get(
        "/prediction/statistics"
    )


# ==========================================================
# Utility
# ==========================================================

def get_api_url() -> str:
    """
    Return backend URL.
    """

    return BASE_URL
