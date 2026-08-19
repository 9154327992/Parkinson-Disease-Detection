import streamlit as st

from utils.api_client import (
    get_user_settings,
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
# Session Defaults
# ==========================================================

if "prediction_display" not in st.session_state:

    st.session_state.prediction_display = "Detailed"


if "auto_refresh_history" not in st.session_state:

    st.session_state.auto_refresh_history = True


if "show_disclaimer" not in st.session_state:

    st.session_state.show_disclaimer = True


if "save_chat_history" not in st.session_state:

    st.session_state.save_chat_history = True


# ==========================================================
# Header
# ==========================================================

st.title("⚙️ Settings")

st.write(
    "Customize how the Parkinson Disease Detection "
    "application works."
)

st.divider()


# ==========================================================
# Account
# ==========================================================

st.subheader("👤 Account")


user = get_user_settings()


if isinstance(user, dict):

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


col1, col2 = st.columns(2)


with col1:

    st.text_input(
        "Username",
        value=str(username),
        disabled=True,
    )


with col2:

    st.text_input(
        "Role",
        value=str(role),
        disabled=True,
    )


# ==========================================================
# Application Preferences
# ==========================================================

st.divider()

st.subheader("🎛️ Application Preferences")


prediction_display = st.selectbox(
    "Prediction Display",
    options=[
        "Detailed",
        "Simple",
    ],
    index=(
        0
        if st.session_state.prediction_display
        == "Detailed"
        else 1
    ),
    help=(
        "Choose how prediction results are "
        "displayed."
    ),
)


auto_refresh_history = st.toggle(
    "Auto-refresh Prediction History",
    value=st.session_state.auto_refresh_history,
)


show_disclaimer = st.toggle(
    "Show Medical Disclaimer",
    value=st.session_state.show_disclaimer,
)


save_chat_history = st.toggle(
    "Save AI Chat History",
    value=st.session_state.save_chat_history,
)


# ==========================================================
# Save Settings
# ==========================================================

if st.button(
    "💾 Save Settings",
    width="stretch",
):

    st.session_state.prediction_display = (
        prediction_display
    )

    st.session_state.auto_refresh_history = (
        auto_refresh_history
    )

    st.session_state.show_disclaimer = (
        show_disclaimer
    )

    st.session_state.save_chat_history = (
        save_chat_history
    )

    st.success(
        "✅ Settings saved successfully."
    )


# ==========================================================
# Reset Settings
# ==========================================================

if st.button(
    "↩️ Reset to Default",
    width="stretch",
):

    st.session_state.prediction_display = (
        "Detailed"
    )

    st.session_state.auto_refresh_history = True

    st.session_state.show_disclaimer = True

    st.session_state.save_chat_history = True

    st.success(
        "Settings restored to default."
    )

    st.rerun()


# ==========================================================
# System Status
# ==========================================================

st.divider()

st.subheader("🖥️ System Status")


backend_status = health_check()


col1, col2, col3 = st.columns(3)


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

    if backend_status:

        st.success(
            "Database\n\n🟢 Available"
        )

    else:

        st.error(
            "Database\n\n🔴 Unavailable"
        )


with col3:

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

st.subheader("ℹ️ About")

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
# Medical Disclaimer
# ==========================================================

if st.session_state.show_disclaimer:

    st.divider()

    st.info(
        """
        **Medical Disclaimer**

        This application provides AI-assisted
        screening information for educational and
        research purposes.

        It does not provide a medical diagnosis and
        should not replace evaluation by a qualified
        healthcare professional.
        """
    )


# ==========================================================
# Footer
# ==========================================================

st.divider()

st.caption(
    "Parkinson Disease Detection Agent"
)
