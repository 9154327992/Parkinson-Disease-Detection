from datetime import datetime

from app.utils.security import hash_password
from app.database.database import (
    SessionLocal,
    create_tables,
)

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
    Seed and repair database sample data.
    """

    # ==========================================================
    # Initialize
    # ==========================================================

    def __init__(self):

        self.db = SessionLocal()

    # ==========================================================
    # Run Seeder
    # ==========================================================

    def seed(self):

        try:

            create_tables()

            self.seed_users()

            self.seed_patients()

            self.seed_predictions()

            self.seed_reports()

            self.seed_reminders()

            self.seed_chat_history()

            print(
                "Database seeded successfully."
            )

        except Exception as e:

            self.db.rollback()

            print(
                f"Database seeding failed: {e}"
            )

            raise

    # ==========================================================
    # Users
    # ==========================================================

    def seed_users(self):
        """
        Create default users if missing.

        If a default user already exists, repair/update
        the account instead of skipping it.

        This is important because an existing admin account
        may have the wrong role.
        """

        # ======================================================
        # Admin
        # ======================================================

        admin = (
            self.db.query(User)
            .filter(
                User.username == "admin"
            )
            .first()
        )

        if admin:

            admin.email = "admin@example.com"

            admin.password = hash_password(
                "admin123"
            )

            admin.full_name = (
                "System Administrator"
            )

            admin.role = "admin"

            admin.is_active = True

            print(
                "Updated existing admin user."
            )

        else:

            admin = User(

                username="admin",

                email="admin@example.com",

                password=hash_password(
                    "admin123"
                ),

                full_name=(
                    "System Administrator"
                ),

                role="admin",

                is_active=True,
            )

            self.db.add(admin)

            print(
                "Created admin user."
            )

        # ======================================================
        # Doctor
        # ======================================================

        doctor = (
            self.db.query(User)
            .filter(
                User.username == "doctor"
            )
            .first()
        )

        if doctor:

            doctor.email = "doctor@example.com"

            doctor.password = hash_password(
                "doctor123"
            )

            doctor.full_name = "Neurologist"

            doctor.role = "doctor"

            doctor.is_active = True

            print(
                "Updated existing doctor user."
            )

        else:

            doctor = User(

                username="doctor",

                email="doctor@example.com",

                password=hash_password(
                    "doctor123"
                ),

                full_name="Neurologist",

                role="doctor",

                is_active=True,
            )

            self.db.add(doctor)

            print(
                "Created doctor user."
            )

        # ======================================================
        # Patient
        # ======================================================

        patient = (
            self.db.query(User)
            .filter(
                User.username == "patient"
            )
            .first()
        )

        if patient:

            patient.email = "patient@example.com"

            patient.password = hash_password(
                "patient123"
            )

            patient.full_name = "John Smith"

            patient.role = "user"

            patient.is_active = True

            print(
                "Updated existing patient user."
            )

        else:

            patient = User(

                username="patient",

                email="patient@example.com",

                password=hash_password(
                    "patient123"
                ),

                full_name="John Smith",

                role="user",

                is_active=True,
            )

            self.db.add(patient)

            print(
                "Created patient user."
            )

        # ======================================================
        # Commit Users
        # ======================================================

        self.db.commit()

        print(
            "Default users verified."
        )

    # ==========================================================
    # Patients
    # ==========================================================

    def seed_patients(self):
        """
        Create sample patient if no patient exists.
        """

        existing_patient = (
            self.db.query(Patient)
            .first()
        )

        if existing_patient:

            print(
                "Patient data already exists. "
                "Skipping sample patient."
            )

            return

        # ------------------------------------------------------
        # Find patient owner
        # ------------------------------------------------------

        user = (
            self.db.query(User)
            .filter(
                User.username == "patient"
            )
            .first()
        )

        if not user:

            print(
                "Patient user not found. "
                "Skipping patient seed."
            )

            return

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

        self.db.add(
            patient
        )

        self.db.commit()

        print(
            "Sample patient created."
        )

    # ==========================================================
    # Predictions
    # ==========================================================

    def seed_predictions(self):
        """
        Create one sample prediction if none exists.
        """

        existing_prediction = (
            self.db.query(Prediction)
            .first()
        )

        if existing_prediction:

            print(
                "Prediction data already exists. "
                "Skipping sample prediction."
            )

            return

        patient = (
            self.db.query(Patient)
            .first()
        )

        if not patient:

            print(
                "No patient found. "
                "Skipping prediction seed."
            )

            return

        prediction = Prediction(

            patient_id=patient.id,

            prediction="Parkinson Detected",

            probability=0.94,

            confidence=94.0,

            risk_level="High Risk",

            features="[sample features]",
        )

        self.db.add(
            prediction
        )

        self.db.commit()

        print(
            "Sample prediction created."
        )

    # ==========================================================
    # Reports
    # ==========================================================

    def seed_reports(self):
        """
        Create one sample report if none exists.
        """

        existing_report = (
            self.db.query(Report)
            .first()
        )

        if existing_report:

            print(
                "Report data already exists. "
                "Skipping sample report."
            )

            return

        patient = (
            self.db.query(Patient)
            .first()
        )

        if not patient:

            print(
                "No patient found. "
                "Skipping report seed."
            )

            return

        report = Report(

            patient_id=patient.id,

            report_name="Initial Assessment",

            report_path="reports/report1.pdf",

            generated_at=datetime.utcnow(),
        )

        self.db.add(
            report
        )

        self.db.commit()

        print(
            "Sample report created."
        )

    # ==========================================================
    # Medication Reminders
    # ==========================================================

    def seed_reminders(self):
        """
        Create sample medication reminders if none exist.
        """

        existing_reminder = (
            self.db.query(
                MedicationReminder
            ).first()
        )

        if existing_reminder:

            print(
                "Medication reminders already exist. "
                "Skipping reminder seed."
            )

            return

        patient = (
            self.db.query(Patient)
            .first()
        )

        if not patient:

            print(
                "No patient found. "
                "Skipping reminder seed."
            )

            return

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

        self.db.add_all(
            reminders
        )

        self.db.commit()

        print(
            "Medication reminders created."
        )

    # ==========================================================
    # Chat History
    # ==========================================================

    def seed_chat_history(self):
        """
        Create sample chat history if none exists.
        """

        existing_chat = (
            self.db.query(
                ChatHistory
            ).first()
        )

        if existing_chat:

            print(
                "Chat history already exists. "
                "Skipping chat seed."
            )

            return

        patient = (
            self.db.query(Patient)
            .first()
        )

        if not patient:

            print(
                "No patient found. "
                "Skipping chat history seed."
            )

            return

        history = ChatHistory(

            patient_id=patient.id,

            question=(
                "What does my prediction mean?"
            ),

            answer=(
                "Your prediction indicates that "
                "the model detected patterns associated "
                "with Parkinson disease. This is not a "
                "diagnosis and should be discussed with "
                "a healthcare professional."
            ),
        )

        self.db.add(
            history
        )

        self.db.commit()

        print(
            "Sample chat history created."
        )

    # ==========================================================
    # Clear Database
    # ==========================================================

    def clear(self):
        """
        Delete all seeded/application data.
        """

        self.db.query(
            ChatHistory
        ).delete()

        self.db.query(
            MedicationReminder
        ).delete()

        self.db.query(
            Report
        ).delete()

        self.db.query(
            Prediction
        ).delete()

        self.db.query(
            Patient
        ).delete()

        self.db.query(
            User
        ).delete()

        self.db.commit()

        print(
            "Database cleared."
        )

    # ==========================================================
    # Close
    # ==========================================================

    def close(self):

        self.db.close()


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    seeder = DatabaseSeeder()

    try:

        seeder.seed()

    finally:

        seeder.close()
