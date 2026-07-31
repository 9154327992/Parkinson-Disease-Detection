"""
Database Models

SQLAlchemy ORM models for the Parkinson Disease
Detection System.
"""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)

from sqlalchemy.orm import relationship

from app.database.database import Base


# ==========================================================
# User
# ==========================================================

class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String(100), unique=True, nullable=False)

    email = Column(String(255), unique=True, nullable=False)

    password = Column(String(255), nullable=False)

    full_name = Column(String(150))

    role = Column(String(50), default="user")

    is_active = Column(Boolean, default=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    patients = relationship(
        "Patient",
        back_populates="owner",
        cascade="all, delete",
    )


# ==========================================================
# Patient
# ==========================================================

class Patient(Base):

    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)

    owner_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    first_name = Column(String(100))

    last_name = Column(String(100))

    gender = Column(String(20))

    age = Column(Integer)

    phone = Column(String(30))

    email = Column(String(255))

    address = Column(Text)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    owner = relationship(
        "User",
        back_populates="patients",
    )

    predictions = relationship(
        "Prediction",
        back_populates="patient",
        cascade="all, delete",
    )

    reports = relationship(
        "Report",
        back_populates="patient",
        cascade="all, delete",
    )

    reminders = relationship(
        "MedicationReminder",
        back_populates="patient",
        cascade="all, delete",
    )

    chats = relationship(
        "ChatHistory",
        back_populates="patient",
        cascade="all, delete",
    )


# ==========================================================
# Prediction
# ==========================================================

class Prediction(Base):

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True)

    patient_id = Column(
        Integer,
        ForeignKey("patients.id")
    )

    prediction = Column(String(100))

    probability = Column(Float)

    confidence = Column(Float)

    risk_level = Column(String(50))

    features = Column(Text)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    patient = relationship(
        "Patient",
        back_populates="predictions",
    )


# ==========================================================
# Report
# ==========================================================

class Report(Base):

    __tablename__ = "reports"

    id = Column(Integer, primary_key=True)

    patient_id = Column(
        Integer,
        ForeignKey("patients.id")
    )

    report_name = Column(String(200))

    report_path = Column(String(500))

    generated_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    patient = relationship(
        "Patient",
        back_populates="reports",
    )


# ==========================================================
# Medication Reminder
# ==========================================================

class MedicationReminder(Base):

    __tablename__ = "medication_reminders"

    id = Column(Integer, primary_key=True)

    patient_id = Column(
        Integer,
        ForeignKey("patients.id")
    )

    medication_name = Column(String(200))

    reminder_time = Column(String(20))

    frequency = Column(String(100))

    is_active = Column(
        Boolean,
        default=True,
    )

    patient = relationship(
        "Patient",
        back_populates="reminders",
    )


# ==========================================================
# Chat History
# ==========================================================

class ChatHistory(Base):

    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True)

    patient_id = Column(
        Integer,
        ForeignKey("patients.id")
    )

    question = Column(Text)

    answer = Column(Text)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    patient = relationship(
        "Patient",
        back_populates="chats",
    )
