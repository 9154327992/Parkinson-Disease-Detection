# Import Streamlit library
import streamlit as st

# Import joblib for loading model files
import joblib

# Import SQLite for storing records
import sqlite3

# Import NumPy
import numpy as np


# Load saved machine learning model
model = joblib.load("model.pkl")

# Load saved scaler
scaler = joblib.load("scaler.pkl")


# Create page title
st.title("Parkinson's Disease Monitoring Agent")

# Create page description
st.write(
    "AI-powered Parkinson's disease risk prediction and monitoring system."
)


# Ask user for patient name
patient_name = st.text_input("Patient Name")

# Create input fields for all 22 features
fo = st.number_input("MDVP:Fo(Hz)")
fhi = st.number_input("MDVP:Fhi(Hz)")
flo = st.number_input("MDVP:Flo(Hz)")
jitter_percent = st.number_input("MDVP:Jitter(%)")
jitter_abs = st.number_input("MDVP:Jitter(Abs)")
rap = st.number_input("MDVP:RAP")
ppq = st.number_input("MDVP:PPQ")
ddp = st.number_input("Jitter:DDP")
shimmer = st.number_input("MDVP:Shimmer")
shimmer_db = st.number_input("MDVP:Shimmer(dB)")
apq3 = st.number_input("Shimmer:APQ3")
apq5 = st.number_input("Shimmer:APQ5")
apq = st.number_input("MDVP:APQ")
dda = st.number_input("Shimmer:DDA")
nhr = st.number_input("NHR")
hnr = st.number_input("HNR")
rpde = st.number_input("RPDE")
dfa = st.number_input("DFA")
spread1 = st.number_input("spread1")
spread2 = st.number_input("spread2")
d2 = st.number_input("D2")
ppe = st.number_input("PPE")


# Analyze button
if st.button("Analyze Patient"):

    # Create feature array
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

    # Scale input data
    scaled_data = scaler.transform(patient_data)

    # Predict Parkinson's disease
    prediction = model.predict(scaled_data)[0]

    # Predict probability score
    probability = model.predict_proba(
        scaled_data
    )[0][1]

    # Determine diagnosis
    if prediction == 1:
        diagnosis = "Parkinson's Disease Detected"
    else:
        diagnosis = "Healthy"

    # Determine risk level
    if probability >= 0.80:
        risk_level = "High Risk"
    elif probability >= 0.50:
        risk_level = "Moderate Risk"
    else:
        risk_level = "Low Risk"

    # Generate recommendation
    if risk_level == "High Risk":
        recommendation = (
            "Immediate neurological consultation recommended."
        )
    elif risk_level == "Moderate Risk":
        recommendation = (
            "Further clinical evaluation recommended."
        )
    else:
        recommendation = (
            "Continue routine monitoring."
        )

    # Display report title
    st.subheader("Diagnostic Report")

    # Display diagnosis
    st.write("Diagnosis:", diagnosis)

    # Display probability score
    st.write(
        "Risk Score:",
        f"{probability*100:.2f}%"
    )

    # Display risk level
    st.write("Risk Level:", risk_level)

    # Display recommendation
    st.write(
        "Recommendation:",
        recommendation
    )

    # Connect to SQLite database
    conn = sqlite3.connect(
        "patient_records.db"
    )

    # Create cursor object
    cursor = conn.cursor()

    # Create records table if needed
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS records(
        patient_name TEXT,
        diagnosis TEXT,
        risk_score TEXT
    )
    """)

    # Insert record into database
    cursor.execute("""
    INSERT INTO records
    VALUES (?,?,?)
    """, (
        patient_name,
        diagnosis,
        f"{probability*100:.2f}%"
    ))

    # Save changes
    conn.commit()

    # Close database connection
    conn.close()

    # Display success message
    st.success(
        "Patient record saved successfully."
    )


# View history button
if st.button("View Patient History"):

    # Connect to database
    conn = sqlite3.connect(
        "patient_records.db"
    )

    # Create cursor object
    cursor = conn.cursor()

    # Retrieve all records
    cursor.execute(
        "SELECT * FROM records"
    )

    # Store records
    records = cursor.fetchall()

    # Close database connection
    conn.close()

    # Display records
    st.subheader("Patient History")

    for record in records:
        st.write(record)