import streamlit as st
import pandas as pd

from utils.api_client import (
    get_reports,
    download_report,
)


# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="Reports",
    page_icon="📄",
    layout="wide",
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

reports_response = get_reports()


# ==========================================================
# Handle Backend Error
# ==========================================================

if reports_response is None:

    st.error("Unable to load reports.")

    st.stop()


# ==========================================================
# Handle Report Response
# ==========================================================

if isinstance(reports_response, dict):

    reports = reports_response.get(
        "reports",
        []
    )

else:

    reports = reports_response


# ==========================================================
# No Reports
# ==========================================================

if not reports:

    st.info(
        "No reports available."
    )

    st.stop()


# ==========================================================
# Create DataFrame
# ==========================================================

df = pd.DataFrame(
    reports
)


# ==========================================================
# Search
# ==========================================================

st.subheader("🔍 Search Report")

search = st.text_input(
    "Search by Patient Name"
)


if search:

    if "patient_name" in df.columns:

        df = df[
            df["patient_name"]
            .astype(str)
            .str.contains(
                search,
                case=False,
                na=False,
            )
        ]

    else:

        st.warning(
            "Patient name is not available in the report data."
        )


# ==========================================================
# Search Result Check
# ==========================================================

if df.empty:

    st.info(
        "No reports match your search."
    )

    st.stop()


# ==========================================================
# Reports Table
# ==========================================================

st.subheader("📋 Report List")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
)


st.divider()


# ==========================================================
# Select Report
# ==========================================================

st.subheader("📄 Report Details")


if "report_id" not in df.columns:

    st.error(
        "Report ID is missing from the backend response."
    )

    st.stop()


# ----------------------------------------------------------
# Create readable report selection
# ----------------------------------------------------------

def report_label(row):

    patient_name = row.get(
        "patient_name",
        "Patient"
    )

    report_name = row.get(
        "report_name",
        "Report"
    )

    report_id = row.get(
        "report_id",
        ""
    )

    return (
        f"{patient_name} - "
        f"{report_name} "
        f"(ID: {report_id})"
    )


report_options = [
    report_label(row)
    for _, row in df.iterrows()
]


selected_report_label = st.selectbox(
    "Select Report",
    report_options,
)


selected_index = report_options.index(
    selected_report_label
)


report = df.iloc[
    selected_index
]


# ==========================================================
# Report Information
# ==========================================================

left, right = st.columns(2)


with left:

    st.write("### 👤 Patient Information")

    st.write(
        f"**Name:** "
        f"{report.get('patient_name', 'Not available')}"
    )

    st.write(
        f"**Patient ID:** "
        f"{report.get('patient_id', 'Not available')}"
    )


with right:

    st.write("### 📄 Report Information")

    st.write(
        f"**Report ID:** "
        f"{report.get('report_id', 'Not available')}"
    )

    st.write(
        f"**Report Name:** "
        f"{report.get('report_name', 'Not available')}"
    )

    st.write(
        f"**Generated On:** "
        f"{report.get('generated_at', 'Not available')}"
    )


st.divider()


# ==========================================================
# Report Details
# ==========================================================

st.subheader("📋 Report Status")

st.info(
    """
The report list currently contains report metadata.

Detailed prediction information such as diagnosis,
confidence, risk score, risk level, and recommendation
will be displayed when the report is connected to the
corresponding prediction record.
"""
)


st.divider()


# ==========================================================
# Download Report
# ==========================================================

st.subheader("⬇ Download Report")


report_id = int(
    report["report_id"]
)


download = download_report(
    report_id
)


if download:

    # ------------------------------------------------------
    # Actual PDF bytes
    # ------------------------------------------------------

    if isinstance(
        download,
        bytes
    ):

        patient_name = str(
            report.get(
                "patient_name",
                "Patient"
            )
        )

        st.download_button(
            label="📄 Download PDF",

            data=download,

            file_name=(
                f"{patient_name}_Report.pdf"
            ),

            mime="application/pdf",

            use_container_width=True,
        )

    # ------------------------------------------------------
    # Backend returned metadata
    # ------------------------------------------------------

    elif isinstance(
        download,
        dict
    ):

        st.info(
            "PDF generation is not implemented yet."
        )

        download_url = download.get(
            "download_url"
        )

        if download_url:

            st.write(
                f"Download endpoint: "
                f"{download_url}"
            )

    else:

        st.warning(
            "PDF report is not available."
        )

else:

    st.warning(
        "PDF report is not available."
    )


st.divider()


# ==========================================================
# Export CSV
# ==========================================================

st.subheader("⬇ Export Reports")

csv = df.to_csv(
    index=False
)


st.download_button(
    label="⬇ Export Reports (CSV)",

    data=csv,

    file_name="reports.csv",

    mime="text/csv",

    use_container_width=True,
)
