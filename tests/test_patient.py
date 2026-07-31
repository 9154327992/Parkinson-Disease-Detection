"""
Unit Tests for Patient Module
"""

import pytest

from app.services.patient_service import PatientService
from app.schemas.patient import PatientCreate


# ==========================================================
# Fixtures
# ==========================================================

@pytest.fixture
def patient_service():
    return PatientService()


@pytest.fixture
def sample_patient():
    return PatientCreate(
        first_name="John",
        last_name="Doe",
        age=65,
        gender="Male",
        phone="+1234567890",
        email="john@example.com",
        address="123 Main Street"
    )


# ==========================================================
# Create Patient
# ==========================================================

def test_create_patient(
    patient_service,
    sample_patient,
):

    patient = patient_service.create_patient(sample_patient)

    assert patient is not None
    assert patient.first_name == "John"
    assert patient.last_name == "Doe"


# ==========================================================
# Get Patient
# ==========================================================

def test_get_patient(
    patient_service,
    sample_patient,
):

    patient = patient_service.create_patient(sample_patient)

    result = patient_service.get_patient(patient.id)

    assert result.id == patient.id


def test_get_invalid_patient(
    patient_service,
):

    result = patient_service.get_patient(999999)

    assert result is None


# ==========================================================
# Update Patient
# ==========================================================

def test_update_patient(
    patient_service,
    sample_patient,
):

    patient = patient_service.create_patient(sample_patient)

    updated = patient_service.update_patient(
        patient.id,
        {
            "age": 70,
            "phone": "+1111111111"
        }
    )

    assert updated.age == 70
    assert updated.phone == "+1111111111"


# ==========================================================
# Delete Patient
# ==========================================================

def test_delete_patient(
    patient_service,
    sample_patient,
):

    patient = patient_service.create_patient(sample_patient)

    deleted = patient_service.delete_patient(patient.id)

    assert deleted is True


def test_delete_non_existing_patient(
    patient_service,
):

    deleted = patient_service.delete_patient(100000)

    assert deleted is False


# ==========================================================
# List Patients
# ==========================================================

def test_list_patients(
    patient_service,
):

    patients = patient_service.get_all_patients()

    assert isinstance(patients, list)


# ==========================================================
# Search Patient
# ==========================================================

def test_search_patient(
    patient_service,
    sample_patient,
):

    patient_service.create_patient(sample_patient)

    results = patient_service.search_patients("John")

    assert len(results) >= 1


# ==========================================================
# Patient History
# ==========================================================

def test_patient_prediction_history(
    patient_service,
    sample_patient,
):

    patient = patient_service.create_patient(sample_patient)

    history = patient_service.get_prediction_history(
        patient.id
    )

    assert isinstance(history, list)


def test_patient_report_history(
    patient_service,
    sample_patient,
):

    patient = patient_service.create_patient(sample_patient)

    reports = patient_service.get_report_history(
        patient.id
    )

    assert isinstance(reports, list)


# ==========================================================
# Validation
# ==========================================================

def test_invalid_age():

    with pytest.raises(Exception):

        PatientCreate(
            first_name="John",
            last_name="Doe",
            age=-1,
            gender="Male",
            phone="123456789",
            email="john@example.com",
            address="Test"
        )


def test_invalid_email():

    with pytest.raises(Exception):

        PatientCreate(
            first_name="John",
            last_name="Doe",
            age=60,
            gender="Male",
            phone="123456789",
            email="invalid-email",
            address="Test"
        )


# ==========================================================
# Duplicate Email
# ==========================================================

def test_duplicate_email(
    patient_service,
    sample_patient,
):

    patient_service.create_patient(sample_patient)

    with pytest.raises(Exception):

        patient_service.create_patient(sample_patient)


# ==========================================================
# Statistics
# ==========================================================

def test_patient_statistics(
    patient_service,
):

    stats = patient_service.patient_statistics()

    assert isinstance(stats, dict)


# ==========================================================
# Health Check
# ==========================================================

def test_patient_service_status(
    patient_service,
):

    status = patient_service.status()

    assert status["status"] == "Online"
