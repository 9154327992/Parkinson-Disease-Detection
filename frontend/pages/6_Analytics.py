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
predictions, patient demographics, and risk distribution.
"""
)

st.divider()


# ==========================================================
# Load Analytics
# ==========================================================

analytics = get_analytics()


if analytics is None:

    st.error(
        "Unable to load analytics data."
    )

    st.stop()


# ==========================================================
# Extract Sections
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

risk_distribution = analytics.get(
    "risk_distribution",
    [],
)

disease_distribution = analytics.get(
    "disease_distribution",
    [],
)

gender_distribution = analytics.get(
    "gender_distribution",
    [],
)

age_distribution = analytics.get(
    "age_distribution",
    [],
)

monthly_trend = analytics.get(
    "monthly_trend",
    [],
)

recent_predictions = analytics.get(
    "recent_predictions",
    [],
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
        dashboard.get(
            "total_patients",
            0,
        ),
    )


with col2:

    st.metric(
        "Total Predictions",
        dashboard.get(
            "total_predictions",
            0,
        ),
    )


with col3:

    st.metric(
        "Healthy Cases",
        dashboard.get(
            "healthy_cases",
            0,
        ),
    )


with col4:

    st.metric(
        "Parkinson Cases",
        dashboard.get(
            "parkinson_cases",
            0,
        ),
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
        prediction.get(
            "total_predictions",
            0,
        ),
    )


with col2:

    st.metric(
        "Healthy",
        prediction.get(
            "healthy_predictions",
            0,
        ),
    )


with col3:

    st.metric(
        "Parkinson",
        prediction.get(
            "parkinson_predictions",
            0,
        ),
    )


with col4:

    st.metric(
        "Average Confidence",
        f"{prediction.get('average_confidence', 0)}%",
    )


st.write(
    f"**Average Risk Score:** "
    f"{prediction.get('average_risk_score', 0)}%"
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

        st.bar_chart(
            risk_df.set_index(
                "risk_level"
            )["count"]
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

        st.bar_chart(
            disease_df.set_index(
                "label"
            )["count"]
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


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Male",
        patient.get(
            "male_patients",
            0,
        ),
    )


with col2:

    st.metric(
        "Female",
        patient.get(
            "female_patients",
            0,
        ),
    )


with col3:

    st.metric(
        "Other",
        patient.get(
            "other_patients",
            0,
        ),
    )


with col4:

    st.metric(
        "Average Age",
        patient.get(
            "average_age",
            0,
        ),
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

        st.bar_chart(
            gender_df.set_index(
                "gender"
            )["count"]
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

        st.bar_chart(
            age_df.set_index(
                "age_group"
            )["count"]
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
    "📅 Monthly Predictions"
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

        st.line_chart(
            monthly_df.set_index(
                "month"
            )["predictions"]
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

    csv = pd.DataFrame(
        recent_predictions
    ).to_csv(
        index=False
    )

else:

    csv = pd.DataFrame().to_csv(
        index=False
    )


st.download_button(
    label="⬇ Export Analytics (CSV)",
    data=csv,
    file_name="analytics.csv",
    mime="text/csv",
    use_container_width=True,
)
