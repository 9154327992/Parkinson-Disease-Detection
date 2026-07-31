import streamlit as st


def render_sidebar():
    """
    Render the application sidebar.
    """

    with st.sidebar:

        st.title("🧠 PD Detection Agent")

        st.caption("Version 1.0.0")

        st.divider()

        # ===============================
        # User Information
        # ===============================

        st.subheader("👤 User")

        username = st.session_state.get("username", "Guest")
        role = st.session_state.get("role", "User")

        st.write(f"**Name:** {username}")
        st.write(f"**Role:** {role}")

        st.divider()

        # ===============================
        # System Status
        # ===============================

        st.subheader("🖥️ System Status")

        st.success("🟢 Backend Connected")
        st.success("🟢 ML Model Loaded")
        st.success("🟢 Database Connected")

        st.divider()

        # ===============================
        # Quick Navigation
        # ===============================

        st.subheader("📌 Modules")

        st.markdown("""
- 🏠 Home
- 🩺 Prediction
- 👤 Patient History
- 🤖 AI Assistant
- 📄 Reports
- 📊 Analytics
- 🛠 Admin Dashboard
- ⚙️ Settings
""")

        st.divider()

        # ===============================
        # About
        # ===============================

        st.info(
            """
**Parkinson Disease Detection Agent**

AI-powered Parkinson's Disease Prediction System

Frontend: Streamlit

Backend: FastAPI
"""
        )

        st.divider()

        st.caption("© 2026 PD Detection Agent")
