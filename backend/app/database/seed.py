from app.database.database import (
    SessionLocal,
    create_tables,
)


class DatabaseSeeder:
    """
    Initialize the database structure.

    No default users are created.
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
    # Disabled Sample Data
    # ==========================================================

    def seed_users(self):

        print(
            "Default user seeding disabled."
        )

    def seed_patients(self):

        print(
            "Sample patient seeding disabled."
        )

    def seed_predictions(self):

        print(
            "Sample prediction seeding disabled."
        )

    def seed_reports(self):

        print(
            "Sample report seeding disabled."
        )

    def seed_reminders(self):

        print(
            "Sample medication reminder seeding disabled."
        )

    def seed_chat_history(self):

        print(
            "Sample chat history seeding disabled."
        )

    # ==========================================================
    # Clear Patient Data
    # ==========================================================

    def clear_patient_data(self):

        from app.database.models import (
            Patient,
            Prediction,
            Report,
            MedicationReminder,
            ChatHistory,
        )

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
            "Patient data cleared."
        )

    # ==========================================================
    # Clear Users
    # ==========================================================

    def clear_users(self):

        from app.database.models import User

        self.db.query(
            User
        ).delete(
            synchronize_session=False
        )

        self.db.commit()

        print(
            "All users cleared."
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
