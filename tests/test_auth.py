"""
Unit Tests for Authentication Module
"""

import pytest

from app.services.auth_service import AuthService
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    validate_token,
    is_admin,
    is_doctor,
    is_user,
)
from app.schemas.auth import (
    UserRegister,
    UserLogin,
)


# ==========================================================
# Fixtures
# ==========================================================

@pytest.fixture
def auth_service():
    return AuthService()


@pytest.fixture
def sample_user():
    return UserRegister(
        username="john_doe",
        email="john@example.com",
        password="StrongPassword123!",
        role="user",
    )


# ==========================================================
# Password Hashing
# ==========================================================

def test_hash_password():

    password = "MySecurePassword"

    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)


def test_wrong_password():

    password = "password123"

    hashed = hash_password(password)

    assert not verify_password(
        "wrongpassword",
        hashed,
    )


# ==========================================================
# User Registration
# ==========================================================

def test_register_user(
    auth_service,
    sample_user,
):

    user = auth_service.register(sample_user)

    assert user.username == "john_doe"
    assert user.email == "john@example.com"


def test_duplicate_registration(
    auth_service,
    sample_user,
):

    auth_service.register(sample_user)

    with pytest.raises(Exception):

        auth_service.register(sample_user)


# ==========================================================
# User Login
# ==========================================================

def test_login(
    auth_service,
    sample_user,
):

    auth_service.register(sample_user)

    credentials = UserLogin(
        username="john_doe",
        password="StrongPassword123!",
    )

    result = auth_service.login(credentials)

    assert "access_token" in result
    assert "refresh_token" in result


def test_login_invalid_password(
    auth_service,
    sample_user,
):

    auth_service.register(sample_user)

    credentials = UserLogin(
        username="john_doe",
        password="WrongPassword",
    )

    with pytest.raises(Exception):

        auth_service.login(credentials)


# ==========================================================
# JWT Access Token
# ==========================================================

def test_create_access_token():

    token = create_access_token("john_doe")

    assert isinstance(token, str)
    assert validate_token(token)


def test_decode_access_token():

    token = create_access_token("john_doe")

    payload = decode_token(token)

    assert payload["sub"] == "john_doe"
    assert payload["type"] == "access"


# ==========================================================
# Refresh Token
# ==========================================================

def test_create_refresh_token():

    token = create_refresh_token("john_doe")

    payload = decode_token(token)

    assert payload["sub"] == "john_doe"
    assert payload["type"] == "refresh"


# ==========================================================
# Invalid Token
# ==========================================================

def test_invalid_token():

    assert not validate_token("invalid.token.value")


# ==========================================================
# Role Helpers
# ==========================================================

def test_admin_role():

    assert is_admin("admin")


def test_doctor_role():

    assert is_doctor("doctor")


def test_user_role():

    assert is_user("user")


# ==========================================================
# Logout
# ==========================================================

def test_logout(
    auth_service,
):

    result = auth_service.logout()

    assert result is True


# ==========================================================
# Password Change
# ==========================================================

def test_change_password(
    auth_service,
    sample_user,
):

    user = auth_service.register(sample_user)

    changed = auth_service.change_password(
        user.id,
        "StrongPassword123!",
        "NewPassword456!",
    )

    assert changed is True


# ==========================================================
# Authentication Status
# ==========================================================

def test_auth_service_status(
    auth_service,
):

    status = auth_service.status()

    assert status["status"] == "Online"
