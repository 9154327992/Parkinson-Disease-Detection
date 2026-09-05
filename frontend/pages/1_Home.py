import streamlit as st
import pandas as pd

from utils.api_client import (
    get_analytics,
    get_reports,
    get_patients,
    get_patient_history,
)

from pathlib import Path

# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="Home",
    page_icon="🏠",
    layout="wide",
)

# ==========================================================
# Banner
# ==========================================================

IMAGE_PATH = (
    Path(__file__).resolve().parents[1]
    / "assets"
    / "images"
    / "home_banner.png"
)


if IMAGE_PATH.exists():

    st.image(
        str(IMAGE_PATH),
        width="stretch",
    )

# ==========================================================
# Header
# ==========================================================

st.title(
    "🏠 Home Dashboard"
)

st.write(
    """
Welcome to the **Parkinson Disease Detection Agent**.

This platform uses machine learning and AI-assisted tools
for Parkinson's disease prediction, patient management,
analytics, reports, and health education.
"""
)

st.divider()


# ==========================================================
# Load Data
# ==========================================================

analytics_response = get_analytics()
reports_response = get_reports()
patients_response = get_patients()
history_response = get_patient_history()


# ==========================================================
# Validate Responses
# ==========================================================

analytics_available = isinstance(
    analytics_response,
    dict,
)

reports = (
    reports_response
    if isinstance(reports_response, list)
    else []
)

patients = (
    patients_response
    if isinstance(patients_response, list)
    else []
)

history = (
    history_response
    if isinstance(history_response, list)
    else []
)

analytics = (
    analytics_response
    if analytics_available
    else {}
)


# ==========================================================
# Helper Functions
# ==========================================================

def first_value(
    record,
    keys,
    default=None,
):
    """
    Return the first available value from a dictionary.
    """

    if not isinstance(
        record,
        dict,
    ):
        return default

    for key in keys:

        value = record.get(
            key
        )

        if value is not None:
            return value

    return default


def normalize_patient_name(
    patient,
):
    """
    Safely determine patient name.
    """

    name = first_value(
        patient,
        [
            "patient_name",
            "name",
            "full_name",
            "patient",
        ],
    )

    if isinstance(
        name,
        dict,
    ):

        name = (
            name.get("patient_name")
            or name.get("name")
            or name.get("full_name")
        )

    if name:
        return str(name)

    first_name = first_value(
        patient,
        [
            "first_name",
            "firstName",
        ],
        "",
    )

    last_name = first_value(
        patient,
        [
            "last_name",
            "lastName",
        ],
        "",
    )

    full_name = (
        f"{first_name} {last_name}"
    ).strip()

    return full_name or "Unknown"


def normalize_risk_level(
    record,
):
    """
    Safely extract risk level.
    """

    risk = first_value(
        record,
        [
            "risk_level",
            "risk_category",
            "risk",
        ],
    )

    if isinstance(
        risk,
        dict,
    ):

        risk = (
            risk.get("risk_level")
            or risk.get("level")
            or risk.get("category")
        )

    if risk is None:
        return None

    risk = str(
        risk
    ).strip().lower()

    if "high" in risk:
        return "High Risk"

    if "medium" in risk:
        return "Medium Risk"

    if "low" in risk:
        return "Low Risk"

    return str(risk).title()


def normalize_diagnosis(
    record,
):
    """
    Safely extract prediction/diagnosis.
    """

    diagnosis = first_value(
        record,
        [
            "diagnosis",
            "prediction",
            "prediction_result",
            "result",
        ],
    )

    if isinstance(
        diagnosis,
        dict,
    ):

        diagnosis = (
            diagnosis.get("diagnosis")
            or diagnosis.get("prediction")
            or diagnosis.get("result")
        )

    if diagnosis is None:
        return "Unknown"

    return str(
        diagnosis
    )


def normalize_patient_id(
    record,
):
    """
    Safely extract patient ID.
    """

    return first_value(
        record,
        [
            "patient_id",
            "id",
        ],
        "N/A",
    )


# ==========================================================
# Analytics Data
# ==========================================================

dashboard_data = analytics.get(
    "dashboard",
    {},
)

prediction_data = analytics.get(
    "prediction",
    {},
)

if not isinstance(
    dashboard_data,
    dict,
):
    dashboard_data = {}

if not isinstance(
    prediction_data,
    dict,
):
    prediction_data = {}


# ==========================================================
# Dashboard Statistics
#
# IMPORTANT:
# All dashboard totals come from Analytics.
# This prevents Home from displaying numbers that
# disagree with the backend dashboard statistics.
# ==========================================================

total_patients = int(
    dashboard_data.get(
        "total_patients",
        analytics.get(
            "total_patients",
            0,
        ),
    )
    or 0
)

total_predictions = int(
    prediction_data.get(
        "total_predictions",
        dashboard_data.get(
            "total_predictions",
            analytics.get(
                "total_predictions",
                0,
            ),
        ),
    )
    or 0
)

total_reports = int(
    dashboard_data.get(
        "total_reports",
        analytics.get(
            "total_reports",
            0,
        ),
    )
    or 0
)

high_risk_cases = int(
    dashboard_data.get(
        "high_risk_cases",
        analytics.get(
            "high_risk_cases",
            0,
        ),
    )
    or 0
)

medium_risk_cases = int(
    dashboard_data.get(
        "medium_risk_cases",
        analytics.get(
            "medium_risk_cases",
            0,
        ),
    )
    or 0
)

low_risk_cases = int(
    dashboard_data.get(
        "low_risk_cases",
        analytics.get(
            "low_risk_cases",
            0,
        ),
    )
    or 0
)


# ==========================================================
# Dashboard Overview
# ==========================================================

st.subheader(
    "📊 Dashboard Overview"
)

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

st.subheader(
    "🚀 Quick Actions"
)

action1, action2, action3, action4 = (
    st.columns(4)
)


with action1:

    if st.button(
        "🩺 New Prediction",
        use_container_width=True,
    ):

        st.switch_page(
            "pages/2_Prediction.py"
        )


with action2:

    if st.button(
        "👤 Patient History",
        use_container_width=True,
    ):

        st.switch_page(
            "pages/3_Patient_History.py"
        )


with action3:

    if st.button(
        "📄 Reports",
        use_container_width=True,
    ):

        st.switch_page(
            "pages/5_Reports.py"
        )


with action4:

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

st.subheader(
    "👥 Recent Patients"
)


if patients:

    patient_rows = []

    for patient in patients:

        patient_rows.append(
            {
                "ID": first_value(
                    patient,
                    [
                        "id",
                        "patient_id",
                    ],
                    "N/A",
                ),

                "Patient Name":
                    normalize_patient_name(
                        patient
                    ),

                "Age":
                    first_value(
                        patient,
                        [
                            "age",
                        ],
                        "N/A",
                    ),

                "Gender":
                    first_value(
                        patient,
                        [
                            "gender",
                        ],
                        "N/A",
                    ),
            }
        )

    patient_df = pd.DataFrame(
        patient_rows
    )

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
# Recent Predictions
# ==========================================================

st.subheader(
    "🧠 Recent Predictions"
)


if history:

    prediction_rows = []

    for record in history[:10]:

        prediction_rows.append(
            {
                "Prediction ID":
                    first_value(
                        record,
                        [
                            "prediction_id",
                            "id",
                        ],
                        "N/A",
                    ),

                "Patient":
                    normalize_patient_name(
                        record
                    ),

                "Diagnosis":
                    normalize_diagnosis(
                        record
                    ),

                "Risk Level":
                    normalize_risk_level(
                        record
                    )
                    or "Unknown",

                "Risk Score":
                    first_value(
                        record,
                        [
                            "risk_score",
                        ],
                        "N/A",
                    ),

                "Created":
                    first_value(
                        record,
                        [
                            "created_at",
                            "timestamp",
                            "date",
                        ],
                        "N/A",
                    ),
            }
        )

    prediction_df = pd.DataFrame(
        prediction_rows
    )

    st.dataframe(
        prediction_df,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "No prediction records available yet."
    )


st.divider()


# ==========================================================
# Risk Summary
# ==========================================================

st.subheader(
    "⚠️ Risk Summary"
)

risk_col1, risk_col2, risk_col3 = (
    st.columns(3)
)


with risk_col1:

    st.metric(
        "🔴 High Risk",
        high_risk_cases,
    )


with risk_col2:

    st.metric(
        "🟠 Medium Risk",
        medium_risk_cases,
    )


with risk_col3:

    st.metric(
        "🟢 Low Risk",
        low_risk_cases,
    )


if (
    high_risk_cases
    + medium_risk_cases
    + low_risk_cases
    == 0
):

    st.info(
        "No risk classification data is currently available."
    )


st.divider()


# ==========================================================
# Workflow
# ==========================================================

st.subheader(
    "📋 How It Works"
)

st.markdown(
    """
**1.** Open **Prediction**

**2.** Enter patient information

**3.** Enter the required voice measurements or provide an audio recording

**4.** Analyze the patient

**5.** Review the prediction and risk information

**6.** View the prediction in **Patient History**

**7.** Review generated **Reports**

**8.** Monitor trends in **Analytics**
"""
)


st.divider()


# ==========================================================
# System Status
# ==========================================================

st.subheader(
    "💻 System Status"
)

status_col1, status_col2 = (
    st.columns(2)
)


with status_col1:

    if analytics_available:

        st.success(
            "🟢 FastAPI Backend Connected"
        )

    else:

        st.error(
            "🔴 FastAPI Backend Unavailable"
        )


with status_col2:

    if analytics_available:

        st.success(
            "🟢 Analytics Service Available"
        )

    else:

        st.warning(
            "🟡 Analytics Service Unavailable"
        )


st.divider()


# ==========================================================
# Footer
# ==========================================================

st.caption(
    "© 2026 Parkinson Disease Detection Agent | "
    "Streamlit + FastAPI + Scikit-learn"
)
