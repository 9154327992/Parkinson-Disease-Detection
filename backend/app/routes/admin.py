from fastapi import APIRouter, HTTPException, status

from app.database.database import SessionLocal
from app.database.models import (
    User,
    Patient,
    Prediction,
    Report,
)

from app.utils.security import is_admin


router = APIRouter()


# ==========================================================
# Admin Authorization
# ==========================================================

def require_admin(
    user_id: int,
):
    """
    Verify that the supplied user is an administrator.
    """

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(
                User.id == user_id
            )
            .first()
        )

        if user is None:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found.",
            )

        if not user.is_active:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive.",
            )

        if not is_admin(
            user.role
        ):

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Administrator privileges required."
                ),
            )

        return user

    finally:

        db.close()


# ==========================================================
# Admin Dashboard
# ==========================================================

@router.get(
    "/dashboard",
    tags=["Admin"],
)
def admin_dashboard(
    user_id: int = 1,
):
    """
    Return administrator dashboard statistics.
    """

    admin = require_admin(
        user_id
    )

    db = SessionLocal()

    try:

        # --------------------------------------------------
        # Overall counts
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
        # User roles
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
        # Recent users
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
            )

        # --------------------------------------------------
        # Recent activity
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

        return {
            "status": "success",

            "administrator": {
                "id": admin.id,

                "username":
                    admin.username,

                "role":
                    admin.role,
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
def admin_users(
    user_id: int = 1,
):
    """
    Return all users.
    """

    require_admin(
        user_id
    )

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
def admin_patients(
    user_id: int = 1,
):
    """
    Return all patients.
    """

    require_admin(
        user_id
    )

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

            result.append(
                {
                    "id":
                        patient.id,

                    "patient_name": (
                        f"{patient.first_name} "
                        f"{patient.last_name}"
                    ).strip(),

                    "first_name":
                        patient.first_name,

                    "last_name":
                        patient.last_name,

                    "gender":
                        patient.gender,

                    "age":
                        patient.age,

                    "email":
                        patient.email,

                    "phone":
                        patient.phone,
                }
            )

        return result

    finally:

        db.close()
