import streamlit as st

from pathlib import Path


# ==========================================================
# API Imports
# ==========================================================

from utils.api_client import (
    get_patient_history,
    get_reports,
)


# ==========================================================
# Session Import
# ==========================================================

from utils.session import (
    initialize_session,
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
# Initialize Session
# ==========================================================

initialize_session()

# ==========================================================
# Home Banner
# ==========================================================

HOME_BANNER = (
    Path(__file__).resolve().parents[1]
    / "assets"
    / "images"
    / "home_banner.png"
)


if HOME_BANNER.exists():

    import base64


    banner_base64 = base64.b64encode(
        HOME_BANNER.read_bytes()
    ).decode(
        "utf-8"
    )


    st.html(
        f"""
        <style>

        .home-banner-wrapper {{
            width: 100%;
            margin: 0 0 1rem 0;
            padding: 0;
        }}


        .home-banner {{
            /*
            Responsive width:

            Small screens:
            Banner becomes smaller.

            Large/high-resolution screens:
            Banner becomes larger.
            */

            width: min(100%, 1600px);

            height: auto;

            display: block;

            margin-left: auto;
            margin-right: auto;

            object-fit: contain;

            border-radius: 12px;
        }}


        /* Small screens */

        @media (max-width: 768px) {{

            .home-banner {{
                width: 100%;
            }}

        }}


        /* Medium screens */

        @media (min-width: 769px) and (max-width: 1400px) {{

            .home-banner {{
                width: 100%;
            }}

        }}


        /* Large / high-resolution screens */

        @media (min-width: 1401px) {{

            .home-banner {{
                width: 100%;
                max-width: 1600px;
            }}

        }}

        </style>


        <div class="home-banner-wrapper">

            <img
                class="home-banner"
                src="data:image/png;base64,{banner_base64}"
                alt="Parkinson Disease Detection Home"
            >

        </div>
        """
    )


else:

    st.warning(
        "Home banner image was not found."
    )

# ==========================================================
# Title
# ==========================================================

st.title(
    "🏠 Parkinson Disease Detection Agent"
)


st.write(
    """
    An AI-assisted platform for Parkinson's disease
    screening using voice measurements, patient
    management, prediction history, analytics,
    medical reports, and an AI Health Assistant.
    """
)


st.divider()


# ==========================================================
# Safe Helper Functions
# ==========================================================

def safe_list(
    value,
):

    if isinstance(
        value,
        list,
    ):

        return value


    if isinstance(
        value,
        dict,
    ):

        return (
            value.get("data")
            or value.get("items")
            or value.get("records")
            or value.get("predictions")
            or value.get("history")
            or value.get("reports")
            or []
        )


    return []


def safe_count(
    value,
):

    if value is None:

        return 0


    if isinstance(
        value,
        (list, tuple, set),
    ):

        return len(value)


    if isinstance(
        value,
        dict,
    ):

        for key in [
            "count",
            "total",
            "total_count",
        ]:

            number = value.get(
                key
            )

            if isinstance(
                number,
                (int, float),
            ):

                return int(
                    number
                )


        for key in [
            "data",
            "items",
            "records",
            "predictions",
            "history",
            "reports",
        ]:

            item = value.get(
                key
            )

            if isinstance(
                item,
                list,
            ):

                return len(
                    item
                )


    return 0


def get_metric(
    data,
    keys,
    default=0,
):

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


# ==========================================================
# Fetch Data Safely
# ==========================================================

try:

    history_response = (
        get_patient_history()
    )

except Exception:

    history_response = None


try:

    reports_response = (
        get_reports()
    )

except Exception:

    reports_response = None


history = safe_list(
    history_response
)


reports = safe_list(
    reports_response
)


# ==========================================================
# Dashboard Metrics
# ==========================================================

st.subheader(
    "📊 Overview"
)


metric1, metric2, metric3, metric4 = (
    st.columns(
        4
    )
)


# ----------------------------------------------------------
# Prediction Count
# ----------------------------------------------------------

prediction_count = (
    safe_count(
        history
    )
)


# ----------------------------------------------------------
# Report Count
# ----------------------------------------------------------

report_count = (
    safe_count(
        reports
    )
)


# ----------------------------------------------------------
# Patient Count
#
# This version derives a unique patient count from
# prediction history so it does not depend on get_analytics().
# ----------------------------------------------------------

patient_ids = set()


for item in history:

    if not isinstance(
        item,
        dict,
    ):

        continue


    patient_id = (
        item.get("patient_id")
        or item.get("patientId")
    )


    if patient_id is not None:

        patient_ids.add(
            str(patient_id)
        )


patient_count = len(
    patient_ids
)


# ----------------------------------------------------------
# High Risk Count
# ----------------------------------------------------------

high_risk_count = 0


for item in history:

    if not isinstance(
        item,
        dict,
    ):

        continue


    risk_level = str(
        item.get(
            "risk_level",
            ""
        )
    ).lower()


    if (
        "high" in risk_level
    ):

        high_risk_count += 1


# ==========================================================
# Display Metrics
# ==========================================================

with metric1:

    st.metric(
        "👤 Patients",
        patient_count,
    )


with metric2:

    st.metric(
        "🧪 Predictions",
        prediction_count,
    )


with metric3:

    st.metric(
        "📄 Reports",
        report_count,
    )


with metric4:

    st.metric(
        "⚠️ High Risk",
        high_risk_count,
    )


st.divider()


# ==========================================================
# Quick Navigation
# ==========================================================

st.subheader(
    "🚀 Quick Navigation"
)


nav1, nav2, nav3, nav4 = (
    st.columns(
        4
    )
)


with nav1:

    if st.button(
        "🧪 New Prediction",
        width="stretch",
    ):

        st.switch_page(
            "pages/2_Prediction.py"
        )


with nav2:

    if st.button(
        "👤 Patient History",
        width="stretch",
    ):

        st.switch_page(
            "pages/3_Patient_History.py"
        )


with nav3:

    if st.button(
        "🤖 AI Assistant",
        width="stretch",
    ):

        st.switch_page(
            "pages/4_AI_Health_Assistant.py"
        )


with nav4:

    if st.button(
        "📄 Reports",
        width="stretch",
    ):

        st.switch_page(
            "pages/5_Reports.py"
        )


st.divider()


# ==========================================================
# Recent Predictions
# ==========================================================

st.subheader(
    "🕒 Recent Predictions"
)


if history:

    rows = []


    for item in history[:5]:

        if not isinstance(
            item,
            dict,
        ):

            continue


        patient_name = (
            item.get(
                "patient_name"
            )
            or item.get(
                "name"
            )
            or "Unknown"
        )


        diagnosis = (
            item.get(
                "prediction"
            )
            or item.get(
                "diagnosis"
            )
            or "Unknown"
        )


        risk_level = (
            item.get(
                "risk_level"
            )
            or "Unknown"
        )


        risk_score = (
            item.get(
                "risk_score"
            )
        )


        created_at = (
            item.get(
                "created_at"
            )
            or item.get(
                "prediction_date"
            )
            or ""
        )


        if isinstance(
            risk_score,
            (int, float),
        ):

            risk_score = (
                f"{risk_score:.2f}"
            )

        elif risk_score is None:

            risk_score = "N/A"


        rows.append(
            {
                "Patient":
                    patient_name,

                "Prediction":
                    diagnosis,

                "Risk Level":
                    risk_level,

                "Risk Score":
                    risk_score,

                "Date":
                    created_at,
            }
        )


    if rows:

        st.dataframe(
            rows,
            width="stretch",
            hide_index=True,
        )

    else:

        st.info(
            "No prediction records available."
        )


else:

    st.info(
        "No prediction history available yet."
    )


st.divider()


# ==========================================================
# System Features
# ==========================================================

st.subheader(
    "✨ Platform Features"
)


feature1, feature2, feature3 = (
    st.columns(
        3
    )
)


with feature1:

    st.markdown(
        """
### 🧪 AI Prediction

Analyze 22 voice measurements using a machine-learning
model to provide AI-assisted screening information.
        """
    )


with feature2:

    st.markdown(
        """
### 👤 Patient Management

Store and manage patient information, prediction history,
and related medical screening records.
        """
    )


with feature3:

    st.markdown(
        """
### 🤖 AI Health Assistant

Ask educational questions about Parkinson's disease,
symptoms, diagnosis, exercise, nutrition, and healthy habits.
        """
    )


st.divider()


# ==========================================================
# About
# ==========================================================

st.subheader(
    "ℹ️ About"
)


st.markdown(
    """
### Parkinson Disease Detection Agent

This platform provides:

- 🩺 AI-assisted Parkinson's screening
- 🎙️ Voice-based analysis
- 👤 Patient management
- 📋 Prediction history
- 📄 Medical report management
- 📊 Analytics
- 🤖 AI Health Assistant
- 🛠️ Administrator management

**Important:** Prediction results are AI-assisted
screening information and should not be treated as
a medical diagnosis.
"""
)


# ==========================================================
# Medical Disclaimer
# ==========================================================

st.warning(
    """
⚠️ **Medical Disclaimer**

This application provides educational and AI-assisted
screening information.

Prediction results are not a diagnosis and should not
replace professional medical advice, diagnosis,
or treatment.

If you have persistent or concerning symptoms,
consult a qualified healthcare professional.
"""
)


# ==========================================================
# Footer
# ==========================================================

st.divider()


st.caption(
    "© 2026 Parkinson Disease Detection Agent | "
    "Streamlit + FastAPI + Scikit-learn"
)
