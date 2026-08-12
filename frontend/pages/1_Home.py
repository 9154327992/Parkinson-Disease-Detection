import streamlit as st
import pandas as pd

from utils.api_client import (
    get_analytics,
    get_reports,
    get_patients,
    get_patient_history,
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

st.title(
    "🏠 Home Dashboard"
)

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
history = get_patient_history()


# ==========================================================
# Safe List Helpers
# ==========================================================

if not isinstance(
    patients,
    list,
):
    patients = []


if not isinstance(
    reports,
    list,
):
    reports = []


if not isinstance(
    history,
    list,
):
    history = []


if not isinstance(
    analytics,
    dict,
):

    analytics = {}


# ==========================================================
# Helper Functions
# ==========================================================

def first_value(
    record,
    keys,
    default=None,
):
    """
    Return the first available value from a record.
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
    Safely determine patient name from different
    possible backend response formats.
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

    if full_name:
        return full_name

    return "Unknown"


def normalize_risk_level(
    record,
):
    """
    Safely extract risk level from prediction/history.
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

    return None


def normalize_diagnosis(
    record,
):
    """
    Safely extract diagnosis/prediction.
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
# Analytics Sections
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
# Patient Count
# ==========================================================

# Prefer actual patient records.
total_patients = len(
    patients
)

# If the patient endpoint returned no records,
# use analytics as fallback.

if total_patients == 0:

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


# ==========================================================
# Prediction Count
# ==========================================================

# Prefer actual prediction history.

total_predictions = len(
    history
)

if total_predictions == 0:

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


# ==========================================================
# Risk Calculation From History
# ==========================================================

high_risk_cases = 0
medium_risk_cases = 0
low_risk_cases = 0


for record in history:

    risk = normalize_risk_level(
        record
    )

    if risk == "High Risk":

        high_risk_cases += 1

    elif risk == "Medium Risk":

        medium_risk_cases += 1

    elif risk == "Low Risk":

        low_risk_cases += 1


# ==========================================================
# Analytics Risk Fallback
# ==========================================================

if (
    high_risk_cases
    + medium_risk_cases
    + low_risk_cases
    == 0
):

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
# High Risk Count
# ==========================================================

# This value must reflect the same source as the
# Risk Summary below.

high_risk_display = high_risk_cases


# ==========================================================
# Reports
# ==========================================================

total_reports = len(
    reports
)

if total_reports == 0:

    total_reports = int(
        analytics.get(
            "total_reports",
            0,
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
        high_risk_display,
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

                "Email":
                    first_value(
                        patient,
                        [
                            "email",
                        ],
                        "N/A",
                    ),

                "Phone":
                    first_value(
                        patient,
                        [
                            "phone",
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
                            "risk",
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

**3.** Enter all 22 voice measurements

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

st.subheader(
    "💻 System Status"
)


status_col1, status_col2 = (
    st.columns(2)
)


backend_available = (
    analytics != {}
    or bool(patients)
    or bool(history)
    or bool(reports)
)


with status_col1:

    if backend_available:

        st.success(
            "🟢 FastAPI Backend Connected"
        )

    else:

        st.error(
            "🔴 FastAPI Backend Unavailable"
        )


with status_col2:

    if analytics:

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
