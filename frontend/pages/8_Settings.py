import streamlit as st

from utils.api_client import (
    get_user_settings,
    update_user_settings,
    change_password,
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
Manage your account information and security settings.
"""
)

st.divider()


# ==========================================================
# Load Settings
# ==========================================================

with st.spinner(
    "Loading account information..."
):

    settings = get_user_settings()


# ==========================================================
# Validate Settings Response
# ==========================================================

if settings is None:

    st.error(
        "Unable to load your account information."
    )

    st.info(
        """
Please check your login session and make sure
the FastAPI backend is available.
"""
    )

    st.stop()


if not isinstance(
    settings,
    dict,
):

    st.error(
        "The backend returned an invalid account response."
    )

    st.stop()


# ==========================================================
# Support Nested User Response
# ==========================================================

user_data = settings.get(
    "user"
)

if isinstance(
    user_data,
    dict,
):

    account = user_data

else:

    account = settings


# ==========================================================
# Helper
# ==========================================================

def get_value(
    data,
    keys,
    default="",
):
    """
    Safely retrieve the first available value.
    """

    if not isinstance(
        data,
        dict,
    ):
        return default

    for key in keys:

        value = data.get(
            key
        )

        if value is not None:

            return value

    return default


# ==========================================================
# Current Account Values
# ==========================================================

current_username = get_value(
    account,
    [
        "username",
        "user_name",
    ],
    st.session_state.get(
        "username",
        "",
    ),
)


current_email = get_value(
    account,
    [
        "email",
    ],
    "",
)


current_full_name = get_value(
    account,
    [
        "full_name",
        "name",
    ],
    "",
)


current_role = get_value(
    account,
    [
        "role",
        "user_role",
    ],
    st.session_state.get(
        "role",
        "User",
    ),
)


current_active = get_value(
    account,
    [
        "is_active",
        "active",
    ],
    True,
)


user_id = get_value(
    account,
    [
        "id",
        "user_id",
    ],
    st.session_state.get(
        "user_id",
        None,
    ),
)


# ==========================================================
# Account Overview
# ==========================================================

st.subheader(
    "👤 Account Information"
)


info1, info2, info3, info4 = (
    st.columns(4)
)


with info1:

    st.metric(
        "Username",
        current_username
        or "N/A",
    )


with info2:

    st.metric(
        "Role",
        str(
            current_role
        ),
    )


with info3:

    status_text = (
        "Active"
        if current_active
        else "Inactive"
    )

    st.metric(
        "Status",
        status_text,
    )


with info4:

    st.metric(
        "User ID",
        user_id
        if user_id is not None
        else "N/A",
    )


st.divider()


# ==========================================================
# Profile
# ==========================================================

st.subheader(
    "👤 Profile"
)


with st.form(
    "profile_form",
    clear_on_submit=False,
):

    username = st.text_input(
        "Username",
        value=str(
            current_username
        ),
        help="Your login username.",
    )


    email = st.text_input(
        "Email",
        value=str(
            current_email
        ),
        help="Your account email address.",
    )


    full_name = st.text_input(
        "Full Name",
        value=str(
            current_full_name
        ),
        help="Your displayed name.",
    )


    profile_submitted = (
        st.form_submit_button(
            "💾 Save Profile",
            use_container_width=True,
        )
    )


# ==========================================================
# Update Profile
# ==========================================================

if profile_submitted:

    username = username.strip()
    email = email.strip()
    full_name = full_name.strip()


    # ------------------------------------------------------
    # Validation
    # ------------------------------------------------------

    if not username:

        st.error(
            "Username cannot be empty."
        )

        st.stop()


    if not email:

        st.error(
            "Email cannot be empty."
        )

        st.stop()


    # ------------------------------------------------------
    # Email Validation
    # ------------------------------------------------------

    if (
        "@"
        not in email
        or "."
        not in email.split(
            "@"
        )[-1]
    ):

        st.error(
            "Please enter a valid email address."
        )

        st.stop()


    # ------------------------------------------------------
    # Update Backend
    # ------------------------------------------------------

    with st.spinner(
        "Updating profile..."
    ):

        response = update_user_settings(
            {
                "username":
                    username,

                "email":
                    email,

                "full_name":
                    full_name,
            }
        )


    if response:

        # --------------------------------------------------
        # Update Session
        # --------------------------------------------------

        st.session_state.username = (
            username
        )


        st.success(
            "✅ Profile updated successfully."
        )


        st.info(
            "Your account information has been updated."
        )


    else:

        st.error(
            "Unable to update your profile."
        )


st.divider()


# ==========================================================
# Security
# ==========================================================

st.subheader(
    "🔐 Change Password"
)


st.caption(
    "Use a strong password and never share it with anyone."
)


with st.form(
    "password_form",
    clear_on_submit=True,
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


    password_submitted = (
        st.form_submit_button(
            "🔐 Update Password",
            use_container_width=True,
        )
    )


# ==========================================================
# Password Validation
# ==========================================================

if password_submitted:

    if not current_password:

        st.error(
            "Please enter your current password."
        )

        st.stop()


    if not new_password:

        st.error(
            "Please enter a new password."
        )

        st.stop()


    if len(new_password) < 6:

        st.error(
            "New password must contain at least 6 characters."
        )

        st.stop()


    if new_password != confirm_password:

        st.error(
            "New passwords do not match."
        )

        st.stop()


    if current_password == new_password:

        st.error(
            "New password must be different from the current password."
        )

        st.stop()


    # ------------------------------------------------------
    # Change Password
    # ------------------------------------------------------

    with st.spinner(
        "Updating password..."
    ):

        password_success = (
            change_password(
                current_password,
                new_password,
            )
        )


    if password_success:

        st.success(
            "✅ Password updated successfully."
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


api_url = get_value(
    settings,
    [
        "api_url",
        "backend_url",
    ],
    "Configured FastAPI backend",
)


st.info(
    f"API URL: {api_url}"
)


# ==========================================================
# Backend Status
# ==========================================================

backend_status = settings.get(
    "status"
)


if backend_status in [
    "success",
    "connected",
    "ok",
]:

    st.success(
        "🟢 Backend Connected"
    )

else:

    # If account information was successfully
    # retrieved, the backend is clearly responding.

    st.success(
        "🟢 Backend Connected"
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
### Parkinson Disease Detection Agent

**Version:** 1.0.0

**Frontend**
- Streamlit

**Backend**
- FastAPI

**Machine Learning**
- Scikit-learn

**Database**
- SQLite / PostgreSQL

This application provides AI-assisted Parkinson's
disease screening, patient management, prediction
history, analytics, reports, and health assistance.
"""
)


st.divider()


# ==========================================================
# Security Notice
# ==========================================================

st.subheader(
    "🛡️ Security"
)


st.info(
    """
Your password is sent to the backend only when you
explicitly submit the password-change form.

Never enter or share your password in the AI Assistant,
patient notes, reports, or other application fields.
"""
)


st.divider()


# ==========================================================
# Footer
# ==========================================================

st.caption(
    "© 2026 Parkinson Disease Detection Agent"
)
