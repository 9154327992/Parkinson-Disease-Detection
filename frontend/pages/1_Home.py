import streamlit as st
import pandas as pd

from utils.api_client import (
    get_analytics,
    get_reports,
    get_patients,
    get_prediction_history,
    check_backend,
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

with st.spinner("Loading dashboard..."):

    analytics = get_analytics()
    reports = get_reports()
    patients = get_patients()
    history = get_prediction_history()


# ==========================================================
# Safe Data
# ==========================================================

if not isinstance(
    analytics,
    dict,
):
    analytics = {}


if not isinstance(
    reports,
    list,
):
    reports = []


if not isinstance(
    patients,
    list,
):
    patients = []


if not isinstance(
    history,
    list,
):
    history = []


# ==========================================================
# Helper Functions
# ==========================================================

def first_value(
    data,
    keys,
    default=0,
):
    """
    Return the first available value from a dictionary.
    """

    if not isinstance(
        data,
        dict,
    ):
        return default

    for key in keys:

        value = data.get(
            key
        )

        if value is not None:

            return value

    return default


def safe_number(
    value,
    default=0,
):
    """
    Safely convert a value to a number.
    """

    try:

        return float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):

        return default


# ==========================================================
# Dashboard Metrics
# ==========================================================

total_patients = first_value(
    analytics,
    [
        "total_patients",
        "patients",
        "patient_count",
    ],
    len(patients),
)


total_predictions = first_value(
    analytics,
    [
        "total_predictions",
        "predictions",
        "prediction_count",
    ],
    len(history),
)


total_reports = len(
    reports
)


high_risk_cases = first_value(
    analytics,
    [
        "high_risk_cases",
        "high_risk",
        "high_risk_count",
    ],
    0,
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
        int(
            safe_number(
                total_patients
            )
        ),
    )


with col2:

    st.metric(
        "🧠 Predictions",
        int(
            safe_number(
                total_predictions
            )
        ),
    )


with col3:

    st.metric(
        "⚠️ High Risk Cases",
        int(
            safe_number(
                high_risk_cases
            )
        ),
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

c1, c2, c3, c4 = st.columns(4)


with c1:

    if st.button(
        "🩺 New Prediction",
        width="stretch",
    ):

        st.switch_page(
            "pages/2_Prediction.py"
        )


with c2:

    if st.button(
        "👤 Patient History",
        width="stretch",
    ):

        st.switch_page(
            "pages/3_Patient_History.py"
        )


with c3:

    if st.button(
        "📄 Reports",
        width="stretch",
    ):

        st.switch_page(
            "pages/5_Reports.py"
        )


with c4:

    if st.button(
        "📊 Analytics",
        width="stretch",
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

    patient_df = pd.DataFrame(
        patients
    )


    # ------------------------------------------------------
    # Normalize patient name
    # ------------------------------------------------------

    if (
        "patient_name"
        not in patient_df.columns
    ):

        if (
            "first_name"
            in patient_df.columns
        ):

            patient_df[
                "patient_name"
            ] = (
                patient_df[
                    "first_name"
                ]
                .fillna("")
                .astype(str)
                + " "
                + patient_df.get(
                    "last_name",
                    "",
                )
                .fillna("")
                .astype(str)
            ).str.strip()

        else:

            patient_df[
                "patient_name"
            ] = "Unknown"


    preferred_columns = [
        "id",
        "patient_name",
        "age",
        "gender",
        "diagnosis",
        "risk_level",
        "risk_score",
    ]


    available_columns = [
        column
        for column in preferred_columns
        if column
        in patient_df.columns
    ]


    if available_columns:

        display_patients = patient_df[
            available_columns
        ].head(5).copy()


        display_patients = (
            display_patients.rename(
                columns={
                    "id": "ID",
                    "patient_name": "Patient",
                    "age": "Age",
                    "gender": "Gender",
                    "diagnosis": "Diagnosis",
                    "risk_level": "Risk Level",
                    "risk_score": "Risk Score",
                }
            )
        )


        st.dataframe(
            display_patients,
            width="stretch",
            hide_index=True,
        )

    else:

        st.dataframe(
            patient_df.head(5),
            width="stretch",
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

    history_df = pd.DataFrame(
        history
    )


    # ------------------------------------------------------
    # Normalize prediction fields
    # ------------------------------------------------------

    if (
        "patient_name"
        not in history_df.columns
    ):

        history_df[
            "patient_name"
        ] = "Unknown"


    if (
        "diagnosis"
        not in history_df.columns
    ):

        if (
            "prediction"
            in history_df.columns
        ):

            history_df[
                "diagnosis"
            ] = history_df[
                "prediction"
            ]

        elif (
            "prediction_result"
            in history_df.columns
        ):

            history_df[
                "diagnosis"
            ] = history_df[
                "prediction_result"
            ]

        else:

            history_df[
                "diagnosis"
            ] = "Unknown"


    if (
        "risk_level"
        not in history_df.columns
    ):

        history_df[
            "risk_level"
        ] = "Unknown"


    if (
        "risk_score"
        not in history_df.columns
    ):

        history_df[
            "risk_score"
        ] = None


    if (
        "created_at"
        not in history_df.columns
    ):

        history_df[
            "created_at"
        ] = ""


    prediction_columns = [
        "id",
        "patient_name",
        "diagnosis",
        "risk_level",
        "risk_score",
        "created_at",
    ]


    available_prediction_columns = [
        column
        for column in prediction_columns
        if column
        in history_df.columns
    ]


    recent_predictions = (
        history_df[
            available_prediction_columns
        ]
        .head(5)
        .copy()
    )


    recent_predictions = (
        recent_predictions.rename(
            columns={
                "id": "ID",
                "patient_name": "Patient",
                "diagnosis": "Diagnosis",
                "risk_level": "Risk Level",
                "risk_score": "Risk Score",
                "created_at": "Date",
            }
        )
    )


    st.dataframe(
        recent_predictions,
        width="stretch",
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


high = first_value(
    analytics,
    [
        "high_risk_cases",
        "high_risk",
        "high_risk_count",
    ],
    0,
)


medium = first_value(
    analytics,
    [
        "medium_risk_cases",
        "medium_risk",
        "medium_risk_count",
    ],
    0,
)


low = first_value(
    analytics,
    [
        "low_risk_cases",
        "low_risk",
        "low_risk_count",
    ],
    0,
)


risk_col1, risk_col2, risk_col3 = (
    st.columns(3)
)


with risk_col1:

    st.metric(
        "🔴 High Risk",
        int(
            safe_number(
                high
            )
        ),
    )


with risk_col2:

    st.metric(
        "🟠 Medium Risk",
        int(
            safe_number(
                medium
            )
        ),
    )


with risk_col3:

    st.metric(
        "🟢 Low Risk",
        int(
            safe_number(
                low
            )
        ),
    )


# ==========================================================
# Risk Progress
# ==========================================================

total_risk_records = (
    safe_number(high)
    + safe_number(medium)
    + safe_number(low)
)


if total_risk_records > 0:

    st.write(
        "Risk distribution"
    )


    high_percentage = (
        safe_number(high)
        / total_risk_records
    )


    medium_percentage = (
        safe_number(medium)
        / total_risk_records
    )


    low_percentage = (
        safe_number(low)
        / total_risk_records
    )


    st.write(
        f"🔴 High: "
        f"{high_percentage * 100:.1f}%"
    )

    st.progress(
        high_percentage
    )


    st.write(
        f"🟠 Medium: "
        f"{medium_percentage * 100:.1f}%"
    )

    st.progress(
        medium_percentage
    )


    st.write(
        f"🟢 Low: "
        f"{low_percentage * 100:.1f}%"
    )

    st.progress(
        low_percentage
    )

else:

    st.info(
        "Risk statistics are currently unavailable."
    )


st.divider()


# ==========================================================
# Workflow
# ==========================================================

st.subheader(
    "📋 How It Works"
)

workflow_col1, workflow_col2 = (
    st.columns(2)
)


with workflow_col1:

    st.markdown(
        """
        **1.** Open **Prediction**

        **2.** Enter patient information

        **3.** Enter the 22 voice measurements

        **4.** Analyze the patient

        **5.** Review diagnosis and risk score
        """
    )


with workflow_col2:

    st.markdown(
        """
        **6.** View the prediction in
        **Patient History**

        **7.** Review generated reports

        **8.** Monitor trends in **Analytics**

        **9.** Ask questions using the
        **AI Health Assistant**
        """
    )


st.divider()


# ==========================================================
# System Status
# ==========================================================

st.subheader(
    "💻 System Status"
)


status_col1, status_col2, status_col3 = (
    st.columns(3)
)


# ----------------------------------------------------------
# Backend
# ----------------------------------------------------------

with status_col1:

    try:

        backend_online = check_backend()

    except Exception:

        backend_online = (
            analytics is not None
        )


    if backend_online:

        st.success(
            "🟢 FastAPI Backend Connected"
        )

    else:

        st.error(
            "🔴 FastAPI Backend Unavailable"
        )


# ----------------------------------------------------------
# Analytics
# ----------------------------------------------------------

with status_col2:

    if analytics:

        st.success(
            "🟢 Analytics Available"
        )

    else:

        st.warning(
            "🟡 Analytics Unavailable"
        )


# ----------------------------------------------------------
# Data
# ----------------------------------------------------------

with status_col3:

    if (
        patients
        or history
        or reports
    ):

        st.success(
            "🟢 Application Data Available"
        )

    else:

        st.warning(
            "🟡 No Application Data"
        )


st.divider()


# ==========================================================
# Quick Information
# ==========================================================

st.subheader(
    "ℹ️ Platform Information"
)


info_col1, info_col2, info_col3 = (
    st.columns(3)
)


with info_col1:

    st.info(
        """
        **Machine Learning**

        Uses patient voice measurements
        to assist with Parkinson's disease
        prediction.
        """
    )


with info_col2:

    st.info(
        """
        **Patient Management**

        Maintain patient records and
        review previous prediction results.
        """
    )


with info_col3:

    st.info(
        """
        **AI Assistant**

        Provides general educational
        information about Parkinson's disease.
        """
    )


# ==========================================================
# Medical Disclaimer
# ==========================================================

st.divider()

st.warning(
    """
    ⚠️ **Medical Disclaimer**

    This application provides AI-assisted screening
    and educational information. It is not a substitute
    for professional medical diagnosis or treatment.

    Always consult a qualified healthcare professional
    for medical decisions.
    """
)


# ==========================================================
# Footer
# ==========================================================

st.caption(
    "© 2026 Parkinson Disease Detection Agent | "
    "Streamlit + FastAPI + Scikit-learn"
)
