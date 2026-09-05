import streamlit as st
from pathlib import Path
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
# Prediction Banner
# ==========================================================

PREDICTION_BANNER = (
    Path(__file__).resolve().parents[1]
    / "assets"
    / "images"
    / "prediction_banner.png"
)


if PREDICTION_BANNER.exists():

    import base64


    banner_base64 = base64.b64encode(
        PREDICTION_BANNER.read_bytes()
    ).decode(
        "utf-8"
    )


    st.html(
        f"""
        <style>

        .prediction-banner-wrapper {{
            width: 100%;
            margin: 0 0 1rem 0;
            padding: 0;
        }}


        .prediction-banner {{
            width: min(100%, 1600px);

            height: auto;

            display: block;

            margin-left: auto;
            margin-right: auto;

            object-fit: contain;

            border-radius: 12px;
        }}


        /* Small screens */

        @media (max-width: 768px) {{

            .prediction-banner {{
                width: 100%;
            }}

        }}


        /* Medium screens */

        @media (min-width: 769px) and (max-width: 1400px) {{

            .prediction-banner {{
                width: 100%;
            }}

        }}


        /* Large / High Resolution Screens */

        @media (min-width: 1401px) {{

            .prediction-banner {{
                width: 100%;
                max-width: 1600px;
            }}

        }}

        </style>


        <div class="prediction-banner-wrapper">

            <img
                class="prediction-banner"
                src="data:image/png;base64,{banner_base64}"
                alt="Parkinson Disease Prediction"
            >

        </div>
        """
    )


else:

    st.warning(
        "Prediction banner image was not found."
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

    # ======================================================
    # Native Streamlit Audio Recorder
    # ======================================================

    st.write(
        "🎙️ Record the patient's voice:"
    )

    st.caption(
        "Use your microphone to record the patient's voice."
    )


    audio_file = st.audio_input(
        "🎙️ Record voice"
    )


    if audio_file is not None:

        st.audio(
            audio_file,
            format="audio/wav",
        )

        st.success(
            "✅ Voice recording captured successfully."
        )

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
    "MDVP:Fo(Hz) - Average Fundamental Frequency",
    "MDVP:Fhi(Hz) - Maximum Fundamental Frequency",
    "MDVP:Flo(Hz) - Minimum Fundamental Frequency",
    "MDVP:Jitter(%) - Percentage of Cycle-to-Cycle Frequency Variation",
    "MDVP:Jitter(Abs) - Absolute Cycle-to-Cycle Frequency Variation",
    "MDVP:RAP - Relative Average Perturbation",
    "MDVP:PPQ - Five-Point Period Perturbation Quotient",
    "Jitter:DDP - Average Absolute Difference of Consecutive Period Differences",
    "MDVP:Shimmer - Cycle-to-Cycle Amplitude Variation",
    "MDVP:Shimmer(dB) - Shimmer in Decibels",
    "Shimmer:APQ3 - Three-Point Amplitude Perturbation Quotient",
    "Shimmer:APQ5 - Five-Point Amplitude Perturbation Quotient",
    "MDVP:APQ - Eleven-Point Amplitude Perturbation Quotient",
    "Shimmer:DDA - Average Absolute Difference of Consecutive Amplitude Differences",
    "NHR - Noise-to-Harmonics Ratio",
    "HNR - Harmonics-to-Noise Ratio",
    "RPDE - Recurrence Period Density Entropy",
    "DFA - Detrended Fluctuation Analysis",
    "spread1 - Fundamental Frequency Variation Measure 1",
    "spread2 - Fundamental Frequency Variation Measure 2",
    "D2 - Correlation Dimension",
    "PPE - Pitch Period Entropy",
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

1. MDVP:Fo(Hz): Average fundamental frequency of the voice, representing the typical vocal pitch.
2. MDVP:Fhi(Hz): Highest fundamental frequency detected in the voice recording.
3. MDVP:Flo(Hz): Lowest fundamental frequency detected in the voice recording.
4. MDVP:Jitter(%): Percentage of short-term variation in vocal pitch from one cycle to the next.
5. MDVP:Jitter(Abs): Absolute amount of short-term variation in vocal pitch.
6. MDVP:RAP: Relative average perturbation measuring short-term pitch instability.
7. MDVP:PPQ: Pitch perturbation quotient measuring periodic variation in vocal frequency.
8. Jitter:DDP: A derived measure of pitch variation based on differences between consecutive pitch periods.
9. MDVP:Shimmer: Short-term variation in the amplitude or loudness of consecutive voice cycles.
10. MDVP:Shimmer(dB): Shimmer expressed in decibels, describing short-term amplitude variation.
11. Shimmer:APQ3: Amplitude perturbation measured over three consecutive voice cycles.
12. Shimmer:APQ5: Amplitude perturbation measured over five consecutive voice cycles.
13. MDVP:APQ: Average perturbation quotient measuring variation in vocal amplitude.
14. Shimmer:DDA: Derived measure representing amplitude variation across consecutive voice cycles.
15. NHR: Noise-to-harmonics ratio estimating the amount of noise relative to harmonic voice components.
16. HNR: Harmonics-to-noise ratio estimating how strong harmonic components are compared with noise.
17. RPDE: Recurrence period density entropy describing irregularity and complexity in vocal dynamics.
18. DFA: Detrended fluctuation analysis measuring long-range correlations in the voice signal.
19. spread1: Nonlinear frequency variation measure associated with the distribution of voice frequencies.
20. spread2: Another nonlinear measure describing variation in the voice frequency characteristics.
21. D2: Correlation dimension measuring the complexity of the vocal signal.
22. PPE: Pitch period entropy measuring the unpredictability or irregularity of vocal pitch.
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
