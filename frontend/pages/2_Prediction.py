import streamlit as st
from utils.api_client import predict_patient

# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="Prediction",
    page_icon="🩺",
    layout="wide"
)

# ==========================================================
# Header
# ==========================================================

st.title("🩺 Parkinson Disease Prediction")

st.write(
    """
Enter the patient's information and voice measurements to predict
the likelihood of Parkinson's Disease.
"""
)

st.divider()

# ==========================================================
# Patient Information
# ==========================================================

st.subheader("👤 Patient Information")

col1, col2, col3 = st.columns(3)

with col1:
    patient_name = st.text_input("Patient Name")

with col2:
    patient_age = st.number_input(
        "Age",
        min_value=1,
        max_value=120,
        value=30
    )

with col3:
    patient_gender = st.selectbox(
        "Gender",
        [
            "Male",
            "Female",
            "Other"
        ]
    )

st.divider()

# ==========================================================
# Voice Features
# ==========================================================

st.subheader("🎤 Voice Measurements")

feature_names = [

    "MDVP:Fo(Hz)",
    "MDVP:Fhi(Hz)",
    "MDVP:Flo(Hz)",

    "MDVP:Jitter(%)",
    "MDVP:Jitter(Abs)",
    "MDVP:RAP",
    "MDVP:PPQ",
    "Jitter:DDP",

    "MDVP:Shimmer",
    "MDVP:Shimmer(dB)",
    "Shimmer:APQ3",
    "Shimmer:APQ5",
    "MDVP:APQ",
    "Shimmer:DDA",

    "NHR",
    "HNR",

    "RPDE",
    "DFA",

    "Spread1",
    "Spread2",

    "D2",
    "PPE"
]

values = []

cols = st.columns(2)

for index, feature in enumerate(feature_names):

    with cols[index % 2]:

        value = st.number_input(
            feature,
            value=0.0,
            format="%.6f",
            key=feature
        )

        values.append(value)

st.divider()

# ==========================================================
# Prediction Button
# ==========================================================

if st.button(
    "🧠 Analyze Patient",
    use_container_width=True
):

    if patient_name.strip() == "":

        st.warning("Please enter the patient name.")

        st.stop()

    if all(v == 0 for v in values):

        st.warning("Please enter valid voice measurements.")

        st.stop()

    with st.spinner("Analyzing patient..."):

        result = predict_patient(values)

    if result is None:

        st.error("Unable to connect to FastAPI Backend.")

        st.stop()

    st.success("Prediction Completed Successfully")

    st.divider()

    st.subheader("📋 Prediction Result")

    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "Diagnosis",
            result["diagnosis"]
        )

        st.metric(
            "Risk Score",
            f'{result["risk_score"]:.2f}%'
        )

    with c2:

        st.metric(
            "Risk Level",
            result["risk_level"]
        )

    st.info(result["recommendation"])

    st.divider()

    st.download_button(
        label="📄 Download Report",
        data="Report generation will be implemented later.",
        file_name="prediction_report.txt",
        mime="text/plain"
    )
