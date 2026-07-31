from datetime import datetime
from typing import Any, List
import pandas as pd


# ==========================================================
# Date & Time
# ==========================================================

def format_date(date_string: str) -> str:
    """
    Convert ISO datetime to readable format.
    """

    try:
        date = datetime.fromisoformat(date_string)

        return date.strftime("%d %b %Y")

    except Exception:
        return date_string


def format_datetime(date_string: str) -> str:
    """
    Convert ISO datetime to readable date & time.
    """

    try:
        date = datetime.fromisoformat(date_string)

        return date.strftime("%d %b %Y %I:%M %p")

    except Exception:
        return date_string


# ==========================================================
# Risk Level
# ==========================================================

def get_risk_level(score: float) -> str:
    """
    Calculate risk level from score.
    """

    if score < 30:
        return "Low Risk"

    elif score < 70:
        return "Medium Risk"

    return "High Risk"


# ==========================================================
# Percentage
# ==========================================================

def percentage(value: float, total: float) -> float:

    if total == 0:
        return 0

    return round((value / total) * 100, 2)


# ==========================================================
# DataFrame
# ==========================================================

def to_dataframe(data: List[dict]) -> pd.DataFrame:
    """
    Convert list to DataFrame.
    """

    if data is None:
        return pd.DataFrame()

    return pd.DataFrame(data)


# ==========================================================
# CSV
# ==========================================================

def dataframe_to_csv(df: pd.DataFrame):

    return df.to_csv(index=False).encode("utf-8")


# ==========================================================
# API
# ==========================================================

def api_success(response: Any) -> bool:

    return response is not None


# ==========================================================
# Empty Check
# ==========================================================

def is_empty(value):

    if value is None:
        return True

    if isinstance(value, str):

        return value.strip() == ""

    if isinstance(value, list):

        return len(value) == 0

    return False


# ==========================================================
# Greeting
# ==========================================================

def greeting():

    hour = datetime.now().hour

    if hour < 12:
        return "Good Morning"

    elif hour < 17:
        return "Good Afternoon"

    return "Good Evening"


# ==========================================================
# File Size
# ==========================================================

def format_size(size):

    if size < 1024:
        return f"{size} B"

    elif size < 1024 ** 2:
        return f"{size / 1024:.2f} KB"

    elif size < 1024 ** 3:
        return f"{size / (1024 ** 2):.2f} MB"

    return f"{size / (1024 ** 3):.2f} GB"


# ==========================================================
# Status Badge
# ==========================================================

def status_badge(status: bool):

    return "🟢 Online" if status else "🔴 Offline"


# ==========================================================
# Patient Initials
# ==========================================================

def initials(name: str):

    if not name:
        return ""

    parts = name.split()

    if len(parts) == 1:
        return parts[0][0].upper()

    return (parts[0][0] + parts[-1][0]).upper()


# ==========================================================
# Truncate Text
# ==========================================================

def truncate(text, length=60):

    if len(text) <= length:
        return text

    return text[:length] + "..."
