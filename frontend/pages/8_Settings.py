import streamlit as st

from utils.api_client import (
    get_user_settings,
    update_user_settings,
    change_password,
    check_backend,
)

from utils.session import (
    initialize_session,
    is_logged_in,
)


# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="Settings",
    page_icon="⚙️",
    layout="wide",
)


# ==========================================================
# Initialize Session
# ==========================================================

initialize_session()


# ==========================================================
# Authentication
# ==========================================================

if not is_logged_in():

    st.error(
        "🔐 Please login first."
    )

    st.stop()


# ==========================================================
# Header
# ==========================================================

st.title(
    "⚙️ Settings"
)

st.write(
    """
    Manage your account profile and security settings.
    """
)

st.divider()


# ==========================================================
# Load Settings
# ==========================================================

with st.spinner(
    "Loading account settings..."
):

    settings = get_user_settings()


if not isinstance(
    settings,
    dict,
):

    settings = {}


# ==========================================================
# Profile
# ==========================================================

st.subheader(
    "👤 Profile"
)


with st.form(
    "profile_form"
):

    username = st.text_input(
        "Username",
        value=str(
            settings.get(
                "username",
                st.session_state.get(
                    "username",
                    "",
                ),
            )
        ),
    )


    email = st.text_input(
        "Email",
        value=str(
            settings.get(
                "email",
                "",
            )
        ),
    )


    full_name = st.text_input(
        "Full Name",
        value=str(
            settings.get(
                "full_name",
                "",
            )
        ),
    )


    submitted = st.form_submit_button(
        "💾 Save Profile",
        width="stretch",
    )


    if submitted:

        if not username.strip():

            st.error(
                "Username cannot be empty."
            )

        else:

            response = update_user_settings(
                {
                    "username": username.strip(),
                    "email": email.strip(),
                    "full_name": full_name.strip(),
                }
            )


            if response:

                # Keep local session synchronized.
                st.session_state.username = (
                    username.strip()
                )

                st.success(
                    "Profile updated successfully."
                )

            else:

                st.error(
                    "Unable to update profile."
                )


st.divider()


# ==========================================================
# Security
# ==========================================================

st.subheader(
    "🔐 Change Password"
)


with st.form(
    "password_form"
):

    current_password = st.text_input(
        "Current Password",
        type="password",
    )


    new_password = st.text_input(
        "New Password",
        type="password",
    )


    confirm_password = st.text_input(
        "Confirm New Password",
        type="password",
    )


    password_submit = st.form_submit_button(
        "🔑 Update Password",
        width="stretch",
    )


    if password_submit:

        if not current_password:

            st.error(
                "Please enter your current password."
            )

        elif not new_password:

            st.error(
                "Please enter a new password."
            )

        elif len(new_password) < 8:

            st.error(
                "New password must contain at least "
                "8 characters."
            )

        elif new_password != confirm_password:

            st.error(
                "Passwords do not match."
            )

        elif new_password == current_password:

            st.error(
                "New password must be different "
                "from the current password."
            )

        else:

            with st.spinner(
                "Updating password..."
            ):

                success = change_password(
                    current_password,
                    new_password,
                )


            if success:

                st.success(
                    "Password updated successfully."
                )

                st.info(
                    "Your new password is now active."
                )

            else:

                st.error(
                    "Unable to change password. "
                    "Please verify your current password."
                )


st.divider()


# ==========================================================
# Backend Information
# ==========================================================

st.subheader(
    "🖥️ Backend"
)


api_url = settings.get(
    "api_url",
    "",
)


if not api_url:

    api_url = (
        "https://parkinson-disease-detection-"
        "wced.onrender.com"
    )


st.code(
    api_url,
    language=None,
)


try:

    backend_status = check_backend()

except Exception:

    backend_status = False


if backend_status:

    st.success(
        "🟢 Backend Status: Connected"
    )

else:

    st.error(
        "🔴 Backend Status: Unavailable"
    )


st.divider()


# ==========================================================
# Account Information
# ==========================================================

st.subheader(
    "👤 Account Information"
)


account_col1, account_col2 = (
    st.columns(2)
)


with account_col1:

    st.write(
        f"**Username:** "
        f"{settings.get('username', 'N/A')}"
    )

    st.write(
        f"**Full Name:** "
        f"{settings.get('full_name', 'N/A')}"
    )


with account_col2:

    st.write(
        f"**Email:** "
        f"{settings.get('email', 'N/A')}"
    )

    st.write(
        f"**Role:** "
        f"{settings.get('role', st.session_state.get('role', 'N/A'))}"
    )


st.divider()


# ==========================================================
# About
# ==========================================================

st.subheader(
    "ℹ️ About"
)


st.markdown(
    """
    **Parkinson Disease Detection Agent**

    **Version:** 1.0.0

    **Frontend**
    - Streamlit

    **Backend**
    - FastAPI

    **Machine Learning**
    - Scikit-learn

    **Database**
    - SQLite / PostgreSQL

    Developed for AI-assisted Parkinson's disease
    prediction, patient management, analytics,
    reporting, and health education.
    """
)


st.divider()


# ==========================================================
# Medical Disclaimer
# ==========================================================

st.warning(
    """
    ⚠️ **Medical Disclaimer**

    This application provides AI-assisted screening
    and educational information. It is not a substitute
    for professional medical diagnosis or treatment.
    """
)


st.divider()


# ==========================================================
# Footer
# ==========================================================

st.caption(
    "© 2026 Parkinson Disease Detection Agent"
)
