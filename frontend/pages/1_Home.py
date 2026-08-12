import streamlit as st
import pandas as pd

from utils.api_client import (
    get_analytics,
    get_reports,
    get_patients,
)


# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="Home",
    page_icon="🏠",
    layout="wide",
)


# ==========================================================
# Header
# ==========================================================

st.title("🏠 Home Dashboard")

st.write(
    """
    Welcome to the **Parkinson Disease Detection Agent**.

    This platform uses machine learning and AI to assist with
    Parkinson's disease prediction, patient management,
    analytics, reports, and health recommendations.
    """
)

st.divider()


# ==========================================================
# Load Data
# ==========================================================

analytics = get_analytics()
reports = get_reports()
patients = get_patients()


# ==========================================================
# Safe Values
# ==========================================================

if isinstance(analytics, dict):

    total_patients = analytics.get(
        "total_patients",
        0,
    )

    total_predictions = analytics.get(
        "total_predictions",
        0,
    )

    high_risk_cases = analytics.get(
        "high_risk_cases",
        0,
    )

else:

    total_patients = 0
    total_predictions = 0
    high_risk_cases = 0


if isinstance(reports, list):
    total_reports = len(reports)
else:
    total_reports = 0


if not isinstance(patients, list):
    patients = []


# ==========================================================
# Dashboard Metrics
# ==========================================================

st.subheader("📊 Dashboard Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "👤 Total Patients",
        total_patients,
    )

with col2:

    st.metric(
        "🧠 Predictions",
        total_predictions,
    )

with col3:

    st.metric(
        "⚠️ High Risk Cases",
        high_risk_cases,
    )

with col4:

    st.metric(
        "📄 Reports",
        total_reports,
    )


st.divider()


# ==========================================================
# Quick Actions
# ==========================================================

st.subheader("🚀 Quick Actions")

c1, c2, c3, c4 = st.columns(4)

with c1:

    if st.button(
        "🩺 New Prediction",
        use_container_width=True,
    ):
        st.switch_page(
            "pages/2_Prediction.py"
        )

with c2:

    if st.button(
        "👤 Patient History",
        use_container_width=True,
    ):
        st.switch_page(
            "pages/3_Patient_History.py"
        )

with c3:

    if st.button(
        "📄 Reports",
        use_container_width=True,
    ):
        st.switch_page(
            "pages/5_Reports.py"
        )

with c4:

    if st.button(
        "📊 Analytics",
        use_container_width=True,
    ):
        st.switch_page(
            "pages/6_Analytics.py"
        )


st.divider()


# ==========================================================
# Recent Patients
# ==========================================================

st.subheader("👥 Recent Patients")

if patients:

    patient_df = pd.DataFrame(
        patients
    )

    preferred_columns = [
        column
        for column in [
            "id",
            "patient_name",
            "age",
            "gender",
            "diagnosis",
            "risk_level",
            "risk_score",
        ]
        if column in patient_df.columns
    ]

    if preferred_columns:

        st.dataframe(
            patient_df[
                preferred_columns
            ].head(5),
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.dataframe(
            patient_df.head(5),
            use_container_width=True,
            hide_index=True,
        )

else:

    st.info(
        "No patient records available yet."
    )


st.divider()


# ==========================================================
# Risk Summary
# ==========================================================

st.subheader("⚠️ Risk Summary")

if isinstance(analytics, dict):

    high = analytics.get(
        "high_risk_cases",
        0,
    )

    medium = analytics.get(
        "medium_risk_cases",
        0,
    )

    low = analytics.get(
        "low_risk_cases",
        0,
    )

    risk_col1, risk_col2, risk_col3 = st.columns(3)

    with risk_col1:

        st.metric(
            "🔴 High Risk",
            high,
        )

    with risk_col2:

        st.metric(
            "🟠 Medium Risk",
            medium,
        )

    with risk_col3:

        st.metric(
            "🟢 Low Risk",
            low,
        )

else:

    st.info(
        "Risk statistics are currently unavailable."
    )


st.divider()


# ==========================================================
# Workflow
# ==========================================================

st.subheader("📋 How It Works")

st.markdown(
    """
    **1.** Open **Prediction**  
    **2.** Enter patient information  
    **3.** Enter the 22 voice measurements  
    **4.** Analyze the patient  
    **5.** Review diagnosis and risk score  
    **6.** View the prediction in Patient History  
    **7.** Review generated reports  
    **8.** Monitor trends in Analytics
    """
)


st.divider()


# ==========================================================
# System Status
# ==========================================================

st.subheader("💻 System Status")

status_col1, status_col2 = st.columns(2)

with status_col1:

    if analytics is not None:
        st.success(
            "🟢 FastAPI Backend Connected"
        )
    else:
        st.error(
            "🔴 FastAPI Backend Unavailable"
        )

with status_col2:

    if analytics is not None:
        st.success(
            "🟢 Analytics Service Available"
        )
    else:
        st.warning(
            "🟡 Analytics Service Unavailable"
        )


st.divider()


st.caption(
    "© 2026 Parkinson Disease Detection Agent | "
    "Streamlit + FastAPI + Scikit-learn"
)
