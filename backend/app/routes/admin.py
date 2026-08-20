from fastapi import APIRouter, HTTPException, status

from app.database.database import SessionLocal

from app.database.models import (
    User,
    Patient,
    Prediction,
    Report,
)


# ==========================================================
# Router
# ==========================================================

router = APIRouter()


# ==========================================================
# Admin Dashboard
# ==========================================================

@router.get(
    "/dashboard",
    tags=["Admin"],
)
def admin_dashboard():
    """
    Return administrator dashboard statistics.

    Authentication is disabled for this application.
    """

    db = SessionLocal()

    try:

        # --------------------------------------------------
        # Overall Counts
        # --------------------------------------------------

        total_users = (
            db.query(User).count()
        )

        total_patients = (
            db.query(Patient).count()
        )

        total_predictions = (
            db.query(Prediction).count()
        )

        total_reports = (
            db.query(Report).count()
        )

        # --------------------------------------------------
        # User Roles
        # --------------------------------------------------

        admin_users = (
            db.query(User)
            .filter(
                User.role.ilike("admin")
            )
            .count()
        )

        doctor_users = (
            db.query(User)
            .filter(
                User.role.ilike("doctor")
            )
            .count()
        )

        normal_users = (
            db.query(User)
            .filter(
                User.role.ilike("user")
            )
            .count()
        )

        # --------------------------------------------------
        # Recent Users
        # --------------------------------------------------

        users = (
            db.query(User)
            .order_by(
                User.created_at.desc()
            )
            .limit(10)
            .all()
        )

        recent_users = []

        for user in users:

            recent_users.append(
                {
                    "id": user.id,

                    "username": user.username,

                    "full_name": user.full_name,

                    "email": user.email,

                    "role": user.role,

                    "is_active": user.is_active,

                    "created_at": (
                        user.created_at.isoformat()
                        if user.created_at
                        else None
                    ),
                }
            )

        # --------------------------------------------------
        # Recent Activity
        # --------------------------------------------------

        recent_activity = []

        for user in users:

            recent_activity.append(
                {
                    "type": "User",

                    "description": (
                        f"User '{user.username}' "
                        "registered."
                    ),

                    "created_at": (
                        user.created_at.isoformat()
                        if user.created_at
                        else None
                    ),
                }
            )

        # --------------------------------------------------
        # Response
        # --------------------------------------------------

        return {
            "status": "success",

            "administrator": {
                "id": None,
                "username": "Administrator",
                "role": "Administrator",
            },

            "total_users":
                total_users,

            "total_patients":
                total_patients,

            "total_predictions":
                total_predictions,

            "total_reports":
                total_reports,

            "user_roles": {
                "admins":
                    admin_users,

                "doctors":
                    doctor_users,

                "users":
                    normal_users,
            },

            "recent_users":
                recent_users,

            "recent_activity":
                recent_activity,
        }

    finally:

        db.close()


# ==========================================================
# Admin Users
# ==========================================================

@router.get(
    "/users",
    tags=["Admin"],
)
def admin_users():
    """
    Return all users.

    Authentication is disabled.
    """

    db = SessionLocal()

    try:

        users = (
            db.query(User)
            .order_by(
                User.id.asc()
            )
            .all()
        )

        return [
            {
                "id":
                    user.id,

                "username":
                    user.username,

                "full_name":
                    user.full_name,

                "email":
                    user.email,

                "role":
                    user.role,

                "is_active":
                    user.is_active,

                "created_at": (
                    user.created_at.isoformat()
                    if user.created_at
                    else None
                ),
            }

            for user in users
        ]

    finally:

        db.close()


# ==========================================================
# Admin Patients
# ==========================================================

@router.get(
    "/patients",
    tags=["Admin"],
)
def admin_patients():
    """
    Return all patients.

    Only basic patient information is returned.
    Email and phone are intentionally excluded.
    """

    db = SessionLocal()

    try:

        patients = (
            db.query(Patient)
            .order_by(
                Patient.id.asc()
            )
            .all()
        )

        result = []

        for patient in patients:

            first_name = (
                patient.first_name
                or ""
            )

            last_name = (
                patient.last_name
                or ""
            )

            full_patient_name = (
                f"{first_name} "
                f"{last_name}"
            ).strip()

            result.append(
                {
                    "id":
                        patient.id,

                    "patient_id":
                        patient.id,

                    "patient_name":
                        full_patient_name,

                    "first_name":
                        patient.first_name,

                    "last_name":
                        patient.last_name,

                    "gender":
                        patient.gender,

                    "age":
                        patient.age,
                }
            )

        return result

    finally:

        db.close()
