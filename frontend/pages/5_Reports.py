import streamlit as st
import pandas as pd

from utils.api_client import (
    get_reports,
    download_report,
    get,
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
# Backend Error
# ==========================================================

if reports_response is None:

    st.error(
        "Unable to load reports."
    )

    st.stop()


# ==========================================================
# Extract Reports
# ==========================================================

if isinstance(
    reports_response,
    dict,
):

    reports = reports_response.get(
        "reports",
        [],
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
# DataFrame
# ==========================================================

df = pd.DataFrame(
    reports
)


# ==========================================================
# Search
# ==========================================================

st.subheader("🔍 Search Report")

search = st.text_input(
    "Search by Patient Name",
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


# ==========================================================
# Search Result Check
# ==========================================================

if df.empty:

    st.info(
        "No reports match your search."
    )

    st.stop()


st.divider()


# ==========================================================
# Report List
# ==========================================================

st.subheader("📋 Report List")

display_columns = [
    column
    for column in [
        "report_id",
        "patient_id",
        "patient_name",
        "report_name",
        "generated_at",
    ]
    if column in df.columns
]

st.dataframe(
    df[display_columns],
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
# Create selection labels
# ----------------------------------------------------------

report_options = []

report_lookup = {}


for _, row in df.iterrows():

    report_id = int(
        row["report_id"]
    )

    patient_name = str(
        row.get(
            "patient_name",
            "Patient",
        )
    )

    report_name = str(
        row.get(
            "report_name",
            "Report",
        )
    )

    label = (
        f"{patient_name} - "
        f"{report_name} "
        f"(ID: {report_id})"
    )

    report_options.append(
        label
    )

    report_lookup[label] = report_id


selected_report = st.selectbox(
    "Select Report",
    report_options,
)


selected_report_id = report_lookup[
    selected_report
]


# ==========================================================
# Load Full Report
# ==========================================================

with st.spinner(
    "Loading report details..."
):

    full_report = get(
        f"/reports/{selected_report_id}"
    )


# ==========================================================
# Full Report Error
# ==========================================================

if full_report is None:

    st.error(
        "Unable to load the selected report."
    )

    st.stop()


# ==========================================================
# Extract Report Sections
# ==========================================================

metadata = full_report.get(
    "metadata",
    {},
)

patient = full_report.get(
    "patient",
    {},
)

prediction = full_report.get(
    "prediction",
    {},
)

recommendations = full_report.get(
    "recommendations",
    [],
)

exercises = full_report.get(
    "exercises",
    [],
)

medication = full_report.get(
    "medication",
    [],
)

follow_up = full_report.get(
    "follow_up",
    {},
)

doctor_notes = full_report.get(
    "doctor_notes",
)


# ==========================================================
# Patient Information
# ==========================================================

left, right = st.columns(2)


with left:

    st.subheader(
        "👤 Patient Information"
    )

    st.write(
        f"**Name:** "
        f"{patient.get('full_name', 'Not available')}"
    )

    st.write(
        f"**Patient ID:** "
        f"{patient.get('patient_id', 'Not available')}"
    )

    st.write(
        f"**Age:** "
        f"{patient.get('age', 'Not available')}"
    )

    st.write(
        f"**Gender:** "
        f"{patient.get('gender', 'Not available')}"
    )

    medical_history = patient.get(
        "medical_history"
    )

    if medical_history:

        st.write(
            f"**Medical History:** "
            f"{medical_history}"
        )


with right:

    st.subheader(
        "📄 Report Information"
    )

    st.write(
        f"**Report ID:** "
        f"{metadata.get('report_id', selected_report_id)}"
    )

    st.write(
        f"**Report Name:** "
        f"{metadata.get('report_name', 'Not available')}"
    )

    st.write(
        f"**Report Type:** "
        f"{metadata.get('report_type', 'Not available')}"
    )

    st.write(
        f"**Generated By:** "
        f"{metadata.get('generated_by', 'Not available')}"
    )

    st.write(
        f"**Generated On:** "
        f"{metadata.get('generated_at', 'Not available')}"
    )

    st.write(
        f"**Version:** "
        f"{metadata.get('version', 'Not available')}"
    )


st.divider()


# ==========================================================
# Prediction Result
# ==========================================================

st.subheader(
    "🧠 Prediction Result"
)


prediction_left, prediction_right = st.columns(2)


with prediction_left:

    st.write(
        f"**Prediction:** "
        f"{prediction.get('prediction', 'Not available')}"
    )

    st.write(
        f"**Confidence:** "
        f"{prediction.get('confidence', 'Not available')}%"
    )

    st.write(
        f"**Risk Score:** "
        f"{prediction.get('risk_score', 'Not available')}%"
    )


with prediction_right:

    st.write(
        f"**Risk Level:** "
        f"{prediction.get('risk_level', 'Not available')}"
    )

    st.write(
        f"**Recommendation:** "
        f"{prediction.get('recommendation', 'Not available')}"
    )


st.divider()


# ==========================================================
# Recommendations
# ==========================================================

st.subheader(
    "💡 Recommendations"
)


if recommendations:

    for item in recommendations:

        title = item.get(
            "title",
            "Recommendation",
        )

        description = item.get(
            "description",
            "",
        )

        st.write(
            f"**{title}**"
        )

        st.info(
            description
        )

else:

    st.info(
        "No recommendations available."
    )


st.divider()


# ==========================================================
# Exercises
# ==========================================================

st.subheader(
    "🏃 Recommended Exercises"
)


if exercises:

    exercise_data = []

    for exercise in exercises:

        exercise_data.append(
            {
                "Exercise": exercise.get(
                    "name",
                    "",
                ),

                "Duration": exercise.get(
                    "duration",
                    "",
                ),

                "Frequency": exercise.get(
                    "frequency",
                    "",
                ),

                "Description": exercise.get(
                    "description",
                    "",
                ),
            }
        )

    st.dataframe(
        pd.DataFrame(
            exercise_data
        ),
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "No exercise recommendations available."
    )


st.divider()


# ==========================================================
# Medication Guidance
# ==========================================================

st.subheader(
    "💊 Medication Guidance"
)


if medication:

    for item in medication:

        title = item.get(
            "title",
            "Medication Guidance",
        )

        description = item.get(
            "description",
            "",
        )

        st.write(
            f"**{title}**"
        )

        st.info(
            description
        )

else:

    st.info(
        "No medication guidance available."
    )


st.divider()


# ==========================================================
# Follow-up
# ==========================================================

st.subheader(
    "📅 Follow-up Plan"
)


follow_left, follow_right = st.columns(2)


with follow_left:

    st.write(
        f"**Next Visit:** "
        f"{follow_up.get('next_visit', 'Not available')}"
    )

    st.write(
        f"**Specialist:** "
        f"{follow_up.get('specialist', 'Not available')}"
    )


with follow_right:

    st.write(
        f"**Notes:** "
        f"{follow_up.get('notes', 'Not available')}"
    )


# ==========================================================
# Doctor Notes
# ==========================================================

if doctor_notes:

    st.divider()

    st.subheader(
        "📝 Doctor Notes"
    )

    st.info(
        doctor_notes
    )


st.divider()


# ==========================================================
# Download PDF
# ==========================================================

st.subheader(
    "⬇ Download Report"
)


download_response = download_report(
    selected_report_id
)


if isinstance(
    download_response,
    bytes,
):

    patient_name = str(
        patient.get(
            "full_name",
            "Patient",
        )
    )

    safe_patient_name = (
        patient_name
        .replace("/", "_")
        .replace("\\", "_")
        .replace(" ", "_")
    )

    st.download_button(
        label="📄 Download PDF",

        data=download_response,

        file_name=(
            f"{safe_patient_name}_Report.pdf"
        ),

        mime="application/pdf",

        use_container_width=True,
    )


elif isinstance(
    download_response,
    dict,
):

    # ------------------------------------------------------
    # Backend currently returns metadata rather than bytes.
    # ------------------------------------------------------

    download_url = download_response.get(
        "download_url"
    )

    if download_url:

        st.info(
            "The report download endpoint is available, "
            "but the backend has not generated the PDF file yet."
        )

        st.code(
            download_url
        )

    else:

        st.warning(
            "PDF report is not available yet."
        )


else:

    st.warning(
        "PDF report is not available."
    )


st.divider()


# ==========================================================
# Export Current Report List
# ==========================================================

st.subheader(
    "⬇ Export Reports"
)


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
