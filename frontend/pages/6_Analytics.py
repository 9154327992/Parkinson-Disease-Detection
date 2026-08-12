import streamlit as st
import pandas as pd

from utils.api_client import (
    get_analytics,
    get_patient_history,
)


# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="Analytics",
    page_icon="📊",
    layout="wide",
)


# ==========================================================
# Header
# ==========================================================

st.title(
    "📊 Analytics Dashboard"
)

st.write(
    """
View insights and statistics about Parkinson's disease
predictions, patient demographics, and risk distribution.
"""
)

st.divider()


# ==========================================================
# Helper Functions
# ==========================================================

def get_value(
    record,
    keys,
    default=None,
):
    """
    Safely retrieve the first available value.
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


def get_risk_level(
    record,
):
    """
    Normalize risk level.
    """

    value = get_value(
        record,
        [
            "risk_level",
            "risk_category",
            "risk",
        ],
        None,
    )

    if isinstance(
        value,
        dict,
    ):

        value = (
            value.get("risk_level")
            or value.get("level")
            or value.get("category")
        )

    if value is None:
        return "Unknown"

    text = str(
        value
    ).strip().lower()

    if "high" in text:
        return "High Risk"

    if "medium" in text:
        return "Medium Risk"

    if "low" in text:
        return "Low Risk"

    return str(value)


def get_diagnosis(
    record,
):
    """
    Normalize prediction/diagnosis.
    """

    value = get_value(
        record,
        [
            "diagnosis",
            "prediction",
            "prediction_result",
            "result",
        ],
        "Unknown",
    )

    if isinstance(
        value,
        dict,
    ):

        value = (
            value.get("diagnosis")
            or value.get("prediction")
            or value.get("result")
            or "Unknown"
        )

    return str(value)


def get_patient_name(
    record,
):
    """
    Safely construct patient name.
    """

    value = get_value(
        record,
        [
            "patient_name",
            "name",
            "full_name",
        ],
        None,
    )

    if value:
        return str(value)

    first_name = get_value(
        record,
        [
            "first_name",
            "firstName",
        ],
        "",
    )

    last_name = get_value(
        record,
        [
            "last_name",
            "lastName",
        ],
        "",
    )

    combined = (
        f"{first_name} {last_name}"
    ).strip()

    return combined or "Unknown"


def to_number(
    value,
):
    """
    Convert a value to float safely.
    """

    if value is None:
        return None

    try:
        return float(value)

    except (
        TypeError,
        ValueError,
    ):
        return None


def confidence_percentage(
    value,
):
    """
    Normalize confidence to percentage.
    """

    number = to_number(
        value
    )

    if number is None:
        return None

    if number <= 1:
        number *= 100

    return number


# ==========================================================
# Load Data
# ==========================================================

with st.spinner(
    "Loading analytics..."
):

    analytics = get_analytics()

with st.spinner(
    "Loading prediction history..."
):

    history = get_patient_history()


# ==========================================================
# Normalize Analytics
# ==========================================================

if not isinstance(
    analytics,
    dict,
):

    analytics = {}


if isinstance(
    history,
    dict,
):

    history = (
        history.get("history")
        or history.get("predictions")
        or history.get("records")
        or []
    )


if not isinstance(
    history,
    list,
):

    history = []


# ==========================================================
# Build Local Analytics From History
# ==========================================================

total_predictions = len(
    history
)

high_risk = 0
medium_risk = 0
low_risk = 0
unknown_risk = 0

healthy_cases = 0
parkinson_cases = 0

risk_scores = []
confidence_values = []

patient_names = []
genders = []
ages = []

recent_predictions = []


for record in history:

    if not isinstance(
        record,
        dict,
    ):
        continue


    # ------------------------------------------------------
    # Risk
    # ------------------------------------------------------

    risk = get_risk_level(
        record
    )


    if risk == "High Risk":

        high_risk += 1

    elif risk == "Medium Risk":

        medium_risk += 1

    elif risk == "Low Risk":

        low_risk += 1

    else:

        unknown_risk += 1


    # ------------------------------------------------------
    # Diagnosis
    # ------------------------------------------------------

    diagnosis = get_diagnosis(
        record
    )

    diagnosis_lower = (
        diagnosis.lower()
    )


    if (
        "healthy" in diagnosis_lower
        or "normal" in diagnosis_lower
        or "negative" in diagnosis_lower
    ):

        healthy_cases += 1

    elif (
        "parkinson" in diagnosis_lower
        or "positive" in diagnosis_lower
        or "detected" in diagnosis_lower
    ):

        parkinson_cases += 1


    # ------------------------------------------------------
    # Risk Score
    # ------------------------------------------------------

    risk_score = to_number(
        get_value(
            record,
            [
                "risk_score",
                "risk_percentage",
            ],
            None,
        )
    )


    if risk_score is not None:

        risk_scores.append(
            risk_score
        )


    # ------------------------------------------------------
    # Confidence
    # ------------------------------------------------------

    confidence = confidence_percentage(
        get_value(
            record,
            [
                "confidence",
                "prediction_confidence",
            ],
            None,
        )
    )


    if confidence is not None:

        confidence_values.append(
            confidence
        )


    # ------------------------------------------------------
    # Patient
    # ------------------------------------------------------

    patient_name = get_patient_name(
        record
    )

    if patient_name != "Unknown":

        patient_names.append(
            patient_name
        )


    # ------------------------------------------------------
    # Gender
    # ------------------------------------------------------

    gender = get_value(
        record,
        [
            "gender",
            "patient_gender",
        ],
        None,
    )

    if gender:

        genders.append(
            str(gender)
        )


    # ------------------------------------------------------
    # Age
    # ------------------------------------------------------

    age = to_number(
        get_value(
            record,
            [
                "age",
                "patient_age",
            ],
            None,
        )
    )

    if age is not None:

        ages.append(
            age
        )


    # ------------------------------------------------------
    # Recent Prediction
    # ------------------------------------------------------

    recent_predictions.append(
        {
            "Prediction ID":
                get_value(
                    record,
                    [
                        "prediction_id",
                        "id",
                    ],
                    "N/A",
                ),

            "Patient":
                patient_name,

            "Diagnosis":
                diagnosis,

            "Risk Level":
                risk,

            "Risk Score":
                (
                    f"{risk_score:.2f}%"
                    if risk_score is not None
                    else "N/A"
                ),

            "Confidence":
                (
                    f"{confidence:.2f}%"
                    if confidence is not None
                    else "N/A"
                ),

            "Created":
                get_value(
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


# ==========================================================
# Analytics Backend Values
# ==========================================================

dashboard = analytics.get(
    "dashboard",
    {},
)

prediction = analytics.get(
    "prediction",
    {},
)

patient = analytics.get(
    "patient",
    {},
)


if not isinstance(
    dashboard,
    dict,
):

    dashboard = {}


if not isinstance(
    prediction,
    dict,
):

    prediction = {}


if not isinstance(
    patient,
    dict,
):

    patient = {}


# ==========================================================
# Use Backend Values Only As Fallback
# ==========================================================

if total_predictions == 0:

    total_predictions = int(
        prediction.get(
            "total_predictions",
            dashboard.get(
                "total_predictions",
                0,
            ),
        )
        or 0
    )


if (
    high_risk
    + medium_risk
    + low_risk
    == 0
):

    high_risk = int(
        dashboard.get(
            "high_risk_cases",
            analytics.get(
                "high_risk_cases",
                0,
            ),
        )
        or 0
    )

    medium_risk = int(
        dashboard.get(
            "medium_risk_cases",
            analytics.get(
                "medium_risk_cases",
                0,
            ),
        )
        or 0
    )

    low_risk = int(
        dashboard.get(
            "low_risk_cases",
            analytics.get(
                "low_risk_cases",
                0,
            ),
        )
        or 0
    )


# ==========================================================
# Average Risk Score
# ==========================================================

if risk_scores:

    average_risk_score = (
        sum(risk_scores)
        / len(risk_scores)
    )

else:

    average_risk_score = to_number(
        prediction.get(
            "average_risk_score"
        )
    )


# ==========================================================
# Average Confidence
# ==========================================================

if confidence_values:

    average_confidence = (
        sum(confidence_values)
        / len(confidence_values)
    )

else:

    average_confidence = to_number(
        prediction.get(
            "average_confidence"
        )
    )


# ==========================================================
# Total Patients
# ==========================================================

unique_patient_names = set(
    patient_names
)

total_patients = len(
    unique_patient_names
)

if total_patients == 0:

    total_patients = int(
        dashboard.get(
            "total_patients",
            0,
        )
        or 0
    )


# ==========================================================
# Healthy / Parkinson Fallback
# ==========================================================

if (
    healthy_cases
    + parkinson_cases
    == 0
):

    healthy_cases = int(
        dashboard.get(
            "healthy_cases",
            0,
        )
        or 0
    )

    parkinson_cases = int(
        dashboard.get(
            "parkinson_cases",
            0,
        )
        or 0
    )


# ==========================================================
# Overview
# ==========================================================

st.subheader(
    "📈 Overview"
)

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Total Patients",
        total_patients,
    )


with col2:

    st.metric(
        "Total Predictions",
        total_predictions,
    )


with col3:

    st.metric(
        "Healthy Cases",
        healthy_cases,
    )


with col4:

    st.metric(
        "Parkinson Cases",
        parkinson_cases,
    )


st.divider()


# ==========================================================
# Prediction Statistics
# ==========================================================

st.subheader(
    "🧠 Prediction Statistics"
)

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Predictions",
        total_predictions,
    )


with col2:

    st.metric(
        "Healthy",
        healthy_cases,
    )


with col3:

    st.metric(
        "Parkinson",
        parkinson_cases,
    )


with col4:

    if average_confidence is not None:

        st.metric(
            "Average Confidence",
            f"{average_confidence:.2f}%",
        )

    else:

        st.metric(
            "Average Confidence",
            "N/A",
        )


if average_risk_score is not None:

    st.write(
        f"**Average Risk Score:** "
        f"{average_risk_score:.2f}%"
    )

else:

    st.write(
        "**Average Risk Score:** N/A"
    )


st.divider()


# ==========================================================
# Risk Distribution
# ==========================================================

st.subheader(
    "⚠️ Risk Level Distribution"
)


risk_data = pd.DataFrame(
    {
        "Risk Level": [
            "High Risk",
            "Medium Risk",
            "Low Risk",
        ],
        "Count": [
            high_risk,
            medium_risk,
            low_risk,
        ],
    }
)


if risk_data["Count"].sum() > 0:

    st.bar_chart(
        risk_data.set_index(
            "Risk Level"
        )
    )

else:

    st.info(
        "No risk distribution data available."
    )


st.divider()


# ==========================================================
# Risk Metrics
# ==========================================================

st.subheader(
    "🚨 Risk Summary"
)

risk_col1, risk_col2, risk_col3 = (
    st.columns(3)
)


with risk_col1:

    st.metric(
        "🔴 High Risk",
        high_risk,
    )


with risk_col2:

    st.metric(
        "🟠 Medium Risk",
        medium_risk,
    )


with risk_col3:

    st.metric(
        "🟢 Low Risk",
        low_risk,
    )


st.divider()


# ==========================================================
# Disease Distribution
# ==========================================================

st.subheader(
    "🧠 Disease Distribution"
)


disease_data = pd.DataFrame(
    {
        "Diagnosis": [
            "Healthy",
            "Parkinson",
        ],
        "Count": [
            healthy_cases,
            parkinson_cases,
        ],
    }
)


if disease_data["Count"].sum() > 0:

    st.bar_chart(
        disease_data.set_index(
            "Diagnosis"
        )
    )

else:

    st.info(
        "No disease distribution data available."
    )


st.divider()


# ==========================================================
# Gender Distribution
# ==========================================================

st.subheader(
    "👥 Gender Distribution"
)


gender_counts = {}


for gender in genders:

    normalized_gender = (
        gender.strip().title()
    )

    gender_counts[
        normalized_gender
    ] = (
        gender_counts.get(
            normalized_gender,
            0,
        )
        + 1
    )


# Backend fallback

if not gender_counts:

    gender_distribution = analytics.get(
        "gender_distribution",
        [],
    )

    if isinstance(
        gender_distribution,
        list,
    ):

        for item in gender_distribution:

            if not isinstance(
                item,
                dict,
            ):
                continue

            gender = get_value(
                item,
                [
                    "gender",
                    "label",
                ],
                "Unknown",
            )

            count = get_value(
                item,
                [
                    "count",
                ],
                0,
            )

            gender_counts[
                str(gender)
            ] = count


if gender_counts:

    gender_df = pd.DataFrame(
        {
            "Gender":
                list(
                    gender_counts.keys()
                ),

            "Count":
                list(
                    gender_counts.values()
                ),
        }
    )

    st.bar_chart(
        gender_df.set_index(
            "Gender"
        )
    )

else:

    st.info(
        "No gender distribution data available."
    )


st.divider()


# ==========================================================
# Age Distribution
# ==========================================================

st.subheader(
    "🎂 Age Distribution"
)


if ages:

    age_df = pd.DataFrame(
        {
            "Age": ages
        }
    )

    st.bar_chart(
        age_df["Age"].value_counts()
        .sort_index()
    )

else:

    st.info(
        "No age distribution data available."
    )


if ages:

    average_age = (
        sum(ages)
        / len(ages)
    )

    st.write(
        f"**Average Patient Age:** "
        f"{average_age:.1f} years"
    )


st.divider()


# ==========================================================
# Monthly Prediction Trend
# ==========================================================

st.subheader(
    "📅 Monthly Predictions"
)


monthly_trend = analytics.get(
    "monthly_trend",
    [],
)


if isinstance(
    monthly_trend,
    list,
) and monthly_trend:

    monthly_rows = []

    for item in monthly_trend:

        if not isinstance(
            item,
            dict,
        ):
            continue

        month = get_value(
            item,
            [
                "month",
            ],
            None,
        )

        predictions = get_value(
            item,
            [
                "predictions",
                "count",
            ],
            0,
        )

        if month is not None:

            monthly_rows.append(
                {
                    "Month":
                        month,

                    "Predictions":
                        predictions,
                }
            )


    if monthly_rows:

        monthly_df = pd.DataFrame(
            monthly_rows
        )

        st.line_chart(
            monthly_df.set_index(
                "Month"
            )[
                "Predictions"
            ]
        )

    else:

        st.info(
            "No monthly prediction data available."
        )

else:

    st.info(
        "No monthly prediction data available."
    )


st.divider()


# ==========================================================
# Recent Predictions
# ==========================================================

st.subheader(
    "📝 Recent Predictions"
)


if recent_predictions:

    recent_df = pd.DataFrame(
        recent_predictions
    )

    st.dataframe(
        recent_df,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "No recent predictions available."
    )


st.divider()


# ==========================================================
# Export Analytics
# ==========================================================

st.subheader(
    "⬇ Export Analytics"
)


if recent_predictions:

    export_df = pd.DataFrame(
        recent_predictions
    )

else:

    export_df = pd.DataFrame(
        {
            "Metric": [
                "Total Patients",
                "Total Predictions",
                "Healthy Cases",
                "Parkinson Cases",
                "High Risk",
                "Medium Risk",
                "Low Risk",
            ],

            "Value": [
                total_patients,
                total_predictions,
                healthy_cases,
                parkinson_cases,
                high_risk,
                medium_risk,
                low_risk,
            ],
        }
    )


csv_data = export_df.to_csv(
    index=False
)


st.download_button(
    label="⬇ Export Analytics (CSV)",
    data=csv_data,
    file_name="analytics.csv",
    mime="text/csv",
    use_container_width=True,
)


st.divider()


# ==========================================================
# Data Quality Information
# ==========================================================

with st.expander(
    "ℹ️ Analytics Data Source"
):

    st.write(
        """
Analytics uses prediction history as the primary source
for prediction, diagnosis, risk, confidence, and patient
statistics.

Backend aggregate analytics are used as a fallback when
individual history records do not contain the required data.

This prevents missing API fields from being incorrectly
displayed as zero values.
"""
    )


# ==========================================================
# Footer
# ==========================================================

st.caption(
    "Analytics | "
    "Parkinson Disease Detection Agent"
)
