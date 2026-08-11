import requests


# ==========================================================
# Backend Configuration
# ==========================================================

API_BASE_URL = (
    "https://parkinson-disease-detection-wced.onrender.com"
)


# ==========================================================
# Generic GET
# ==========================================================

def _get(
    endpoint: str,
    timeout: int = 30,
):
    """
    Perform a GET request.
    """

    try:
        response = requests.get(
            f"{API_BASE_URL}{endpoint}",
            timeout=timeout,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:

        print(
            f"GET {endpoint} error: {e}"
        )

        return None


# ==========================================================
# Generic POST
# ==========================================================

def _post(
    endpoint: str,
    data=None,
    token: str = None,
    timeout: int = 60,
):
    """
    Perform a POST request.
    """

    try:

        headers = {}

        if token:
            headers["Authorization"] = (
                f"Bearer {token}"
            )

        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            json=data,
            headers=headers,
            timeout=timeout,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:

        print(
            f"POST {endpoint} error: {e}"
        )

        return None


# ==========================================================
# Generic PUT
# ==========================================================

def _put(
    endpoint: str,
    data=None,
    token: str = None,
    timeout: int = 30,
):
    """
    Perform a PUT request.
    """

    try:

        headers = {}

        if token:
            headers["Authorization"] = (
                f"Bearer {token}"
            )

        response = requests.put(
            f"{API_BASE_URL}{endpoint}",
            json=data,
            headers=headers,
            timeout=timeout,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:

        print(
            f"PUT {endpoint} error: {e}"
        )

        return None


# ==========================================================
# Generic DELETE
# ==========================================================

def _delete(
    endpoint: str,
    token: str = None,
    timeout: int = 30,
):
    """
    Perform a DELETE request.
    """

    try:

        headers = {}

        if token:
            headers["Authorization"] = (
                f"Bearer {token}"
            )

        response = requests.delete(
            f"{API_BASE_URL}{endpoint}",
            headers=headers,
            timeout=timeout,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:

        print(
            f"DELETE {endpoint} error: {e}"
        )

        return None


# ==========================================================
# Authentication
# ==========================================================

def login_user(
    username: str,
    password: str,
):
    """
    Login user.
    """

    return _post(
        "/auth/login",
        {
            "username": username,
            "password": password,
        },
        timeout=30,
    )


def get_current_user(
    token: str,
):
    """
    Get authenticated user.
    """

    return _get_authenticated(
        "/auth/me",
        token,
    )


def logout_user(
    token: str,
):
    """
    Logout user.
    """

    return _post_authenticated(
        "/auth/logout",
        {},
        token,
    )


# ==========================================================
# Authenticated GET
# ==========================================================

def _get_authenticated(
    endpoint: str,
    token: str,
    timeout: int = 30,
):
    """
    Perform authenticated GET request.
    """

    try:

        headers = {
            "Authorization":
                f"Bearer {token}"
        }

        response = requests.get(
            f"{API_BASE_URL}{endpoint}",
            headers=headers,
            timeout=timeout,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:

        print(
            f"Authenticated GET error: {e}"
        )

        return None


# ==========================================================
# Authenticated POST
# ==========================================================

def _post_authenticated(
    endpoint: str,
    data=None,
    token: str = None,
    timeout: int = 30,
):
    """
    Perform authenticated POST request.
    """

    return _post(
        endpoint,
        data,
        token=token,
        timeout=timeout,
    )


# ==========================================================
# Prediction
# ==========================================================

def predict(
    data,
):
    """
    Send prediction request.
    """

    return _post(
        "/prediction/predict",
        data,
        timeout=60,
    )


def predict_patient(
    data,
):
    """
    Compatibility function used by the Prediction page.
    """

    return predict(
        data
    )


def get_prediction(
    prediction_id: int,
):
    """
    Get one prediction.
    """

    return _get(
        f"/prediction/{prediction_id}"
    )


def get_prediction_history(
    patient_id: int = 1,
):
    """
    Get prediction history.

    Supports list or dictionary responses.
    """

    # Primary endpoint
    data = _get(
        f"/prediction/history/{patient_id}"
    )

    if data is None:

        # Compatibility fallback
        data = _get(
            "/prediction/history"
        )

    if data is None:
        return None

    if isinstance(
        data,
        list,
    ):
        return data

    if isinstance(
        data,
        dict,
    ):

        if "history" in data:
            return data["history"]

        if "predictions" in data:
            return data["predictions"]

        if "records" in data:
            return data["records"]

        return []

    return []


def get_prediction_statistics():
    """
    Get prediction statistics.
    """

    return _get(
        "/prediction/statistics"
    )


def get_model_info():
    """
    Get ML model information.
    """

    return _get(
        "/prediction/model-info"
    )


def delete_prediction(
    prediction_id: int,
):
    """
    Delete prediction.
    """

    return _delete(
        f"/prediction/{prediction_id}"
    )


# ==========================================================
# Patients
# ==========================================================

def get_patients():
    """
    Get all patients.
    """

    return _get(
        "/patients"
    )


def get_patient(
    patient_id: int,
):
    """
    Get one patient.
    """

    return _get(
        f"/patients/{patient_id}"
    )


def create_patient(
    data,
):
    """
    Create patient.
    """

    return _post(
        "/patients",
        data,
    )


def update_patient(
    patient_id: int,
    data,
):
    """
    Update patient.
    """

    return _put(
        f"/patients/{patient_id}",
        data,
    )


def delete_patient(
    patient_id: int,
):
    """
    Delete patient.
    """

    return _delete(
        f"/patients/{patient_id}"
    )


# ==========================================================
# Reports
# ==========================================================

def get_reports():
    """
    Get all patient reports.
    """

    data = _get(
        "/reports"
    )

    if data is None:
        return None

    if isinstance(
        data,
        list,
    ):
        return data

    if isinstance(
        data,
        dict,
    ):

        return data.get(
            "reports",
            [],
        )

    return []


def get_report(
    report_id: int,
):
    """
    Get one report.
    """

    return _get(
        f"/reports/{report_id}"
    )


def download_report(
    report_id: int,
):
    """
    Get report download information.
    """

    return _get(
        f"/reports/{report_id}/download"
    )


def delete_report(
    report_id: int,
):
    """
    Delete report.
    """

    return _delete(
        f"/reports/{report_id}"
    )


# ==========================================================
# Analytics
# ==========================================================

def get_analytics():
    """
    Get analytics dashboard.
    """

    return _get(
        "/analytics"
    )


def get_analytics_summary():
    """
    Get analytics summary.
    """

    return _get(
        "/analytics/summary"
    )


# ==========================================================
# Recommendations
# ==========================================================

def get_recommendations():
    """
    Get recommendations.
    """

    return _get(
        "/recommendations"
    )


def get_patient_recommendations(
    patient_id: int,
):
    """
    Get recommendations for a patient.
    """

    return _get(
        f"/recommendations/patient/{patient_id}"
    )


# ==========================================================
# AI Assistant
# ==========================================================

def ask_ai_assistant(
    question: str,
):
    """
    Ask the AI Assistant.
    """

    return _post(
        "/chatbot/",
        {
            "message": question,
        },
        timeout=60,
    )


# ==========================================================
# Admin Dashboard
# ==========================================================

def get_admin_dashboard():
    """
    Get administrator dashboard.
    """

    return _get(
        "/admin/dashboard"
    )


def get_users():
    """
    Get users through administrator endpoint.

    Backend:
        GET /admin/users
    """

    return _get(
        "/admin/users"
    )


def get_admin_patients():
    """
    Get patients through administrator endpoint.
    """

    return _get(
        "/admin/patients"
    )


def delete_user(
    user_id: int,
):
    """
    Delete user through administrator endpoint.
    """

    return _delete(
        f"/admin/users/{user_id}"
    )


def delete_admin_patient(
    patient_id: int,
):
    """
    Delete patient through administrator endpoint.
    """

    return _delete(
        f"/admin/patients/{patient_id}"
    )


# ==========================================================
# User Settings
# ==========================================================

def get_user_settings():
    """
    Get current user's settings.

    No Streamlit UI is created here.
    """

    try:

        import streamlit as st

        token = st.session_state.get(
            "access_token"
        )

        username = st.session_state.get(
            "username",
            "",
        )

        role = st.session_state.get(
            "role",
            "user",
        )

        email = st.session_state.get(
            "email",
            "",
        )

        full_name = st.session_state.get(
            "full_name",
            "",
        )

        result = None

        if token:

            result = _get_authenticated(
                "/auth/me",
                token,
            )

        if isinstance(
            result,
            dict,
        ):

            username = result.get(
                "username",
                username,
            )

            email = result.get(
                "email",
                email,
            )

            full_name = result.get(
                "full_name",
                full_name,
            )

            role = result.get(
                "role",
                role,
            )

        return {
            "username":
                username,

            "email":
                email,

            "full_name":
                full_name,

            "role":
                role,

            "api_url":
                API_BASE_URL,
        }

    except Exception as e:

        print(
            f"Get user settings error: {e}"
        )

        return None


def update_user_settings(
    data,
):
    """
    Update frontend session profile information.

    The current backend does not expose a dedicated
    profile update endpoint, so this updates the current
    Streamlit session only.
    """

    try:

        import streamlit as st

        if "username" in data:

            st.session_state[
                "username"
            ] = data["username"]

        if "email" in data:

            st.session_state[
                "email"
            ] = data["email"]

        if "full_name" in data:

            st.session_state[
                "full_name"
            ] = data["full_name"]

        return {
            "status":
                "success",

            "message":
                "Profile updated successfully.",
        }

    except Exception as e:

        print(
            f"Update settings error: {e}"
        )

        return None


def change_password(
    current_password: str,
    new_password: str,
):
    """
    Change the authenticated user's password.
    """

    try:

        import streamlit as st

        token = st.session_state.get(
            "access_token"
        )

        if not token:

            return False

        if not current_password:
            return False

        if not new_password:
            return False

        if len(
            new_password.encode(
                "utf-8"
            )
        ) > 72:

            return False

        response = requests.post(
            f"{API_BASE_URL}/auth/change-password",

            json={
                "old_password":
                    current_password,

                "new_password":
                    new_password,
            },

            headers={
                "Authorization":
                    f"Bearer {token}"
            },

            timeout=30,
        )

        response.raise_for_status()

        return True

    except requests.RequestException as e:

        print(
            f"Change password error: {e}"
        )

        return False


# ==========================================================
# Backend Health
# ==========================================================

def health_check():
    """
    Check backend health.
    """

    return _get(
        "/health"
    )
