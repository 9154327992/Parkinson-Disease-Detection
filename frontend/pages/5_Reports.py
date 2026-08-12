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
    View, search, download, and manage generated
    patient reports.
    """
)

st.divider()


# ==========================================================
# Load Reports
# ==========================================================

with st.spinner("Loading reports..."):

    reports = get_reports()


if reports is None:

    st.error(
        "Unable to connect to the Reports API."
    )

    st.info(
        "Please make sure you are logged in "
        "and the FastAPI backend is running."
    )

    st.stop()


if not isinstance(
    reports,
    list,
):

    reports = []


if len(reports) == 0:

    st.info(
        "📭 No reports are available yet."
    )

    st.write(
        """
        Generate a patient prediction first.
        A report can then be generated from the
        prediction information.
        """
    )

    st.stop()


# ==========================================================
# Convert to DataFrame
# ==========================================================

df = pd.DataFrame(
    reports
)


# ==========================================================
# Normalize Column Names
# ==========================================================

# Make sure commonly used columns exist.
default_columns = {
    "id": "",
    "patient_name": "Unknown",
    "diagnosis": "Unknown",
    "prediction": "",
    "risk_score": 0,
    "risk_level": "Unknown",
    "recommendation": "",
    "created_at": "",
}


for column, default in default_columns.items():

    if column not in df.columns:

        df[column] = default


# ==========================================================
# Search
# ==========================================================

st.subheader("🔍 Search Reports")

search = st.text_input(
    "Search by Patient Name",
    placeholder="Enter patient name...",
)


filtered_df = df.copy()


if search:

    filtered_df = filtered_df[
        filtered_df[
            "patient_name"
        ]
        .astype(str)
        .str.contains(
            search,
            case=False,
            na=False,
        )
    ]


if len(filtered_df) == 0:

    st.warning(
        "No reports match your search."
    )

    st.stop()


st.divider()


# ==========================================================
# Summary
# ==========================================================

st.subheader("📊 Report Summary")

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Total Reports",
        len(filtered_df),
    )


with col2:

    high_risk = len(
        filtered_df[
            filtered_df[
                "risk_level"
            ]
            .astype(str)
            .str.contains(
                "high",
                case=False,
                na=False,
            )
        ]
    )

    st.metric(
        "High Risk",
        high_risk,
    )


with col3:

    parkinson = len(
        filtered_df[
            filtered_df[
                "diagnosis"
            ]
            .astype(str)
            .str.contains(
                "parkinson",
                case=False,
                na=False,
            )
            |
            filtered_df[
                "prediction"
            ]
            .astype(str)
            .str.contains(
                "parkinson",
                case=False,
                na=False,
            )
        ]
    )

    st.metric(
        "Parkinson Cases",
        parkinson,
    )


with col4:

    healthy = len(
        filtered_df[
            filtered_df[
                "diagnosis"
            ]
            .astype(str)
            .str.contains(
                "healthy",
                case=False,
                na=False,
            )
            |
            filtered_df[
                "prediction"
            ]
            .astype(str)
            .str.contains(
                "healthy",
                case=False,
                na=False,
            )
        ]
    )

    st.metric(
        "Healthy Cases",
        healthy,
    )


st.divider()


# ==========================================================
# Reports Table
# ==========================================================

st.subheader("📋 Report List")


display_columns = [
    "id",
    "patient_name",
    "diagnosis",
    "prediction",
    "risk_score",
    "risk_level",
    "created_at",
]


available_columns = [
    column
    for column in display_columns
    if column in filtered_df.columns
]


display_df = filtered_df[
    available_columns
].copy()


# Rename columns for better display.
display_df = display_df.rename(
    columns={
        "id": "Report ID",
        "patient_name": "Patient Name",
        "diagnosis": "Diagnosis",
        "prediction": "Prediction",
        "risk_score": "Risk Score",
        "risk_level": "Risk Level",
        "created_at": "Generated On",
    }
)


st.dataframe(
    display_df,
    width="stretch",
    hide_index=True,
)


st.divider()


# ==========================================================
# Select Report
# ==========================================================

st.subheader("📄 Report Details")


# Use index rather than patient name so
# duplicate patient names do not cause ambiguity.

report_indices = filtered_df.index.tolist()


selected_index = st.selectbox(
    "Select Report",
    report_indices,
    format_func=lambda index: (
        f"Report #{filtered_df.loc[index, 'id']} "
        f"— "
        f"{filtered_df.loc[index, 'patient_name']}"
    ),
)


report = filtered_df.loc[
    selected_index
]


# ==========================================================
# Patient Information
# ==========================================================

left, right = st.columns(2)


with left:

    st.write(
        "### 👤 Patient Information"
    )

    st.write(
        f"**Name:** "
        f"{report.get('patient_name', 'Unknown')}"
    )

    if (
        "age" in report
        and pd.notna(report["age"])
    ):

        st.write(
            f"**Age:** "
            f"{report['age']}"
        )

    if (
        "gender" in report
        and pd.notna(report["gender"])
    ):

        st.write(
            f"**Gender:** "
            f"{report['gender']}"
        )


with right:

    st.write(
        "### 🧠 Prediction"
    )

    diagnosis = (
        report.get(
            "diagnosis"
        )
        or report.get(
            "prediction"
        )
        or "Unknown"
    )

    st.write(
        f"**Diagnosis:** "
        f"{diagnosis}"
    )

    st.write(
        f"**Risk Score:** "
        f"{report.get('risk_score', 0)}%"
    )

    st.write(
        f"**Risk Level:** "
        f"{report.get('risk_level', 'Unknown')}"
    )


st.divider()


# ==========================================================
# Recommendation
# ==========================================================

st.subheader("💡 Recommendation")


recommendation = report.get(
    "recommendation",
    "",
)


if recommendation:

    st.info(
        recommendation
    )

else:

    st.info(
        "No recommendation is available "
        "for this report."
    )


st.divider()


# ==========================================================
# Report Metadata
# ==========================================================

st.subheader("ℹ️ Report Information")


metadata_col1, metadata_col2 = st.columns(2)


with metadata_col1:

    st.write(
        f"**Report ID:** "
        f"{report.get('id', 'N/A')}"
    )


with metadata_col2:

    st.write(
        f"**Generated On:** "
        f"{report.get('created_at', 'N/A')}"
    )


st.divider()


# ==========================================================
# Download PDF
# ==========================================================

st.subheader("⬇️ Download Report")


report_id = report.get(
    "id"
)


if not report_id:

    st.warning(
        "This report does not have a valid ID."
    )

else:

    if st.button(
        "📄 Prepare PDF Report",
        width="stretch",
    ):

        with st.spinner(
            "Preparing PDF report..."
        ):

            pdf = download_report(
                int(report_id)
            )

        if pdf:

            # Store PDF in session so that
            # Streamlit reruns don't immediately
            # lose the generated download.
            st.session_state[
                "report_pdf"
            ] = pdf

            st.session_state[
                "report_pdf_id"
            ] = report_id

            st.success(
                "PDF report is ready."
            )

        else:

            st.error(
                "Unable to generate or download "
                "the PDF report."
            )


# ----------------------------------------------------------
# Display Download Button
# ----------------------------------------------------------

pdf = st.session_state.get(
    "report_pdf"
)

pdf_id = st.session_state.get(
    "report_pdf_id"
)


if (
    pdf
    and pdf_id == report_id
):

    patient_name = str(
        report.get(
            "patient_name",
            "Patient",
        )
    )

    safe_name = (
        patient_name
        .replace(
            " ",
            "_",
        )
        .replace(
            "/",
            "_",
        )
        .replace(
            "\\",
            "_",
        )
    )

    st.download_button(
        label="⬇️ Download PDF",
        data=pdf,
        file_name=(
            f"{safe_name}_Report.pdf"
        ),
        mime="application/pdf",
        width="stretch",
    )


st.divider()


# ==========================================================
# Export CSV
# ==========================================================

st.subheader(
    "⬇️ Export Reports"
)


csv_data = filtered_df.to_csv(
    index=False
)


st.download_button(
    label="📊 Export Reports (CSV)",
    data=csv_data,
    file_name="reports.csv",
    mime="text/csv",
    width="stretch",
)


st.divider()


# ==========================================================
# Footer
# ==========================================================

st.caption(
    "Parkinson Disease Detection System "
    "• Patient Reports"
)
