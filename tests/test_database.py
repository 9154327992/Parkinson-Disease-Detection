"""
Unit Tests for Database Module
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base
from app.database.models import (
    User,
    Patient,
    Prediction,
)
from app.database.crud import CRUD


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

Base.metadata.create_all(bind=engine)


# ==========================================================
# Fixtures
# ==========================================================

@pytest.fixture
def db():

    session = TestingSessionLocal()

    yield session

    session.close()


@pytest.fixture
def crud(db):

    return CRUD(db)


# ==========================================================
# User CRUD
# ==========================================================

def test_create_user(crud):

    user = crud.create_user(

        username="admin",

        email="admin@example.com",

        password="hashed_password",

        role="admin",

    )

    assert user.id is not None
    assert user.username == "admin"


def test_get_user(crud):

    user = crud.create_user(

        username="doctor",

        email="doctor@example.com",

        password="hashed",

        role="doctor",

    )

    result = crud.get_user(user.id)

    assert result.id == user.id


def test_delete_user(crud):

    user = crud.create_user(

        username="user1",

        email="user1@example.com",

        password="hashed",

        role="user",

    )

    assert crud.delete_user(user.id)


# ==========================================================
# Patient CRUD
# ==========================================================

def test_create_patient(crud):

    patient = crud.create_patient(

        first_name="John",

        last_name="Doe",

        age=65,

        gender="Male",

        phone="123456789",

        email="john@example.com",

        address="Street",

    )

    assert patient.id is not None


def test_update_patient(crud):

    patient = crud.create_patient(

        first_name="John",

        last_name="Doe",

        age=60,

        gender="Male",

        phone="111",

        email="john@test.com",

        address="A",

    )

    updated = crud.update_patient(

        patient.id,

        {

            "age": 70,

        },

    )

    assert updated.age == 70


def test_delete_patient(crud):

    patient = crud.create_patient(

        first_name="Jane",

        last_name="Doe",

        age=55,

        gender="Female",

        phone="222",

        email="jane@test.com",

        address="B",

    )

    assert crud.delete_patient(patient.id)


# ==========================================================
# Prediction CRUD
# ==========================================================

def test_create_prediction(crud):

    patient = crud.create_patient(

        first_name="Test",

        last_name="Patient",

        age=65,

        gender="Male",

        phone="999",

        email="test@test.com",

        address="Test",

    )

    prediction = crud.create_prediction(

        patient_id=patient.id,

        prediction="Positive",

        probability=0.91,

        confidence=96.2,

        risk_level="High",

    )

    assert prediction.id is not None


def test_prediction_relationship(crud):

    patient = crud.create_patient(

        first_name="Alice",

        last_name="Smith",

        age=67,

        gender="Female",

        phone="555",

        email="alice@test.com",

        address="Road",

    )

    crud.create_prediction(

        patient_id=patient.id,

        prediction="Negative",

        probability=0.15,

        confidence=87,

        risk_level="Low",

    )

    predictions = crud.get_predictions_by_patient(

        patient.id

    )

    assert len(predictions) == 1


# ==========================================================
# Statistics
# ==========================================================

def test_dashboard_statistics(crud):

    stats = crud.dashboard_statistics()

    assert isinstance(stats, dict)


# ==========================================================
# Database Transactions
# ==========================================================

def test_transaction_commit(db):

    user = User(

        username="commit",

        email="commit@test.com",

        password="hash",

        role="user",

    )

    db.add(user)

    db.commit()

    assert user.id is not None


def test_transaction_rollback(db):

    user = User(

        username="rollback",

        email="rollback@test.com",

        password="hash",

        role="user",

    )

    db.add(user)

    db.rollback()

    result = db.query(User).filter_by(

        username="rollback"

    ).first()

    assert result is None


# ==========================================================
# Relationships
# ==========================================================

def test_patient_prediction_relationship(crud):

    patient = crud.create_patient(

        first_name="Relationship",

        last_name="Test",

        age=70,

        gender="Male",

        phone="111",

        email="relation@test.com",

        address="XYZ",

    )

    crud.create_prediction(

        patient_id=patient.id,

        prediction="Positive",

        probability=0.89,

        confidence=94,

        risk_level="Moderate",

    )

    patient = crud.get_patient(patient.id)

    assert len(patient.predictions) == 1


# ==========================================================
# Database Health
# ==========================================================

def test_database_status():

    from app.database.database import database_status

    status = database_status()

    assert status["status"] == "Online"
