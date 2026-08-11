import streamlit as st


# ==========================================================
# Default Session Values
# ==========================================================

DEFAULT_SESSION = {

    "logged_in": False,

    "username": "Guest",

    "user_id": None,

    "email": "",

    "role": "User",

    "theme": "Light",

    "language": "English",

    "token": None,

    "chat_history": [],

    "selected_patient": None,

    "prediction_result": None,
}


# ==========================================================
# Initialize Session
# ==========================================================

def initialize_session():

    for key, value in DEFAULT_SESSION.items():

        if key not in st.session_state:

            st.session_state[key] = value


# ==========================================================
# Generic Methods
# ==========================================================

def get(
    key,
    default=None,
):

    return st.session_state.get(
        key,
        default,
    )


def set(
    key,
    value,
):

    st.session_state[key] = value


def remove(key):

    if key in st.session_state:

        del st.session_state[key]


def clear():

    st.session_state.clear()


# ==========================================================
# Authentication
# ==========================================================

def login(
    user_id,
    username,
    email,
    role,
    token,
):

    st.session_state.logged_in = True

    st.session_state.user_id = user_id

    st.session_state.username = username

    st.session_state.email = email

    # Normalize role
    st.session_state.role = str(
        role
    ).strip()

    st.session_state.token = token


def logout():

    clear()

    initialize_session()


def is_logged_in():

    return bool(
        st.session_state.get(
            "logged_in",
            False,
        )
    )


def is_admin():

    role = str(
        st.session_state.get(
            "role",
            "",
        )
    ).strip().lower()

    return role == "admin"


# ==========================================================
# Chat
# ==========================================================

def get_chat():

    return st.session_state.chat_history


def add_chat(
    role,
    message,
):

    st.session_state.chat_history.append(
        {
            "role": role,
            "content": message,
        }
    )


def clear_chat():

    st.session_state.chat_history = []


# ==========================================================
# Prediction
# ==========================================================

def save_prediction(result):

    st.session_state.prediction_result = result


def get_prediction():

    return st.session_state.prediction_result


# ==========================================================
# Patient
# ==========================================================

def select_patient(patient):

    st.session_state.selected_patient = patient


def get_selected_patient():

    return st.session_state.selected_patient


# ==========================================================
# Theme
# ==========================================================

def get_theme():

    return st.session_state.theme


def set_theme(theme):

    st.session_state.theme = theme


# ==========================================================
# Language
# ==========================================================

def get_language():

    return st.session_state.language


def set_language(language):

    st.session_state.language = language
