import streamlit as st


# ==========================================================
# Patient Information Form
# ==========================================================

def patient_form():
    """
    Display the patient information form.

    Returns
    -------
    dict
        Patient details
    """

    st.subheader("👤 Patient Information")

    col1, col2, col3 = st.columns(3)

    with col1:
        patient_name = st.text_input("Patient Name")

    with col2:
        age = st.number_input(
            "Age",
            min_value=1,
            max_value=120,
            value=30
        )

    with col3:
        gender = st.selectbox(
            "Gender",
            [
                "Male",
                "Female",
                "Other"
            ]
        )

    return {
        "patient_name": patient_name,
        "age": age,
        "gender": gender
    }


# ==========================================================
# Login Form
# ==========================================================

def login_form():
    """
    Display login form.
    """

    st.subheader("🔐 Login")

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    login = st.form_submit_button("Login")

    return login, username, password


# ==========================================================
# Register Form
# ==========================================================

def register_form():
    """
    Display registration form.
    """

    st.subheader("📝 Register")

    username = st.text_input("Username")

    email = st.text_input("Email")

    password = st.text_input(
        "Password",
        type="password"
    )

    confirm_password = st.text_input(
        "Confirm Password",
        type="password"
    )

    register = st.form_submit_button("Register")

    return (
        register,
        username,
        email,
        password,
        confirm_password
    )


# ==========================================================
# Change Password Form
# ==========================================================

def password_form():
    """
    Display password change form.
    """

    st.subheader("🔒 Change Password")

    current_password = st.text_input(
        "Current Password",
        type="password"
    )

    new_password = st.text_input(
        "New Password",
        type="password"
    )

    confirm_password = st.text_input(
        "Confirm Password",
        type="password"
    )

    submit = st.form_submit_button(
        "Update Password"
    )

    return (
        submit,
        current_password,
        new_password,
        confirm_password
    )


# ==========================================================
# Search Box
# ==========================================================

def search_box(label="Search"):
    """
    Display search input.
    """

    return st.text_input(label)


# ==========================================================
# Confirmation Dialog
# ==========================================================

def confirmation_box(message):
    """
    Display confirmation checkbox.
    """

    st.warning(message)

    return st.checkbox("I confirm this action.")


# ==========================================================
# Save / Cancel Buttons
# ==========================================================

def action_buttons():

    col1, col2 = st.columns(2)

    with col1:
        save = st.button(
            "💾 Save",
            use_container_width=True
        )

    with col2:
        cancel = st.button(
            "❌ Cancel",
            use_container_width=True
        )

    return save, cancel
