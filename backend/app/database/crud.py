"""
CRUD Operations

Reusable database operations for the Parkinson Disease
Detection System.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.database.models import (
    User,
    Patient,
    Prediction,
    Report,
    MedicationReminder,
    ChatHistory,
)


class CRUD:
    """
    Generic CRUD helper.
    """

    # =====================================================
    # USER
    # =====================================================

    @staticmethod
    def create_user(db: Session, user: User) -> User:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_user_by_id(
        db: Session,
        user_id: int,
    ) -> Optional[User]:

        return (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    @staticmethod
    def get_user_by_email(
        db: Session,
        email: str,
    ) -> Optional[User]:

        return (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

    @staticmethod
    def get_users(
        db: Session,
    ) -> List[User]:

        return db.query(User).all()

    @staticmethod
    def delete_user(
        db: Session,
        user_id: int,
    ) -> bool:

        user = CRUD.get_user_by_id(
            db,
            user_id,
        )

        if not user:
            return False

        db.delete(user)
        db.commit()

        return True

    # =====================================================
    # PATIENT
    # =====================================================

    @staticmethod
    def create_patient(
        db: Session,
        patient: Patient,
    ) -> Patient:

        db.add(patient)
        db.commit()
        db.refresh(patient)

        return patient

    @staticmethod
    def get_patient(
        db: Session,
        patient_id: int,
    ) -> Optional[Patient]:

        return (
            db.query(Patient)
            .filter(Patient.id == patient_id)
            .first()
        )

    @staticmethod
    def get_patients(
        db: Session,
    ) -> List[Patient]:

        return db.query(Patient).all()

    @staticmethod
    def update_patient(
        db: Session,
        patient: Patient,
    ) -> Patient:

        db.commit()
        db.refresh(patient)

        return patient

    @staticmethod
    def delete_patient(
        db: Session,
        patient_id: int,
    ) -> bool:

        patient = CRUD.get_patient(
            db,
            patient_id,
        )

        if not patient:
            return False

        db.delete(patient)
        db.commit()

        return True

    # =====================================================
    # PREDICTION
    # =====================================================

    @staticmethod
    def create_prediction(
        db: Session,
        prediction: Prediction,
    ) -> Prediction:

        db.add(prediction)
        db.commit()
        db.refresh(prediction)

        return prediction

    @staticmethod
    def get_prediction(
        db: Session,
        prediction_id: int,
    ) -> Optional[Prediction]:

        return (
            db.query(Prediction)
            .filter(
                Prediction.id == prediction_id
            )
            .first()
        )

    @staticmethod
    def get_patient_predictions(
        db: Session,
        patient_id: int,
    ) -> List[Prediction]:

        return (
            db.query(Prediction)
            .filter(
                Prediction.patient_id == patient_id
            )
            .all()
        )

    @staticmethod
    def delete_prediction(
        db: Session,
        prediction_id: int,
    ) -> bool:

        prediction = CRUD.get_prediction(
            db,
            prediction_id,
        )

        if not prediction:
            return False

        db.delete(prediction)
        db.commit()

        return True

    # =====================================================
    # REPORT
    # =====================================================

    @staticmethod
    def create_report(
        db: Session,
        report: Report,
    ) -> Report:

        db.add(report)
        db.commit()
        db.refresh(report)

        return report

    @staticmethod
    def get_reports(
        db: Session,
        patient_id: int,
    ) -> List[Report]:

        return (
            db.query(Report)
            .filter(
                Report.patient_id == patient_id
            )
            .all()
        )

    # =====================================================
    # MEDICATION REMINDER
    # =====================================================

    @staticmethod
    def create_reminder(
        db: Session,
        reminder: MedicationReminder,
    ) -> MedicationReminder:

        db.add(reminder)
        db.commit()
        db.refresh(reminder)

        return reminder

    @staticmethod
    def get_reminders(
        db: Session,
        patient_id: int,
    ) -> List[MedicationReminder]:

        return (
            db.query(
                MedicationReminder
            )
            .filter(
                MedicationReminder.patient_id
                == patient_id
            )
            .all()
        )

    @staticmethod
    def delete_reminder(
        db: Session,
        reminder_id: int,
    ) -> bool:

        reminder = (
            db.query(MedicationReminder)
            .filter(
                MedicationReminder.id == reminder_id
            )
            .first()
        )

        if not reminder:
            return False

        db.delete(reminder)
        db.commit()

        return True

    # =====================================================
    # CHAT HISTORY
    # =====================================================

    @staticmethod
    def save_chat(
        db: Session,
        chat: ChatHistory,
    ) -> ChatHistory:

        db.add(chat)
        db.commit()
        db.refresh(chat)

        return chat

    @staticmethod
    def get_chat_history(
        db: Session,
        patient_id: int,
    ) -> List[ChatHistory]:

        return (
            db.query(ChatHistory)
            .filter(
                ChatHistory.patient_id == patient_id
            )
            .order_by(
                ChatHistory.created_at.desc()
            )
            .all()
        )

    # =====================================================
    # DASHBOARD
    # =====================================================

    @staticmethod
    def dashboard_statistics(
        db: Session,
    ):

        return {

            "users":
                db.query(User).count(),

            "patients":
                db.query(Patient).count(),

            "predictions":
                db.query(Prediction).count(),

            "reports":
                db.query(Report).count(),

            "reminders":
                db.query(
                    MedicationReminder
                ).count(),

            "chat_messages":
                db.query(
                    ChatHistory
                ).count(),
        }
