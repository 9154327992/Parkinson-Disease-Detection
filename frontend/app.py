import streamlit as st

# ==========================================
# Page Configuration
# ==========================================

st.set_page_config(
    page_title="Parkinson Disease Detection Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# Sidebar
# ==========================================

with st.sidebar:
    st.title("🧠 PD Detection Agent")

    st.markdown("---")

    st.write("### Navigation")
    st.info(
        """
        Select a page from the sidebar.

        • Home

        • Prediction

        • Patient History

        • AI Health Assistant

        • Reports

        • Analytics

        • Admin Dashboard

        • Settings
        """
    )

    st.markdown("---")

    st.write("### Model Information")

    st.success("Machine Learning Model Loaded")

    st.write("Dataset : Parkinson Voice Dataset")

    st.write("Backend : FastAPI")

    st.write("Frontend : Streamlit")

    st.markdown("---")

    st.caption("Version 1.0.0")

# ==========================================
# Main Page
# ==========================================

st.title("🧠 Parkinson Disease Detection Agent")

st.markdown(
    """
Welcome to the **AI-powered Parkinson Disease Detection and Monitoring System**.

Use the navigation menu on the left to access the different modules of the application.
"""
)

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Prediction Model",
        "Ready"
    )

with col2:
    st.metric(
        "Backend API",
        "Connected"
    )

with col3:
    st.metric(
        "Database",
        "Ready"
    )

st.markdown("---")

st.subheader("Available Modules")

modules = [
    "🏠 Home",
    "🩺 Parkinson Prediction",
    "👤 Patient History",
    "🤖 AI Health Assistant",
    "📄 Reports",
    "📊 Analytics",
    "🛠️ Admin Dashboard",
    "⚙️ Settings",
]

for module in modules:
    st.write(f"✅ {module}")

st.markdown("---")

st.info(
    "Choose any page from the sidebar to begin using the application."
)
