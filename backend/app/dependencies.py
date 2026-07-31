"""
Shared FastAPI dependencies.
"""

from typing import Generator

from app.database.database import SessionLocal


# ==========================================================
# Database Dependency
# ==========================================================

def get_db() -> Generator:
    """
    Provide a database session to API routes.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ==========================================================
# Current User (Placeholder)
# ==========================================================

def get_current_user():
    """
    Placeholder for JWT authentication.
    Replace this implementation when authentication is added.
    """

    return {
        "id": 1,
        "username": "admin",
        "role": "Admin"
    }


# ==========================================================
# Admin Authorization
# ==========================================================

def get_admin_user():

    user = get_current_user()

    if user["role"] != "Admin":
        raise PermissionError("Administrator privileges required.")

    return user
