import streamlit as st
import pandas as pd

from utils.api_client import (
    get_patient_history,
    delete_patient
)

# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="Patient History",
    page_icon="👤",
    layout="wide"
)

# ==========================================================
# Header
# ==========================================================

st.title("👤 Patient History")

st.write(
    """
View, search, and manage previously analyzed patient records.
"""
)

st.divider()

# ==========================================================
# Load Patient Records
# ==========================================================

patients = get_patient_history()

if patients is None:

    st.error("Unable to fetch patient records.")

    st.stop()

if len(patients) == 0:

    st.info("No patient records found.")

    st.stop()

df = pd.DataFrame(patients)

# ==========================================================
# Search
# ==========================================================

st.subheader("🔍 Search Patient")

search = st.text_input(
    "Search by Patient Name"
)

if search:

    df = df[
        df["patient_name"]
        .str.contains(
            search,
            case=False,
            na=False
        )
    ]

st.divider()

# ==========================================================
# Patient Table
# ==========================================================

st.subheader("📋 Patient Records")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

st.divider()

# ==========================================================
# Patient Details
# ==========================================================

st.subheader("📄 Patient Details")

patient_names = df["patient_name"].tolist()

selected = st.selectbox(
    "Select Patient",
    patient_names
)

patient = df[
    df["patient_name"] == selected
].iloc[0]

left, right = st.columns(2)

with left:

    st.write("### Patient Information")

    st.write(f"**Name:** {patient['patient_name']}")

    if "age" in patient:
        st.write(f"**Age:** {patient['age']}")

    if "gender" in patient:
        st.write(f"**Gender:** {patient['gender']}")

with right:

    st.write("### Prediction")

    st.write(f"**Diagnosis:** {patient['diagnosis']}")

    st.write(f"**Risk Score:** {patient['risk_score']}%")

    st.write(f"**Risk Level:** {patient['risk_level']}")

st.divider()

# ==========================================================
# Recommendation
# ==========================================================

st.subheader("💡 Recommendation")

st.info(patient["recommendation"])

st.divider()

# ==========================================================
# Delete Record
# ==========================================================

st.subheader("🗑 Delete Patient Record")

if st.button(
    "Delete Record",
    use_container_width=True
):

    response = delete_patient(
        patient["id"]
    )

    if response:

        st.success(
            "Patient record deleted successfully."
        )

        st.rerun()

    else:

        st.error(
            "Unable to delete patient."
        )

st.divider()

# ==========================================================
# Export
# ==========================================================

csv = df.to_csv(index=False)

st.download_button(
    label="⬇ Download CSV",
    data=csv,
    file_name="patient_history.csv",
    mime="text/csv",
    use_container_width=True
)
