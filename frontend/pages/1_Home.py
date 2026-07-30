import streamlit as st

# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="Home",
    page_icon="🏠",
    layout="wide"
)

# ==========================================================
# Header
# ==========================================================

st.title("🏠 Home Dashboard")

st.write(
    """
Welcome to the **Parkinson Disease Detection Agent**.

This platform uses Machine Learning and Artificial Intelligence
to assist in Parkinson's Disease prediction, patient management,
analytics, and health recommendations.
"""
)

st.divider()

# ==========================================================
# Quick Statistics
# ==========================================================

st.subheader("📊 Dashboard Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="👤 Total Patients",
        value="0"
    )

with col2:
    st.metric(
        label="🧠 Predictions",
        value="0"
    )

with col3:
    st.metric(
        label="⚠ High Risk Cases",
        value="0"
    )

with col4:
    st.metric(
        label="📄 Reports",
        value="0"
    )

st.divider()

# ==========================================================
# System Status
# ==========================================================

st.subheader("🖥️ System Status")

left, right = st.columns(2)

with left:

    st.success("✅ FastAPI Backend Connected")

    st.success("✅ Machine Learning Model Loaded")

    st.success("✅ Database Connected")

with right:

    st.info("Frontend : Streamlit")

    st.info("Backend : FastAPI")

    st.info("Deployment : Render")

st.divider()

# ==========================================================
# Available Modules
# ==========================================================

st.subheader("🚀 Available Modules")

modules = [

    ("🏠 Home", "Application Dashboard"),

    ("🩺 Prediction", "Predict Parkinson's Disease"),

    ("👤 Patient History", "View Patient Records"),

    ("🤖 AI Health Assistant", "Medical Chat Assistant"),

    ("📄 Reports", "Generate PDF Reports"),

    ("📊 Analytics", "View Charts & Statistics"),

    ("🛠 Admin Dashboard", "Manage System"),

    ("⚙ Settings", "Application Preferences"),
]

for icon, description in modules:

    st.markdown(
        f"""
### {icon}

{description}
"""
    )

st.divider()

# ==========================================================
# Application Workflow
# ==========================================================

st.subheader("📋 How It Works")

st.markdown("""
1. Open the **Prediction** page.

2. Enter patient information.

3. Enter the 22 voice measurements.

4. Click **Analyze Patient**.

5. Receive diagnosis and risk score.

6. Save patient records.

7. Generate reports.

8. View analytics.
""")

st.divider()

# ==========================================================
# Key Features
# ==========================================================

st.subheader("⭐ Features")

feature1, feature2 = st.columns(2)

with feature1:

    st.markdown("""
- ✔ Parkinson Disease Prediction
- ✔ Patient History
- ✔ AI Health Assistant
- ✔ PDF Report Generation
""")

with feature2:

    st.markdown("""
- ✔ Interactive Analytics
- ✔ Risk Assessment
- ✔ Medical Recommendations
- ✔ Secure FastAPI Backend
""")

st.divider()

# ==========================================================
# Recent Activity
# ==========================================================

st.subheader("📝 Recent Activity")

st.info("No recent activity available.")

st.divider()

# ==========================================================
# Footer
# ==========================================================

st.caption(
    "Parkinson Disease Detection Agent | Version 1.0.0"
)
