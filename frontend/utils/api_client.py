import requests


# ==========================================================
# Backend Configuration
# ==========================================================

API_BASE_URL = (
    "https://parkinson-disease-detection-wced.onrender.com"
)


# ==========================================================
# Generic GET Helper
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
# Generic POST Helper
# ==========================================================

def _post(
    endpoint: str,
    data=None,
    timeout: int = 60,
):
    """
    Perform a POST request.
    """

    try:

        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            json=data,
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
# Generic DELETE Helper
# ==========================================================

def _delete(
    endpoint: str,
    timeout: int = 30,
):
    """
    Perform a DELETE request.
    """

    try:

        response = requests.delete(
            f"{API_BASE_URL}{endpoint}",
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
    Get authenticated user information.
    """

    try:

        response = requests.get(
            f"{API_BASE_URL}/auth/me",
            headers={
                "Authorization":
                    f"Bearer {token}"
            },
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:

        print(
            f"Get current user error: {e}"
        )

        return None


def logout_user(
    token: str,
):
    """
    Logout user.
    """

    try:

        response = requests.post(
            f"{API_BASE_URL}/auth/logout",
            headers={
                "Authorization":
                    f"Bearer {token}"
            },
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:

        print(
            f"Logout error: {e}"
        )

        return None


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
    """

    return _get(
        f"/prediction/history/{patient_id}"
    )


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

    try:

        response = requests.put(
            f"{API_BASE_URL}/patients/{patient_id}",
            json=data,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:

        print(
            f"Update patient error: {e}"
        )

        return None


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
    Get all reports.
    """

    data = _get(
        "/reports"
    )

    if data is None:
        return None

    # ReportList response:
    #
    # {
    #     "total_reports": 1,
    #     "reports": [...]
    # }

    if isinstance(
        data,
        dict,
    ):

        return data.get(
            "reports",
            [],
        )

    return data


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
    Get analytics dashboard data.
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
    Ask the Parkinson Disease AI Assistant.
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
    Get administrator dashboard statistics.

    Backend endpoint:
        GET /admin/dashboard
    """

    return _get(
        "/admin/dashboard"
    )


def get_users():
    """
    Get all users for the administrator.

    IMPORTANT:
    The admin router is registered with the
    /admin prefix, therefore the correct endpoint is:

        GET /admin/users
    """

    return _get(
        "/admin/users"
    )


def get_admin_patients():
    """
    Get all patients through the admin endpoint.

    Backend endpoint:
        GET /admin/patients
    """

    return _get(
        "/admin/patients"
    )


# ==========================================================
# Admin Delete User
# ==========================================================

def delete_user(
    user_id: int,
):
    """
    Delete a user.

    Uses the admin endpoint.
    """

    return _delete(
        f"/admin/users/{user_id}"
    )


# ==========================================================
# Admin Delete Patient
# ==========================================================

def delete_admin_patient(
    patient_id: int,
):
    """
    Delete a patient through the admin endpoint.
    """

    return _delete(
        f"/admin/patients/{patient_id}"
    )


# ==========================================================
# Compatibility
# ==========================================================

def health_check():
    """
    Check backend health.
    """

    return _get(
        "/health"
    )

import streamlit as st

# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="Settings",
    page_icon="⚙️",
    layout="wide"
)

# ==========================================================
# Header
# ==========================================================

st.title("⚙️ Settings")

st.write("""
Manage your account, application preferences, and security settings.
""")

st.divider()

# ==========================================================
# Load User Settings
# ==========================================================

settings = get_user_settings()

if settings is None:
    st.error("Unable to load user settings.")
    st.stop()

# ==========================================================
# Profile Settings
# ==========================================================

st.subheader("👤 Profile")

with st.form("profile_form"):

    username = st.text_input(
        "Username",
        value=settings.get("username", "")
    )

    email = st.text_input(
        "Email",
        value=settings.get("email", "")
    )

    full_name = st.text_input(
        "Full Name",
        value=settings.get("full_name", "")
    )

    submitted = st.form_submit_button("💾 Save Profile")

    if submitted:

        response = update_user_settings({
            "username": username,
            "email": email,
            "full_name": full_name
        })

        if response:
            st.success("Profile updated successfully.")
        else:
            st.error("Unable to update profile.")

st.divider()

# ==========================================================
# Appearance
# ==========================================================

st.subheader("🎨 Appearance")

theme = st.selectbox(
    "Theme",
    ["Light", "Dark"],
    index=0 if settings.get("theme", "Light") == "Light" else 1
)

language = st.selectbox(
    "Language",
    [
        "English",
        "Hindi"
    ]
)

if st.button("Save Appearance"):

    response = update_user_settings({
        "theme": theme,
        "language": language
    })

    if response:
        st.success("Appearance updated.")
    else:
        st.error("Unable to save settings.")

st.divider()

# ==========================================================
# Security
# ==========================================================

st.subheader("🔐 Change Password")

with st.form("password_form"):

    current_password = st.text_input(
        "Current Password",
        type="password"
    )

    new_password = st.text_input(
        "New Password",
        type="password"
    )

    confirm_password = st.text_input(
        "Confirm Password",
        type="password"
    )

    password_submit = st.form_submit_button(
        "Update Password"
    )

    if password_submit:

        if new_password != confirm_password:

            st.error("Passwords do not match.")

        else:

            success = change_password(
                current_password,
                new_password
            )

            if success:
                st.success("Password updated successfully.")
            else:
                st.error("Unable to change password.")

st.divider()

# ==========================================================
# Backend Information
# ==========================================================

st.subheader("🖥️ Backend")

st.info(f"API URL: {settings.get('api_url', 'http://127.0.0.1:8000')}")

st.success("Backend Status: Connected")

st.divider()

# ==========================================================
# About
# ==========================================================

st.subheader("ℹ️ About")

st.markdown("""
**Parkinson Disease Detection Agent**

Version: **1.0.0**

**Frontend**
- Streamlit

**Backend**
- FastAPI

**Machine Learning**
- Scikit-learn

**Database**
- SQLite / PostgreSQL

Developed for AI-assisted Parkinson's disease prediction, patient management, analytics, and reporting.
""")

st.divider()

# ==========================================================
# Footer
# ==========================================================

st.caption("© 2026 Parkinson Disease Detection Agent")
