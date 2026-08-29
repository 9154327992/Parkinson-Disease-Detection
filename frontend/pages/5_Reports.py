import streamlit as st
import pandas as pd
from pathlib import Path
from utils.api_client import (
    get,
    get_reports,
    download_report,
)

IMAGE_PATH = (
    Path(__file__).resolve().parents[1]
    / "assets"
    / "images"
    / "report_banner.png"
)

if IMAGE_PATH.exists():
    st.image(
        str(IMAGE_PATH),
        use_container_width=True,
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
View, search, download, and manage generated
patient assessment reports.
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
    Return the first available value from a dictionary.
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


def get_report_id(
    report,
):
    """
    Support report_id and id.
    """

    return get_value(
        report,
        [
            "report_id",
            "id",
        ],
        None,
    )


def get_patient_name(
    report,
):
    """
    Support different patient name fields.
    """

    name = get_value(
        report,
        [
            "patient_name",
            "name",
            "full_name",
        ],
        None,
    )

    if name:
        return str(name)

    first_name = get_value(
        report,
        [
            "first_name",
            "firstName",
        ],
        "",
    )

    last_name = get_value(
        report,
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


def get_generated_at(
    report,
):
    """
    Support generated_at and created_at.
    """

    return get_value(
        report,
        [
            "generated_at",
            "created_at",
            "created",
            "date",
        ],
        "N/A",
    )


def get_report_name(
    report,
):
    """
    Get report name.
    """

    return get_value(
        report,
        [
            "report_name",
            "name",
            "title",
        ],
        "Assessment Report",
    )


def extract_prediction(
    detail,
):
    """
    Extract prediction section from a detailed
    report response when the backend provides one.
    """

    if not isinstance(
        detail,
        dict,
    ):
        return {}

    prediction = detail.get(
        "prediction"
    )

    if isinstance(
        prediction,
        dict,
    ):
        return prediction

    return {}


def normalize_risk(
    value,
):
    """
    Normalize risk level.
    """

    if value is None:
        return "Not available"

    text = str(
        value
    ).strip()

    if "high" in text.lower():
        return "High Risk"

    if "medium" in text.lower():
        return "Medium Risk"

    if "low" in text.lower():
        return "Low Risk"

    return text


# ==========================================================
# Load Reports
# ==========================================================

with st.spinner(
    "Loading reports..."
):

    reports = get_reports()


if reports is None:

    st.error(
        "Unable to load reports."
    )

    st.info(
        """
The FastAPI `/reports` endpoint could not be reached.
Please check the backend connection.
"""
    )

    st.stop()


# ==========================================================
# Normalize Response
# ==========================================================

if isinstance(
    reports,
    dict,
):

    reports = (
        reports.get("reports")
        or reports.get("data")
        or reports.get("records")
        or []
    )


if not isinstance(
    reports,
    list,
):

    reports = []


# ==========================================================
# Empty State
# ==========================================================

if not reports:

    st.info(
        "📭 No reports are available yet."
    )

    st.divider()

    if st.button(
        "🩺 Create New Prediction",
        use_container_width=True,
    ):

        st.switch_page(
            "pages/2_Prediction.py"
        )

    st.stop()


# ==========================================================
# Normalize Reports
# ==========================================================

normalized_reports = []

for report in reports:

    if not isinstance(
        report,
        dict,
    ):
        continue

    normalized_reports.append(
        {
            "report_id":
                get_report_id(
                    report
                ),

            "patient_id":
                get_value(
                    report,
                    [
                        "patient_id",
                    ],
                    "N/A",
                ),

            "patient_name":
                get_patient_name(
                    report
                ),

            "report_name":
                get_report_name(
                    report
                ),

            "generated_at":
                get_generated_at(
                    report
                ),

            "_raw":
                report,
        }
    )


if not normalized_reports:

    st.warning(
        "Reports were returned, but no usable report records were found."
    )

    st.stop()


# ==========================================================
# Summary
# ==========================================================

st.subheader(
    "📊 Report Summary"
)

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "📄 Total Reports",
        len(
            normalized_reports
        ),
    )

with col2:

    unique_patients = len(
        {
            str(
                report["patient_id"]
            )
            for report in normalized_reports
            if report["patient_id"] != "N/A"
        }
    )

    st.metric(
        "👤 Patients",
        unique_patients,
    )

with col3:

    st.metric(
        "📋 Report Type",
        "Assessment",
    )


st.divider()


# ==========================================================
# Search
# ==========================================================

st.subheader(
    "🔍 Search Reports"
)

search = st.text_input(
    "Search by Patient Name",
    placeholder="Enter patient name...",
)


filtered_reports = normalized_reports


if search:

    search_lower = (
        search
        .strip()
        .lower()
    )

    filtered_reports = [
        report
        for report in normalized_reports
        if search_lower
        in report[
            "patient_name"
        ].lower()
    ]


st.caption(
    f"Showing {len(filtered_reports)} "
    f"of {len(normalized_reports)} reports."
)


# ==========================================================
# Report List
# ==========================================================

st.subheader(
    "📋 Report List"
)


if not filtered_reports:

    st.warning(
        "No reports match your search."
    )

else:

    table_rows = []

    for report in filtered_reports:

        table_rows.append(
            {
                "Report ID":
                    report["report_id"],

                "Patient ID":
                    report["patient_id"],

                "Patient Name":
                    report["patient_name"],

                "Report":
                    report["report_name"],

                "Generated On":
                    report["generated_at"],
            }
        )


    reports_df = pd.DataFrame(
        table_rows
    )


    st.dataframe(
        reports_df,
        use_container_width=True,
        hide_index=True,
    )


st.divider()


# ==========================================================
# Select Report
# ==========================================================

st.subheader(
    "📄 Report Details"
)


if not filtered_reports:

    st.info(
        "Selectable reports are unavailable."
    )

    st.stop()


report_options = []

for index, report in enumerate(
    filtered_reports
):

    report_id = report[
        "report_id"
    ]

    report_options.append(
        (
            f"{report['patient_name']} "
            f"— {report['report_name']} "
            f"(ID: {report_id})",
            index,
        )
    )


selected_label = st.selectbox(
    "Select Report",
    [
        item[0]
        for item in report_options
    ],
)


selected_index = next(
    index
    for label, index
    in report_options
    if label == selected_label
)


report = filtered_reports[
    selected_index
]


report_id = report[
    "report_id"
]


# ==========================================================
# Fetch Detailed Report
# ==========================================================

detail = None


if report_id is not None:

    with st.spinner(
        "Loading report details..."
    ):

        detail = get(
            f"/reports/{report_id}"
        )


# ==========================================================
# Determine Prediction Details
# ==========================================================

prediction = extract_prediction(
    detail
)


diagnosis = get_value(
    prediction,
    [
        "prediction",
        "diagnosis",
        "prediction_result",
    ],
    None,
)


confidence = get_value(
    prediction,
    [
        "confidence",
        "prediction_confidence",
    ],
    None,
)


risk_score = get_value(
    prediction,
    [
        "risk_score",
        "risk",
    ],
    None,
)


risk_level = get_value(
    prediction,
    [
        "risk_level",
        "risk_category",
    ],
    None,
)


recommendation = get_value(
    prediction,
    [
        "recommendation",
    ],
    None,
)


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
        f"{report['patient_name']}"
    )

    st.write(
        f"**Patient ID:** "
        f"{report['patient_id']}"
    )


with right:

    st.write(
        "### 📄 Report Information"
    )

    st.write(
        f"**Report ID:** "
        f"{report_id}"
    )

    st.write(
        f"**Report Name:** "
        f"{report['report_name']}"
    )

    st.write(
        f"**Generated On:** "
        f"{report['generated_at']}"
    )


st.divider()


# ==========================================================
# Prediction Information
# ==========================================================

st.subheader(
    "🧠 Prediction Information"
)


if prediction:

    prediction_col1, prediction_col2, prediction_col3 = (
        st.columns(3)
    )


    with prediction_col1:

        st.metric(
            "Diagnosis",
            diagnosis or "Not available",
        )


    with prediction_col2:

        if risk_score is None:

            score_display = "Not available"

        else:

            try:

                score_display = (
                    f"{float(risk_score):.2f}%"
                )

            except (
                TypeError,
                ValueError,
            ):

                score_display = str(
                    risk_score
                )


        st.metric(
            "Risk Score",
            score_display,
        )


    with prediction_col3:

        st.metric(
            "Risk Level",
            normalize_risk(
                risk_level
            )
            if risk_level
            else "Not available",
        )


    if confidence is not None:

        try:

            confidence_value = float(
                confidence
            )

            if confidence_value <= 1:
                confidence_value *= 100

            st.write(
                f"**Confidence:** "
                f"{confidence_value:.2f}%"
            )

        except (
            TypeError,
            ValueError,
        ):

            st.write(
                f"**Confidence:** "
                f"{confidence}"
            )


else:

    st.info(
        """
The report list currently contains report metadata only.
Detailed prediction information is not available from
the selected report endpoint.
"""
    )


st.divider()


# ==========================================================
# Recommendation
# ==========================================================

st.subheader(
    "💡 Recommendation"
)


if recommendation:

    st.info(
        str(
            recommendation
        )
    )

else:

    st.info(
        """
No recommendation is available in the current
report response.
"""
    )


st.divider()


# ==========================================================
# Raw Backend Details
# ==========================================================

with st.expander(
    "🔎 View Backend Report Data"
):

    if detail is not None:

        st.json(
            detail
        )

    else:

        st.json(
            report["_raw"]
        )


st.divider()


# ==========================================================
# Download PDF
# ==========================================================

st.subheader(
    "⬇ Download Report"
)


if report_id is None:

    st.warning(
        "This report does not have a valid report ID."
    )

else:

    with st.spinner(
        "Preparing PDF..."
    ):

        pdf = download_report(
            report_id
        )


    # ------------------------------------------------------
    # Binary PDF
    # ------------------------------------------------------

    if isinstance(
        pdf,
        bytes,
    ) and pdf:

        filename = (
            f"{report['patient_name']}"
            f"_Report_{report_id}.pdf"
        )


        st.download_button(
            label="📄 Download PDF",
            data=pdf,
            file_name=filename,
            mime="application/pdf",
            use_container_width=True,
        )


    # ------------------------------------------------------
    # Backend returned metadata/string
    # ------------------------------------------------------

    elif pdf:

        st.warning(
            """
The backend returned report download information,
but not the PDF file itself.
"""
        )

        if isinstance(
            pdf,
            dict,
        ):

            download_url = (
                pdf.get(
                    "download_url"
                )
                or pdf.get(
                    "url"
                )
            )

            if download_url:

                st.write(
                    f"Download endpoint: "
                    f"`{download_url}`"
                )

    else:

        st.warning(
            "PDF report is not currently available."
        )


st.divider()


# ==========================================================
# Export CSV
# ==========================================================

st.subheader(
    "⬇ Export Reports"
)


export_rows = []

for item in filtered_reports:

    export_rows.append(
        {
            "Report ID":
                item["report_id"],

            "Patient ID":
                item["patient_id"],

            "Patient Name":
                item["patient_name"],

            "Report Name":
                item["report_name"],

            "Generated At":
                item["generated_at"],
        }
    )


export_df = pd.DataFrame(
    export_rows
)


csv_data = export_df.to_csv(
    index=False
)


st.download_button(
    label="⬇ Export Reports (CSV)",
    data=csv_data,
    file_name="reports.csv",
    mime="text/csv",
    use_container_width=True,
)


st.divider()


# ==========================================================
# Navigation
# ==========================================================

st.subheader(
    "🚀 Next Actions"
)

nav1, nav2 = st.columns(2)


with nav1:

    if st.button(
        "🩺 New Prediction",
        use_container_width=True,
    ):

        st.switch_page(
            "pages/2_Prediction.py"
        )


with nav2:

    if st.button(
        "📋 Patient History",
        use_container_width=True,
    ):

        st.switch_page(
            "pages/3_Patient_History.py"
        )


# ==========================================================
# Footer
# ==========================================================

st.caption(
    "Reports | "
    "Parkinson Disease Detection Agent"
)
