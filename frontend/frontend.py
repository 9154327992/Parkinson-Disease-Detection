from pathlib import Path
import streamlit as st

# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="Parkinson Disease Detection Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================
# Load Global CSS
# ==========================================================

def load_css():
    css_file = Path(__file__).parent / "assets" / "style.css"

    if css_file.exists():
        with open(css_file, encoding="utf-8") as f:
            st.markdown(
                f"<style>{f.read()}</style>",
                unsafe_allow_html=True,
            )

load_css()

# ==========================================================
# Initialize Session State
# ==========================================================

defaults = {
    "logged_in": False,
    "username": "Guest",
    "role": "User",
    "theme": "Light",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ==========================================================
# Sidebar
# ==========================================================

with st.sidebar:

    from pathlib import Path
    
    import streamlit as st

    BASE_DIR = Path(__file__).parent

    logo_path = BASE_DIR / "assets" / "logo.png"

    st.image(str(logo_path), width=100)

    st.title("🧠 PD Detection Agent")

    st.caption("Version 1.0.0")

    st.divider()

    st.write("### User")

    st.write(f"**Name:** {st.session_state.username}")

    st.write(f"**Role:** {st.session_state.role}")

    st.divider()

    st.write("### System Status")

    st.success("🟢 FastAPI Connected")

    st.success("🟢 ML Model Loaded")

    st.success("🟢 Database Connected")

    st.divider()

    st.info(
        """
Select a module from the sidebar.

🏠 Home

🩺 Prediction

👤 Patient History

🤖 AI Assistant

📄 Reports

📊 Analytics

🛠 Admin Dashboard

⚙ Settings
"""
    )

# ==========================================================
# Main Dashboard
# ==========================================================

st.title("🧠 Parkinson Disease Detection Agent")

st.write(
    """
Welcome to the **AI-powered Parkinson Disease Detection and Monitoring System**.

This application uses machine learning to predict Parkinson's disease from
voice measurements and provides patient management, analytics, reports,
and an AI health assistant.
"""
)

st.divider()

# ==========================================================
# Quick Status
# ==========================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Patients", "0")

with col2:
    st.metric("Predictions", "0")

with col3:
    st.metric("Reports", "0")

with col4:
    st.metric("AI Status", "Ready")

st.divider()

# ==========================================================
# Features
# ==========================================================

st.subheader("✨ Application Features")

feature1, feature2 = st.columns(2)

with feature1:

    st.markdown("""
- ✅ Parkinson Disease Prediction
- ✅ Patient History
- ✅ Report Generation
- ✅ Analytics Dashboard
""")

with feature2:

    st.markdown("""
- ✅ AI Health Assistant
- ✅ Exercise Recommendations
- ✅ Medication Guidance
- ✅ Admin Dashboard
""")

st.divider()

# ==========================================================
# Workflow
# ==========================================================

st.subheader("📋 Workflow")

st.markdown("""
1. Open **Prediction**.
2. Enter patient information.
3. Enter the 22 voice measurements.
4. Click **Analyze Patient**.
5. View diagnosis and recommendations.
6. Save the prediction.
7. Review patient history and reports.
""")

st.divider()

# ==========================================================
# Footer
# ==========================================================

st.caption(
    "© 2026 Parkinson Disease Detection Agent | Streamlit + FastAPI + Scikit-learn"
)
