import streamlit as st

from utils.api_client import (
    get_user_settings,
    change_password,
    health_check,
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
# Header
# ==========================================================

st.title(
    "⚙️ Settings"
)

st.write(
    "Manage your account security and application status."
)

st.divider()


# ==========================================================
# Account Security
# ==========================================================

st.subheader(
    "🔐 Security"
)


user = get_user_settings()


if isinstance(
    user,
    dict,
):

    username = (
        user.get("username")
        or st.session_state.get(
            "username",
            "admin",
        )
    )

    role = (
        user.get("role")
        or st.session_state.get(
            "role",
            "admin",
        )
    )

else:

    username = st.session_state.get(
        "username",
        "admin",
    )

    role = st.session_state.get(
        "role",
        "admin",
    )


col1, col2 = st.columns(
    2
)


with col1:

    st.text_input(
        "Username",
        value=str(
            username
        ),
        disabled=True,
    )


with col2:

    st.text_input(
        "Role",
        value=str(
            role
        ),
        disabled=True,
    )


# ==========================================================
# Change Password
# ==========================================================

with st.form(
    "change_password_form"
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


    submitted = st.form_submit_button(
        "🔐 Update Password",
        width="stretch",
    )


    if submitted:

        # --------------------------------------------------
        # Validation
        # --------------------------------------------------

        if not current_password:

            st.error(
                "Please enter your current password."
            )

        elif not new_password:

            st.error(
                "Please enter a new password."
            )

        elif not confirm_password:

            st.error(
                "Please confirm your new password."
            )

        elif new_password != confirm_password:

            st.error(
                "New passwords do not match."
            )

        elif current_password == new_password:

            st.error(
                "New password must be different "
                "from your current password."
            )

        else:

            # ----------------------------------------------
            # Change Password
            # ----------------------------------------------

            with st.spinner(
                "Updating password..."
            ):

                result = change_password(
                    current_password,
                    new_password,
                )


            if isinstance(
                result,
                dict,
            ):

                success = result.get(
                    "success",
                    True,
                )

                message = (
                    result.get(
                        "message"
                    )
                    or "Password updated successfully."
                )

                if success:

                    st.success(
                        message
                    )

                else:

                    st.error(
                        message
                    )

            elif result is True:

                st.success(
                    "Password updated successfully."
                )

            else:

                st.error(
                    "Unable to update password. "
                    "Please check your current password."
                )


# ==========================================================
# System Status
# ==========================================================

st.divider()

st.subheader(
    "🖥️ System"
)


backend_status = health_check()


col1, col2, col3 = st.columns(
    3
)


with col1:

    if backend_status:

        st.success(
            "Backend\n\n🟢 Connected"
        )

    else:

        st.error(
            "Backend\n\n🔴 Offline"
        )


with col2:

    # ------------------------------------------------------
    # Database
    #
    # Database connectivity is handled by the backend.
    # ------------------------------------------------------

    if backend_status:

        st.success(
            "Database\n\n🟢 Available"
        )

    else:

        st.error(
            "Database\n\n🔴 Unavailable"
        )


with col3:

    # ------------------------------------------------------
    # AI Assistant
    #
    # The AI Assistant uses the FastAPI backend.
    # ------------------------------------------------------

    if backend_status:

        st.success(
            "AI Assistant\n\n🟢 Available"
        )

    else:

        st.error(
            "AI Assistant\n\n🔴 Unavailable"
        )


# ==========================================================
# About
# ==========================================================

st.divider()

st.subheader(
    "ℹ️ About"
)


st.write(
    "**Parkinson Disease Detection**"
)

st.caption(
    "Version 1.0.0"
)

st.caption(
    "Frontend: Streamlit"
)

st.caption(
    "Backend: FastAPI"
)


# ==========================================================
# Footer
# ==========================================================

st.divider()

st.caption(
    "© 2026 Parkinson Disease Detection Agent"
)
