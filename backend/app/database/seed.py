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
    Initialize required database users.

    No sample patients, predictions, reports,
    reminders, or chat history are created.
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

            # Only default application users are created.
            # No fake/sample patient data is inserted.
            self.seed_users()

            print(
                "Database initialized successfully."
            )

        except Exception as e:

            self.db.rollback()

            print(
                f"Database initialization failed: {e}"
            )

            raise

    # ==========================================================
    # Users
    # ==========================================================

    def seed_users(self):
        """
        Create or repair the default application users.

        These are application accounts, not patient records.
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

            self.db.add(
                admin
            )

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

            self.db.add(
                doctor
            )

            print(
                "Created doctor user."
            )

        # ======================================================
        # Regular User
        # ======================================================

        user = (
            self.db.query(User)
            .filter(
                User.username == "patient"
            )
            .first()
        )

        if user:

            user.email = "patient@example.com"

            user.password = hash_password(
                "patient123"
            )

            user.full_name = "User"

            user.role = "user"

            user.is_active = True

            print(
                "Updated existing regular user."
            )

        else:

            user = User(

                username="patient",

                email="patient@example.com",

                password=hash_password(
                    "patient123"
                ),

                full_name="User",

                role="user",

                is_active=True,
            )

            self.db.add(
                user
            )

            print(
                "Created regular user."
            )

        # ======================================================
        # Commit Users
        # ======================================================

        self.db.commit()

        print(
            "Default users verified."
        )

    # ==========================================================
    # Patient Seeding Disabled
    # ==========================================================

    def seed_patients(self):
        """
        Sample patient creation is intentionally disabled.

        Patients must only be created through the
        actual Prediction workflow.
        """

        print(
            "Sample patient seeding disabled."
        )

    # ==========================================================
    # Prediction Seeding Disabled
    # ==========================================================

    def seed_predictions(self):
        """
        Sample prediction creation is intentionally disabled.

        Predictions must only be created after an actual
        prediction request.
        """

        print(
            "Sample prediction seeding disabled."
        )

    # ==========================================================
    # Report Seeding Disabled
    # ==========================================================

    def seed_reports(self):
        """
        Sample report creation is intentionally disabled.

        Reports must only be generated from actual
        patient predictions.
        """

        print(
            "Sample report seeding disabled."
        )

    # ==========================================================
    # Medication Reminder Seeding Disabled
    # ==========================================================

    def seed_reminders(self):
        """
        Sample medication reminders are disabled.

        Reminders must belong to actual patients.
        """

        print(
            "Sample medication reminder seeding disabled."
        )

    # ==========================================================
    # Chat History Seeding Disabled
    # ==========================================================

    def seed_chat_history(self):
        """
        Sample chat history is disabled.

        Chat history must belong to actual patients.
        """

        print(
            "Sample chat history seeding disabled."
        )

    # ==========================================================
    # Remove Sample Data
    # ==========================================================

    def remove_sample_data(self):
        """
        Remove the previously seeded John Smith sample
        and its sample prediction/report.

        This does NOT delete users.
        """

        # ------------------------------------------------------
        # Find sample patient
        # ------------------------------------------------------

        sample_patient = (
            self.db.query(Patient)
            .filter(
                Patient.first_name == "John",
                Patient.last_name == "Smith",
                Patient.email == "john@example.com",
            )
            .first()
        )

        if sample_patient:

            # --------------------------------------------------
            # Delete sample chat history
            # --------------------------------------------------

            self.db.query(
                ChatHistory
            ).filter(
                ChatHistory.patient_id
                == sample_patient.id
            ).delete(
                synchronize_session=False
            )

            # --------------------------------------------------
            # Delete sample reminders
            # --------------------------------------------------

            self.db.query(
                MedicationReminder
            ).filter(
                MedicationReminder.patient_id
                == sample_patient.id
            ).delete(
                synchronize_session=False
            )

            # --------------------------------------------------
            # Delete sample reports
            # --------------------------------------------------

            self.db.query(
                Report
            ).filter(
                Report.patient_id
                == sample_patient.id
            ).delete(
                synchronize_session=False
            )

            # --------------------------------------------------
            # Delete sample predictions
            # --------------------------------------------------

            self.db.query(
                Prediction
            ).filter(
                Prediction.patient_id
                == sample_patient.id
            ).delete(
                synchronize_session=False
            )

            # --------------------------------------------------
            # Delete sample patient
            # --------------------------------------------------

            self.db.delete(
                sample_patient
            )

            self.db.commit()

            print(
                "Sample John Smith patient data removed."
            )

        else:

            print(
                "Sample John Smith patient not found."
            )

    # ==========================================================
    # Clear Application Data
    # ==========================================================

    def clear_patient_data(self):
        """
        Delete patient-related application data.

        Users are NOT deleted.
        """

        self.db.query(
            ChatHistory
        ).delete(
            synchronize_session=False
        )

        self.db.query(
            MedicationReminder
        ).delete(
            synchronize_session=False
        )

        self.db.query(
            Report
        ).delete(
            synchronize_session=False
        )

        self.db.query(
            Prediction
        ).delete(
            synchronize_session=False
        )

        self.db.query(
            Patient
        ).delete(
            synchronize_session=False
        )

        self.db.commit()

        print(
            "Patient, prediction, report, reminder, "
            "and chat data cleared."
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

        # Initialize database and default users.
        seeder.seed()

        # Remove the previously created sample
        # John Smith patient and related sample data.
        seeder.remove_sample_data()

    finally:

        seeder.close()
