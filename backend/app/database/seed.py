"""
Database Seeder

Populate the database with sample data for
development and testing.
"""

from datetime import datetime

from app.database.database import SessionLocal
from app.database.database import create_tables

from app.database.models import (
    User,
    Patient,
    Prediction,
    Report,
    MedicationReminder,
    ChatHistory,
)


class DatabaseSeeder:
    """
    Seed the database with sample records.
    """

    def __init__(self):

        self.db = SessionLocal()

    # =====================================================
    # Run Seeder
    # =====================================================

    def seed(self):

        create_tables()

        self.seed_users()
        self.seed_patients()
        self.seed_predictions()
        self.seed_reports()
        self.seed_reminders()
        self.seed_chat_history()

        print("Database seeded successfully.")

    # =====================================================
    # Users
    # =====================================================

    def seed_users(self):

        if self.db.query(User).count() > 0:
            return

        users = [

            User(
                username="admin",
                email="admin@example.com",
                password="admin123",
                full_name="System Administrator",
                role="admin",
            ),

            User(
                username="doctor",
                email="doctor@example.com",
                password="doctor123",
                full_name="Neurologist",
                role="doctor",
            ),

            User(
                username="patient",
                email="patient@example.com",
                password="patient123",
                full_name="John Smith",
                role="user",
            ),
        ]

        self.db.add_all(users)
        self.db.commit()

    # =====================================================
    # Patients
    # =====================================================

    def seed_patients(self):

        if self.db.query(Patient).count() > 0:
            return

        user = (
            self.db.query(User)
            .filter(User.username == "patient")
            .first()
        )

        patient = Patient(

            owner_id=user.id,

            first_name="John",

            last_name="Smith",

            gender="Male",

            age=64,

            phone="1234567890",

            email="john@example.com",

            address="Sample Address",

        )

        self.db.add(patient)
        self.db.commit()

    # =====================================================
    # Predictions
    # =====================================================

    def seed_predictions(self):

        if self.db.query(Prediction).count() > 0:
            return

        patient = self.db.query(Patient).first()

        prediction = Prediction(

            patient_id=patient.id,

            prediction="Parkinson Detected",

            probability=0.94,

            confidence=94.0,

            risk_level="High Risk",

            features="[sample features]",

        )

        self.db.add(prediction)
        self.db.commit()

    # =====================================================
    # Reports
    # =====================================================

    def seed_reports(self):

        if self.db.query(Report).count() > 0:
            return

        patient = self.db.query(Patient).first()

        report = Report(

            patient_id=patient.id,

            report_name="Initial Assessment",

            report_path="reports/report1.pdf",

            generated_at=datetime.utcnow(),

        )

        self.db.add(report)
        self.db.commit()

    # =====================================================
    # Medication Reminders
    # =====================================================

    def seed_reminders(self):

        if self.db.query(MedicationReminder).count() > 0:
            return

        patient = self.db.query(Patient).first()

        reminders = [

            MedicationReminder(

                patient_id=patient.id,

                medication_name="Levodopa",

                reminder_time="08:00",

                frequency="Daily",

            ),

            MedicationReminder(

                patient_id=patient.id,

                medication_name="Levodopa",

                reminder_time="20:00",

                frequency="Daily",

            ),
        ]

        self.db.add_all(reminders)
        self.db.commit()

    # =====================================================
    # Chat History
    # =====================================================

    def seed_chat_history(self):

        if self.db.query(ChatHistory).count() > 0:
            return

        patient = self.db.query(Patient).first()

        history = ChatHistory(

            patient_id=patient.id,

            question="What does my prediction mean?",

            answer=(
                "Your prediction indicates that the model "
                "detected patterns associated with Parkinson "
                "disease. This is not a diagnosis and should "
                "be discussed with a healthcare professional."
            ),

        )

        self.db.add(history)
        self.db.commit()

    # =====================================================
    # Clear Database
    # =====================================================

    def clear(self):

        self.db.query(ChatHistory).delete()
        self.db.query(MedicationReminder).delete()
        self.db.query(Report).delete()
        self.db.query(Prediction).delete()
        self.db.query(Patient).delete()
        self.db.query(User).delete()

        self.db.commit()

        print("Database cleared.")

    # =====================================================
    # Close
    # =====================================================

    def close(self):

        self.db.close()


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    seeder = DatabaseSeeder()

    seeder.seed()

    seeder.close()
