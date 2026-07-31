"""
Helper Utilities

Reusable helper functions for the
Parkinson Disease Detection System.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


# ==========================================================
# Date & Time
# ==========================================================

def current_timestamp() -> datetime:
    """
    Return current UTC timestamp.
    """
    return datetime.utcnow()


def current_date() -> str:
    """
    Return current date.
    """
    return datetime.utcnow().strftime("%Y-%m-%d")


def format_datetime(
    value: datetime,
    fmt: str = "%Y-%m-%d %H:%M:%S",
) -> str:
    """
    Format datetime.
    """
    return value.strftime(fmt)


# ==========================================================
# UUID
# ==========================================================

def generate_uuid() -> str:
    """
    Generate unique identifier.
    """
    return str(uuid.uuid4())


# ==========================================================
# JSON
# ==========================================================

def to_json(data: Any) -> str:
    """
    Convert object to JSON string.
    """
    return json.dumps(
        data,
        default=str,
        indent=4,
    )


def from_json(data: str):
    """
    Parse JSON string.
    """
    return json.loads(data)


# ==========================================================
# Response Helpers
# ==========================================================

def success_response(
    message: str,
    data: Any = None,
) -> Dict:

    return {
        "success": True,
        "message": message,
        "data": data,
        "timestamp": current_timestamp(),
    }


def error_response(
    message: str,
    errors: Any = None,
) -> Dict:

    return {
        "success": False,
        "message": message,
        "errors": errors,
        "timestamp": current_timestamp(),
    }


# ==========================================================
# Pagination
# ==========================================================

def paginate(
    items: List[Any],
    page: int = 1,
    page_size: int = 10,
) -> Dict:

    total = len(items)

    start = (page - 1) * page_size

    end = start + page_size

    return {

        "page": page,

        "page_size": page_size,

        "total": total,

        "items": items[start:end],
    }


# ==========================================================
# File Helpers
# ==========================================================

def file_exists(path: str) -> bool:
    """
    Check if file exists.
    """
    return Path(path).exists()


def create_directory(path: str):
    """
    Create directory.
    """
    Path(path).mkdir(
        parents=True,
        exist_ok=True,
    )


def get_extension(filename: str) -> str:
    """
    Return file extension.
    """
    return Path(filename).suffix.lower()


def filename_without_extension(
    filename: str,
) -> str:
    """
    Return filename without extension.
    """
    return Path(filename).stem


# ==========================================================
# Report Helpers
# ==========================================================

def report_filename(
    patient_id: int,
) -> str:
    """
    Generate report filename.
    """

    return (
        f"report_{patient_id}_"
        f"{datetime.utcnow():%Y%m%d_%H%M%S}.pdf"
    )


# ==========================================================
# Validation
# ==========================================================

def is_empty(value) -> bool:
    """
    Check empty values.
    """

    return value in (
        None,
        "",
        [],
        {},
    )


def safe_float(value):

    try:
        return float(value)

    except (ValueError, TypeError):
        return None


def safe_int(value):

    try:
        return int(value)

    except (ValueError, TypeError):
        return None


# ==========================================================
# List Helpers
# ==========================================================

def remove_duplicates(items: List):

    return list(dict.fromkeys(items))


def flatten(items: List[List]):

    return [

        value

        for sublist in items

        for value in sublist

    ]


# ==========================================================
# Dictionary Helpers
# ==========================================================

def remove_none(data: Dict):

    return {

        k: v

        for k, v in data.items()

        if v is not None

    }


# ==========================================================
# Feature Helpers
# ==========================================================

def validate_feature_count(
    features: List,
    expected: int,
) -> bool:

    return len(features) == expected


# ==========================================================
# Health Check
# ==========================================================

def helper_status():

    return {

        "status": "Online",

        "module": "Helper Utilities",

        "version": "1.0.0",
    }
