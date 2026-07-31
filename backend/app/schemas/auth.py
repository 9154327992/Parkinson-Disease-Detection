"""
Authentication Schemas
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ==========================================================
# Base User Schema
# ==========================================================

class UserBase(BaseModel):
    """
    Base user information.
    """

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique username"
    )

    email: EmailStr


# ==========================================================
# Register Request
# ==========================================================

class RegisterRequest(UserBase):
    """
    User registration request.
    """

    full_name: str = Field(
        ...,
        min_length=3,
        max_length=100
    )

    password: str = Field(
        ...,
        min_length=8,
        description="User password"
    )

    confirm_password: str = Field(
        ...,
        min_length=8
    )

    role: str = Field(
        default="User",
        description="User role"
    )


# ==========================================================
# Login Request
# ==========================================================

class LoginRequest(BaseModel):
    """
    User login request.
    """

    username: str
    password: str


# ==========================================================
# User Response
# ==========================================================

class UserResponse(UserBase):
    """
    User information returned by the API.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int

    full_name: str

    role: str

    is_active: bool

    created_at: datetime


# ==========================================================
# Login Response
# ==========================================================

class LoginResponse(BaseModel):
    """
    JWT login response.
    """

    access_token: str

    token_type: str = "bearer"

    expires_in: int

    user: UserResponse


# ==========================================================
# Change Password
# ==========================================================

class ChangePasswordRequest(BaseModel):
    """
    Change current password.
    """

    old_password: str

    new_password: str = Field(
        ...,
        min_length=8
    )

    confirm_password: str


# ==========================================================
# Password Reset Request
# ==========================================================

class PasswordResetRequest(BaseModel):
    """
    Request password reset.
    """

    email: EmailStr


# ==========================================================
# Reset Password
# ==========================================================

class ResetPasswordRequest(BaseModel):
    """
    Reset password using reset token.
    """

    token: str

    new_password: str = Field(
        ...,
        min_length=8
    )


# ==========================================================
# Refresh Token
# ==========================================================

class RefreshTokenRequest(BaseModel):
    """
    Refresh access token.
    """

    refresh_token: str


# ==========================================================
# Token Response
# ==========================================================

class TokenResponse(BaseModel):
    """
    Generic token response.
    """

    access_token: str

    refresh_token: Optional[str] = None

    token_type: str = "bearer"

    expires_in: int


# ==========================================================
# API Message
# ==========================================================

class MessageResponse(BaseModel):
    """
    Standard API message.
    """

    message: str
