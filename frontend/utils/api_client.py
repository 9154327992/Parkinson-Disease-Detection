import requests


# ==========================================================
# Configuration
# ==========================================================

API_BASE_URL = (
    "https://parkinson-disease-detection-wced.onrender.com"
)


# ==========================================================
# Session Token Helper
# ==========================================================

def _get_token():
    """
    Get JWT access token from Streamlit session.
    """

    try:
        import streamlit as st

        return st.session_state.get(
            "access_token"
        )

    except Exception:
        return None


# ==========================================================
# Headers
# ==========================================================

def _headers():
    """
    Build request headers.
    """

    headers = {
        "Accept": "application/json",
    }

    token = _get_token()

    if token:
        headers["Authorization"] = (
            f"Bearer {token}"
        )

    return headers


# ==========================================================
# GET
# ==========================================================

def get(
    endpoint,
    params=None,
    timeout=60,
):
    """
    Generic GET request.

    Example:
        get("/reports")
    """

    try:

        response = requests.get(
            f"{API_BASE_URL}{endpoint}",
            params=params,
            headers=_headers(),
            timeout=timeout,
        )

        response.raise_for_status()

        content_type = response.headers.get(
            "content-type",
            "",
        ).lower()

        if "application/json" in content_type:

            return response.json()

        return response.content

    except requests.RequestException as e:

        print(
            f"GET {endpoint} failed: {e}"
        )

        return None


# ==========================================================
# POST
# ==========================================================

def post(
    endpoint,
    data=None,
    timeout=60,
):
    """
    Generic POST request.
    """

    try:

        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            json=data,
            headers=_headers(),
            timeout=timeout,
        )

        response.raise_for_status()

        content_type = response.headers.get(
            "content-type",
            "",
        ).lower()

        if "application/json" in content_type:

            return response.json()

        return response.content

    except requests.RequestException as e:

        print(
            f"POST {endpoint} failed: {e}"
        )

        return None


# ==========================================================
# PUT
# ==========================================================

def put(
    endpoint,
    data=None,
    timeout=60,
):
    """
    Generic PUT request.
    """

    try:

        response = requests.put(
            f"{API_BASE_URL}{endpoint}",
            json=data,
            headers=_headers(),
            timeout=timeout,
        )

        response.raise_for_status()

        content_type = response.headers.get(
            "content-type",
            "",
        ).lower()

        if "application/json" in content_type:

            return response.json()

        return response.content

    except requests.RequestException as e:

        print(
            f"PUT {endpoint} failed: {e}"
        )

        return None


# ==========================================================
# DELETE
# ==========================================================

def delete(
    endpoint,
    timeout=60,
):
    """
    Generic DELETE request.
    """

    try:

        response = requests.delete(
            f"{API_BASE_URL}{endpoint}",
            headers=_headers(),
            timeout=timeout,
        )

        response.raise_for_status()

        if not response.content:
            return True

        content_type = response.headers.get(
            "content-type",
            "",
        ).lower()

        if "application/json" in content_type:

            return response.json()

        return True

    except requests.RequestException as e:

        print(
            f"DELETE {endpoint} failed: {e}"
        )

        return None


# ==========================================================
# Compatibility Helpers
# ==========================================================

def _get(
    endpoint,
    timeout=60,
):
    return get(
        endpoint,
        timeout=timeout,
    )


def _post(
    endpoint,
    data=None,
    timeout=60,
):
    return post(
        endpoint,
        data,
        timeout=timeout,
    )


def _put(
    endpoint,
    data=None,
    timeout=60,
):
    return put(
        endpoint,
        data,
        timeout=timeout,
    )


def _delete(
    endpoint,
    timeout=60,
):
    return delete(
        endpoint,
        timeout=timeout,
    )


# ==========================================================
# Authentication
# ==========================================================

def login_user(
    username,
    password,
):
    """
    Login through FastAPI.
    """

    return post(
        "/auth/login",
        {
            "username": username,
            "password": password,
        },
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
    Clear local login session.
    """

    try:

        import streamlit as st

        st.session_state.pop(
            "access_token",
            None,
        )

        st.session_state.pop(
            "username",
            None,
        )

        st.session_state.pop(
            "role",
            None,
        )

        st.session_state.pop(
            "email",
            None,
        )

        st.session_state.pop(
            "full_name",
            None,
        )

        return True

    except Exception:

        return False


# ==========================================================
# Prediction
# ==========================================================

def predict_patient(
    *args,
    **kwargs,
):
    """
    Send Parkinson prediction request.

    Supports:

        predict_patient(values)

    and:

        predict_patient(
            patient_name,
            age,
            gender,
            values
        )
    """

    patient_name = kwargs.get(
        "patient_name",
        "Patient",
    )

    age = kwargs.get(
        "age",
        kwargs.get(
            "patient_age",
            30,
        ),
    )

    gender = kwargs.get(
        "gender",
        kwargs.get(
            "patient_gender",
            "Other",
        ),
    )

    features = kwargs.get(
        "features"
    )

    # ------------------------------------------------------
    # Positional arguments
    # ------------------------------------------------------

    if len(args) == 1:

        features = args[0]

    elif len(args) >= 4:

        patient_name = args[0]
        age = args[1]
        gender = args[2]
        features = args[3]

    elif len(args) == 3:

        patient_name = args[0]
        age = args[1]
        features = args[2]

    elif len(args) == 2:

        patient_name = args[0]
        features = args[1]

    # ------------------------------------------------------
    # Validate features
    # ------------------------------------------------------

    if features is None:

        print(
            "Prediction failed: "
            "No feature values supplied."
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
            "Invalid feature values."
        )

        return None

    if len(features) != 22:

        print(
            "Prediction failed: "
            f"Expected 22 features, "
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
        payload,
        timeout=60,
    )

    if isinstance(
        result,
        dict,
    ):

        # Backend returns "prediction".
        # Frontend may use "diagnosis".
        if "diagnosis" not in result:

            result["diagnosis"] = result.get(
                "prediction",
                "Unknown",
            )

    return result


def predict(data):
    """
    Compatibility prediction function.
    """

    return post(
        "/prediction/predict",
        data,
        timeout=60,
    )


def get_prediction(
    prediction_id,
):
    return get(
        f"/prediction/{prediction_id}"
    )


def get_prediction_history(
    patient_id=1,
):
    """
    Get prediction history.
    """

    result = get(
        f"/prediction/history/{patient_id}"
    )

    if result is None:

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
            or result.get("records")
            or []
        )

    return []


def get_prediction_statistics():
    return get(
        "/prediction/statistics"
    )


def get_model_info():
    return get(
        "/prediction/model-info"
    )


def delete_prediction(
    prediction_id,
):
    return delete(
        f"/prediction/{prediction_id}"
    )


# ==========================================================
# Patients
# ==========================================================

def get_patients():
    return get(
        "/patients"
    )


def get_patient(
    patient_id,
):
    return get(
        f"/patients/{patient_id}"
    )


def create_patient(
    data,
):
    return post(
        "/patients",
        data,
    )


def update_patient(
    patient_id,
    data,
):
    return put(
        f"/patients/{patient_id}",
        data,
    )


def delete_patient(
    patient_id,
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

        return result.get(
            "reports",
            [],
        )

    return []


def get_report(
    report_id,
):
    return get(
        f"/reports/{report_id}"
    )


def download_report(
    report_id,
):
    """
    Download report PDF.

    If backend returns JSON, that JSON is returned.
    If backend returns PDF, raw PDF bytes are returned.
    """

    try:

        response = requests.get(
            f"{API_BASE_URL}/reports/"
            f"{report_id}/download",

            headers=_headers(),

            timeout=60,
        )

        response.raise_for_status()

        content_type = response.headers.get(
            "content-type",
            "",
        ).lower()

        if "application/pdf" in content_type:

            return response.content

        try:

            return response.json()

        except ValueError:

            return response.content

    except requests.RequestException as e:

        print(
            f"Report download failed: {e}"
        )

        return None


def delete_report(
    report_id,
):
    return delete(
        f"/reports/{report_id}"
    )


# ==========================================================
# Analytics
# ==========================================================

def get_analytics():
    return get(
        "/analytics"
    )


def get_analytics_summary():
    return get(
        "/analytics/summary"
    )


# ==========================================================
# Recommendations
# ==========================================================

def get_recommendations():
    return get(
        "/recommendations"
    )


def get_patient_recommendations(
    patient_id,
):
    return get(
        f"/recommendations/patient/"
        f"{patient_id}"
    )


# ==========================================================
# AI Assistant
# ==========================================================

def ask_ai_assistant(
    question,
):
    return post(
        "/chatbot/",
        {
            "message": question,
        },
        timeout=60,
    )


# ==========================================================
# Admin
# ==========================================================

def get_admin_dashboard():
    return get(
        "/admin/dashboard"
    )


def get_users():
    return get(
        "/admin/users"
    )


def get_admin_patients():
    return get(
        "/admin/patients"
    )


def delete_user(
    user_id,
):
    return delete(
        f"/admin/users/{user_id}"
    )


def delete_admin_patient(
    patient_id,
):
    return delete(
        f"/admin/patients/{patient_id}"
    )


# ==========================================================
# Settings
# ==========================================================

def get_user_settings():
    """
    Get current frontend user settings.

    Theme and language are intentionally omitted.
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

        email = st.session_state.get(
            "email",
            "",
        )

        full_name = st.session_state.get(
            "full_name",
            "",
        )

        role = st.session_state.get(
            "role",
            "user",
        )

        if token:

            result = get(
                "/auth/me"
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
            "username": username,
            "email": email,
            "full_name": full_name,
            "role": role,
            "api_url": API_BASE_URL,
        }

    except Exception as e:

        print(
            f"Settings load failed: {e}"
        )

        return None


def update_user_settings(
    data,
):
    """
    Update profile values locally.

    Theme/language are intentionally not handled.
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

        return True

    except Exception as e:

        print(
            f"Settings update failed: {e}"
        )

        return False


def change_password(
    current_password,
    new_password,
):
    """
    Change password using the authenticated API.
    """

    token = _get_token()

    if not token:
        return False

    if not current_password:
        return False

    if not new_password:
        return False

    # bcrypt limit
    if len(
        new_password.encode(
            "utf-8"
        )
    ) > 72:

        return False

    try:

        response = requests.post(
            f"{API_BASE_URL}/auth/"
            f"change-password",

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
            f"Password change failed: {e}"
        )

        return False


# ==========================================================
# Health
# ==========================================================

def health_check():
    return get(
        "/health"
    )
