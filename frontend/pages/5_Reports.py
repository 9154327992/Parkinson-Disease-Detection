import streamlit as st
import pandas as pd

from utils.api_client import (
    get_reports,
    download_report
)

# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="Reports",
    page_icon="📄",
    layout="wide"
)

# ==========================================================
# Header
# ==========================================================

st.title("📄 Patient Reports")

st.write(
    """
View, search, download, and manage generated patient reports.
"""
)

st.divider()

# ==========================================================
# Load Reports
# ==========================================================

reports = get_reports()

if reports is None:

    st.error("Unable to load reports.")

    st.stop()

if len(reports) == 0:

    st.info("No reports available.")

    st.stop()

df = pd.DataFrame(reports)

# ==========================================================
# Search
# ==========================================================

st.subheader("🔍 Search Report")

search = st.text_input(
    "Search by Patient Name"
)

if search:

    df = df[
        df["patient_name"].str.contains(
            search,
            case=False,
            na=False
        )
    ]

# ==========================================================
# Reports Table
# ==========================================================

st.subheader("📋 Report List")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

st.divider()

# ==========================================================
# Select Report
# ==========================================================

st.subheader("📄 Report Details")

selected_patient = st.selectbox(
    "Select Patient",
    df["patient_name"].tolist()
)

report = df[
    df["patient_name"] == selected_patient
].iloc[0]

left, right = st.columns(2)

with left:

    st.write("### Patient Information")

    st.write(f"**Name:** {report['patient_name']}")

    st.write(f"**Diagnosis:** {report['diagnosis']}")

    st.write(f"**Risk Level:** {report['risk_level']}")

with right:

    st.write("### Report")

    st.write(f"**Risk Score:** {report['risk_score']}%")

    st.write(f"**Generated On:** {report['created_at']}")

st.divider()

# ==========================================================
# Recommendation
# ==========================================================

st.subheader("💡 Recommendation")

st.info(report["recommendation"])

st.divider()

# ==========================================================
# Download PDF
# ==========================================================

st.subheader("⬇ Download Report")

pdf = download_report(report["id"])

if pdf:

    st.download_button(

        label="📄 Download PDF",

        data=pdf,

        file_name=f"{report['patient_name']}_Report.pdf",

        mime="application/pdf",

        use_container_width=True

    )

else:

    st.warning("PDF report not available.")

# ==========================================================
# Export CSV
# ==========================================================

csv = df.to_csv(index=False)

st.download_button(

    label="⬇ Export Reports (CSV)",

    data=csv,

    file_name="reports.csv",

    mime="text/csv",

    use_container_width=True

)
