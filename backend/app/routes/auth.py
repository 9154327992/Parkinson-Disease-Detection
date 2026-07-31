"""
Authentication Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    UserResponse,
)

from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

auth_service = AuthService()


# ==========================================================
# Register User
# ==========================================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(request: RegisterRequest):
    """
    Register a new user.
    """

    return auth_service.register(request)


# ==========================================================
# Login
# ==========================================================

@router.post(
    "/login",
    response_model=LoginResponse,
)
def login(request: LoginRequest):
    """
    Authenticate user and return JWT token.
    """

    return auth_service.login(request)


# ==========================================================
# Current User
# ==========================================================

@router.get(
    "/me",
    response_model=UserResponse,
)
def current_user(
    user=Depends(auth_service.get_current_user)
):
    """
    Return logged-in user information.
    """

    return user


# ==========================================================
# Refresh Token
# ==========================================================

@router.post("/refresh")
def refresh_token(
    user=Depends(auth_service.get_current_user)
):
    """
    Generate a fresh access token.
    """

    token = auth_service.create_access_token(user)

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# ==========================================================
# Logout
# ==========================================================

@router.post("/logout")
def logout():
    """
    Logout endpoint.

    JWT logout is generally handled on the client side
    by deleting the stored token. If refresh tokens or
    token blacklisting are implemented, this endpoint
    can revoke them.
    """

    return {
        "message": "Successfully logged out."
    }


# ==========================================================
# Change Password
# ==========================================================

@router.post("/change-password")
def change_password(
    old_password: str,
    new_password: str,
    user=Depends(auth_service.get_current_user),
):
    """
    Change current user's password.
    """

    success = auth_service.change_password(
        user=user,
        old_password=old_password,
        new_password=new_password,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect.",
        )

    return {
        "message": "Password updated successfully."
    }
