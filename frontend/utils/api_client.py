import requests


# ==========================================================
# API Configuration
# ==========================================================

API_BASE_URL = (
    "https://parkinson-disease-detection-wced.onrender.com"
)

DEFAULT_TIMEOUT = 60


# ==========================================================
# Session State
# ==========================================================

def _get_session_state():
    """Safely get Streamlit session state."""

    try:
        import streamlit as st
        return st.session_state
    except Exception:
        return None


def _get_token():
    """Get JWT token from Streamlit session."""

    session = _get_session_state()

    if session is None:
        return None

    return (
        session.get("token")
        or session.get("access_token")
    )


# ==========================================================
# URL
# ==========================================================

def _url(endpoint: str) -> str:

    if not endpoint.startswith("/"):
        endpoint = "/" + endpoint

    return (
        API_BASE_URL.rstrip("/")
        + endpoint
    )


# ==========================================================
# Headers
# ==========================================================

def _headers():

    headers = {
        "Accept": "application/json",
    }

    token = _get_token()

    if token:

        headers[
            "Authorization"
        ] = f"Bearer {token}"

    return headers


# ==========================================================
# GET
# ==========================================================

def get(
    endpoint: str,
    params=None,
    timeout: int = DEFAULT_TIMEOUT,
):
    """Generic GET request."""

    try:

        response = requests.get(
            _url(endpoint),
            params=params,
            headers=_headers(),
            timeout=timeout,
        )

        response.raise_for_status()

        content_type = (
            response.headers
            .get(
                "content-type",
                "",
            )
            .lower()
        )

        if "application/json" in content_type:

            return response.json()

        return response.content

    except requests.HTTPError as e:

        print(
            f"GET {endpoint} HTTP error: {e}"
        )

        return None

    except requests.RequestException as e:

        print(
            f"GET {endpoint} failed: {e}"
        )

        return None


# ==========================================================
# POST
# ==========================================================

def post(
    endpoint: str,
    data=None,
    timeout: int = DEFAULT_TIMEOUT,
):
    """Generic JSON POST request."""

    try:

        response = requests.post(
            _url(endpoint),
            json=data,
            headers=_headers(),
            timeout=timeout,
        )

        response.raise_for_status()

        if not response.content:
            return True

        content_type = (
            response.headers
            .get(
                "content-type",
                "",
            )
            .lower()
        )

        if "application/json" in content_type:

            return response.json()

        return response.content

    except requests.HTTPError as e:

        print(
            f"POST {endpoint} HTTP error: {e}"
        )

        return None

    except requests.RequestException as e:

        print(
            f"POST {endpoint} failed: {e}"
        )

        return None


# ==========================================================
# PUT
# ==========================================================

def put(
    endpoint: str,
    data=None,
    timeout: int = DEFAULT_TIMEOUT,
):
    """Generic PUT request."""

    try:

        response = requests.put(
            _url(endpoint),
            json=data,
            headers=_headers(),
            timeout=timeout,
        )

        response.raise_for_status()

        if not response.content:
            return True

        content_type = (
            response.headers
            .get(
                "content-type",
                "",
            )
            .lower()
        )

        if "application/json" in content_type:

            return response.json()

        return response.content

    except requests.RequestException as e:

        print(
            f"PUT {endpoint} failed: {e}"
        )

        return None


# ==========================================================
# DELETE
# ==========================================================

def delete(
    endpoint: str,
    timeout: int = DEFAULT_TIMEOUT,
):
    """Generic DELETE request."""

    try:

        response = requests.delete(
            _url(endpoint),
            headers=_headers(),
            timeout=timeout,
        )

        response.raise_for_status()

        if not response.content:
            return True

        content_type = (
            response.headers
            .get(
                "content-type",
                "",
            )
            .lower()
        )

        if "application/json" in content_type:

            return response.json()

        return True

    except requests.RequestException as e:

        print(
            f"DELETE {endpoint} failed: {e}"
        )

        return None


# ==========================================================
# Compatibility HTTP Functions
# ==========================================================

def _get(
    endpoint: str,
    params=None,
    timeout: int = DEFAULT_TIMEOUT,
):

    return get(
        endpoint,
        params=params,
        timeout=timeout,
    )


def _post(
    endpoint: str,
    data=None,
    timeout: int = DEFAULT_TIMEOUT,
):

    return post(
        endpoint,
        data=data,
        timeout=timeout,
    )


def _put(
    endpoint: str,
    data=None,
    timeout: int = DEFAULT_TIMEOUT,
):

    return put(
        endpoint,
        data=data,
        timeout=timeout,
    )


def _delete(
    endpoint: str,
    timeout: int = DEFAULT_TIMEOUT,
):

    return delete(
        endpoint,
        timeout=timeout,
    )


# ==========================================================
# Authentication
# ==========================================================

def login_user(
    username: str,
    password: str,
):
    """
    Login through FastAPI.

    Backend expects JSON:
    {
        "username": "...",
        "password": "..."
    }
    """

    try:

        response = requests.post(
            _url("/auth/login"),

            json={
                "username": username,
                "password": password,
            },

            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },

            timeout=30,
        )

        response.raise_for_status()

        result = response.json()

        if not isinstance(
            result,
            dict,
        ):

            return None


        # ==================================================
        # Save authentication
        # ==================================================

        session = _get_session_state()

        token = result.get(
            "access_token"
        )

        user = result.get(
            "user",
            {},
        )


        if session is not None:

            if token:

                session[
                    "token"
                ] = token

                session[
                    "access_token"
                ] = token


            session[
                "logged_in"
            ] = True


            if isinstance(
                user,
                dict,
            ):

                session[
                    "user_id"
                ] = user.get(
                    "id"
                )

                session[
                    "username"
                ] = user.get(
                    "username",
                    username,
                )

                session[
                    "email"
                ] = user.get(
                    "email",
                    "",
                )

                session[
                    "full_name"
                ] = user.get(
                    "full_name",
                    "",
                )

                session[
                    "role"
                ] = str(
                    user.get(
                        "role",
                        "user",
                    )
                ).lower()


        return result


    except requests.HTTPError as e:

        try:
            detail = response.json()
        except Exception:
            detail = response.text

        print(
            f"Login HTTP error: "
            f"{e} | {detail}"
        )

        return None


    except requests.RequestException as e:

        print(
            f"Login connection error: {e}"
        )

        return None


    except Exception as e:

        print(
            f"Login error: {e}"
        )

        return None


def login(
    username: str,
    password: str,
):

    return login_user(
        username,
        password,
    )


def get_current_user():
    """
    Get current authenticated user.

    Backend expects user_id.
    """

    session = _get_session_state()

    if session is None:
        return None

    user_id = session.get(
        "user_id"
    )

    if not user_id:
        return None

    return get(
        "/auth/me",
        params={
            "user_id": user_id
        },
    )


def logout_user():

    session = _get_session_state()

    if session is None:
        return True

    keys = [
        "token",
        "access_token",
        "logged_in",
        "username",
        "email",
        "full_name",
        "role",
        "user",
        "user_id",
    ]

    for key in keys:

        session.pop(
            key,
            None,
        )

    return True


# ==========================================================
# Prediction
# ==========================================================

def predict_patient(
    patient_name,
    age,
    gender,
    features,
):
    """
    Run Parkinson prediction.
    """

    if features is None:

        print(
            "Prediction failed: "
            "features are missing."
        )

        return None


    try:

        features = [
            float(value)
            for value in features
        ]

    except (
        TypeError,
        ValueError,
    ):

        print(
            "Prediction failed: "
            "invalid feature values."
        )

        return None


    if len(features) != 22:

        print(
            "Prediction failed: "
            f"expected 22 features, "
            f"received {len(features)}."
        )

        return None


    payload = {
        "patient_name": str(
            patient_name
        ),

        "age": int(age),

        "gender": str(
            gender
        ),

        "features": features,
    }


    result = post(
        "/prediction/predict",
        data=payload,
        timeout=60,
    )


    if isinstance(
        result,
        dict,
    ):

        if (
            "diagnosis"
            not in result
            and "prediction"
            in result
        ):

            result[
                "diagnosis"
            ] = result[
                "prediction"
            ]


        if (
            "prediction"
            not in result
            and "diagnosis"
            in result
        ):

            result[
                "prediction"
            ] = result[
                "diagnosis"
            ]


    return result


def predict(
    data,
):

    return post(
        "/prediction/predict",
        data=data,
        timeout=60,
    )


# ==========================================================
# Prediction History
# ==========================================================

def get_patient_history():
    """
    Get prediction/patient history.
    """

    result = get(
        "/prediction/history"
    )


    if result is None:
        return None


    if isinstance(
        result,
        list,
    ):

        return result


    if isinstance(
        result,
        dict,
    ):

        return (
            result.get("history")
            or result.get("predictions")
            or result.get("patients")
            or result.get("records")
            or []
        )


    return []


def get_prediction_history():

    return get_patient_history()


def get_prediction(
    prediction_id: int,
):

    return get(
        f"/prediction/{prediction_id}"
    )


def delete_prediction(
    prediction_id: int,
):

    return delete(
        f"/prediction/{prediction_id}"
    )


# ==========================================================
# Patients
# ==========================================================

def get_patients():

    result = get(
        "/patients"
    )


    if result is None:
        return None


    if isinstance(
        result,
        list,
    ):

        return result


    if isinstance(
        result,
        dict,
    ):

        return (
            result.get("patients")
            or result.get("data")
            or []
        )


    return []


def get_patient(
    patient_id: int,
):

    return get(
        f"/patients/{patient_id}"
    )


def create_patient(
    data,
):

    return post(
        "/patients",
        data=data,
    )


def update_patient(
    patient_id: int,
    data,
):

    return put(
        f"/patients/{patient_id}",
        data=data,
    )


def delete_patient(
    patient_id: int,
):

    return delete(
        f"/patients/{patient_id}"
    )


# ==========================================================
# Reports
# ==========================================================

def get_reports():
    """
    Get all reports.
    """

    result = get(
        "/reports"
    )


    if result is None:
        return None


    if isinstance(
        result,
        list,
    ):

        return result


    if isinstance(
        result,
        dict,
    ):

        return result.get(
            "reports",
            [],
        )


    return []


def get_report(
    report_id: int,
):

    return get(
        f"/reports/{report_id}"
    )


def get_patient_reports(
    patient_id: int,
):

    result = get(
        f"/reports/patient/{patient_id}"
    )


    if result is None:
        return None


    if isinstance(
        result,
        list,
    ):

        return result


    if isinstance(
        result,
        dict,
    ):

        return result.get(
            "reports",
            [],
        )


    return []


def download_report(
    report_id: int,
):

    return get(
        f"/reports/{report_id}/download"
    )


def delete_report(
    report_id: int,
):

    return delete(
        f"/reports/{report_id}"
    )


# ==========================================================
# Analytics
# ==========================================================

def get_analytics():

    result = get(
        "/analytics"
    )


    if isinstance(
        result,
        dict,
    ):

        return result


    return {}


def get_analytics_summary():

    result = get(
        "/analytics/summary"
    )

    if result is None:

        return get_analytics()

    return result


# ==========================================================
# Recommendations
# ==========================================================

def get_recommendations():

    result = get(
        "/recommendations"
    )


    if result is None:
        return None


    if isinstance(
        result,
        list,
    ):

        return result


    if isinstance(
        result,
        dict,
    ):

        return (
            result.get(
                "recommendations"
            )
            or result.get(
                "data"
            )
            or []
        )


    return []


def get_patient_recommendations(
    patient_id: int,
):

    result = get(
        f"/recommendations/patient/{patient_id}"
    )


    if isinstance(
        result,
        dict,
    ):

        return (
            result.get(
                "recommendations"
            )
            or result
        )


    return result


# ==========================================================
# Medication
# ==========================================================

def get_medications():

    result = get(
        "/medication"
    )


    if isinstance(
        result,
        dict,
    ):

        return (
            result.get(
                "medications"
            )
            or result.get(
                "data"
            )
            or result
        )


    return result


def get_patient_medications(
    patient_id: int,
):

    result = get(
        f"/medication/patient/{patient_id}"
    )


    if isinstance(
        result,
        dict,
    ):

        return (
            result.get(
                "medications"
            )
            or result.get(
                "data"
            )
            or result
        )


    return result


# ==========================================================
# AI Assistant
# ==========================================================

def ask_ai_assistant(
    question: str,
):

    result = post(
        "/chatbot/",
        data={
            "message": question
        },
        timeout=60,
    )


    if isinstance(
        result,
        dict,
    ):

        if "response" in result:
            return result["response"]

        if "message" in result:
            return result["message"]

        if "answer" in result:
            return result["answer"]


    return result


def ask_chatbot(
    question: str,
):

    return ask_ai_assistant(
        question
    )


# ==========================================================
# Admin
# ==========================================================

def get_admin_dashboard():

    return get(
        "/admin/dashboard"
    )


def get_users():

    result = get(
        "/admin/users"
    )


    if result is None:
        return None


    if isinstance(
        result,
        list,
    ):

        return result


    if isinstance(
        result,
        dict,
    ):

        return (
            result.get(
                "users"
            )
            or result.get(
                "data"
            )
            or []
        )


    return []


def get_admin_patients():

    result = get(
        "/admin/patients"
    )


    if result is None:
        return None


    if isinstance(
        result,
        list,
    ):

        return result


    if isinstance(
        result,
        dict,
    ):

        return (
            result.get(
                "patients"
            )
            or result.get(
                "data"
            )
            or []
        )


    return []


def delete_user(
    user_id: int,
):

    return delete(
        f"/admin/users/{user_id}"
    )


def delete_admin_patient(
    patient_id: int,
):

    return delete(
        f"/admin/patients/{patient_id}"
    )


# ==========================================================
# Settings
# ==========================================================

def get_user_settings():
    """
    Get current user settings.

    Theme and language are intentionally excluded.
    """

    session = _get_session_state()

    username = ""
    email = ""
    full_name = ""
    role = "user"


    if session is not None:

        username = session.get(
            "username",
            "",
        )

        email = session.get(
            "email",
            "",
        )

        full_name = session.get(
            "full_name",
            "",
        )

        role = session.get(
            "role",
            "user",
        )


    backend_user = get_current_user()


    if isinstance(
        backend_user,
        dict,
    ):

        username = backend_user.get(
            "username",
            username,
        )

        email = backend_user.get(
            "email",
            email,
        )

        full_name = backend_user.get(
            "full_name",
            full_name,
        )

        role = backend_user.get(
            "role",
            role,
        )


    return {
        "username": username,
        "email": email,
        "full_name": full_name,
        "role": role,
        "api_url": API_BASE_URL,
    }


def update_user_settings(
    data,
):

    if not isinstance(
        data,
        dict,
    ):

        return False


    session = _get_session_state()


    if session is None:
        return False


    if "username" in data:

        session[
            "username"
        ] = data[
            "username"
        ]


    if "email" in data:

        session[
            "email"
        ] = data[
            "email"
        ]


    if "full_name" in data:

        session[
            "full_name"
        ] = data[
            "full_name"
        ]


    return True


# ==========================================================
# Change Password
# ==========================================================

def change_password(
    current_password: str,
    new_password: str,
):
    """
    Change password.
    """

    if not current_password:
        return False


    if not new_password:
        return False


    if len(
        new_password.encode(
            "utf-8"
        )
    ) > 72:

        return False


    session = _get_session_state()

    if session is None:
        return False


    user_id = session.get(
        "user_id"
    )


    payload = {
        "old_password":
            current_password,

        "new_password":
            new_password,

        "confirm_password":
            new_password,
    }


    # Try user-specific endpoint first
    if user_id:

        result = post(
            f"/auth/change-password/{user_id}",
            data=payload,
            timeout=30,
        )

        if result is not None:

            return True


    # Fallback to generic endpoint
    result = post(
        "/auth/change-password",
        data=payload,
        timeout=30,
    )


    return result is not None


# ==========================================================
# Model Information
# ==========================================================

def get_model_info():

    return get(
        "/prediction/model-info"
    )


# ==========================================================
# Health
# ==========================================================

def health_check():

    return get(
        "/health"
    )


def is_backend_available():

    result = health_check()

    if not isinstance(
        result,
        dict,
    ):

        return False


    return result.get(
        "status"
    ) in [
        "healthy",
        "success",
        "ok",
        "Online",
    ]


# ==========================================================
# API URL
# ==========================================================

def get_api_url():

    return API_BASE_URL
