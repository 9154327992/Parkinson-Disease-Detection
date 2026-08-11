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
    create_refresh_token,
    decode_token,
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
    # User → Response
    # ======================================================

    def _to_response(
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
    # Register
    # ======================================================

    def register(
        self,
        request: RegisterRequest,
    ) -> UserResponse:

        if (
            request.password
            != request.confirm_password
        ):

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match.",
            )

        db = SessionLocal()

        try:

            existing_username = (
                db.query(User)
                .filter(
                    User.username
                    == request.username
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
                    User.email
                    == str(request.email)
                )
                .first()
            )

            if existing_email:

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists.",
                )

            # Never allow normal registration
            # to create an administrator.

            role = (
                str(request.role)
                .strip()
                .lower()
            )

            if role == "admin":

                role = "user"

            if role not in {
                "user",
                "doctor",
            }:

                role = "user"

            user = User(

                username=request.username,

                email=str(request.email),

                full_name=request.full_name,

                password=hash_password(
                    request.password
                ),

                role=role,

                is_active=True,
            )

            db.add(user)

            db.commit()

            db.refresh(user)

            return self._to_response(
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

        db = SessionLocal()

        try:

            user = (
                db.query(User)
                .filter(
                    User.username
                    == request.username
                )
                .first()
            )

            if user is None:

                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid username or password.",
                )

            if not user.is_active:

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is inactive.",
                )

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
            # Use the role stored in the database.
            # ------------------------------------------------

            role = (
                str(user.role)
                .strip()
                .lower()
            )

            # ------------------------------------------------
            # Access token
            # ------------------------------------------------

            access_token = create_access_token(
                str(user.id)
            )

            # ------------------------------------------------
            # Refresh token
            # ------------------------------------------------

            refresh_token = create_refresh_token(
                str(user.id)
            )

            return LoginResponse(

                access_token=access_token,

                token_type="bearer",

                expires_in=3600,

                user=self._to_response(
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
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found.",
                )

            if not user.is_active:

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is inactive.",
                )

            return self._to_response(
                user
            )

        finally:

            db.close()

    # ======================================================
    # Refresh Token
    # ======================================================

    def refresh_token(
        self,
        refresh_token: str,
    ) -> dict:

        payload = decode_token(
            refresh_token
        )

        if payload is None:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token.",
            )

        if payload.get("type") != "refresh":

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token.",
            )

        subject = payload.get(
            "sub"
        )

        if not subject:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token.",
            )

        db = SessionLocal()

        try:

            user = (
                db.query(User)
                .filter(
                    User.id == int(subject)
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

            new_access_token = (
                create_access_token(
                    str(user.id)
                )
            )

            return {

                "access_token":
                    new_access_token,

                "token_type":
                    "bearer",

                "expires_in":
                    3600,
            }

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

        if (
            request.new_password
            != request.confirm_password
        ):

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match.",
            )

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
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found.",
                )

            if not verify_password(
                request.old_password,
                user.password,
            ):

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is incorrect.",
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
    # Logout
    # ======================================================

    def logout(
        self,
        user_id: int,
    ) -> MessageResponse:

        return MessageResponse(
            message="Logged out successfully."
        )

    # ======================================================
    # Create Access Token
    # ======================================================

    def create_access_token(
        self,
        user: UserResponse,
    ) -> str:
        """
        Compatibility method for routes that call
        auth_service.create_access_token().
        """

        return create_access_token(
            str(user.id)
        )
