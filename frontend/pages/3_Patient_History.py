import streamlit as st
import pandas as pd

from utils.api_client import (
    get_prediction_history,
    delete_prediction,
)

# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="Prediction History",
    page_icon="📋",
    layout="wide"
)

# ==========================================================
# Header
# ==========================================================

st.title("📋 Prediction History")

st.write(
    """
View, search, and manage previously analyzed prediction records.
"""
)

st.divider()

# ==========================================================
# Load Prediction History
# ==========================================================

history = get_prediction_history()

if history is None:

    st.error("Unable to fetch prediction history.")

    st.stop()

if len(history) == 0:

    st.info("No prediction records found.")

    st.stop()

df = pd.DataFrame(history)

# ==========================================================
# Search
# ==========================================================

st.subheader("🔍 Search Prediction")

search = st.text_input(
    "Search by Patient Name"
)

if search.strip():

    df = df[
        df["patient_name"]
        .astype(str)
        .str.contains(
            search.strip(),
            case=False,
            na=False
        )
    ]

if df.empty:

    st.info("No matching prediction records found.")

    st.stop()

st.divider()

# ==========================================================
# Prediction Records
# ==========================================================

st.subheader("📋 Prediction Records")

display_df = df[
    [
        "prediction_id",
        "patient_id",
        "patient_name",
        "prediction",
        "confidence",
        "risk_level",
        "created_at"
    ]
].copy()

display_df.columns = [
    "Prediction ID",
    "Patient ID",
    "Patient Name",
    "Prediction",
    "Confidence",
    "Risk Level",
    "Date"
]

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)

st.divider()

# ==========================================================
# Prediction Details
# ==========================================================

st.subheader("📄 Prediction Details")

prediction_ids = df["prediction_id"].tolist()

selected_id = st.selectbox(
    "Select Prediction",
    prediction_ids
)

selected = df[
    df["prediction_id"] == selected_id
].iloc[0]

left, right = st.columns(2)

with left:

    st.write("### 👤 Patient Information")

    st.write(
        f"**Patient:** {selected['patient_name']}"
    )

    st.write(
        f"**Patient ID:** {selected['patient_id']}"
    )

    st.write(
        f"**Prediction ID:** {selected['prediction_id']}"
    )

with right:

    st.write("### 🩺 Prediction Result")

    st.write(
        f"**Prediction:** {selected['prediction']}"
    )

    st.write(
        f"**Confidence:** {selected['confidence']:.2f}%"
    )

    st.write(
        f"**Risk Level:** {selected['risk_level']}"
    )

    st.write(
        f"**Date:** {selected['created_at']}"
    )

st.divider()

# ==========================================================
# Delete Prediction
# ==========================================================

st.subheader("🗑 Delete Prediction")

if st.button(
    "Delete Selected Prediction",
    use_container_width=True
):

    response = delete_prediction(
        selected["prediction_id"]
    )

    if response:

        st.success(
            "Prediction deleted successfully."
        )

        st.rerun()

    else:

        st.error(
            "Unable to delete prediction."
        )

st.divider()

# ==========================================================
# Export
# ==========================================================

csv = df.to_csv(
    index=False
)

st.download_button(
    label="⬇ Download Prediction History",
    data=csv,
    file_name="prediction_history.csv",
    mime="text/csv",
    use_container_width=True
)
