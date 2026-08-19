import streamlit as st

from utils.api_client import (
    predict_patient,
    predict_audio,
)


# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="Prediction",
    page_icon="🩺",
    layout="wide",
)


# ==========================================================
# Header
# ==========================================================

st.title(
    "🩺 Parkinson Disease Prediction"
)

st.write(
    """
Enter the patient's information and all 22 voice
measurements to assess the likelihood of Parkinson's disease.
"""
)

st.info(
    """
This prediction is an AI-assisted screening result and
should not be treated as a medical diagnosis.
"""
)

st.divider()


# ==========================================================
# Patient Information
# ==========================================================

st.subheader(
    "👤 Patient Information"
)

col1, col2, col3 = st.columns(3)


with col1:

    patient_name = st.text_input(
        "Patient Name",
        placeholder="Enter patient name",
    )


with col2:

    patient_age = st.number_input(
        "Age",
        min_value=1,
        max_value=120,
        value=30,
        step=1,
    )


with col3:

    patient_gender = st.selectbox(
        "Gender",
        [
            "Male",
            "Female",
            "Other",
        ],
    )


st.divider()

# ==========================================================
# Voice Audio
# ==========================================================

st.subheader(
    "🎵 Voice Audio"
)

st.caption(
    "Upload a WAV recording or record your voice directly."
)


audio_mode = st.radio(
    "Choose audio input",
    [
        "Upload WAV",
        "Record Audio",
    ],
    horizontal=True,
)


audio_file = None


# ==========================================================
# Upload WAV
# ==========================================================

if audio_mode == "Upload WAV":

    audio_file = st.file_uploader(
        "Upload WAV audio",
        type=["wav"],
        help=(
            "Upload a WAV voice recording "
            "between 2 and 30 seconds."
        ),
    )


    if audio_file is not None:

        st.audio(
            audio_file,
            format="audio/wav",
        )

        st.success(
            f"Audio file ready: {audio_file.name}"
        )


# ==========================================================
# Record Audio
# ==========================================================

else:

    from audio_recorder_streamlit import (
        audio_recorder,
    )


    st.write(
        "🎙️ Record the patient's voice:"
    )


    recorded_audio = audio_recorder(
        text="🎙️ Start / Stop Recording",
        recording_color="#e63946",
        neutral_color="#6c757d",
        icon_name="microphone",
        icon_size="2x",
    )


    if recorded_audio:

        st.audio(
            recorded_audio,
            format="audio/wav",
        )


        st.success(
            "Voice recording captured successfully."
        )


        class RecordedAudio:

            name = "recorded_voice.wav"


            def getvalue(self):

                return recorded_audio


        audio_file = RecordedAudio()

# ==========================================================
# Voice Measurements
# ==========================================================

st.subheader(
    "🎤 Voice Measurements"
)

st.caption(
    "All 22 measurements are required. "
    "Enter the actual values from the patient's voice analysis."
)


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
    "spread1",
    "spread2",
    "D2",
    "PPE",
]

# ==========================================================
# Feature Inputs
# ==========================================================

values = []

cols = st.columns(2)


for index, feature in enumerate(
    feature_names
):

    with cols[index % 2]:

        value = st.number_input(
            feature,
            value=None,
            placeholder="Enter measurement",
            format="%.6f",
            key=f"prediction_feature_{index}",
        )

        values.append(value)


# ==========================================================
# Measurement Validation
# ==========================================================

entered_features = sum(
    value is not None
    for value in values
)

missing_features = [
    index + 1
    for index, value in enumerate(values)
    if value is None
]


st.divider()

st.subheader(
    "📊 Measurement Summary"
)


summary_col1, summary_col2, summary_col3 = (
    st.columns(3)
)


with summary_col1:

    st.metric(
        "Total Features",
        len(feature_names),
    )


with summary_col2:

    st.metric(
        "Entered Features",
        entered_features,
    )


with summary_col3:

    st.metric(
        "Required Features",
        len(feature_names),
    )


# ==========================================================
# Validation Status
# ==========================================================

if entered_features == 22:

    st.success(
        "✅ All 22 voice measurements have been entered."
    )

else:

    st.warning(
        f"⚠️ {22 - entered_features} "
        "voice measurement(s) still need to be entered."
    )


# ==========================================================
# Analyze Button
# ==========================================================

st.divider()


analyze = st.button(
    "🧠 Analyze Patient",
    use_container_width=True,
    type="primary",
)


if analyze:

    # --------------------------------------------------
    # Patient Name
    # --------------------------------------------------

    if not patient_name.strip():

        st.error(
            "Please enter the patient name."
        )

        st.stop()


    # --------------------------------------------------
    # Audio Prediction
    # --------------------------------------------------

    if audio_file is not None:

        with st.spinner(
            "🧠 Extracting voice features and analyzing patient..."
        ):

            result = predict_audio(
                patient_name.strip(),
                int(patient_age),
                patient_gender,
                audio_file,
            )


    # --------------------------------------------------
    # Manual Feature Prediction
    # --------------------------------------------------

    else:

        if len(values) != 22:

            st.error(
                "Exactly 22 voice measurements are required."
            )

            st.stop()


        if missing_features:

            missing_text = ", ".join(
                str(number)
                for number in missing_features
            )

            st.error(
                "Please upload a WAV file or enter all "
                f"22 voice measurements. "
                f"Missing feature(s): {missing_text}"
            )

            st.stop()


        try:

            numeric_values = [
                float(value)
                for value in values
            ]

        except (
            TypeError,
            ValueError,
        ):

            st.error(
                "All voice measurements must be valid numbers."
            )

            st.stop()


        if len(numeric_values) != 22:

            st.error(
                "The prediction requires exactly 22 measurements."
            )

            st.stop()


        with st.spinner(
            "🧠 Analyzing patient..."
        ):

            result = predict_patient(
                patient_name.strip(),
                int(patient_age),
                patient_gender,
                numeric_values,
            )

    # ------------------------------------------------------
    # Backend Error
    # ------------------------------------------------------

    if result is None:

        st.error(
            "Unable to connect to the FastAPI backend "
            "or the prediction request failed."
        )

        st.stop()


    # ------------------------------------------------------
    # Result
    # ------------------------------------------------------

    st.success(
        "✅ Prediction completed successfully."
    )

    st.divider()

    st.subheader(
        "📋 Prediction Result"
    )


    # ------------------------------------------------------
    # Diagnosis
    # ------------------------------------------------------

    if isinstance(
        result,
        dict,
    ):

        diagnosis = (
            result.get("diagnosis")
            or result.get("prediction")
            or result.get("prediction_result")
            or result.get("result")
            or "Unknown"
        )


        risk_score = (
            result.get("risk_score")
            if result.get("risk_score") is not None
            else result.get("risk")
        )


        if risk_score is None:

            risk_score = 0


        risk_level = (
            result.get("risk_level")
            or result.get("risk_category")
            or "Unknown"
        )


        recommendation = (
            result.get("recommendation")
            or result.get("recommendations")
            or "Please consult a qualified healthcare professional."
        )


        prediction_id = (
            result.get("prediction_id")
            or result.get("id")
            or "N/A"
        )


        confidence = (
            result.get("confidence")
            or result.get("prediction_confidence")
        )

    else:

        diagnosis = str(
            result
        )

        risk_score = 0

        risk_level = "Unknown"

        recommendation = (
            "Please consult a qualified healthcare professional."
        )

        prediction_id = "N/A"

        confidence = None


    # ======================================================
    # Result Metrics
    # ======================================================

    result_col1, result_col2, result_col3 = (
        st.columns(3)
    )


    with result_col1:

        st.metric(
            "Diagnosis",
            str(diagnosis),
        )


    with result_col2:

        try:

            score = float(
                risk_score
            )

            st.metric(
                "Risk Score",
                f"{score:.2f}%",
            )

        except (
            TypeError,
            ValueError,
        ):

            st.metric(
                "Risk Score",
                str(risk_score),
            )


    with result_col3:

        st.metric(
            "Risk Level",
            str(risk_level),
        )


    # ------------------------------------------------------
    # Confidence
    # ------------------------------------------------------

    if confidence is not None:

        try:

            confidence_value = float(
                confidence
            )

            if confidence_value <= 1:
                confidence_value *= 100

            st.write(
                f"**Prediction Confidence:** "
                f"{confidence_value:.2f}%"
            )

        except (
            TypeError,
            ValueError,
        ):

            st.write(
                f"**Prediction Confidence:** "
                f"{confidence}"
            )


    st.divider()


    # ======================================================
    # Patient Summary
    # ======================================================

    st.subheader(
        "👤 Patient Summary"
    )


    patient_col1, patient_col2 = (
        st.columns(2)
    )


    with patient_col1:

        st.write(
            f"**Name:** {patient_name}"
        )

        st.write(
            f"**Age:** {patient_age}"
        )


    with patient_col2:

        st.write(
            f"**Gender:** {patient_gender}"
        )

        st.write(
            f"**Prediction ID:** {prediction_id}"
        )


    st.divider()


    # ======================================================
    # Recommendation
    # ======================================================

    st.subheader(
        "💡 Recommendation"
    )

    st.info(
        str(recommendation)
    )


    st.divider()


    # ======================================================
    # Backend Response
    # ======================================================

    with st.expander(
        "🔎 View Backend Response"
    ):

        st.json(
            result
        )


    st.divider()


    # ======================================================
    # Next Actions
    # ======================================================

    st.subheader(
        "🚀 Next Steps"
    )


    next_col1, next_col2 = (
        st.columns(2)
    )


    with next_col1:

        if st.button(
            "📋 View Patient History",
            use_container_width=True,
        ):

            st.switch_page(
                "pages/3_Patient_History.py"
            )


    with next_col2:

        if st.button(
            "📄 View Reports",
            use_container_width=True,
        ):

            st.switch_page(
                "pages/5_Reports.py"
            )


# ==========================================================
# Information
# ==========================================================

st.divider()

with st.expander(
    "ℹ️ About the 22 Measurements"
):

    st.markdown(
        """
The prediction model uses 22 voice measurements:

1. MDVP:Fo(Hz)
2. MDVP:Fhi(Hz)
3. MDVP:Flo(Hz)
4. MDVP:Jitter(%)
5. MDVP:Jitter(Abs)
6. MDVP:RAP
7. MDVP:PPQ
8. Jitter:DDP
9. MDVP:Shimmer
10. MDVP:Shimmer(dB)
11. Shimmer:APQ3
12. Shimmer:APQ5
13. MDVP:APQ
14. Shimmer:DDA
15. NHR
16. HNR
17. RPDE
18. DFA
19. Spread1
20. Spread2
21. D2
22. PPE
        """
    )


# ==========================================================
# Disclaimer
# ==========================================================

st.warning(
    """
⚠️ **Medical Disclaimer**

This tool provides AI-assisted screening information.
It does not diagnose Parkinson's disease and should not
replace evaluation by a qualified healthcare professional.
"""
)


# ==========================================================
# Footer
# ==========================================================

st.caption(
    "Parkinson Disease Detection Agent • Prediction"
)
