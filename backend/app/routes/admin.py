from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from app.database.database import SessionLocal

from app.database.models import (
    User,
    Patient,
    Prediction,
    Report,
)

from app.utils.security import (
    decode_token,
    is_admin,
)


# ==========================================================
# Router
# ==========================================================

router = APIRouter()


# ==========================================================
# HTTP Bearer Authentication
# ==========================================================

bearer_scheme = HTTPBearer(
    auto_error=False
)


# ==========================================================
# Get Current User
# ==========================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme
    ),
):
    """
    Resolve the currently authenticated user from
    the JWT Authorization header.

    This function is local to the Admin router and uses
    the existing security.py implementation.
    """

    # ------------------------------------------------------
    # Check Authorization Header
    # ------------------------------------------------------

    if credentials is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )


    token = credentials.credentials


    if not token:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )


    # ------------------------------------------------------
    # Decode JWT
    # ------------------------------------------------------

    payload = decode_token(
        token
    )


    if payload is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )


    # ------------------------------------------------------
    # Only Access Tokens Allowed
    # ------------------------------------------------------

    token_type = payload.get(
        "type"
    )


    if token_type != "access":

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )


    # ------------------------------------------------------
    # Extract Subject
    # ------------------------------------------------------

    subject = payload.get(
        "sub"
    )


    if subject is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token does not contain a user ID.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )


    try:

        user_id = int(
            subject
        )

    except (
        TypeError,
        ValueError,
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token.",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )


    # ------------------------------------------------------
    # Load User
    # ------------------------------------------------------

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


        return user

    finally:

        db.close()


# ==========================================================
# Admin Authorization
# ==========================================================

def require_admin(
    current_user,
):
    """
    Verify that the authenticated user is an administrator.
    """

    if current_user is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )


    if not is_admin(
        current_user.role
    ):

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Administrator privileges required."
            ),
        )


    return current_user


# ==========================================================
# Admin Dashboard
# ==========================================================

@router.get(
    "/dashboard",
    tags=["Admin"],
)
def admin_dashboard(
    current_user=Depends(
        get_current_user
    ),
):
    """
    Return administrator dashboard statistics.
    """

    admin = require_admin(
        current_user
    )


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
            )


        # --------------------------------------------------
        # Recent Activity
        # --------------------------------------------------

        recent_activity = []


        for user in users:

            recent_activity.append(
                {
                    "type":
                        "User",

                    "description":
                        (
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
            "status":
                "success",

            "administrator": {
                "id":
                    admin.id,

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
    current_user=Depends(
        get_current_user
    ),
):
    """
    Return all users.

    Administrator access required.
    """

    require_admin(
        current_user
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
    current_user=Depends(
        get_current_user
    ),
):
    """
    Return all patients.

    Administrator access required.
    """

    require_admin(
        current_user
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

                    "email":
                        patient.email,

                    "phone":
                        patient.phone,
                }
            )


        return result

    finally:

        db.close()
