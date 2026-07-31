import streamlit as st


# ==========================================================
# Metric Card
# ==========================================================

def metric_card(title: str, value, delta=None):
    """
    Display a metric card.
    """

    st.metric(
        label=title,
        value=value,
        delta=delta
    )


# ==========================================================
# Status Card
# ==========================================================

def status_card(title: str, status: bool):
    """
    Display a system status card.
    """

    if status:
        st.success(f"✅ {title}")
    else:
        st.error(f"❌ {title}")


# ==========================================================
# Information Card
# ==========================================================

def info_card(title: str, message: str):
    """
    Display an information card.
    """

    st.info(f"### {title}\n\n{message}")


# ==========================================================
# Warning Card
# ==========================================================

def warning_card(title: str, message: str):
    """
    Display a warning card.
    """

    st.warning(f"### {title}\n\n{message}")


# ==========================================================
# Error Card
# ==========================================================

def error_card(title: str, message: str):
    """
    Display an error card.
    """

    st.error(f"### {title}\n\n{message}")


# ==========================================================
# Success Card
# ==========================================================

def success_card(title: str, message: str):
    """
    Display a success card.
    """

    st.success(f"### {title}\n\n{message}")


# ==========================================================
# Prediction Result Card
# ==========================================================

def prediction_card(
    diagnosis: str,
    risk_score: float,
    risk_level: str,
    recommendation: str
):
    """
    Display prediction results.
    """

    st.subheader("🧠 Prediction Result")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Diagnosis", diagnosis)
        st.metric("Risk Score", f"{risk_score:.2f}%")

    with col2:
        st.metric("Risk Level", risk_level)

    st.info(recommendation)


# ==========================================================
# Patient Summary Card
# ==========================================================

def patient_card(patient: dict):
    """
    Display patient information.
    """

    st.subheader("👤 Patient Summary")

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Name:** {patient.get('patient_name', '-')}")
        st.write(f"**Age:** {patient.get('age', '-')}")
        st.write(f"**Gender:** {patient.get('gender', '-')}")

    with col2:
        st.write(f"**Diagnosis:** {patient.get('diagnosis', '-')}")
        st.write(f"**Risk Level:** {patient.get('risk_level', '-')}")
        st.write(f"**Risk Score:** {patient.get('risk_score', '-')}%")


# ==========================================================
# Dashboard Card
# ==========================================================

def dashboard_card(title: str, value, icon="📊"):
    """
    Display a dashboard metric card.
    """

    st.markdown(
        f"""
<div style="
padding:18px;
border-radius:12px;
background:#f8f9fa;
border:1px solid #e5e7eb;
margin-bottom:12px;
">

<h4>{icon} {title}</h4>

<h2>{value}</h2>

</div>
""",
        unsafe_allow_html=True
    )
