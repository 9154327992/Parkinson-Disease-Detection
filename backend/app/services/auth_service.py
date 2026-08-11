from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status

from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    LoginResponse,
    UserResponse,
    ChangePasswordRequest,
    MessageResponse,
)

from app.database.database import SessionLocal

from app.database.models import User

from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
)


class AuthService:
    """
    Authentication business logic.
    """

    # ======================================================
    # Initialize
    # ======================================================

    def __init__(self):
        pass

    # ======================================================
    # Database Helper
    # ======================================================

    def _get_db(self):
        return SessionLocal()

    # ======================================================
    # Convert User Model → Response
    # ======================================================

    def _user_response(
        self,
        user: User,
    ) -> UserResponse:

        return UserResponse(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
        )

    # ======================================================
    # Register User
    # ======================================================

    def register(
        self,
        request: RegisterRequest,
    ) -> UserResponse:
        """
        Register a new user.
        """

        if request.password != request.confirm_password:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match.",
            )

        db = self._get_db()

        try:

            existing_username = (
                db.query(User)
                .filter(
                    User.username == request.username
                )
                .first()
            )

            if existing_username:

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already exists.",
                )

            existing_email = (
                db.query(User)
                .filter(
                    User.email == str(request.email)
                )
                .first()
            )

            if existing_email:

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists.",
                )

            # --------------------------------------------------
            # Security:
            # Never allow public registration to create admin
            # accounts.
            # --------------------------------------------------

            requested_role = (
                str(request.role)
                .strip()
                .lower()
            )

            if requested_role == "admin":

                requested_role = "user"

            if requested_role not in {
                "user",
                "doctor",
            }:

                requested_role = "user"

            user = User(

                username=request.username,

                email=str(request.email),

                password=hash_password(
                    request.password
                ),

                full_name=request.full_name,

                role=requested_role,

                is_active=True,
            )

            db.add(user)

            db.commit()

            db.refresh(user)

            return self._user_response(
                user
            )

        finally:

            db.close()

    # ======================================================
    # Login
    # ======================================================

    def login(
        self,
        request: LoginRequest,
    ) -> LoginResponse:
        """
        Authenticate user using the database.
        """

        db = self._get_db()

        try:

            user = (
                db.query(User)
                .filter(
                    User.username == request.username
                )
                .first()
            )

            # ------------------------------------------------
            # User not found
            # ------------------------------------------------

            if user is None:

                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid username or password.",
                )

            # ------------------------------------------------
            # Account disabled
            # ------------------------------------------------

            if not user.is_active:

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is inactive.",
                )

            # ------------------------------------------------
            # Verify password
            # ------------------------------------------------

            if not verify_password(
                request.password,
                user.password,
            ):

                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid username or password.",
                )

            # ------------------------------------------------
            # IMPORTANT:
            # Role comes directly from database.
            # ------------------------------------------------

            access_token = create_access_token(
                {
                    "sub": str(user.id),
                    "username": user.username,
                    "role": user.role,
                }
            )

            return LoginResponse(

                access_token=access_token,

                token_type="bearer",

                expires_in=3600,

                user=self._user_response(
                    user
                ),
            )

        finally:

            db.close()

    # ======================================================
    # Current User
    # ======================================================

    def get_current_user(
        self,
        user_id: int,
    ) -> UserResponse:
        """
        Return the actual authenticated user
        from the database.
        """

        db = self._get_db()

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

            return self._user_response(
                user
            )

        finally:

            db.close()

    # ======================================================
    # Change Password
    # ======================================================

    def change_password(
        self,
        user_id: int,
        request: ChangePasswordRequest,
    ) -> MessageResponse:
        """
        Change current user's password.
        """

        if (
            request.new_password
            != request.confirm_password
        ):

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match.",
            )

        db = self._get_db()

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
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found.",
                )

            if not verify_password(
                request.old_password,
                user.password,
            ):

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Old password is incorrect.",
                )

            user.password = hash_password(
                request.new_password
            )

            db.commit()

            return MessageResponse(
                message="Password changed successfully."
            )

        finally:

            db.close()

    # ======================================================
    # Refresh Token
    # ======================================================

    def refresh_token(
        self,
        user_id: int,
    ) -> dict:
        """
        Generate a new access token.
        """

        db = self._get_db()

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

            token = create_access_token(
                {
                    "sub": str(user.id),
                    "username": user.username,
                    "role": user.role,
                }
            )

            return {
                "access_token": token,
                "token_type": "bearer",
                "expires_in": 3600,
            }

        finally:

            db.close()

    # ======================================================
    # Logout
    # ======================================================

    def logout(
        self,
        user_id: int,
    ) -> MessageResponse:
        """
        Logout user.

        JWT logout is normally handled client-side
        by removing the access token.
        """

        return MessageResponse(
            message="Logged out successfully."
        )
