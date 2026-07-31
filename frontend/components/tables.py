import pandas as pd
import streamlit as st


# ==========================================================
# Generic Table
# ==========================================================

def render_table(data, title=None):
    """
    Display a generic dataframe.
    """

    if title:
        st.subheader(title)

    if data is None or len(data) == 0:
        st.info("No records found.")
        return

    df = pd.DataFrame(data)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


# ==========================================================
# Patient Table
# ==========================================================

def patient_table(patients):

    render_table(
        patients,
        "👤 Patient Records"
    )


# ==========================================================
# Prediction Table
# ==========================================================

def prediction_table(predictions):

    render_table(
        predictions,
        "🧠 Prediction History"
    )


# ==========================================================
# Report Table
# ==========================================================

def report_table(reports):

    render_table(
        reports,
        "📄 Reports"
    )


# ==========================================================
# User Table
# ==========================================================

def user_table(users):

    render_table(
        users,
        "👥 Users"
    )


# ==========================================================
# Analytics Table
# ==========================================================

def analytics_table(data):

    render_table(
        data,
        "📊 Analytics"
    )


# ==========================================================
# Recent Activity Table
# ==========================================================

def activity_table(activity):

    render_table(
        activity,
        "📝 Recent Activity"
    )


# ==========================================================
# Download CSV
# ==========================================================

def download_csv(data, filename="data.csv"):

    if data is None or len(data) == 0:
        return

    df = pd.DataFrame(data)

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇ Download CSV",
        data=csv,
        file_name=filename,
        mime="text/csv",
        use_container_width=True
    )


# ==========================================================
# Record Counter
# ==========================================================

def record_count(data):

    total = len(data) if data else 0

    st.caption(f"Total Records: {total}")
