import streamlit as st

from utils.api_client import predict_patient


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
    Enter the patient's information and voice measurements
    to assess the likelihood of Parkinson's disease.
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
# Voice Measurements
# ==========================================================

st.subheader(
    "🎤 Voice Measurements"
)

st.caption(
    "Enter all 22 voice measurements used by the ML model."
)


feature_names = [

    "MDVP:Fo(Hz): Average fundamental frequency",

    "MDVP:Fhi(Hz): Maximum fundamental frequency",

    "MDVP:Flo(Hz): Minimum fundamental frequency",

    "MDVP:Jitter(%): Percentage variation",

    "MDVP:Jitter(Abs): Absolute variation",

    "MDVP:RAP: Relative Average Perturbation",

    "MDVP:PPQ: Pitch Period Perturbation",

    "Jitter:DDP: Average pitch variation",

    "MDVP:Shimmer: Amplitude variation",

    "MDVP:Shimmer(dB): Shimmer in decibels",

    "Shimmer:APQ3: Three-point amplitude quotient",

    "Shimmer:APQ5: Five-point amplitude quotient",

    "MDVP:APQ: Amplitude Perturbation Quotient",

    "Shimmer:DDA: Average amplitude variation",

    "NHR: Noise-to-Harmonics Ratio",

    "HNR: Harmonics-to-Noise Ratio",

    "RPDE: Recurrence Period Density Entropy",

    "DFA: Detrended Fluctuation Analysis",

    "Spread1: Nonlinear frequency variation",

    "Spread2: Nonlinear voice characteristic",

    "D2: Correlation Dimension",

    "PPE: Pitch Period Entropy",
]


# ==========================================================
# Feature Input
# ==========================================================

values = []

cols = st.columns(2)


for index, feature in enumerate(
    feature_names
):

    with cols[index % 2]:

        value = st.number_input(
            feature,
            value=0.0,
            format="%.6f",
            key=f"feature_{index}",
        )

        values.append(
            value
        )


st.divider()


# ==========================================================
# Measurement Summary
# ==========================================================

st.subheader(
    "📊 Measurement Summary"
)

summary_col1, summary_col2, summary_col3 = (
    st.columns(3)
)


with summary_col1:

    st.metric(
        "Total Features",
        len(values),
    )


with summary_col2:

    entered_features = sum(
        value != 0
        for value in values
    )

    st.metric(
        "Entered Features",
        entered_features,
    )


with summary_col3:

    st.metric(
        "Required Features",
        22,
    )


st.divider()


# ==========================================================
# Analyze Patient
# ==========================================================

if st.button(
    "🧠 Analyze Patient",
    width="stretch",
    type="primary",
):

    # ------------------------------------------------------
    # Patient Validation
    # ------------------------------------------------------

    if not patient_name.strip():

        st.warning(
            "Please enter the patient name."
        )

        st.stop()


    if len(values) != 22:

        st.error(
            "Exactly 22 voice measurements are required."
        )

        st.stop()


    # ------------------------------------------------------
    # Measurement Validation
    # ------------------------------------------------------

    if all(
        value == 0
        for value in values
    ):

        st.warning(
            "Please enter valid voice measurements."
        )

        st.stop()


    # ------------------------------------------------------
    # Prediction Request
    # ------------------------------------------------------

    with st.spinner(
        "Analyzing patient..."
    ):

        try:

            result = predict_patient(
                patient_name=patient_name.strip(),
                age=int(patient_age),
                gender=patient_gender,
                features=values,
            )

        except TypeError as exc:

            st.error(
                "Prediction request format is incompatible "
                "with the current api_client.py."
            )

            st.code(
                str(exc)
            )

            st.stop()

        except Exception as exc:

            st.error(
                "An unexpected error occurred while "
                "requesting the prediction."
            )

            st.code(
                str(exc)
            )

            st.stop()


    # ======================================================
    # Backend Response
    # ======================================================

    if result is None:

        st.error(
            "Unable to connect to the FastAPI backend "
            "or the prediction request failed."
        )

        st.stop()


    if not isinstance(
        result,
        dict,
    ):

        st.error(
            "The backend returned an invalid prediction response."
        )

        st.write(
            result
        )

        st.stop()


    # ======================================================
    # Result
    # ======================================================

    st.success(
        "✅ Prediction completed successfully."
    )

    st.divider()

    st.subheader(
        "📋 Prediction Result"
    )


    # ------------------------------------------------------
    # Extract Result
    # ------------------------------------------------------

    diagnosis = result.get(
        "diagnosis",
        result.get(
            "prediction",
            result.get(
                "result",
                "Unknown",
            ),
        ),
    )


    risk_score = result.get(
        "risk_score",
        result.get(
            "risk",
            0,
        ),
    )


    risk_level = result.get(
        "risk_level",
        "Unknown",
    )


    recommendation = result.get(
        "recommendation",
        (
            "Please consult a qualified healthcare "
            "professional for further evaluation."
        ),
    )


    prediction_id = result.get(
        "prediction_id",
        result.get(
            "id",
            "N/A",
        ),
    )


    confidence = result.get(
        "confidence",
        result.get(
            "prediction_confidence",
            None,
        ),
    )


    # ------------------------------------------------------
    # Result Metrics
    # ------------------------------------------------------

    result_col1, result_col2, result_col3 = (
        st.columns(3)
    )


    with result_col1:

        st.metric(
            "Diagnosis",
            str(
                diagnosis
            ),
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
                str(
                    risk_score
                ),
            )


    with result_col3:

        st.metric(
            "Risk Level",
            str(
                risk_level
            ),
        )


    # ------------------------------------------------------
    # Confidence
    # ------------------------------------------------------

    if confidence is not None:

        try:

            confidence_value = float(
                confidence
            )

            st.progress(
                max(
                    0.0,
                    min(
                        confidence_value / 100,
                        1.0,
                    ),
                )
            )

            st.caption(
                f"Prediction confidence: "
                f"{confidence_value:.2f}%"
            )

        except (
            TypeError,
            ValueError,
        ):

            pass


    st.divider()


    # ======================================================
    # Patient Summary
    # ======================================================

    st.subheader(
        "👤 Patient Summary"
    )


    p1, p2, p3, p4 = (
        st.columns(4)
    )


    with p1:

        st.write(
            f"**Name:** "
            f"{patient_name}"
        )


    with p2:

        st.write(
            f"**Age:** "
            f"{patient_age}"
        )


    with p3:

        st.write(
            f"**Gender:** "
            f"{patient_gender}"
        )


    with p4:

        st.write(
            f"**Prediction ID:** "
            f"{prediction_id}"
        )


    st.divider()


    # ======================================================
    # Recommendation
    # ======================================================

    st.subheader(
        "💡 Recommendation"
    )


    st.info(
        str(
            recommendation
        )
    )


    st.divider()


    # ======================================================
    # Raw Response
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


    next1, next2 = st.columns(2)


    with next1:

        if st.button(
            "📋 View Patient History",
            width="stretch",
        ):

            st.switch_page(
                "pages/3_Patient_History.py"
            )


    with next2:

        if st.button(
            "📄 View Reports",
            width="stretch",
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

    st.write(
        """
        The prediction model expects 22 voice-related
        measurements. These include fundamental frequency,
        jitter, shimmer, noise-to-harmonics ratio,
        recurrence measures, detrended fluctuation,
        nonlinear measures, and pitch entropy.

        The values should come from the same measurement
        process and preprocessing used when the machine
        learning model was trained.
        """
    )


# ==========================================================
# Medical Disclaimer
# ==========================================================

st.warning(
    """
    ⚠️ **Medical Disclaimer**

    This tool provides AI-assisted screening information.
    It does not diagnose Parkinson's disease and should
    not replace evaluation by a qualified healthcare
    professional.
    """
)


# ==========================================================
# Footer
# ==========================================================

st.caption(
    "Parkinson Disease Detection Agent • Prediction"
)
