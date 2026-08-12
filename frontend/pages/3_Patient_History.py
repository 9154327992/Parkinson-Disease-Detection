import streamlit as st
import pandas as pd

from utils.api_client import (
    get_patient_history,
    delete_patient,
)


# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="Patient History",
    page_icon="👤",
    layout="wide",
)


# ==========================================================
# Header
# ==========================================================

st.title(
    "👤 Patient History"
)

st.write(
    """
    Search and review previously analyzed patient records.
    """
)

st.divider()


# ==========================================================
# Load Records
# ==========================================================

patients = get_patient_history()


if patients is None:

    st.error(
        "Unable to fetch patient records."
    )

    st.stop()


if not patients:

    st.info(
        "No patient records found yet."
    )

    st.stop()


df = pd.DataFrame(
    patients
)


# ==========================================================
# Normalize Columns
# ==========================================================

if "patient_name" not in df.columns:

    if (
        "first_name" in df.columns
        and "last_name" in df.columns
    ):

        df["patient_name"] = (
            df["first_name"].fillna("")
            + " "
            + df["last_name"].fillna("")
        ).str.strip()

    else:

        df["patient_name"] = "Unknown Patient"


# ==========================================================
# Filters
# ==========================================================

st.subheader(
    "🔍 Search & Filter"
)

filter1, filter2, filter3 = st.columns(3)

with filter1:

    search = st.text_input(
        "Patient Name",
        placeholder="Search patient...",
    )

with filter2:

    diagnosis_options = ["All"]

    if "diagnosis" in df.columns:

        diagnosis_options += sorted(
            df["diagnosis"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

    diagnosis_filter = st.selectbox(
        "Diagnosis",
        diagnosis_options,
    )

with filter3:

    risk_options = ["All"]

    if "risk_level" in df.columns:

        risk_options += sorted(
            df["risk_level"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

    risk_filter = st.selectbox(
        "Risk Level",
        risk_options,
    )


# ==========================================================
# Apply Filters
# ==========================================================

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


if (
    diagnosis_filter != "All"
    and "diagnosis" in filtered_df.columns
):

    filtered_df = filtered_df[
        filtered_df["diagnosis"]
        == diagnosis_filter
    ]


if (
    risk_filter != "All"
    and "risk_level" in filtered_df.columns
):

    filtered_df = filtered_df[
        filtered_df["risk_level"]
        == risk_filter
    ]


st.divider()


# ==========================================================
# Summary
# ==========================================================

s1, s2, s3 = st.columns(3)

with s1:

    st.metric(
        "Total Records",
        len(df),
    )

with s2:

    st.metric(
        "Matching Records",
        len(filtered_df),
    )

with s3:

    if "risk_level" in filtered_df.columns:

        high_risk = (
            filtered_df["risk_level"]
            .astype(str)
            .str.contains(
                "high",
                case=False,
                na=False,
            )
            .sum()
        )

    else:

        high_risk = 0

    st.metric(
        "High Risk",
        high_risk,
    )


st.divider()


# ==========================================================
# Patient Table
# ==========================================================

st.subheader(
    "📋 Patient Records"
)


if filtered_df.empty:

    st.warning(
        "No records match your filters."
    )

    st.stop()


display_columns = [
    column
    for column in [
        "id",
        "patient_name",
        "age",
        "gender",
        "diagnosis",
        "risk_score",
        "risk_level",
        "recommendation",
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


st.divider()


# ==========================================================
# Patient Details
# ==========================================================

st.subheader(
    "📄 Patient Details"
)


patient_names = (
    filtered_df[
        "patient_name"
    ]
    .astype(str)
    .tolist()
)


selected_name = st.selectbox(
    "Select Patient",
    patient_names,
)


patient = filtered_df[
    filtered_df["patient_name"]
    .astype(str)
    == selected_name
].iloc[0]


left, right = st.columns(2)


with left:

    st.markdown(
        "### 👤 Patient Information"
    )

    st.write(
        f"**Name:** "
        f"{patient.get('patient_name', 'N/A')}"
    )

    st.write(
        f"**Age:** "
        f"{patient.get('age', 'N/A')}"
    )

    st.write(
        f"**Gender:** "
        f"{patient.get('gender', 'N/A')}"
    )


with right:

    st.markdown(
        "### 🧠 Prediction"
    )

    st.write(
        f"**Diagnosis:** "
        f"{patient.get('diagnosis', 'N/A')}"
    )

    st.write(
        f"**Risk Score:** "
        f"{patient.get('risk_score', 'N/A')}%"
    )

    st.write(
        f"**Risk Level:** "
        f"{patient.get('risk_level', 'N/A')}"
    )


# ==========================================================
# Recommendation
# ==========================================================

if "recommendation" in patient:

    st.divider()

    st.subheader(
        "💡 Recommendation"
    )

    st.info(
        patient["recommendation"]
    )


# ==========================================================
# Delete
# ==========================================================

if "id" in patient:

    st.divider()

    st.subheader(
        "🗑 Record Management"
    )

    confirm = st.checkbox(
        "I understand this record will be deleted."
    )

    if st.button(
        "Delete Patient Record",
        disabled=not confirm,
        use_container_width=True,
    ):

        response = delete_patient(
            int(patient["id"])
        )

        if response:

            st.success(
                "Patient record deleted successfully."
            )

            st.rerun()

        else:

            st.error(
                "Unable to delete patient record."
            )


# ==========================================================
# Export
# ==========================================================

st.divider()

csv_data = filtered_df.to_csv(
    index=False
)

st.download_button(
    label="⬇ Download Filtered CSV",
    data=csv_data,
    file_name="patient_history.csv",
    mime="text/csv",
    use_container_width=True,
)
