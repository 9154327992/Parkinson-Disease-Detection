"""
Validation utilities for the Parkinson Disease Detection Agent.
"""

import re
from typing import List


# ==========================================================
# Patient Validation
# ==========================================================

def validate_patient_name(name: str):
    """
    Validate patient name.
    """

    if not name.strip():
        return False, "Patient name is required."

    if len(name.strip()) < 3:
        return False, "Patient name must be at least 3 characters."

    return True, ""


def validate_age(age: int):
    """
    Validate patient age.
    """

    if age < 1 or age > 120:
        return False, "Age must be between 1 and 120."

    return True, ""


def validate_gender(gender: str):
    """
    Validate gender.
    """

    allowed = ["Male", "Female", "Other"]

    if gender not in allowed:
        return False, "Invalid gender selected."

    return True, ""


# ==========================================================
# Voice Features Validation
# ==========================================================

def validate_voice_features(features: List[float]):
    """
    Validate the 22 voice features.
    """

    if len(features) != 22:
        return False, "Exactly 22 voice features are required."

    for value in features:

        if value is None:
            return False, "Voice measurements cannot be empty."

        if not isinstance(value, (int, float)):
            return False, "Voice measurements must be numeric."

    return True, ""


# ==========================================================
# Email Validation
# ==========================================================

def validate_email(email: str):

    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    if not re.match(pattern, email):
        return False, "Invalid email address."

    return True, ""


# ==========================================================
# Username Validation
# ==========================================================

def validate_username(username: str):

    if len(username.strip()) < 4:
        return False, "Username must be at least 4 characters."

    return True, ""


# ==========================================================
# Password Validation
# ==========================================================

def validate_password(password: str):
    """
    Password Requirements

    - Minimum 8 characters
    - One uppercase
    - One lowercase
    - One digit
    - One special character
    """

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain an uppercase letter."

    if not re.search(r"[a-z]", password):
        return False, "Password must contain a lowercase letter."

    if not re.search(r"\d", password):
        return False, "Password must contain a number."

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain a special character."

    return True, ""


def validate_confirm_password(password, confirm):

    if password != confirm:
        return False, "Passwords do not match."

    return True, ""


# ==========================================================
# Search Validation
# ==========================================================

def validate_search(text: str):

    if len(text.strip()) < 2:
        return False, "Please enter at least 2 characters."

    return True, ""


# ==========================================================
# Required Field
# ==========================================================

def validate_required(value, field_name="Field"):

    if value is None:
        return False, f"{field_name} is required."

    if isinstance(value, str):

        if value.strip() == "":
            return False, f"{field_name} is required."

    return True, ""


# ==========================================================
# Numeric Validation
# ==========================================================

def validate_positive_number(value, field_name="Value"):

    if value < 0:
        return False, f"{field_name} must be positive."

    return True, ""


# ==========================================================
# Generic Form Validator
# ==========================================================

def validate_prediction_form(patient, features):
    """
    Validate complete prediction form.
    """

    valid, msg = validate_patient_name(
        patient["patient_name"]
    )

    if not valid:
        return valid, msg

    valid, msg = validate_age(
        patient["age"]
    )

    if not valid:
        return valid, msg

    valid, msg = validate_gender(
        patient["gender"]
    )

    if not valid:
        return valid, msg

    valid, msg = validate_voice_features(
        features
    )

    return valid, msg
