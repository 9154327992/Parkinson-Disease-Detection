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

st.title(
    "📄 Patient Reports"
)

st.write(
    """
    View, search, and manage generated patient reports.
    """
)

st.divider()


# ==========================================================
# Load Reports
# ==========================================================

reports = get_reports()


if reports is None:

    st.error(
        "Unable to load reports from the backend."
    )

    st.stop()


if not reports:

    st.info(
        "No reports are available yet."
    )

    st.stop()


df = pd.DataFrame(
    reports
)


# ==========================================================
# Normalize IDs
# ==========================================================

if "report_id" in df.columns:

    df["id"] = df["report_id"]


if "generated_at" in df.columns:

    df["created_at"] = df[
        "generated_at"
    ]


# ==========================================================
# Search
# ==========================================================

st.subheader(
    "🔍 Search Reports"
)

search = st.text_input(
    "Search by patient name or report name",
    placeholder="Search...",
)


filtered_df = df.copy()


if search:

    patient_match = (
        filtered_df[
            "patient_name"
        ]
        .astype(str)
        .str.contains(
            search,
            case=False,
            na=False,
        )
        if "patient_name"
        in filtered_df.columns
        else False
    )

    report_match = (
        filtered_df[
            "report_name"
        ]
        .astype(str)
        .str.contains(
            search,
            case=False,
            na=False,
        )
        if "report_name"
        in filtered_df.columns
        else False
    )

    filtered_df = filtered_df[
        patient_match
        | report_match
    ]


st.divider()


# ==========================================================
# Summary
# ==========================================================

c1, c2, c3 = st.columns(3)

with c1:

    st.metric(
        "Total Reports",
        len(df),
    )

with c2:

    st.metric(
        "Matching Reports",
        len(filtered_df),
    )

with c3:

    st.metric(
        "Report Type",
        "PDF",
    )


st.divider()


# ==========================================================
# Report List
# ==========================================================

st.subheader(
    "📋 Report List"
)


display_columns = [
    column
    for column in [
        "report_id",
        "patient_id",
        "patient_name",
        "report_name",
        "generated_at",
    ]
    if column in filtered_df.columns
]


st.dataframe(
    filtered_df[
        display_columns
    ] if display_columns else filtered_df,
    use_container_width=True,
    hide_index=True,
)


if filtered_df.empty:

    st.warning(
        "No reports match your search."
    )

    st.stop()


st.divider()


# ==========================================================
# Report Selection
# ==========================================================

st.subheader(
    "📄 Report Details"
)


def report_label(row):

    patient = row.get(
        "patient_name",
        "Unknown Patient",
    )

    name = row.get(
        "report_name",
        "Report",
    )

    report_id = row.get(
        "report_id",
        row.get(
            "id",
            "N/A",
        ),
    )

    return (
        f"{patient} - "
        f"{name} "
        f"(ID: {report_id})"
    )


report_options = [
    report_label(
        row
    )
    for _, row in filtered_df.iterrows()
]


selected_label = st.selectbox(
    "Select Report",
    report_options,
)


selected_index = report_options.index(
    selected_label
)


report = (
    filtered_df
    .iloc[selected_index]
)


# ==========================================================
# Details
# ==========================================================

left, right = st.columns(2)


with left:

    st.markdown(
        "### 👤 Patient Information"
    )

    st.write(
        f"**Name:** "
        f"{report.get('patient_name', 'N/A')}"
    )

    st.write(
        f"**Patient ID:** "
        f"{report.get('patient_id', 'N/A')}"
    )


with right:

    st.markdown(
        "### 📄 Report Information"
    )

    st.write(
        f"**Report ID:** "
        f"{report.get('report_id', 'N/A')}"
    )

    st.write(
        f"**Report Name:** "
        f"{report.get('report_name', 'N/A')}"
    )

    st.write(
        f"**Generated On:** "
        f"{report.get('generated_at', 'N/A')}"
    )


st.divider()


# ==========================================================
# Report Status
# ==========================================================

st.subheader(
    "📋 Report Status"
)

st.info(
    """
    This report list currently contains report metadata.

    Detailed prediction information is displayed when it is
    available from the corresponding prediction/report record.

    Actual PDF generation is intentionally left for a later phase.
    """
)


st.divider()


# ==========================================================
# Download Information
# ==========================================================

st.subheader(
    "⬇ Download Report"
)

report_id = report.get(
    "report_id",
    report.get(
        "id"
    ),
)


if report_id:

    download_info = download_report(
        int(report_id)
    )

    if isinstance(
        download_info,
        bytes,
    ):

        st.download_button(
            label="📄 Download PDF",
            data=download_info,
            file_name=(
                f"{report.get('patient_name', 'Patient')}"
                "_Report.pdf"
            ),
            mime="application/pdf",
            use_container_width=True,
        )

    elif isinstance(
        download_info,
        dict,
    ):

        st.info(
            "The backend currently provides "
            "download metadata. Actual PDF generation "
            "will be implemented later."
        )

    else:

        st.warning(
            "PDF report is not currently available."
        )


st.divider()


# ==========================================================
# CSV Export
# ==========================================================

csv_data = filtered_df.to_csv(
    index=False
)

st.download_button(
    label="⬇ Export Reports (CSV)",
    data=csv_data,
    file_name="reports.csv",
    mime="text/csv",
    use_container_width=True,
)
