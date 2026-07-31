"""
Shared pytest fixtures for the
Parkinson Disease Detection System.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import Base, get_db
from app.utils.security import hash_password
from app.database.models import User


# ==========================================================
# Test Database
# ==========================================================

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ==========================================================
# Create Database
# ==========================================================

Base.metadata.create_all(bind=engine)


# ==========================================================
# Dependency Override
# ==========================================================

def override_get_db():

    db = TestingSessionLocal()

    try:
        yield db

    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# ==========================================================
# Test Client
# ==========================================================

@pytest.fixture(scope="session")
def client():

    with TestClient(app) as test_client:

        yield test_client


# ==========================================================
# Database Session
# ==========================================================

@pytest.fixture(scope="function")
def db():

    connection = engine.connect()

    transaction = connection.begin()

    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()

    transaction.rollback()

    connection.close()


# ==========================================================
# Test User
# ==========================================================

@pytest.fixture(scope="function")
def test_user(db):

    user = User(

        username="tester",

        email="tester@example.com",

        password=hash_password("Password123!"),

        role="user",

    )

    db.add(user)

    db.commit()

    db.refresh(user)

    return user


# ==========================================================
# Admin User
# ==========================================================

@pytest.fixture(scope="function")
def admin_user(db):

    user = User(

        username="admin",

        email="admin@example.com",

        password=hash_password("Admin123!"),

        role="admin",

    )

    db.add(user)

    db.commit()

    db.refresh(user)

    return user


# ==========================================================
# Authentication Token
# ==========================================================

@pytest.fixture(scope="function")
def auth_token(client):

    register_data = {

        "username": "apitest",

        "email": "apitest@example.com",

        "password": "Password123!",

        "role": "user",

    }

    client.post(
        "/api/v1/auth/register",
        json=register_data,
    )

    login = client.post(

        "/api/v1/auth/login",

        json={

            "username": "apitest",

            "password": "Password123!",

        },

    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    return token


# ==========================================================
# Admin Token
# ==========================================================

@pytest.fixture(scope="function")
def admin_token(client):

    register_data = {

        "username": "admin_api",

        "email": "admin_api@example.com",

        "password": "Admin123!",

        "role": "admin",

    }

    client.post(
        "/api/v1/auth/register",
        json=register_data,
    )

    login = client.post(

        "/api/v1/auth/login",

        json={

            "username": "admin_api",

            "password": "Admin123!",

        },

    )

    assert login.status_code == 200

    return login.json()["access_token"]


# ==========================================================
# Sample Patient
# ==========================================================

@pytest.fixture
def sample_patient():

    return {

        "first_name": "John",

        "last_name": "Doe",

        "age": 65,

        "gender": "Male",

        "phone": "123456789",

        "email": "john@example.com",

        "address": "123 Main Street",

    }


# ==========================================================
# Sample Prediction Features
# ==========================================================

@pytest.fixture
def sample_features():

    return [

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


# ==========================================================
# Cleanup
# ==========================================================

@pytest.fixture(autouse=True)
def clean_database(db):

    yield

    for table in reversed(Base.metadata.sorted_tables):

        db.execute(table.delete())

    db.commit()
