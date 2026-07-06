------------------------------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------------------------------------------
🧠 Parkinson's Disease Detection and Neurological Monitoring Agent
------------------------------------------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------------------------------------------

📌 Project Overview

Parkinson's Disease is a progressive neurological disorder that affects movement and speech. Early diagnosis plays a crucial role in improving patient care and treatment planning.

This project presents an AI-powered Parkinson's Disease Detection and Neurological Monitoring System that combines Machine Learning with a modern web application.

The system analyzes biomedical voice measurements, compares multiple Machine Learning algorithms including Logistic Regression, Artificial Neural Network (ANN), Random Forest, XGBoost, Support Vector Machine (SVM), and K-Nearest Neighbors (KNN). Based on the evaluation results, Logistic Regression was selected as the final deployed model. The system generates diagnostic reports, classifies patient risk levels, and stores patient monitoring records for future reference.

The project is deployed as a full-stack web application using FastAPI and Streamlit.

------------------------------------------------------------------------------------------------------------------------------------

🎯 Objectives

Phase 1 – Machine Learning Model

- Data preprocessing

- Feature scaling using StandardScaler

- Train and evaluate multiple Machine Learning models:

  • Logistic Regression
  • Artificial Neural Network (ANN)
  • Random Forest
  • XGBoost
  • Support Vector Machine (SVM)
  • K-Nearest Neighbors (KNN)

- Compare model performance

- Select the best performing model

- Save the final trained model

- Evaluate model performance using:

- Accuracy

- Precision

- Recall

- F1-Score

- ROC-AUC Score

- Confusion Matrix

------------------------------------------------------------------------------------------------------------------------------------

Phase 2 – Intelligent Neurological Monitoring Agent

Develop an intelligent monitoring system capable of:

- Predicting Parkinson's Disease

- Generating diagnostic reports

- Calculating patient risk scores

- Classifying patient risk levels

- Providing medical recommendations

- Storing monitoring records

- Retrieving patient history

- Deploying as a web application

------------------------------------------------------------------------------------------------------------------------------------

📊 Dataset

The project uses the Parkinson's Disease Dataset containing biomedical voice measurements collected from healthy individuals and Parkinson's patients.

Target Variable

| Status | Meaning |

|---------|----------|

|    0    |  Healthy |

|    1    | Parkinson's Disease |

Number of Features

- 22 Biomedical Voice Features

------------------------------------------------------------------------------------------------------------------------------------

🛠 Technologies Used

- Python

- Pandas

- NumPy

- Scikit-learn

- TensorFlow

- Joblib

- FastAPI

- Streamlit

- SQLite

- Requests

- Uvicorn

- Render

- Streamlit Community Cloud

- GitHub

------------------------------------------------------------------------------------------------------------------------------------

🤖 Machine Learning Models

The following Machine Learning models were implemented and evaluated:

• Logistic Regression

• Artificial Neural Network (ANN)

• Random Forest

• XGBoost

• Support Vector Machine (SVM)

• K-Nearest Neighbors (KNN)

All models were compared using:

- Accuracy
- Precision
- Recall
- F1-Score
- ROC-AUC Score

Based on the evaluation results, Logistic Regression achieved the best overall performance and was selected as the final deployed model.

Performance

- Accuracy: 92.31%

Evaluation Metrics

- Accuracy

- Precision

- Recall

- F1-Score

- ROC-AUC Score

- Confusion Matrix

------------------------------------------------------------------------------------------------------------------------------------

🧠 AI Neurological Monitoring Agent

The Intelligent Monitoring Agent performs the following tasks:

- Accepts biomedical voice measurements

- Validates patient input

- Scales features using StandardScaler

- Predicts Parkinson's Disease

- Calculates Risk Score

- Classifies Risk Level

- Generates Diagnostic Reports

- Provides Medical Recommendations

- Stores Patient Records

- Retrieves Patient History

- Communicates using FastAPI

- Provides an interactive Streamlit interface

-----------------------------------------------------------------------------------------------------------------------------------

📋 Diagnostic Report

For every patient, the system generates:

- Diagnosis

- Risk Score

- Risk Level

- Recommendation

Example

Diagnosis

Parkinson's Disease Detected

Risk Score

99.70%

Risk Level

High Risk

Recommendation

Immediate neurological consultation recommended.

-----------------------------------------------------------------------------------------------------------------------------------

📁 Database

Patient monitoring records are stored using SQLite.

Stored Information

- Patient Name

- Diagnosis

- Risk Score

- Risk Level

- Recommendation

-----------------------------------------------------------------------------------------------------------------------------------

🌐 System Architecture

User

│

▼

Streamlit Frontend

(frontend.py)

│

▼

FastAPI Backend

(backend.py)

│

▼

Selected Machine Learning Model
(Logistic Regression)

│

▼

Diagnostic Report

│

▼

SQLite Database

-----------------------------------------------------------------------------------------------------------------------------------

⚙ FastAPI API Endpoints

Home Endpoint

GET

Returns API status.

-----------------------------------------------------------------------------------------------------------------------------------

Health Endpoint

GET /health

Checks whether the backend is running.

-----------------------------------------------------------------------------------------------------------------------------------

Prediction Endpoint

POST /predict

Accepts 22 biomedical voice features and returns:

- Diagnosis

- Risk Score

- Risk Level

- Recommendation

-----------------------------------------------------------------------------------------------------------------------------------

💻 Streamlit Features

The web application provides:

- Patient Name Input

- 22 Biomedical Feature Inputs

- AI Prediction

- Risk Score Display

- Risk Level Classification

- Diagnostic Report

- SQLite Record Storage

- Patient History Retrieval

-----------------------------------------------------------------------------------------------------------------------------------

📂 Project Structure

Parkinson-Disease-Detection/

│

├── Parkinson's.ipynb

├── backend.py

├── frontend.py

├── model.pkl

├── scaler.pkl

├── parkinsons.csv

├── requirements.txt

├── README.md

-----------------------------------------------------------------------------------------------------------------------------------

🚀 Installation

Clone Repository

github link: [https://github.com/9154327992/Parkinson-Disease-Detection]

-----------------------------------------------------------------------------------------------------------------------------------

Install Dependencies

pip install -r requirements.txt

-----------------------------------------------------------------------------------------------------------------------------------

Run FastAPI Backend

uvicorn backend:app --reload

-----------------------------------------------------------------------------------------------------------------------------------

Run Streamlit Frontend

streamlit run frontend.py

-----------------------------------------------------------------------------------------------------------------------------------

☁ Deployment

⚡Backend

Platform: Render

Backend URL (FastAPI Backend): https://parkinson-disease-detection-qy5l.onrender.com/

🌐Frontend

Platform: Streamlit Community Cloud

Frontend URL (Streamlit Web Application): https://parkinson-disease-detection-lwmcky8dmcjtmip8fb43gy.streamlit.app/

-----------------------------------------------------------------------------------------------------------------------------------

✅ Features

- ✔ Data Preprocessing

- ✔ Multiple Machine Learning Models:

     Logistic Regression

     Artificial Neural Network (ANN)

     Random Forest

     XGBoost

     Support Vector Machine (SVM)

     K-Nearest Neighbors (KNN)

- ✔ StandardScaler

- ✔ FastAPI Backend

- ✔ Streamlit Frontend

- ✔ AI Monitoring Agent

- ✔ Risk Score Generation

- ✔ Risk Level Classification

- ✔ Recommendation Engine

- ✔ SQLite Database Integration

- ✔ Input Validation

- ✔ Patient History Retrieval

- ✔ REST API

- ✔ Web Deployment

- ✔ GitHub Repository

-----------------------------------------------------------------------------------------------------------------------------------

📈 Results

Model Comparison

The following Machine Learning algorithms were evaluated:

• Logistic Regression

• Artificial Neural Network (ANN)

• Random Forest

• XGBoost

• Support Vector Machine (SVM)

• K-Nearest Neighbors (KNN)

Evaluation Metrics

- Accuracy

- Precision

- Recall

- F1-Score

- ROC-AUC Score

Best Performing Model

Logistic Regression

Performance

- Accuracy: 92.31%

The Logistic Regression model achieved the best overall performance based on the evaluation metrics and was selected as the final deployed model.

The deployed application successfully:

- Predicts Parkinson's Disease

- Generates Diagnostic Reports

- Calculates Risk Scores

- Classifies Patient Risk Levels

- Provides Medical Recommendations

- Stores Patient Records

- Retrieves Patient History

- Offers an Interactive Web Interface

-----------------------------------------------------------------------------------------------------------------------------------

🎯 Future Enhancements

- Decision Tree Classifier

- Naïve Bayes Classifier

- Ensemble Learning

- Explainable AI (SHAP/LIME)

- Doctor Dashboard

- Cloud Database (PostgreSQL/MySQL)

- Email Report Generation

- Patient Authentication

- Multi-user Support

- Mobile Application

-----------------------------------------------------------------------------------------------------------------------------------

📄 License

This project is developed for educational and research purposes.

-----------------------------------------------------------------------------------------------------------------------------------

👨‍💻 Author

Matta Venkata Karthik

🎓 B.Tech – Computer Science and Design (Data Science)

🏫 College: NRI Institute Of Technology

🔗 LinkedIn: https://www.linkedin.com/in/venkata-karthik-matta-b0536b321

🏫 College LinkedIn: https://www.linkedin.com/company/datascience-nriit

💻 GitHub: https://github.com/9154327992
