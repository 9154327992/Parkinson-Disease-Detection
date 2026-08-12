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

st.subheader("👤 Patient Information")

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


values = []


# ==========================================================
# Feature Input
# ==========================================================

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

        values.append(value)


st.divider()


# ==========================================================
# Form Validation
# ==========================================================

if st.button(
    "🧠 Analyze Patient",
    use_container_width=True,
    type="primary",
):

    if not patient_name.strip():

        st.warning(
            "Please enter the patient name."
        )

        st.stop()


    if all(
        value == 0
        for value in values
    ):

        st.warning(
            "Please enter valid voice measurements."
        )

        st.stop()


    if len(values) != 22:

        st.error(
            "Exactly 22 voice measurements are required."
        )

        st.stop()


    # ======================================================
    # Prediction
    # ======================================================

    with st.spinner(
        "Analyzing patient..."
    ):

        result = predict_patient(
            patient_name,
            patient_age,
            patient_gender,
            values,
        )


    if result is None:

        st.error(
            "Unable to connect to the FastAPI backend."
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


    diagnosis = result.get(
        "diagnosis",
        result.get(
            "prediction",
            "Unknown",
        ),
    )

    risk_score = result.get(
        "risk_score",
        0,
    )

    risk_level = result.get(
        "risk_level",
        "Unknown",
    )

    recommendation = result.get(
        "recommendation",
        "Please consult a qualified healthcare professional.",
    )

    prediction_id = result.get(
        "prediction_id",
        result.get(
            "id",
            "N/A",
        ),
    )


    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Diagnosis",
            diagnosis,
        )

    with c2:

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

    with c3:

        st.metric(
            "Risk Level",
            risk_level,
        )


    st.divider()


    # ======================================================
    # Patient Summary
    # ======================================================

    st.subheader(
        "👤 Patient Summary"
    )

    p1, p2, p3, p4 = st.columns(4)

    with p1:
        st.write(
            f"**Name:** {patient_name}"
        )

    with p2:
        st.write(
            f"**Age:** {patient_age}"
        )

    with p3:
        st.write(
            f"**Gender:** {patient_gender}"
        )

    with p4:
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
        recommendation
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
            use_container_width=True,
        ):

            st.switch_page(
                "pages/3_Patient_History.py"
            )

    with next2:

        if st.button(
            "📄 View Reports",
            use_container_width=True,
        ):

            st.switch_page(
                "pages/5_Reports.py"
            )
