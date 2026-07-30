import streamlit as st
import pandas as pd

from utils.api_client import get_analytics

# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="Analytics",
    page_icon="📊",
    layout="wide"
)

# ==========================================================
# Header
# ==========================================================

st.title("📊 Analytics Dashboard")

st.write("""
View insights and statistics about Parkinson's disease predictions,
patient demographics, and risk distribution.
""")

st.divider()

# ==========================================================
# Load Analytics
# ==========================================================

analytics = get_analytics()

if analytics is None:

    st.error("Unable to load analytics data.")

    st.stop()

# ==========================================================
# Summary Metrics
# ==========================================================

st.subheader("📈 Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Patients",
        analytics["total_patients"]
    )

with col2:
    st.metric(
        "Predictions",
        analytics["total_predictions"]
    )

with col3:
    st.metric(
        "Healthy",
        analytics["healthy_cases"]
    )

with col4:
    st.metric(
        "Parkinson Cases",
        analytics["parkinson_cases"]
    )

st.divider()

# ==========================================================
# Risk Distribution
# ==========================================================

st.subheader("⚠ Risk Level Distribution")

risk_df = pd.DataFrame(
    analytics["risk_distribution"]
)

st.bar_chart(
    risk_df.set_index("risk_level")
)

st.divider()

# ==========================================================
# Diagnosis Distribution
# ==========================================================

st.subheader("🧠 Diagnosis Distribution")

diagnosis_df = pd.DataFrame(
    analytics["diagnosis_distribution"]
)

st.bar_chart(
    diagnosis_df.set_index("diagnosis")
)

st.divider()

# ==========================================================
# Gender Distribution
# ==========================================================

st.subheader("👥 Gender Distribution")

gender_df = pd.DataFrame(
    analytics["gender_distribution"]
)

st.bar_chart(
    gender_df.set_index("gender")
)

st.divider()

# ==========================================================
# Age Distribution
# ==========================================================

st.subheader("🎂 Age Distribution")

age_df = pd.DataFrame(
    analytics["age_distribution"]
)

st.line_chart(
    age_df.set_index("age_group")
)

st.divider()

# ==========================================================
# Monthly Predictions
# ==========================================================

st.subheader("📅 Monthly Predictions")

monthly_df = pd.DataFrame(
    analytics["monthly_predictions"]
)

st.line_chart(
    monthly_df.set_index("month")
)

st.divider()

# ==========================================================
# Recent Predictions
# ==========================================================

st.subheader("📝 Recent Predictions")

recent_df = pd.DataFrame(
    analytics["recent_predictions"]
)

st.dataframe(
    recent_df,
    use_container_width=True,
    hide_index=True
)

st.divider()

# ==========================================================
# Export Analytics
# ==========================================================

csv = recent_df.to_csv(index=False)

st.download_button(
    label="⬇ Export Analytics (CSV)",
    data=csv,
    file_name="analytics.csv",
    mime="text/csv",
    use_container_width=True
)
