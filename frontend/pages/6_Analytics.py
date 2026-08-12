import streamlit as st
import pandas as pd

from utils.api_client import get_analytics


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
    predictions, patient demographics, risk distribution,
    and prediction trends.
    """
)

st.divider()


# ==========================================================
# Load Analytics
# ==========================================================

with st.spinner(
    "Loading analytics..."
):

    analytics = get_analytics()


# ==========================================================
# Validate Response
# ==========================================================

if analytics is None:

    st.error(
        "Unable to load analytics data."
    )

    st.info(
        """
        The analytics service did not return data.
        Please check your backend connection and try again.
        """
    )

    if st.button(
        "🔄 Retry",
        width="stretch",
    ):

        st.rerun()

    st.stop()


if not isinstance(
    analytics,
    dict,
):

    st.error(
        "Invalid analytics response received."
    )

    st.write(
        f"Response type: "
        f"`{type(analytics).__name__}`"
    )

    st.stop()


# ==========================================================
# Safe Dictionary Helper
# ==========================================================

def section(
    name,
):
    value = analytics.get(
        name,
        {},
    )

    if isinstance(
        value,
        dict,
    ):

        return value

    return {}


def list_section(
    name,
):

    value = analytics.get(
        name,
        [],
    )

    if isinstance(
        value,
        list,
    ):

        return value

    return []


def number(
    value,
    default=0,
):

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
# Extract Sections
# ==========================================================

dashboard = section(
    "dashboard"
)

prediction = section(
    "prediction"
)

patient = section(
    "patient"
)

risk_distribution = list_section(
    "risk_distribution"
)

disease_distribution = list_section(
    "disease_distribution"
)

gender_distribution = list_section(
    "gender_distribution"
)

age_distribution = list_section(
    "age_distribution"
)

monthly_trend = list_section(
    "monthly_trend"
)

recent_predictions = list_section(
    "recent_predictions"
)


# ==========================================================
# Overview
# ==========================================================

st.subheader(
    "📈 Overview"
)

col1, col2, col3, col4 = (
    st.columns(4)
)


with col1:

    total_patients = dashboard.get(
        "total_patients",
        0,
    )

    st.metric(
        "👥 Total Patients",
        int(
            number(
                total_patients
            )
        ),
    )


with col2:

    total_predictions = dashboard.get(
        "total_predictions",
        0,
    )

    st.metric(
        "🧠 Total Predictions",
        int(
            number(
                total_predictions
            )
        ),
    )


with col3:

    healthy_cases = dashboard.get(
        "healthy_cases",
        0,
    )

    st.metric(
        "🟢 Healthy Cases",
        int(
            number(
                healthy_cases
            )
        ),
    )


with col4:

    parkinson_cases = dashboard.get(
        "parkinson_cases",
        0,
    )

    st.metric(
        "🔴 Parkinson Cases",
        int(
            number(
                parkinson_cases
            )
        ),
    )


st.divider()


# ==========================================================
# Prediction Statistics
# ==========================================================

st.subheader(
    "🧠 Prediction Statistics"
)

col1, col2, col3, col4 = (
    st.columns(4)
)


with col1:

    st.metric(
        "Predictions",
        int(
            number(
                prediction.get(
                    "total_predictions",
                    0,
                )
            )
        ),
    )


with col2:

    st.metric(
        "Healthy",
        int(
            number(
                prediction.get(
                    "healthy_predictions",
                    0,
                )
            )
        ),
    )


with col3:

    st.metric(
        "Parkinson",
        int(
            number(
                prediction.get(
                    "parkinson_predictions",
                    0,
                )
            )
        ),
    )


with col4:

    average_confidence = number(
        prediction.get(
            "average_confidence",
            0,
        )
    )

    st.metric(
        "Average Confidence",
        f"{average_confidence:.1f}%",
    )


average_risk_score = number(
    prediction.get(
        "average_risk_score",
        0,
    )
)


st.info(
    f"**Average Risk Score:** "
    f"{average_risk_score:.1f}%"
)


st.divider()


# ==========================================================
# Risk Distribution
# ==========================================================

st.subheader(
    "⚠️ Risk Level Distribution"
)


if risk_distribution:

    risk_df = pd.DataFrame(
        risk_distribution
    )


    if {
        "risk_level",
        "count",
    }.issubset(
        risk_df.columns
    ):

        risk_df = risk_df[
            [
                "risk_level",
                "count",
            ]
        ].copy()


        risk_df["count"] = pd.to_numeric(
            risk_df["count"],
            errors="coerce",
        ).fillna(0)


        st.bar_chart(
            risk_df.set_index(
                "risk_level"
            )[
                "count"
            ]
        )


        st.dataframe(
            risk_df.rename(
                columns={
                    "risk_level": "Risk Level",
                    "count": "Count",
                }
            ),
            width="stretch",
            hide_index=True,
        )

    else:

        st.warning(
            "Risk distribution response does not "
            "contain the expected fields."
        )

else:

    st.info(
        "No risk distribution data available."
    )


st.divider()


# ==========================================================
# Disease Distribution
# ==========================================================

st.subheader(
    "🧠 Disease Distribution"
)


if disease_distribution:

    disease_df = pd.DataFrame(
        disease_distribution
    )


    if {
        "label",
        "count",
    }.issubset(
        disease_df.columns
    ):

        disease_df = disease_df[
            [
                "label",
                "count",
            ]
        ].copy()


        disease_df["count"] = pd.to_numeric(
            disease_df["count"],
            errors="coerce",
        ).fillna(0)


        st.bar_chart(
            disease_df.set_index(
                "label"
            )[
                "count"
            ]
        )


        st.dataframe(
            disease_df.rename(
                columns={
                    "label": "Diagnosis",
                    "count": "Count",
                }
            ),
            width="stretch",
            hide_index=True,
        )

    else:

        st.warning(
            "Disease distribution response does not "
            "contain the expected fields."
        )

else:

    st.info(
        "No disease distribution data available."
    )


st.divider()


# ==========================================================
# Patient Demographics
# ==========================================================

st.subheader(
    "👥 Patient Demographics"
)

col1, col2, col3, col4 = (
    st.columns(4)
)


with col1:

    st.metric(
        "Male",
        int(
            number(
                patient.get(
                    "male_patients",
                    0,
                )
            )
        ),
    )


with col2:

    st.metric(
        "Female",
        int(
            number(
                patient.get(
                    "female_patients",
                    0,
                )
            )
        ),
    )


with col3:

    st.metric(
        "Other",
        int(
            number(
                patient.get(
                    "other_patients",
                    0,
                )
            )
        ),
    )


with col4:

    average_age = number(
        patient.get(
            "average_age",
            0,
        )
    )

    st.metric(
        "Average Age",
        f"{average_age:.1f}",
    )


st.divider()


# ==========================================================
# Gender Distribution
# ==========================================================

st.subheader(
    "👥 Gender Distribution"
)


if gender_distribution:

    gender_df = pd.DataFrame(
        gender_distribution
    )


    if {
        "gender",
        "count",
    }.issubset(
        gender_df.columns
    ):

        gender_df = gender_df[
            [
                "gender",
                "count",
            ]
        ].copy()


        gender_df["count"] = pd.to_numeric(
            gender_df["count"],
            errors="coerce",
        ).fillna(0)


        st.bar_chart(
            gender_df.set_index(
                "gender"
            )[
                "count"
            ]
        )

    else:

        st.warning(
            "Gender distribution data has "
            "an unexpected format."
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


if age_distribution:

    age_df = pd.DataFrame(
        age_distribution
    )


    if {
        "age_group",
        "count",
    }.issubset(
        age_df.columns
    ):

        age_df = age_df[
            [
                "age_group",
                "count",
            ]
        ].copy()


        age_df["count"] = pd.to_numeric(
            age_df["count"],
            errors="coerce",
        ).fillna(0)


        st.bar_chart(
            age_df.set_index(
                "age_group"
            )[
                "count"
            ]
        )

    else:

        st.warning(
            "Age distribution data has "
            "an unexpected format."
        )

else:

    st.info(
        "No age distribution data available."
    )


st.divider()


# ==========================================================
# Monthly Prediction Trend
# ==========================================================

st.subheader(
    "📅 Monthly Prediction Trend"
)


if monthly_trend:

    monthly_df = pd.DataFrame(
        monthly_trend
    )


    if {
        "month",
        "predictions",
    }.issubset(
        monthly_df.columns
    ):

        monthly_df = monthly_df[
            [
                "month",
                "predictions",
            ]
        ].copy()


        monthly_df["predictions"] = (
            pd.to_numeric(
                monthly_df[
                    "predictions"
                ],
                errors="coerce",
            )
            .fillna(0)
        )


        st.line_chart(
            monthly_df.set_index(
                "month"
            )[
                "predictions"
            ]
        )


        st.dataframe(
            monthly_df.rename(
                columns={
                    "month": "Month",
                    "predictions": "Predictions",
                }
            ),
            width="stretch",
            hide_index=True,
        )

    else:

        st.warning(
            "Monthly trend data has "
            "an unexpected format."
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


    # ------------------------------------------------------
    # Friendly column names
    # ------------------------------------------------------

    rename_columns = {
        "id": "ID",
        "patient_id": "Patient ID",
        "patient_name": "Patient",
        "diagnosis": "Diagnosis",
        "prediction": "Prediction",
        "risk_score": "Risk Score",
        "risk_level": "Risk Level",
        "confidence": "Confidence",
        "created_at": "Date",
    }


    recent_df = recent_df.rename(
        columns=rename_columns
    )


    st.dataframe(
        recent_df,
        width="stretch",
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
    "⬇️ Export Analytics"
)


# Export the complete analytics response
# in a readable flattened CSV when possible.

export_rows = []


for record in recent_predictions:

    if isinstance(
        record,
        dict,
    ):

        export_rows.append(
            record
        )


if export_rows:

    export_df = pd.DataFrame(
        export_rows
    )

else:

    export_df = pd.DataFrame(
        {
            "Metric": [
                "Total Patients",
                "Total Predictions",
                "Healthy Cases",
                "Parkinson Cases",
                "Average Confidence",
                "Average Risk Score",
            ],
            "Value": [
                dashboard.get(
                    "total_patients",
                    0,
                ),
                dashboard.get(
                    "total_predictions",
                    0,
                ),
                dashboard.get(
                    "healthy_cases",
                    0,
                ),
                dashboard.get(
                    "parkinson_cases",
                    0,
                ),
                prediction.get(
                    "average_confidence",
                    0,
                ),
                prediction.get(
                    "average_risk_score",
                    0,
                ),
            ],
        }
    )


csv = export_df.to_csv(
    index=False
)


st.download_button(
    label="⬇️ Export Analytics (CSV)",
    data=csv,
    file_name="analytics.csv",
    mime="text/csv",
    width="stretch",
)


st.divider()


# ==========================================================
# Analytics Status
# ==========================================================

st.subheader(
    "💻 Analytics Status"
)


if analytics:

    st.success(
        "🟢 Analytics data loaded successfully."
    )

else:

    st.warning(
        "🟡 Analytics service returned no data."
    )


st.divider()


# ==========================================================
# Medical Disclaimer
# ==========================================================

st.warning(
    """
    ⚠️ **Medical Disclaimer**

    Analytics and prediction results are intended
    for AI-assisted screening and educational purposes.
    They are not a substitute for professional medical
    diagnosis or treatment.

    Always consult a qualified healthcare professional
    for medical decisions.
    """
)


# ==========================================================
# Footer
# ==========================================================

st.caption(
    "Parkinson Disease Detection Agent "
    "• Analytics Dashboard"
)
