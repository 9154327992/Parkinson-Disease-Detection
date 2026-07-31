"""
Integration Tests for FastAPI API
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ==========================================================
# Health Check
# ==========================================================

def test_health():

    response = client.get("/")

    assert response.status_code == 200

    body = response.json()

    assert "status" in body


# ==========================================================
# Authentication
# ==========================================================

def test_register_user():

    payload = {
        "username": "apitest",
        "email": "apitest@example.com",
        "password": "Password123!",
        "role": "user",
    }

    response = client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    assert response.status_code in (200, 201)


def test_login():

    payload = {
        "username": "apitest",
        "password": "Password123!",
    }

    response = client.post(
        "/api/v1/auth/login",
        json=payload,
    )

    assert response.status_code == 200

    body = response.json()

    assert "access_token" in body
    assert "refresh_token" in body


# ==========================================================
# Patient API
# ==========================================================

def test_create_patient(auth_token):

    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "age": 65,
        "gender": "Male",
        "phone": "123456789",
        "email": "john@example.com",
        "address": "123 Main Street",
    }

    response = client.post(
        "/api/v1/patients",
        json=payload,
        headers={
            "Authorization": f"Bearer {auth_token}"
        },
    )

    assert response.status_code == 201


def test_get_patients(auth_token):

    response = client.get(
        "/api/v1/patients",
        headers={
            "Authorization": f"Bearer {auth_token}"
        },
    )

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        list,
    )


# ==========================================================
# Prediction API
# ==========================================================

def test_prediction(auth_token):

    payload = {

        "features": [

            119.992,
            157.302,
            74.997,
            0.00784,
            0.00007,
            0.00370,
            0.00554,
            0.01109,
            0.04374,
            0.426,
            0.02182,
            0.03130,
            0.02971,
            0.06545,
            0.02211,
            21.033,
            0.414783,
            0.815285,
            -4.813031,
            0.266482,
            2.301442,
            0.284654,

        ]

    }

    response = client.post(

        "/api/v1/predictions",

        json=payload,

        headers={
            "Authorization": f"Bearer {auth_token}"
        },

    )

    assert response.status_code == 200

    body = response.json()

    assert "prediction" in body

    assert "probability" in body


# ==========================================================
# Reports
# ==========================================================

def test_generate_report(auth_token):

    response = client.post(

        "/api/v1/reports/1",

        headers={
            "Authorization": f"Bearer {auth_token}"
        },

    )

    assert response.status_code == 200


# ==========================================================
# Analytics
# ==========================================================

def test_dashboard(auth_token):

    response = client.get(

        "/api/v1/analytics/dashboard",

        headers={
            "Authorization": f"Bearer {auth_token}"
        },

    )

    assert response.status_code == 200


# ==========================================================
# Chatbot
# ==========================================================

def test_chatbot(auth_token):

    payload = {

        "message": "What is Parkinson disease?"

    }

    response = client.post(

        "/api/v1/chatbot",

        json=payload,

        headers={
            "Authorization": f"Bearer {auth_token}"
        },

    )

    assert response.status_code == 200


# ==========================================================
# Unauthorized Access
# ==========================================================

def test_unauthorized_patient_access():

    response = client.get(

        "/api/v1/patients"

    )

    assert response.status_code in (

        401,
        403,

    )


# ==========================================================
# Invalid Prediction
# ==========================================================

def test_invalid_prediction(auth_token):

    payload = {

        "features": [1, 2]

    }

    response = client.post(

        "/api/v1/predictions",

        json=payload,

        headers={
            "Authorization": f"Bearer {auth_token}"
        },

    )

    assert response.status_code == 422


# ==========================================================
# 404
# ==========================================================

def test_invalid_route():

    response = client.get(

        "/api/v1/unknown"

    )

    assert response.status_code == 404


# ==========================================================
# API Status
# ==========================================================

def test_openapi():

    response = client.get(

        "/openapi.json"

    )

    assert response.status_code == 200


def test_docs():

    response = client.get(

        "/docs"

    )

    assert response.status_code == 200
