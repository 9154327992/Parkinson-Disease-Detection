from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import numpy as np

app = FastAPI(
    title="Parkinson's Disease Detection API",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Replace "*" with your Streamlit URL after deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    model = joblib.load("model.pkl")
    scaler = joblib.load("scaler.pkl")
except Exception as e:
    raise RuntimeError(f"Failed to load model or scaler: {e}")


class PatientData(BaseModel):
    features: list[float]


class PredictionResponse(BaseModel):
    diagnosis: str
    risk_score: float
    risk_level: str
    recommendation: str

@app.get("/")
def home():
    return {
        "message": "Parkinson's Disease Detection API is running"
    }

@app.get("/health")
def health():
    return {
        "status": "Healthy",
        "api": "Running"
    }

@app.post("/predict", response_model=PredictionResponse)
def predict(data: PatientData):

    if len(data.features) != 22:
        raise HTTPException(
            status_code=400,
            detail="Exactly 22 input features are required."
        )

    try:
        patient = np.array(data.features).reshape(1, -1)

        scaled = scaler.transform(patient)

        prediction = model.predict(scaled)[0]

        probability = model.predict_proba(scaled)[0][1]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction Error: {str(e)}"
        )

    if prediction == 1:
        diagnosis = "Parkinson's Disease Detected"
    else:
        diagnosis = "Healthy"

    if probability >= 0.80:
        risk_level = "High Risk"
        recommendation = "Immediate neurological consultation recommended."
    elif probability >= 0.50:
        risk_level = "Moderate Risk"
        recommendation = "Further clinical evaluation recommended."
    else:
        risk_level = "Low Risk"
        recommendation = "Continue routine monitoring."

    return {
        "diagnosis": diagnosis,
        "risk_score": round(probability * 100, 2),
        "risk_level": risk_level,
        "recommendation": recommendation
    }
