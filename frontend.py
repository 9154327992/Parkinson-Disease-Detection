# ==========================================================
# Import Required Libraries
# ==========================================================

# Used to send HTTP requests to the FastAPI backend
import requests

# Streamlit library for creating the web application
import streamlit as st

# SQLite library for storing patient records locally
# (You can remove this later if database is moved to FastAPI)
import sqlite3

# NumPy library for numerical operations
import numpy as np


# ==========================================================
# FastAPI Backend URL
# ==========================================================

# Local development URL
API_URL = "https://parkinson-disease-detection-qy5l.onrender.com"

# ==========================================================
# Streamlit Page Title
# ==========================================================

st.title("🧠 Parkinson's Disease Monitoring Agent")

st.write(
    "AI-powered Parkinson's Disease Risk Prediction and Monitoring System."
)


# ==========================================================
# Patient Information
# ==========================================================

# Get patient name
patient_name = st.text_input("Patient Name")


# ==========================================================
# Voice Feature Inputs
# ==========================================================

fo = st.number_input(
    "MDVP:Fo(Hz): Average Fundamental Frequency",
    format="%.6f"
)

fhi = st.number_input(
    "MDVP:Fhi(Hz): Maximum fundamental frequency",
    format="%.6f"
)

flo = st.number_input(
    "MDVP:Flo(Hz): Minimum fundamental frequency",
    format="%.6f"
)

jitter_percent = st.number_input(
    "MDVP:Jitter(%): Percentage variation in voice frequency",
    format="%.6f"
)

jitter_abs = st.number_input(
    "MDVP:Jitter(Abs): Absolute variation in voice frequency",
    format="%.6f"
)

rap = st.number_input(
    "MDVP:RAP: Relative Average Perturbation",
    format="%.6f"
)

ppq = st.number_input(
    "MDVP:PPQ: Pitch Period Perturbation Quotient",
    format="%.6f"
)

ddp = st.number_input(
    "Jitter:DDP: Average absolute pitch variation",
    format="%.6f"
)

shimmer = st.number_input(
    "MDVP:Shimmer: Amplitude variation in voice",
    format="%.6f"
)

shimmer_db = st.number_input(
    "MDVP:Shimmer(dB): Shimmer measured in decibels",
    format="%.6f"
)

apq3 = st.number_input(
    "Shimmer:APQ3: Three-point amplitude perturbation quotient",
    format="%.6f"
)

apq5 = st.number_input(
    "Shimmer:APQ5: Five-point amplitude perturbation quotient",
    format="%.6f"
)

apq = st.number_input(
    "MDVP:APQ: Amplitude Perturbation Quotient",
    format="%.6f"
)

dda = st.number_input(
    "Shimmer:DDA: Average amplitude variation",
    format="%.6f"
)

nhr = st.number_input(
    "NHR: Noise-to-Harmonics Ratio",
    format="%.6f"
)

hnr = st.number_input(
    "HNR: Harmonics-to-Noise Ratio",
    format="%.6f"
)

rpde = st.number_input(
    "RPDE: Recurrence Period Density Entropy",
    format="%.6f"
)

dfa = st.number_input(
    "DFA: Detrended Fluctuation Analysis",
    format="%.6f"
)

spread1 = st.number_input(
    "spread1: Nonlinear frequency variation measure",
    format="%.6f"
)

spread2 = st.number_input(
    "spread2: Nonlinear voice characteristic measure",
    format="%.6f"
)

d2 = st.number_input(
    "D2: Correlation Dimension",
    format="%.6f"
)

ppe = st.number_input(
    "PPE: Pitch Period Entropy",
    format="%.6f"
)


# ==========================================================
# Analyze Patient Button
# ==========================================================

if st.button("Analyze Patient"):

    # Check whether patient name is entered
    if patient_name.strip() == "":
        st.error("Please enter the patient name.")
        st.stop()

    # Create NumPy array from all 22 input features
    patient_data = np.array([
        fo,
        fhi,
        flo,
        jitter_percent,
        jitter_abs,
        rap,
        ppq,
        ddp,
        shimmer,
        shimmer_db,
        apq3,
        apq5,
        apq,
        dda,
        nhr,
        hnr,
        rpde,
        dfa,
        spread1,
        spread2,
        d2,
        ppe
    ]).reshape(1, -1)

    # Prevent prediction if all inputs are zero
    if np.all(patient_data == 0):
        st.error("Please enter valid patient feature values.")
        st.stop()

    # Show loading animation while communicating with backend
    with st.spinner("Analyzing patient..."):

        try:

            # Send patient data to FastAPI backend
            response = requests.post(
                f"{API_URL}/predict",
                json={
                    "features": patient_data.flatten().tolist()
                },
                timeout=20
            )

        except requests.exceptions.ConnectionError:

            st.error("Unable to connect to FastAPI backend.")
            st.stop()

        except requests.exceptions.Timeout:

            st.error("Request timed out.")
            st.stop()

    # ==========================================================
    # Process API Response
    # ==========================================================

    if response.status_code == 200:

        result = response.json()

        diagnosis = result["diagnosis"]

        probability = result["risk_score"] / 100

        risk_level = result["risk_level"]

        recommendation = result["recommendation"]

    else:

        st.error(response.json()["detail"])

        st.stop()

    # ==========================================================
    # Display Diagnostic Report
    # ==========================================================

    st.subheader("Diagnostic Report")

    st.success(f"Diagnosis: {diagnosis}")

    st.metric(
        "Risk Score",
        f"{probability * 100:.2f}%"
    )

    st.write("Risk Level:", risk_level)

    st.write("Recommendation:")

    st.info(recommendation)

    # ==========================================================
    # Save Patient Record into SQLite Database
    # ==========================================================

    # Connect to SQLite database
    conn = sqlite3.connect("patient_records.db")

    # Create cursor object
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS records(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT,
        diagnosis TEXT,
        risk_score REAL,
        risk_level TEXT,
        recommendation TEXT
    )
    """)

    # Insert patient record
    cursor.execute("""
    INSERT INTO records
    (patient_name, diagnosis, risk_score, risk_level, recommendation)
    VALUES (?,?,?,?,?)
    """, (
        patient_name,
        diagnosis,
        probability * 100,
        risk_level,
        recommendation
    ))

    # Save changes
    conn.commit()

    # Close database connection
    conn.close()

    # Display success message
    st.success("Patient record saved successfully.")
