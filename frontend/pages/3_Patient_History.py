import streamlit as st
import pandas as pd

from utils.api_client import (
    get_patient_history,
    delete_prediction,
)


# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="Patient History",
    page_icon="📋",
    layout="wide",
)


# ==========================================================
# Header
# ==========================================================

st.title("📋 Patient History")

st.write(
    """
View, search, filter, and manage previously analyzed
Parkinson's disease prediction records.
"""
)

st.divider()


# ==========================================================
# Helper Functions
# ==========================================================

def get_value(
    record,
    keys,
    default="",
):
    """
    Safely get the first available value from a record.

    Supports values stored at the top level as well as
    inside common nested objects such as:
        prediction
        patient
        user
    """

    if not isinstance(
        record,
        dict,
    ):
        return default

    # ------------------------------------------------------
    # Check top-level record first
    # ------------------------------------------------------

    for key in keys:

        value = record.get(
            key
        )

        if value is not None:
            return value

    # ------------------------------------------------------
    # Check nested objects
    # ------------------------------------------------------

    nested_objects = [
        record.get("prediction"),
        record.get("patient"),
        record.get("user"),
    ]

    for nested in nested_objects:

        if not isinstance(
            nested,
            dict,
        ):
            continue

        for key in keys:

            value = nested.get(
                key
            )

            if value is not None:
                return value

    return default


def get_patient_name(record):
    """
    Support multiple backend patient-name formats.
    """

    name = get_value(
        record,
        [
            "patient_name",
            "name",
            "full_name",
        ],
        "",
    )

    if name:
        return str(name)

    first_name = get_value(
        record,
        [
            "first_name",
            "firstName",
        ],
        "",
    )

    last_name = get_value(
        record,
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


def get_risk_level(record):
    """
    Normalize risk level.
    """

    risk = get_value(
        record,
        [
            "risk_level",
            "risk_category",
            "risk",
        ],
        "",
    )

    if isinstance(risk, dict):

        risk = (
            risk.get("risk_level")
            or risk.get("level")
            or risk.get("category")
            or ""
        )

    risk = str(
        risk
    ).strip()

    if "high" in risk.lower():
        return "High Risk"

    if "medium" in risk.lower():
        return "Medium Risk"

    if "low" in risk.lower():
        return "Low Risk"

    return risk or "Unknown"


def get_diagnosis(record):
    """
    Normalize diagnosis/prediction field.
    """

    value = get_value(
        record,
        [
            "diagnosis",
            "prediction",
            "prediction_result",
            "result",
        ],
        "Unknown",
    )

    if isinstance(value, dict):

        value = (
            value.get("diagnosis")
            or value.get("prediction")
            or value.get("result")
            or "Unknown"
        )

    return str(value)


def get_prediction_id(record):
    """
    Normalize prediction ID.
    """

    return get_value(
        record,
        [
            "prediction_id",
            "id",
        ],
        None,
    )


def get_risk_score(record):
    """
    Normalize risk score.
    """

    return get_value(
        record,
        [
            "risk_score",
            "risk_percentage",
            "score",
        ],
        None,
    )


def format_risk_score(value):
    """
    Format risk score safely.
    """

    if value is None:
        return "N/A"

    try:

        number = float(value)

        return f"{number:.2f}%"

    except (
        TypeError,
        ValueError,
    ):

        return str(value)


# ==========================================================
# Load History
# ==========================================================

with st.spinner(
    "Loading patient history..."
):

    history = get_patient_history()


# ==========================================================
# Backend Error
# ==========================================================

if history is None:

    st.error(
        "Unable to fetch prediction history."
    )

    st.info(
        """
Please check that the FastAPI backend is running
and that the `/prediction/history` endpoint is available.
"""
    )

    st.stop()


# ==========================================================
# Normalize Response
# ==========================================================

if isinstance(
    history,
    dict,
):

    history = (
        history.get("history")
        or history.get("predictions")
        or history.get("patients")
        or history.get("records")
        or []
    )


if not isinstance(
    history,
    list,
):

    history = []


# ==========================================================
# Empty State
# ==========================================================

if not history:

    st.info(
        "📭 No prediction history is available yet."
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
# Build Display Records
# ==========================================================

display_records = []

for record in history:

    if not isinstance(
        record,
        dict,
    ):
        continue

    display_records.append(
        {
            "Prediction ID":
                get_prediction_id(
                    record
                ),

            "Patient Name":
                get_patient_name(
                    record
                ),

            "Age":
                get_value(
                    record,
                    [
                        "age",
                        "patient_age",
                    ],
                    "N/A",
                ),

            "Gender":
                get_value(
                    record,
                    [
                        "gender",
                        "patient_gender",
                    ],
                    "N/A",
                ),

            "Diagnosis":
                get_diagnosis(
                    record
                ),

            "Risk Level":
                get_risk_level(
                    record
                ),

            "Risk Score":
                format_risk_score(
                    get_risk_score(
                        record
                    )
                ),

            "Created At":
                get_value(
                    record,
                    [
                        "created_at",
                        "created",
                        "timestamp",
                        "date",
                        "prediction_date",
                    ],
                    "N/A",
                ),

            "_raw":
                record,
        }
    )


if not display_records:

    st.warning(
        "History records were returned, but no usable records were found."
    )

    st.stop()


# ==========================================================
# Summary Metrics
# ==========================================================

total_records = len(
    display_records
)

high_count = sum(
    1
    for item in display_records
    if item["Risk Level"] == "High Risk"
)

medium_count = sum(
    1
    for item in display_records
    if item["Risk Level"] == "Medium Risk"
)

low_count = sum(
    1
    for item in display_records
    if item["Risk Level"] == "Low Risk"
)


st.subheader(
    "📊 History Overview"
)

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Total Predictions",
        total_records,
    )

with col2:

    st.metric(
        "🔴 High Risk",
        high_count,
    )

with col3:

    st.metric(
        "🟠 Medium Risk",
        medium_count,
    )

with col4:

    st.metric(
        "🟢 Low Risk",
        low_count,
    )


st.divider()


# ==========================================================
# Search & Filters
# ==========================================================

st.subheader(
    "🔎 Search & Filter"
)

filter_col1, filter_col2, filter_col3 = (
    st.columns(3)
)


with filter_col1:

    search_text = st.text_input(
        "Search Patient",
        placeholder="Enter patient name...",
    )


with filter_col2:

    risk_options = [
        "All",
        "High Risk",
        "Medium Risk",
        "Low Risk",
        "Unknown",
    ]

    selected_risk = st.selectbox(
        "Risk Level",
        risk_options,
    )


with filter_col3:

    diagnosis_options = [
        "All"
    ]

    diagnosis_values = sorted(
        {
            str(item["Diagnosis"])
            for item in display_records
            if item["Diagnosis"]
        }
    )

    diagnosis_options.extend(
        diagnosis_values
    )

    selected_diagnosis = st.selectbox(
        "Diagnosis",
        diagnosis_options,
    )


# ==========================================================
# Apply Filters
# ==========================================================

filtered_records = []

search_text = (
    search_text
    .strip()
    .lower()
)


for item in display_records:

    # ------------------------------------------------------
    # Patient Search
    # ------------------------------------------------------

    if search_text:

        patient_name = (
            item["Patient Name"]
            .lower()
        )

        if search_text not in patient_name:
            continue

    # ------------------------------------------------------
    # Risk Filter
    # ------------------------------------------------------

    if (
        selected_risk != "All"
        and item["Risk Level"]
        != selected_risk
    ):

        continue

    # ------------------------------------------------------
    # Diagnosis Filter
    # ------------------------------------------------------

    if (
        selected_diagnosis != "All"
        and item["Diagnosis"]
        != selected_diagnosis
    ):

        continue

    filtered_records.append(
        item
    )


# ==========================================================
# Filter Result
# ==========================================================

st.caption(
    f"Showing {len(filtered_records)} "
    f"of {total_records} prediction records."
)


# ==========================================================
# History Table
# ==========================================================

st.subheader(
    "📋 Prediction Records"
)


if not filtered_records:

    st.warning(
        "No records match the selected filters."
    )

else:

    table_rows = []

    for item in filtered_records:

        table_rows.append(
            {
                "Prediction ID":
                    item["Prediction ID"],

                "Patient Name":
                    item["Patient Name"],

                "Age":
                    item["Age"],

                "Gender":
                    item["Gender"],

                "Diagnosis":
                    item["Diagnosis"],

                "Risk Level":
                    item["Risk Level"],

                "Risk Score":
                    item["Risk Score"],

                "Created At":
                    item["Created At"],
            }
        )

    history_df = pd.DataFrame(
        table_rows
    )

    st.dataframe(
        history_df,
        use_container_width=True,
        hide_index=True,
    )


st.divider()


# ==========================================================
# Record Details
# ==========================================================

st.subheader(
    "🔍 Prediction Details"
)


if filtered_records:

    detail_labels = []

    for index, item in enumerate(
        filtered_records
    ):

        prediction_id = (
            item["Prediction ID"]
        )

        patient_name = (
            item["Patient Name"]
        )

        label = (
            f"{patient_name} "
            f"— Prediction #{prediction_id}"
        )

        detail_labels.append(
            label
        )

    selected_detail = st.selectbox(
        "Select a prediction",
        detail_labels,
    )

    selected_index = detail_labels.index(
        selected_detail
    )

    selected_record = (
        filtered_records[
            selected_index
        ]
    )


    detail_col1, detail_col2 = (
        st.columns(2)
    )


    with detail_col1:

        st.write(
            f"**Patient:** "
            f"{selected_record['Patient Name']}"
        )

        st.write(
            f"**Age:** "
            f"{selected_record['Age']}"
        )

        st.write(
            f"**Gender:** "
            f"{selected_record['Gender']}"
        )

        st.write(
            f"**Prediction ID:** "
            f"{selected_record['Prediction ID']}"
        )


    with detail_col2:

        st.write(
            f"**Diagnosis:** "
            f"{selected_record['Diagnosis']}"
        )

        st.write(
            f"**Risk Level:** "
            f"{selected_record['Risk Level']}"
        )

        st.write(
            f"**Risk Score:** "
            f"{selected_record['Risk Score']}"
        )

        st.write(
            f"**Created At:** "
            f"{selected_record['Created At']}"
        )


    st.divider()


    # ======================================================
    # Delete Prediction
    # ======================================================

    prediction_id = (
        selected_record["Prediction ID"]
    )


    if prediction_id is not None:

        st.subheader(
            "🗑 Record Management"
        )

        confirm_delete = st.checkbox(
            "I understand that deleting this prediction cannot be undone."
        )


        if st.button(
            "🗑 Delete Selected Prediction",
            type="secondary",
            disabled=not confirm_delete,
            use_container_width=True,
        ):

            try:

                success = delete_prediction(
                    prediction_id
                )

            except Exception:

                success = False


            if success:

                st.success(
                    "Prediction deleted successfully."
                )

                st.rerun()

            else:

                st.error(
                    "Unable to delete the selected prediction."
                )


st.divider()


# ==========================================================
# Export
# ==========================================================

st.subheader(
    "⬇ Export History"
)


export_rows = []

for item in filtered_records:

    export_rows.append(
        {
            "Prediction ID":
                item["Prediction ID"],

            "Patient Name":
                item["Patient Name"],

            "Age":
                item["Age"],

            "Gender":
                item["Gender"],

            "Diagnosis":
                item["Diagnosis"],

            "Risk Level":
                item["Risk Level"],

            "Risk Score":
                item["Risk Score"],

            "Created At":
                item["Created At"],
        }
    )


export_df = pd.DataFrame(
    export_rows
)


csv_data = export_df.to_csv(
    index=False
)


st.download_button(
    label="⬇ Download Patient History (CSV)",
    data=csv_data,
    file_name="patient_history.csv",
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
        "📄 View Reports",
        use_container_width=True,
    ):

        st.switch_page(
            "pages/5_Reports.py"
        )


# ==========================================================
# Footer
# ==========================================================

st.caption(
    "Patient History | "
    "Parkinson Disease Detection Agent"
)
