import requests


# ==========================================================
# API Configuration
# ==========================================================

API_BASE_URL = (
    "https://parkinson-disease-detection-wced.onrender.com"
)


DEFAULT_TIMEOUT = 60


# ==========================================================
# Streamlit Session Helpers
# ==========================================================

def _get_session_state():
    """
    Safely return Streamlit session state.
    """

    try:
        import streamlit as st

        return st.session_state

    except Exception:
        return None


def _get_token():
    """
    Get JWT access token from Streamlit session.
    """

    session = _get_session_state()

    if session is None:
        return None

    return (
        session.get("token")
        or session.get("access_token")
    )


# ==========================================================
# HTTP Headers
# ==========================================================

def _headers():
    """
    Build common HTTP headers.
    """

    headers = {
        "Accept": "application/json",
    }

    token = _get_token()

    if token:
        headers[
            "Authorization"
        ] = f"Bearer {token}"

    return headers


# ==========================================================
# URL Helper
# ==========================================================

def _url(endpoint: str) -> str:
    """
    Build complete backend URL.
    """

    if not endpoint.startswith("/"):
        endpoint = "/" + endpoint

    return (
        API_BASE_URL.rstrip("/")
        + endpoint
    )


# ==========================================================
# Generic GET
# ==========================================================

def get(
    endpoint: str,
    params=None,
    timeout: int = DEFAULT_TIMEOUT,
):
    """
    Generic GET request.

    Example:
        get("/reports")
    """

    try:

        response = requests.get(
            _url(endpoint),
            params=params,
            headers=_headers(),
            timeout=timeout,
        )

        response.raise_for_status()

        content_type = (
            response.headers
            .get(
                "content-type",
                "",
            )
            .lower()
        )

        if (
            "application/json"
            in content_type
        ):

            return response.json()

        return response.content

    except requests.RequestException as e:

        print(
            f"GET {endpoint} failed: {e}"
        )

        return None


# ==========================================================
# Generic POST
# ==========================================================

def post(
    endpoint: str,
    data=None,
    timeout: int = DEFAULT_TIMEOUT,
    form_data=None,
):
    """
    Generic POST request.

    JSON:
        post("/endpoint", {"key": "value"})

    Form:
        post(
            "/auth/login",
            form_data={
                "username": "...",
                "password": "..."
            }
        )
    """

    try:

        kwargs = {
            "headers": _headers(),
            "timeout": timeout,
        }

        if form_data is not None:

            kwargs["data"] = form_data

        else:

            kwargs["json"] = data

        response = requests.post(
            _url(endpoint),
            **kwargs,
        )

        response.raise_for_status()

        content_type = (
            response.headers
            .get(
                "content-type",
                "",
            )
            .lower()
        )

        if (
            "application/json"
            in content_type
        ):

            return response.json()

        if not response.content:

            return True

        return response.content

    except requests.RequestException as e:

        print(
            f"POST {endpoint} failed: {e}"
        )

        return None


# ==========================================================
# Generic PUT
# ==========================================================

def put(
    endpoint: str,
    data=None,
    timeout: int = DEFAULT_TIMEOUT,
):
    """
    Generic PUT request.
    """

    try:

        response = requests.put(
            _url(endpoint),
            json=data,
            headers=_headers(),
            timeout=timeout,
        )

        response.raise_for_status()

        content_type = (
            response.headers
            .get(
                "content-type",
                "",
            )
            .lower()
        )

        if (
            "application/json"
            in content_type
        ):

            return response.json()

        if not response.content:

            return True

        return response.content

    except requests.RequestException as e:

        print(
            f"PUT {endpoint} failed: {e}"
        )

        return None


# ==========================================================
# Generic DELETE
# ==========================================================

def delete(
    endpoint: str,
    timeout: int = DEFAULT_TIMEOUT,
):
    """
    Generic DELETE request.
    """

    try:

        response = requests.delete(
            _url(endpoint),
            headers=_headers(),
            timeout=timeout,
        )

        response.raise_for_status()

        if not response.content:

            return True

        content_type = (
            response.headers
            .get(
                "content-type",
                "",
            )
            .lower()
        )

        if (
            "application/json"
            in content_type
        ):

            return response.json()

        return True

    except requests.RequestException as e:

        print(
            f"DELETE {endpoint} failed: {e}"
        )

        return None


# ==========================================================
# Compatibility HTTP Helpers
# ==========================================================

def _get(
    endpoint: str,
    params=None,
    timeout: int = DEFAULT_TIMEOUT,
):
    return get(
        endpoint,
        params=params,
        timeout=timeout,
    )


def _post(
    endpoint: str,
    data=None,
    timeout: int = DEFAULT_TIMEOUT,
):
    return post(
        endpoint,
        data=data,
        timeout=timeout,
    )


def _put(
    endpoint: str,
    data=None,
    timeout: int = DEFAULT_TIMEOUT,
):
    return put(
        endpoint,
        data=data,
        timeout=timeout,
    )


def _delete(
    endpoint: str,
    timeout: int = DEFAULT_TIMEOUT,
):
    return delete(
        endpoint,
        timeout=timeout,
    )


# ==========================================================
# Authentication
# ==========================================================

def login_user(
    username: str,
    password: str,
):
    """
    Login user.

    FastAPI authentication commonly expects
    application/x-www-form-urlencoded data.
    """

    try:

        response = requests.post(
            _url("/auth/login"),
            json={
                "username": username,
                "password": password,
            },
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:

        print(
            f"Login failed: {e}"
        )

        return None


def login(
    username: str,
    password: str,
):
    """
    Compatibility alias.
    """

    return login_user(
        username,
        password,
    )


def get_current_user():
    """
    Get currently authenticated user.
    """

    return get(
        "/auth/me"
    )


def logout_user():
    """
    Clear local authentication session.
    """

    session = _get_session_state()

    if session is None:

        return True

    keys = [
        "access_token",
        "token",
        "username",
        "email",
        "full_name",
        "role",
        "user",
        "user_id",
    ]

    for key in keys:

        try:
            session.pop(
                key,
                None,
            )

        except Exception:
            pass

    return True


# ==========================================================
# Prediction
# ==========================================================

def predict_patient(
    patient_name,
    age,
    gender,
    features,
):
    """
    Run Parkinson prediction.

    Expected:
        patient_name
        age
        gender
        22 voice features
    """

    if features is None:

        print(
            "Prediction failed: "
            "features are missing."
        )

        return None

    try:

        features = [
            float(value)
            for value in features
        ]

    except (
        TypeError,
        ValueError,
    ):

        print(
            "Prediction failed: "
            "invalid feature values."
        )

        return None


    if len(features) != 22:

        print(
            "Prediction failed: "
            f"expected 22 features, "
            f"received {len(features)}."
        )

        return None


    payload = {
        "patient_name": str(
            patient_name
        ),
        "age": int(age),
        "gender": str(
            gender
        ),
        "features": features,
    }


    result = post(
        "/prediction/predict",
        data=payload,
        timeout=60,
    )


    if isinstance(
        result,
        dict,
    ):

        # --------------------------------------------------
        # Normalize backend response
        # --------------------------------------------------

        if (
            "diagnosis"
            not in result
            and "prediction"
            in result
        ):

            result["diagnosis"] = (
                result["prediction"]
            )


        if (
            "prediction"
            not in result
            and "diagnosis"
            in result
        ):

            result["prediction"] = (
                result["diagnosis"]
            )


    return result


def predict(
    data,
):
    """
    Generic prediction compatibility helper.
    """

    return post(
        "/prediction/predict",
        data=data,
        timeout=60,
    )


# ==========================================================
# Prediction History
# ==========================================================

def get_patient_history():
    """
    Get prediction/patient history.

    Backend endpoint:
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
            result.get("history")
            or result.get("predictions")
            or result.get("patients")
            or result.get("records")
            or []
        )


    return []


def get_prediction_history():
    """
    Compatibility alias for prediction history.
    """

    return get_patient_history()


def get_prediction(
    prediction_id: int,
):
    """
    Get one prediction.
    """

    return get(
        f"/prediction/{prediction_id}"
    )


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
            result.get("patients")
            or result.get("data")
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
    data,
):
    """
    Create patient.
    """

    return post(
        "/patients",
        data=data,
    )


def update_patient(
    patient_id: int,
    data,
):
    """
    Update patient.
    """

    return put(
        f"/patients/{patient_id}",
        data=data,
    )


def delete_patient(
    patient_id: int,
):
    """
    Delete patient.
    """

    # Primary patient endpoint.
    result = delete(
        f"/patients/{patient_id}"
    )

    return result


# ==========================================================
# Reports
# ==========================================================

def get_reports():
    """
    Get all reports.

    Backend:
        GET /reports

    Backend response:
        {
            "total_reports": 1,
            "reports": [...]
        }
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

        return result.get(
            "reports",
            [],
        )


    return []


def get_report(
    report_id: int,
):
    """
    Get detailed report.
    """

    return get(
        f"/reports/{report_id}"
    )


def get_patient_reports(
    patient_id: int,
):
    """
    Get reports for one patient.
    """

    result = get(
        f"/reports/patient/{patient_id}"
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

        return result.get(
            "reports",
            [],
        )


    return []


def download_report(
    report_id: int,
):
    """
    Get report download information.

    IMPORTANT:
    The current backend returns metadata rather than
    actual PDF bytes. The backend report service currently
    returns filename/download_url/file_type/file_size.
    """

    return get(
        f"/reports/{report_id}/download"
    )


def delete_report(
    report_id: int,
):
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
    Get analytics dashboard data.
    """

    result = get(
        "/analytics"
    )


    if result is None:

        return None


    if isinstance(
        result,
        dict,
    ):

        return result


    return {}


def get_analytics_summary():
    """
    Compatibility analytics helper.
    """

    result = get(
        "/analytics/summary"
    )

    if result is None:

        return get_analytics()

    return result


# ==========================================================
# Recommendations
# ==========================================================

def get_recommendations():
    """
    Get recommendations.
    """

    result = get(
        "/recommendations"
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
            result.get("recommendations")
            or result.get("data")
            or []
        )


    return []


def get_patient_recommendations(
    patient_id: int,
):
    """
    Get recommendations for patient.
    """

    result = get(
        f"/recommendations/patient/{patient_id}"
    )


    if isinstance(
        result,
        dict,
    ):

        return (
            result.get("recommendations")
            or result
        )


    return result


# ==========================================================
# Medication
# ==========================================================

def get_medications():
    """
    Get medication information.
    """

    result = get(
        "/medication"
    )


    if isinstance(
        result,
        dict,
    ):

        return (
            result.get("medications")
            or result.get("data")
            or result
        )


    return result


def get_patient_medications(
    patient_id: int,
):
    """
    Get medication information for a patient.
    """

    result = get(
        f"/medication/patient/{patient_id}"
    )


    if isinstance(
        result,
        dict,
    ):

        return (
            result.get("medications")
            or result.get("data")
            or result
        )


    return result


# ==========================================================
# AI Assistant / Chatbot
# ==========================================================

def ask_ai_assistant(
    question: str,
):
    """
    Send question to AI assistant.
    """

    payload = {
        "message": question,
    }


    result = post(
        "/chatbot/",
        data=payload,
        timeout=60,
    )


    if isinstance(
        result,
        dict,
    ):

        # Normalize possible response keys.

        if "response" in result:
            return result["response"]

        if "message" in result:
            return result["message"]

        if "answer" in result:
            return result["answer"]


    return result


def ask_chatbot(
    question: str,
):
    """
    Compatibility alias.
    """

    return ask_ai_assistant(
        question
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
    Get all users for admin.
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
            or []
        )


    return []


def get_admin_patients():
    """
    Get all patients for admin.
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
            or []
        )


    return []


def delete_user(
    user_id: int,
):
    """
    Delete admin user.

    Uses admin endpoint.
    """

    return delete(
        f"/admin/users/{user_id}"
    )


def delete_admin_patient(
    patient_id: int,
):
    """
    Delete admin patient.
    """

    return delete(
        f"/admin/patients/{patient_id}"
    )


# ==========================================================
# User Settings
# ==========================================================

def get_user_settings():
    """
    Get current user information.

    Theme and language are intentionally NOT included.
    """

    session = _get_session_state()


    username = ""
    email = ""
    full_name = ""
    role = "user"


    if session is not None:

        username = session.get(
            "username",
            "",
        )

        email = session.get(
            "email",
            "",
        )

        full_name = session.get(
            "full_name",
            "",
        )

        role = session.get(
            "role",
            "user",
        )


    # ------------------------------------------------------
    # Try backend profile
    # ------------------------------------------------------

    backend_user = get_current_user()


    if isinstance(
        backend_user,
        dict,
    ):

        username = backend_user.get(
            "username",
            username,
        )

        email = backend_user.get(
            "email",
            email,
        )

        full_name = backend_user.get(
            "full_name",
            full_name,
        )

        role = backend_user.get(
            "role",
            role,
        )


    return {
        "username": username,
        "email": email,
        "full_name": full_name,
        "role": role,
        "api_url": API_BASE_URL,
    }


def update_user_settings(
    data,
):
    """
    Update user profile.

    The current backend may not expose a dedicated settings
    endpoint, so profile values are kept in the frontend
    session unless a supported backend endpoint is available.
    """

    if not isinstance(
        data,
        dict,
    ):

        return False


    session = _get_session_state()


    if session is None:

        return False


    # ------------------------------------------------------
    # Update local session
    # ------------------------------------------------------

    if "username" in data:

        session[
            "username"
        ] = data["username"]


    if "email" in data:

        session[
            "email"
        ] = data["email"]


    if "full_name" in data:

        session[
            "full_name"
        ] = data["full_name"]


    return True


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


    # bcrypt maximum password size
    if (
        len(
            new_password.encode(
                "utf-8"
            )
        )
        > 72
    ):

        return False


    # ------------------------------------------------------
    # Try expected endpoint
    # ------------------------------------------------------

    result = post(
        "/auth/change-password",
        data={
            "old_password":
                current_password,

            "new_password":
                new_password,
        },
        timeout=30,
    )


    return result is not None


# ==========================================================
# Model Information
# ==========================================================

def get_model_info():
    """
    Get ML model information.
    """

    return get(
        "/prediction/model-info"
    )


# ==========================================================
# Health
# ==========================================================

def health_check():
    """
    Check FastAPI backend health.
    """

    return get(
        "/health"
    )


def is_backend_available():
    """
    Return True when backend responds.
    """

    result = health_check()

    return (
        isinstance(
            result,
            dict,
        )
        and result.get(
            "status"
        ) in (
            "healthy",
            "success",
            "ok",
            "Online",
        )
    )


# ==========================================================
# Utility
# ==========================================================

def get_api_url():
    """
    Return configured backend URL.
    """

    return API_BASE_URL


# ==========================================================
# End of API Client
# ==========================================================
