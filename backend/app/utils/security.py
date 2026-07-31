"""
Security Utilities

Authentication and authorization helpers for the
Parkinson Disease Detection System.
"""

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.utils.config import settings


# ==========================================================
# Password Hashing
# ==========================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    """
    Hash a plain-text password.
    """
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Verify password.
    """
    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


# ==========================================================
# JWT Tokens
# ==========================================================

def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create JWT access token.
    """

    expire = (
        datetime.utcnow()
        + (
            expires_delta
            or timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        )
    )

    payload = {
        "sub": subject,
        "type": "access",
        "exp": expire,
        "iat": datetime.utcnow(),
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def create_refresh_token(
    subject: str,
) -> str:
    """
    Create refresh token.
    """

    expire = datetime.utcnow() + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    payload = {
        "sub": subject,
        "type": "refresh",
        "exp": expire,
        "iat": datetime.utcnow(),
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


# ==========================================================
# Decode JWT
# ==========================================================

def decode_token(
    token: str,
) -> Optional[dict]:
    """
    Decode JWT token.
    """

    try:

        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

    except JWTError:

        return None


def get_token_subject(
    token: str,
) -> Optional[str]:
    """
    Return subject from token.
    """

    payload = decode_token(token)

    if payload is None:
        return None

    return payload.get("sub")


# ==========================================================
# Token Validation
# ==========================================================

def validate_token(
    token: str,
) -> bool:
    """
    Validate JWT token.
    """

    return decode_token(token) is not None


def is_refresh_token(
    token: str,
) -> bool:
    """
    Check refresh token.
    """

    payload = decode_token(token)

    if payload is None:
        return False

    return payload.get("type") == "refresh"


# ==========================================================
# Role Helpers
# ==========================================================

def is_admin(
    role: str,
) -> bool:

    return role.lower() == "admin"


def is_doctor(
    role: str,
) -> bool:

    return role.lower() == "doctor"


def is_user(
    role: str,
) -> bool:

    return role.lower() == "user"


def has_role(
    role: str,
    allowed_roles: list[str],
) -> bool:
    """
    Generic role check.
    """

    return role.lower() in [
        r.lower()
        for r in allowed_roles
    ]


# ==========================================================
# Authentication Header
# ==========================================================

def extract_bearer_token(
    authorization: str,
) -> Optional[str]:
    """
    Extract Bearer token from header.

    Example:
        Bearer eyJhb...
    """

    if not authorization:
        return None

    parts = authorization.split()

    if len(parts) != 2:
        return None

    if parts[0].lower() != "bearer":
        return None

    return parts[1]


# ==========================================================
# Security Status
# ==========================================================

def security_status():
    """
    Security module information.
    """

    return {
        "status": "Online",
        "jwt_algorithm": settings.ALGORITHM,
        "password_hashing": "bcrypt",
        "version": "1.0.0",
    }
