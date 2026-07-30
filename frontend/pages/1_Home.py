import streamlit as st

# ==========================================
# Page Configuration
# ==========================================

st.set_page_config(
    page_title="Home",
    page_icon="🏠",
    layout="wide"
)

# ==========================================
# Header
# ==========================================

st.title("🏠 Home")

st.write(
    """
    Welcome to the **Parkinson Disease Detection Agent**.

    This AI-powered system helps healthcare professionals and researchers
    predict Parkinson's disease risk using voice features, monitor patients,
    generate reports, and provide AI-assisted health guidance.
    """
)

st.divider()

# ==========================================
# System Status
# ==========================================

st.subheader("🖥️ System Status")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Backend API", "🟢 Online")

with col2:
    st.metric("ML Model", "🟢 Loaded")

with col3:
    st.metric("Database", "🟢 Connected")

st.divider()

# ==========================================
# Dashboard Overview
# ==========================================

st.subheader("📊 Dashboard Overview")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Total Patients", "0")

with c2:
    st.metric("Predictions", "0")

with c3:
    st.metric("High Risk Cases", "0")

with c4:
    st.metric("Reports Generated", "0")

st.divider()

# ==========================================
# Application Modules
# ==========================================

st.subheader("🚀 Available Modules")

modules = [
    ("🩺", "Prediction", "Predict Parkinson's disease risk."),
    ("👤", "Patient History", "View and manage patient records."),
    ("🤖", "AI Health Assistant", "Ask health-related questions."),
    ("📄", "Reports", "Generate and download reports."),
    ("📊", "Analytics", "Visualize prediction statistics."),
    ("🛠️", "Admin Dashboard", "Manage users and system."),
    ("⚙️", "Settings", "Configure the application.")
]

for icon, title, description in modules:
    st.markdown(
        f"""
        ### {icon} {title}
        {description}
        """
    )

st.divider()

# ==========================================
# Project Features
# ==========================================

st.subheader("✨ Key Features")

st.markdown("""
- ✅ AI-based Parkinson Disease Prediction
- ✅ Voice Feature Analysis
- ✅ Patient Record Management
- ✅ AI Health Assistant
- ✅ Risk Score & Recommendations
- ✅ Analytics Dashboard
- ✅ PDF Report Generation
- ✅ Secure FastAPI Backend
- ✅ Streamlit Interactive Interface
""")

st.divider()

# ==========================================
# How to Use
# ==========================================

st.subheader("📖 How to Use")

st.markdown("""
1. Open **Prediction** from the sidebar.
2. Enter the patient's voice feature values.
3. Click **Analyze Patient**.
4. View the diagnosis, risk score, and recommendations.
5. Save the patient record.
6. Review previous records in **Patient History**.
7. Generate reports or explore analytics.
""")

st.divider()

# ==========================================
# Footer
# ==========================================

st.caption("Parkinson Disease Detection Agent • Version 1.0.0")
