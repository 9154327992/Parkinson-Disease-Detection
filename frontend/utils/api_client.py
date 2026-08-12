import requests


API_BASE_URL = (
    "https://parkinson-disease-detection-wced.onrender.com"
)


# ==========================================================
# Generic GET
# ==========================================================

def _get(endpoint: str, timeout: int = 60):
    try:
        response = requests.get(
            f"{API_BASE_URL}{endpoint}",
            timeout=timeout,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:
        print(f"GET {endpoint} failed: {e}")
        return None


# ==========================================================
# Generic POST
# ==========================================================

def _post(
    endpoint: str,
    data=None,
    timeout: int = 60,
):
    try:
        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            json=data,
            timeout=timeout,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:
        print(f"POST {endpoint} failed: {e}")
        return None


# ==========================================================
# Prediction
# ==========================================================

def predict_patient(
    *args,
    **kwargs,
):
    """
    Supports the current Prediction page:

        predict_patient(values)

    and the full form:

        predict_patient(
            patient_name,
            patient_age,
            patient_gender,
            values
        )
    """

    patient_name = "Patient"
    patient_age = 30
    patient_gender = "Other"
    features = None

    # ------------------------------------------------------
    # Current page
    # predict_patient(values)
    # ------------------------------------------------------

    if len(args) == 1:

        features = args[0]

    # ------------------------------------------------------
    # Full patient information
    # ------------------------------------------------------

    elif len(args) >= 4:

        patient_name = args[0]
        patient_age = args[1]
        patient_gender = args[2]
        features = args[3]

    elif len(args) == 2:

        patient_name = args[0]
        features = args[1]

    elif len(args) == 3:

        patient_name = args[0]
        patient_age = args[1]
        features = args[2]

    # ------------------------------------------------------
    # Keyword arguments
    # ------------------------------------------------------

    if "patient_name" in kwargs:
        patient_name = kwargs["patient_name"]

    if "patient_age" in kwargs:
        patient_age = kwargs["patient_age"]

    if "patient_gender" in kwargs:
        patient_gender = kwargs["patient_gender"]

    if "features" in kwargs:
        features = kwargs["features"]

    if features is None:
        return None

    try:
        features = [
            float(value)
            for value in features
        ]
    except (TypeError, ValueError):
        return None

    if len(features) != 22:
        print(
            f"Expected 22 features, got {len(features)}"
        )
        return None

    payload = {
        "patient_name": str(patient_name),
        "age": int(patient_age),
        "gender": str(patient_gender),
        "features": features,
    }

    result = _post(
        "/prediction/predict",
        payload,
    )

    if isinstance(result, dict):

        # Backend uses "prediction".
        # Frontend Prediction page uses "diagnosis".
        if "diagnosis" not in result:
            result["diagnosis"] = result.get(
                "prediction",
                "Unknown",
            )

    return result


# ==========================================================
# Prediction History
# ==========================================================

def get_prediction_history(
    patient_id: int = 1,
):
    data = _get(
        f"/prediction/history/{patient_id}"
    )

    if data is None:
        data = _get(
            "/prediction/history"
        )

    if data is None:
        return None

    if isinstance(data, list):
        return data

    if isinstance(data, dict):

        return (
            data.get("history")
            or data.get("predictions")
            or data.get("records")
            or []
        )

    return []


# ==========================================================
# Reports
# ==========================================================

def get_reports():
    """
    Get report list.

    Backend response currently has:

    {
        "total_reports": ...,
        "reports": [...]
    }
    """

    data = _get(
        "/reports"
    )

    if data is None:
        return None

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        return data.get(
            "reports",
            [],
        )

    return []


def download_report(
    report_id: int,
):
    """
    Download a report.

    Returns raw PDF bytes when the backend provides
    a PDF response.
    """

    try:

        response = requests.get(
            f"{API_BASE_URL}/reports/{report_id}/download",
            timeout=60,
        )

        response.raise_for_status()

        content_type = response.headers.get(
            "content-type",
            "",
        ).lower()

        if "application/pdf" in content_type:
            return response.content

        # Compatibility with JSON download responses
        try:
            return response.json()
        except ValueError:
            return response.content

    except requests.RequestException as e:

        print(
            f"Download report failed: {e}"
        )

        return None


# ==========================================================
# Admin
# ==========================================================

def get_admin_dashboard():
    return _get(
        "/admin/dashboard"
    )


def get_users():
    return _get(
        "/admin/users"
    )


def get_patients():
    return _get(
        "/patients"
    )


def delete_user(
    user_id: int,
):
    try:

        response = requests.delete(
            f"{API_BASE_URL}/admin/users/{user_id}",
            timeout=30,
        )

        response.raise_for_status()

        return True

    except requests.RequestException as e:

        print(
            f"Delete user failed: {e}"
        )

        return False


def delete_patient(
    patient_id: int,
):
    try:

        response = requests.delete(
            f"{API_BASE_URL}/admin/patients/{patient_id}",
            timeout=30,
        )

        response.raise_for_status()

        return True

    except requests.RequestException as e:

        print(
            f"Delete patient failed: {e}"
        )

        return False


# ==========================================================
# User Settings
# ==========================================================

def get_user_settings():

    try:

        import streamlit as st

        return {
            "username":
                st.session_state.get(
                    "username",
                    "",
                ),

            "email":
                st.session_state.get(
                    "email",
                    "",
                ),

            "full_name":
                st.session_state.get(
                    "full_name",
                    "",
                ),

            "role":
                st.session_state.get(
                    "role",
                    "user",
                ),

            "api_url":
                API_BASE_URL,
        }

    except Exception as e:

        print(
            f"Settings error: {e}"
        )

        return None


def update_user_settings(
    data,
):

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

        return True

    except Exception as e:

        print(
            f"Update settings failed: {e}"
        )

        return False


def change_password(
    current_password: str,
    new_password: str,
):

    try:

        import streamlit as st

        token = st.session_state.get(
            "access_token"
        )

        if not token:
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
            f"Change password failed: {e}"
        )

        return False


# ==========================================================
# Health
# ==========================================================

def health_check():

    return _get(
        "/health"
    )
