import streamlit as st

from utils.api_client import (
    login_user,
    get_analytics,
    get_patient_history,
    get_reports,
    get_api_url,
)

from utils.session import (
    initialize_session,
    login,
    logout,
    is_logged_in,
)


# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="Parkinson Disease Detection Agent",
    page_icon="🧠",
    layout="wide",
)


# ==========================================================
# Initialize Session
# ==========================================================

initialize_session()


# ==========================================================
# Helper Functions
# ==========================================================

def safe_list(
    value,
):
    """
    Convert common API responses into a list.
    """

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


def get_metric(
    data,
    keys,
    default=0,
):
    """
    Safely retrieve a numeric metric.
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

            try:
                return int(
                    value
                )

            except (
                TypeError,
                ValueError,
            ):

                return default


    return default


# ==========================================================
# Header
# ==========================================================

st.title(
    "🧠 Parkinson Disease Detection Agent"
)

st.write(
    """
AI-assisted Parkinson's disease screening,
patient management, prediction history,
analytics, reports, and health assistance.
"""
)

st.divider()


# ==========================================================
# Authentication
# ==========================================================

st.session_state["logged_in"] = True

username = st.session_state.get(
    "username",
    "User",
)

role = st.session_state.get(
    "role",
    "User",
)

# ==========================================================
# Logged-in Header
# ==========================================================

username = st.session_state.get(
    "username",
    "User",
)

role = st.session_state.get(
    "role",
    "User",
)


st.success(
    f"Welcome, {username}"
)


# ==========================================================
# Sidebar
# ==========================================================

with st.sidebar:

    st.subheader(
        "👤 Account"
    )

    st.write(
        f"**User:** {username}"
    )

    st.write(
        f"**Role:** {role}"
    )


    st.divider()


    if st.button(
        "🚪 Logout",
        use_container_width=True,
    ):

        try:

            logout()

        except Exception:

            pass


        for key in [
            "logged_in",
            "username",
            "role",
            "user_id",
            "access_token",
            "token",
            "jwt_token",
        ]:

            st.session_state.pop(
                key,
                None,
            )


        st.rerun()


    st.divider()


    st.caption(
        f"Backend: {get_api_url()}"
    )


# ==========================================================
# Load Dashboard Data
# ==========================================================

with st.spinner(
    "Loading dashboard..."
):

    analytics = get_analytics()

    history = get_patient_history()

    reports = get_reports()


# ==========================================================
# Normalize Data
# ==========================================================

history_list = safe_list(
    history
)

reports_list = safe_list(
    reports
)


if not isinstance(
    analytics,
    dict,
):

    analytics = {}


dashboard_data = analytics.get(
    "dashboard",
    {},
)


if not isinstance(
    dashboard_data,
    dict,
):

    dashboard_data = {}


prediction_data = analytics.get(
    "prediction",
    {},
)


if not isinstance(
    prediction_data,
    dict,
):

    prediction_data = {}


# ==========================================================
# Calculate Real Values
# ==========================================================

# ----------------------------------------------------------
# Predictions
# ----------------------------------------------------------

history_prediction_count = len(
    history_list
)


analytics_prediction_count = get_metric(
    prediction_data,
    [
        "total_predictions",
    ],
    0,
)


analytics_dashboard_predictions = get_metric(
    dashboard_data,
    [
        "total_predictions",
    ],
    0,
)


total_predictions = (
    history_prediction_count
    or analytics_prediction_count
    or analytics_dashboard_predictions
)


# ----------------------------------------------------------
# Reports
# ----------------------------------------------------------

total_reports = len(
    reports_list
)


if total_reports == 0:

    total_reports = get_metric(
        dashboard_data,
        [
            "total_reports",
        ],
        0,
    )


# ----------------------------------------------------------
# Patients
# ----------------------------------------------------------

total_patients = get_metric(
    dashboard_data,
    [
        "total_patients",
    ],
    0,
)


if total_patients == 0:

    # Try analytics patient section.

    patient_data = analytics.get(
        "patient",
        {},
    )


    if isinstance(
        patient_data,
        dict,
    ):

        total_patients = get_metric(
            patient_data,
            [
                "total_patients",
                "count",
            ],
            0,
        )


# ----------------------------------------------------------
# Risk
# ----------------------------------------------------------

high_risk = get_metric(
    dashboard_data,
    [
        "high_risk_cases",
        "high_risk",
    ],
    0,
)


medium_risk = get_metric(
    dashboard_data,
    [
        "medium_risk_cases",
        "medium_risk",
    ],
    0,
)


low_risk = get_metric(
    dashboard_data,
    [
        "low_risk_cases",
        "low_risk",
    ],
    0,
)


# ==========================================================
# Main Dashboard
# ==========================================================

st.subheader(
    "📊 Dashboard Overview"
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "👤 Patients",
        total_patients,
    )


with col2:

    st.metric(
        "🧠 Predictions",
        total_predictions,
    )


with col3:

    st.metric(
        "📄 Reports",
        total_reports,
    )


with col4:

    risk_total = (
        high_risk
        + medium_risk
        + low_risk
    )

    st.metric(
        "⚠️ High Risk",
        high_risk,
    )


st.divider()


# ==========================================================
# Risk Overview
# ==========================================================

st.subheader(
    "⚠️ Risk Overview"
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
        "📋 Patient History",
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
# Recent Predictions
# ==========================================================

st.subheader(
    "📝 Recent Predictions"
)


if history_list:

    recent = history_list[
        :5
    ]


    rows = []


    for item in recent:

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
                "diagnosis"
            )
            or item.get(
                "prediction"
            )
            or item.get(
                "prediction_result"
            )
            or "Unknown"
        )


        risk_level = (
            item.get(
                "risk_level"
            )
            or item.get(
                "risk_category"
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
                "timestamp"
            )
            or item.get(
                "date"
            )
            or "N/A"
        )


        rows.append(
            {
                "Patient":
                    patient_name,

                "Diagnosis":
                    diagnosis,

                "Risk Level":
                    risk_level,

                "Risk Score":
                    (
                        f"{float(risk_score):.2f}%"
                        if risk_score is not None
                        else "N/A"
                    ),

                "Date":
                    created_at,
            }
        )


    if rows:

        st.dataframe(
            rows,
            use_container_width=True,
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
# System Status
# ==========================================================

st.subheader(
    "💻 System Status"
)


status1, status2, status3, status4 = (
    st.columns(4)
)


with status1:

    if analytics is not None:

        st.success(
            "🟢 Analytics"
        )

    else:

        st.error(
            "🔴 Analytics"
        )


with status2:

    if history is not None:

        st.success(
            "🟢 Predictions"
        )

    else:

        st.error(
            "🔴 Predictions"
        )


with status3:

    if reports is not None:

        st.success(
            "🟢 Reports"
        )

    else:

        st.error(
            "🔴 Reports"
        )


with status4:

    st.success(
        "🟢 AI Assistant"
    )


st.divider()


# ==========================================================
# Information
# ==========================================================

st.subheader(
    "ℹ️ About"
)


st.markdown(
    """
### Parkinson Disease Detection Agent

This platform provides:

- 🩺 AI-assisted Parkinson's screening
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


st.divider()


# ==========================================================
# Footer
# ==========================================================

st.caption(
    "© 2026 Parkinson Disease Detection Agent | "
    "Streamlit + FastAPI + Scikit-learn"
)
