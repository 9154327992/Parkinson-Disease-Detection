import streamlit as st

from utils.api_client import (
    get_user_settings,
    update_user_settings,
    change_password
)

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
