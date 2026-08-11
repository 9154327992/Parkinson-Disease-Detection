from datetime import datetime, timedelta
from typing import Optional

import bcrypt

from jose import JWTError, jwt

from app.utils.config import settings


# ==========================================================
# Password Hashing
# ==========================================================

def hash_password(
    password: str,
) -> str:
    """
    Hash a plain-text password using bcrypt.
    """

    if not isinstance(password, str):
        raise ValueError(
            "Password must be a string."
        )

    password_bytes = password.encode(
        "utf-8"
    )

    if len(password_bytes) > 72:
        raise ValueError(
            "Password cannot be longer than 72 bytes."
        )

    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt(),
    )

    return hashed.decode(
        "utf-8"
    )


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Verify a plain-text password against
    a bcrypt password hash.
    """

    if not isinstance(
        plain_password,
        str,
    ):
        return False

    if not isinstance(
        hashed_password,
        str,
    ):
        return False

    password_bytes = (
        plain_password.encode(
            "utf-8"
        )
    )

    if len(password_bytes) > 72:
        return False

    try:

        return bcrypt.checkpw(
            password_bytes,
            hashed_password.encode(
                "utf-8"
            ),
        )

    except (
        ValueError,
        TypeError,
    ):

        return False


# ==========================================================
# JWT Tokens
# ==========================================================

def create_access_token(
    subject: str,
    expires_delta: Optional[
        timedelta
    ] = None,
) -> str:
    """
    Create JWT access token.
    """

    expire = (
        datetime.utcnow()
        + (
            expires_delta
            or timedelta(
                minutes=(
                    settings
                    .ACCESS_TOKEN_EXPIRE_MINUTES
                )
            )
        )
    )

    payload = {
        "sub": str(subject),

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
    Create JWT refresh token.
    """

    expire = (
        datetime.utcnow()
        + timedelta(
            days=(
                settings
                .REFRESH_TOKEN_EXPIRE_DAYS
            )
        )
    )

    payload = {
        "sub": str(subject),

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

    if not token:
        return None

    try:

        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[
                settings.ALGORITHM
            ],
        )

    except JWTError:

        return None


def get_token_subject(
    token: str,
) -> Optional[str]:
    """
    Return subject from token.
    """

    payload = decode_token(
        token
    )

    if payload is None:
        return None

    subject = payload.get(
        "sub"
    )

    if subject is None:
        return None

    return str(subject)


# ==========================================================
# Token Validation
# ==========================================================

def validate_token(
    token: str,
) -> bool:
    """
    Validate JWT token.
    """

    return (
        decode_token(token)
        is not None
    )


def is_refresh_token(
    token: str,
) -> bool:
    """
    Check whether token is a refresh token.
    """

    payload = decode_token(
        token
    )

    if payload is None:
        return False

    return (
        payload.get("type")
        == "refresh"
    )


# ==========================================================
# Role Helpers
# ==========================================================

def is_admin(
    role: str,
) -> bool:
    """
    Check administrator role.
    """

    if not role:
        return False

    return (
        role.strip().lower()
        == "admin"
    )


def is_doctor(
    role: str,
) -> bool:
    """
    Check doctor role.
    """

    if not role:
        return False

    return (
        role.strip().lower()
        == "doctor"
    )


def is_user(
    role: str,
) -> bool:
    """
    Check normal user role.
    """

    if not role:
        return False

    return (
        role.strip().lower()
        == "user"
    )


def has_role(
    role: str,
    allowed_roles: list[str],
) -> bool:
    """
    Generic role check.
    """

    if not role:
        return False

    normalized_role = (
        role.strip().lower()
    )

    return normalized_role in [
        str(allowed_role)
        .strip()
        .lower()
        for allowed_role
        in allowed_roles
    ]


# ==========================================================
# Authentication Header
# ==========================================================

def extract_bearer_token(
    authorization: str,
) -> Optional[str]:
    """
    Extract Bearer token from Authorization header.

    Example:

        Bearer eyJhb...
    """

    if not authorization:
        return None

    parts = authorization.split()

    if len(parts) != 2:
        return None

    if (
        parts[0].lower()
        != "bearer"
    ):
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

        "jwt_algorithm":
            settings.ALGORITHM,

        "password_hashing":
            "bcrypt",

        "version":
            "1.0.0",
    }
