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
    View, search, and manage previously analyzed
    patient prediction records.
    """
)

st.divider()

# ==========================================================
# Load History
# ==========================================================

with st.spinner("Loading patient history..."):

    history = get_patient_history()

if history is None:

    st.error(
        "Unable to fetch patient history."
    )

    st.info(
        "Please check your login and backend connection."
    )

    st.stop()

if not isinstance(history, list):

    history = []

if len(history) == 0:

    st.info(
        "📭 No prediction history available."
    )

    st.write(
        """
        Create a prediction from the Prediction page
        to see patient history here.
        """
    )

    st.stop()

# ==========================================================
# DataFrame
# ==========================================================

df = pd.DataFrame(history)

# ==========================================================
# Normalize Backend Fields
# ==========================================================

field_defaults = {
    "id": "",
    "patient_id": "",
    "patient_name": "Unknown",
    "age": None,
    "gender": "Unknown",
    "diagnosis": "",
    "prediction": "",
    "prediction_result": "",
    "risk_score": None,
    "risk_level": "Unknown",
    "confidence": None,
    "recommendation": "",
    "created_at": "",
}

for field, default in field_defaults.items():

    if field not in df.columns:

        df[field] = default

# ==========================================================
# Normalize Diagnosis
# ==========================================================

def get_diagnosis(row):

    diagnosis = row.get(
        "diagnosis"
    )

    if (
        diagnosis is not None
        and str(diagnosis).strip()
        and str(diagnosis).lower()
        != "nan"
    ):

        return str(diagnosis)

    prediction = row.get(
        "prediction"
    )

    if (
        prediction is not None
        and str(prediction).strip()
        and str(prediction).lower()
        != "nan"
    ):

        return str(prediction)

    prediction_result = row.get(
        "prediction_result"
    )

    if (
        prediction_result is not None
        and str(prediction_result).strip()
        and str(prediction_result).lower()
        != "nan"
    ):

        return str(
            prediction_result
        )

    return "Unknown"


df["display_diagnosis"] = df.apply(
    get_diagnosis,
    axis=1,
)

# ==========================================================
# Normalize Risk Score
# ==========================================================

def get_risk_score(row):

    value = row.get(
        "risk_score"
    )

    if (
        value is None
        or pd.isna(value)
    ):

        value = row.get(
            "risk"
        )

    if (
        value is None
        or pd.isna(value)
    ):

        return None

    try:

        return float(value)

    except (
        TypeError,
        ValueError,
    ):

        return None


df["display_risk_score"] = df.apply(
    get_risk_score,
    axis=1,
)

# ==========================================================
# Normalize Confidence
# ==========================================================

def get_confidence(row):

    value = row.get(
        "confidence"
    )

    if (
        value is None
        or pd.isna(value)
    ):

        return None

    try:

        return float(value)

    except (
        TypeError,
        ValueError,
    ):

        return None


df["display_confidence"] = df.apply(
    get_confidence,
    axis=1,
)

# ==========================================================
# Search
# ==========================================================

st.subheader("🔍 Search Patient")

search = st.text_input(
    "Search by patient name",
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
        "No patients match your search."
    )

    st.stop()

# ==========================================================
# Summary
# ==========================================================

st.subheader("📊 History Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Total Records",
        len(filtered_df),
    )

with col2:

    parkinson_count = (
        filtered_df[
            "display_diagnosis"
        ]
        .astype(str)
        .str.contains(
            "parkinson",
            case=False,
            na=False,
        )
        .sum()
    )

    st.metric(
        "Parkinson Cases",
        int(parkinson_count),
    )

with col3:

    high_risk_count = (
        filtered_df[
            "risk_level"
        ]
        .astype(str)
        .str.contains(
            "high",
            case=False,
            na=False,
        )
        .sum()
    )

    st.metric(
        "High Risk",
        int(high_risk_count),
    )

with col4:

    valid_scores = (
        filtered_df[
            "display_risk_score"
        ]
        .dropna()
    )

    if len(valid_scores):

        average_risk = (
            valid_scores.mean()
        )

        risk_display = (
            f"{average_risk:.1f}%"
        )

    else:

        risk_display = "N/A"

    st.metric(
        "Average Risk",
        risk_display,
    )

st.divider()

# ==========================================================
# History Table
# ==========================================================

st.subheader("📋 Prediction Records")

table = filtered_df.copy()

table["Diagnosis"] = table[
    "display_diagnosis"
]

table["Risk Score"] = table[
    "display_risk_score"
].apply(
    lambda x:
        f"{x:.1f}%"
        if x is not None
        and not pd.isna(x)
        else "N/A"
)

table["Confidence"] = table[
    "display_confidence"
].apply(
    lambda x:
        f"{x:.1f}%"
        if x is not None
        and not pd.isna(x)
        else "N/A"
)

table["Age"] = table[
    "age"
].apply(
    lambda x:
        str(int(x))
        if pd.notna(x)
        and str(x).replace(
            ".",
            "",
            1,
        ).isdigit()
        else "N/A"
)

table["Gender"] = table[
    "gender"
].fillna(
    "Unknown"
)

table["Risk Level"] = table[
    "risk_level"
].fillna(
    "Unknown"
)

display_columns = [
    "id",
    "patient_name",
    "Age",
    "Gender",
    "Diagnosis",
    "Risk Score",
    "Risk Level",
    "Confidence",
    "created_at",
]

available_columns = [
    column
    for column in display_columns
    if column in table.columns
]

display_table = table[
    available_columns
].copy()

display_table = display_table.rename(
    columns={
        "id": "ID",
        "patient_name": "Patient",
        "created_at": "Date",
    }
)

st.dataframe(
    display_table,
    width="stretch",
    hide_index=True,
)

st.divider()

# ==========================================================
# Select Record
# ==========================================================

st.subheader("👤 Patient Details")

record_indices = (
    filtered_df.index.tolist()
)

selected_index = st.selectbox(
    "Select Prediction Record",
    record_indices,
    format_func=lambda index: (
        f"#{filtered_df.loc[index, 'id']} "
        f"— "
        f"{filtered_df.loc[index, 'patient_name']}"
    ),
)

record = filtered_df.loc[
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
        f"**Patient Name:** "
        f"{record.get('patient_name', 'Unknown')}"
    )

    age = record.get(
        "age"
    )

    if (
        age is not None
        and not pd.isna(age)
    ):

        try:

            age_display = int(
                float(age)
            )

        except (
            TypeError,
            ValueError,
        ):

            age_display = age

    else:

        age_display = "N/A"

    st.write(
        f"**Age:** {age_display}"
    )

    gender = record.get(
        "gender"
    )

    if (
        gender is None
        or pd.isna(gender)
        or str(gender).strip() == ""
    ):

        gender = "Unknown"

    st.write(
        f"**Gender:** {gender}"
    )

    patient_id = record.get(
        "patient_id"
    )

    if (
        patient_id is not None
        and not pd.isna(patient_id)
    ):

        st.write(
            f"**Patient ID:** {patient_id}"
        )

with right:

    st.write(
        "### 🧠 Prediction Result"
    )

    diagnosis = record.get(
        "display_diagnosis",
        "Unknown",
    )

    st.write(
        f"**Diagnosis:** {diagnosis}"
    )

    risk_level = record.get(
        "risk_level"
    )

    if (
        risk_level is None
        or pd.isna(risk_level)
    ):

        risk_level = "Unknown"

    st.write(
        f"**Risk Level:** {risk_level}"
    )

    risk_score = record.get(
        "display_risk_score"
    )

    if (
        risk_score is not None
        and not pd.isna(risk_score)
    ):

        st.write(
            f"**Risk Score:** "
            f"{risk_score:.2f}%"
        )

    else:

        st.write(
            "**Risk Score:** N/A"
        )

    confidence = record.get(
        "display_confidence"
    )

    if (
        confidence is not None
        and not pd.isna(confidence)
    ):

        st.write(
            f"**Confidence:** "
            f"{confidence:.2f}%"
        )

    else:

        st.write(
            "**Confidence:** N/A"
        )

st.divider()

# ==========================================================
# Recommendation
# ==========================================================

st.subheader("💡 Recommendation")

recommendation = record.get(
    "recommendation"
)

if (
    recommendation
    and not pd.isna(recommendation)
):

    st.info(
        str(recommendation)
    )

else:

    st.info(
        "No recommendation is available "
        "for this prediction."
    )

st.divider()

# ==========================================================
# Date
# ==========================================================

st.subheader("📅 Prediction Information")

created_at = record.get(
    "created_at"
)

st.write(
    f"**Created:** "
    f"{created_at or 'N/A'}"
)

st.divider()

# ==========================================================
# Delete Prediction
# ==========================================================

st.subheader("🗑️ Manage Record")

record_id = record.get(
    "id"
)

if record_id:

    confirm_delete = st.checkbox(
        "I understand that deleting this record cannot be undone."
    )

    if st.button(
        "🗑 Delete Prediction",
        disabled=not confirm_delete,
        width="stretch",
    ):

        with st.spinner(
            "Deleting prediction..."
        ):

            success = delete_prediction(
                int(record_id)
            )

        if success:

            st.success(
                "Prediction deleted successfully."
            )

            st.rerun()

        else:

            st.error(
                "Unable to delete prediction."
            )

# ==========================================================
# Export
# ==========================================================

st.divider()

st.subheader(
    "⬇️ Export History"
)

csv_data = filtered_df.to_csv(
    index=False
)

st.download_button(
    label="📊 Export Patient History (CSV)",
    data=csv_data,
    file_name="patient_history.csv",
    mime="text/csv",
    width="stretch",
)

# ==========================================================
# Footer
# ==========================================================

st.divider()

st.caption(
    "Parkinson Disease Detection System "
    "• Patient History"
)
