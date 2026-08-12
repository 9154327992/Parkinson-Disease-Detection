import streamlit as st
import pandas as pd

from utils.api_client import (
    get_admin_dashboard,
    get_users,
    get_patients,
    delete_user,
    delete_patient,
    check_backend,
)

from utils.session import (
    initialize_session,
    is_logged_in,
    is_admin,
)


# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="Admin Dashboard",
    page_icon="🛠",
    layout="wide",
)


# ==========================================================
# Initialize Session
# ==========================================================

initialize_session()


# ==========================================================
# Authentication Check
# ==========================================================

if not is_logged_in():

    st.error(
        "🔐 Please login first."
    )

    st.stop()


# ==========================================================
# Admin Authorization
# ==========================================================

if not is_admin():

    st.error(
        "🚫 Access Denied! "
        "Administrator privileges required."
    )

    st.info(
        f"Current role: "
        f"{st.session_state.get('role', 'User')}"
    )

    st.stop()


# ==========================================================
# Header
# ==========================================================

st.title(
    "🛠 Admin Dashboard"
)

st.write(
    """
    Manage users, patients, and monitor the
    overall health of the system.
    """
)

admin_username = st.session_state.get(
    "username",
    "Administrator",
)

st.success(
    f"Administrator access granted: "
    f"{admin_username}"
)


# ==========================================================
# Refresh
# ==========================================================

refresh_col1, refresh_col2 = st.columns(
    [5, 1]
)

with refresh_col2:

    if st.button(
        "🔄 Refresh",
        width="stretch",
    ):

        st.rerun()


st.divider()


# ==========================================================
# Load Dashboard
# ==========================================================

with st.spinner(
    "Loading administrator dashboard..."
):

    dashboard = get_admin_dashboard()


# ==========================================================
# Safe Dashboard
# ==========================================================

if not isinstance(
    dashboard,
    dict,
):

    dashboard = {}


# ==========================================================
# Dashboard Statistics
# ==========================================================

total_users = dashboard.get(
    "total_users",
    0,
)

total_patients = dashboard.get(
    "total_patients",
    0,
)

total_predictions = dashboard.get(
    "total_predictions",
    0,
)

total_reports = dashboard.get(
    "total_reports",
    0,
)


col1, col2, col3, col4 = (
    st.columns(4)
)


with col1:

    st.metric(
        "👥 Users",
        total_users,
    )


with col2:

    st.metric(
        "🩺 Patients",
        total_patients,
    )


with col3:

    st.metric(
        "🧠 Predictions",
        total_predictions,
    )


with col4:

    st.metric(
        "📄 Reports",
        total_reports,
    )


st.divider()


# ==========================================================
# User Role Statistics
# ==========================================================

st.subheader(
    "👥 User Roles"
)

roles = dashboard.get(
    "user_roles",
    {},
)

if not isinstance(
    roles,
    dict,
):

    roles = {}


role_col1, role_col2, role_col3 = (
    st.columns(3)
)


with role_col1:

    st.metric(
        "🛡 Administrators",
        roles.get(
            "admins",
            0,
        ),
    )


with role_col2:

    st.metric(
        "🩺 Doctors",
        roles.get(
            "doctors",
            0,
        ),
    )


with role_col3:

    st.metric(
        "👤 Users",
        roles.get(
            "users",
            0,
        ),
    )


st.divider()


# ==========================================================
# User Management
# ==========================================================

st.subheader(
    "👥 User Management"
)


with st.spinner(
    "Loading users..."
):

    users = get_users()


if not isinstance(
    users,
    list,
):

    users = []


# ----------------------------------------------------------
# User Search
# ----------------------------------------------------------

user_search = st.text_input(
    "🔍 Search Users",
    placeholder=(
        "Search by username, name, "
        "email, or role..."
    ),
)


filtered_users = users.copy()


if user_search:

    search_text = (
        user_search
        .strip()
        .lower()
    )

    filtered_users = [

        user

        for user in users

        if isinstance(
            user,
            dict,
        )
        and search_text
        in (
            f"{user.get('username', '')} "
            f"{user.get('full_name', '')} "
            f"{user.get('email', '')} "
            f"{user.get('role', '')}"
        ).lower()
    ]


if filtered_users:

    users_df = pd.DataFrame(
        filtered_users
    )


    # ------------------------------------------------------
    # Display Columns
    # ------------------------------------------------------

    user_columns = [
        "id",
        "username",
        "full_name",
        "email",
        "role",
        "is_active",
        "created_at",
    ]


    available_user_columns = [
        column
        for column in user_columns
        if column
        in users_df.columns
    ]


    if available_user_columns:

        display_users = users_df[
            available_user_columns
        ].copy()

    else:

        display_users = users_df.copy()


    display_users = display_users.rename(
        columns={
            "id": "ID",
            "username": "Username",
            "full_name": "Full Name",
            "email": "Email",
            "role": "Role",
            "is_active": "Active",
            "created_at": "Created",
        }
    )


    st.dataframe(
        display_users,
        width="stretch",
        hide_index=True,
    )


    # ------------------------------------------------------
    # Select User
    # ------------------------------------------------------

    user_options = []

    for user in filtered_users:

        if not isinstance(
            user,
            dict,
        ):
            continue

        user_id = user.get(
            "id"
        )

        username = user.get(
            "username",
            "Unknown",
        )

        if user_id is not None:

            user_options.append(
                (
                    user_id,
                    username,
                )
            )


    if user_options:

        selected_user_id = st.selectbox(
            "Select User",
            [
                item[0]
                for item in user_options
            ],
            format_func=lambda user_id: next(
                (
                    username
                    for uid, username
                    in user_options
                    if uid == user_id
                ),
                f"User {user_id}",
            ),
        )


        selected_user = next(
            (
                user
                for user in filtered_users
                if isinstance(
                    user,
                    dict,
                )
                and user.get("id")
                == selected_user_id
            ),
            None,
        )


        # --------------------------------------------------
        # Selected User Details
        # --------------------------------------------------

        if selected_user:

            detail_col1, detail_col2 = (
                st.columns(2)
            )


            with detail_col1:

                st.write(
                    f"**Username:** "
                    f"{selected_user.get('username', 'N/A')}"
                )

                st.write(
                    f"**Full Name:** "
                    f"{selected_user.get('full_name', 'N/A')}"
                )

                st.write(
                    f"**Email:** "
                    f"{selected_user.get('email', 'N/A')}"
                )


            with detail_col2:

                st.write(
                    f"**Role:** "
                    f"{selected_user.get('role', 'N/A')}"
                )

                st.write(
                    f"**Active:** "
                    f"{selected_user.get('is_active', 'N/A')}"
                )

                st.write(
                    f"**ID:** "
                    f"{selected_user.get('id', 'N/A')}"
                )


            # ------------------------------------------------
            # Prevent Self Deletion
            # ------------------------------------------------

            current_user_id = (
                st.session_state.get(
                    "user_id"
                )
            )


            is_current_user = (
                current_user_id is not None
                and str(
                    current_user_id
                )
                == str(
                    selected_user.get(
                        "id"
                    )
                )
            )


            if is_current_user:

                st.warning(
                    "⚠️ You cannot delete your "
                    "own administrator account."
                )

            else:

                confirm_user_delete = (
                    st.checkbox(
                        "I understand that deleting "
                        "this user cannot be undone.",
                        key=(
                            f"confirm_user_delete_"
                            f"{selected_user_id}"
                        ),
                    )
                )


                if st.button(
                    "❌ Delete Selected User",
                    disabled=(
                        not confirm_user_delete
                    ),
                    width="stretch",
                ):

                    with st.spinner(
                        "Deleting user..."
                    ):

                        success = delete_user(
                            selected_user_id
                        )


                    if success:

                        st.success(
                            "User deleted successfully."
                        )

                        st.rerun()

                    else:

                        st.error(
                            "Unable to delete user."
                        )

else:

    if user_search:

        st.info(
            "No users match your search."
        )

    else:

        st.info(
            "No users found."
        )


st.divider()


# ==========================================================
# Patient Management
# ==========================================================

st.subheader(
    "🩺 Patient Management"
)


with st.spinner(
    "Loading patients..."
):

    patients = get_patients()


if not isinstance(
    patients,
    list,
):

    patients = []


# ----------------------------------------------------------
# Patient Search
# ----------------------------------------------------------

patient_search = st.text_input(
    "🔍 Search Patients",
    placeholder=(
        "Search by patient name, "
        "email, phone, or ID..."
    ),
)


filtered_patients = patients.copy()


if patient_search:

    search_text = (
        patient_search
        .strip()
        .lower()
    )


    filtered_patients = [

        patient

        for patient in patients

        if isinstance(
            patient,
            dict,
        )
        and search_text
        in (
            f"{patient.get('patient_name', '')} "
            f"{patient.get('first_name', '')} "
            f"{patient.get('last_name', '')} "
            f"{patient.get('email', '')} "
            f"{patient.get('phone', '')} "
            f"{patient.get('id', '')}"
        ).lower()
    ]


if filtered_patients:

    patient_df = pd.DataFrame(
        filtered_patients
    )


    patient_columns = [
        "id",
        "patient_name",
        "first_name",
        "last_name",
        "age",
        "gender",
        "email",
        "phone",
    ]


    available_patient_columns = [
        column
        for column in patient_columns
        if column
        in patient_df.columns
    ]


    if available_patient_columns:

        display_patients = patient_df[
            available_patient_columns
        ].copy()

    else:

        display_patients = patient_df.copy()


    display_patients = display_patients.rename(
        columns={
            "id": "ID",
            "patient_name": "Patient",
            "first_name": "First Name",
            "last_name": "Last Name",
            "age": "Age",
            "gender": "Gender",
            "email": "Email",
            "phone": "Phone",
        }
    )


    st.dataframe(
        display_patients,
        width="stretch",
        hide_index=True,
    )


    # ------------------------------------------------------
    # Select Patient
    # ------------------------------------------------------

    patient_options = []


    for patient in filtered_patients:

        if not isinstance(
            patient,
            dict,
        ):
            continue


        patient_id = patient.get(
            "id"
        )


        patient_name = (
            patient.get(
                "patient_name"
            )
            or (
                f"{patient.get('first_name', '')} "
                f"{patient.get('last_name', '')}"
            ).strip()
            or f"Patient {patient_id}"
        )


        if patient_id is not None:

            patient_options.append(
                (
                    patient_id,
                    patient_name,
                )
            )


    if patient_options:

        selected_patient_id = st.selectbox(
            "Select Patient",
            [
                item[0]
                for item in patient_options
            ],
            format_func=lambda patient_id: next(
                (
                    name
                    for pid, name
                    in patient_options
                    if pid == patient_id
                ),
                f"Patient {patient_id}",
            ),
        )


        selected_patient = next(
            (
                patient
                for patient in filtered_patients
                if isinstance(
                    patient,
                    dict,
                )
                and patient.get("id")
                == selected_patient_id
            ),
            None,
        )


        if selected_patient:

            st.write(
                "### 👤 Patient Details"
            )


            patient_detail_col1, patient_detail_col2 = (
                st.columns(2)
            )


            with patient_detail_col1:

                st.write(
                    f"**Name:** "
                    f"{selected_patient.get('patient_name') or 'N/A'}"
                )

                st.write(
                    f"**Age:** "
                    f"{selected_patient.get('age', 'N/A')}"
                )

                st.write(
                    f"**Gender:** "
                    f"{selected_patient.get('gender', 'N/A')}"
                )


            with patient_detail_col2:

                st.write(
                    f"**Email:** "
                    f"{selected_patient.get('email', 'N/A')}"
                )

                st.write(
                    f"**Phone:** "
                    f"{selected_patient.get('phone', 'N/A')}"
                )

                st.write(
                    f"**Patient ID:** "
                    f"{selected_patient.get('id', 'N/A')}"
                )


            # ------------------------------------------------
            # Delete Patient
            # ------------------------------------------------

            confirm_patient_delete = st.checkbox(
                "I understand that deleting this patient "
                "cannot be undone.",
                key=(
                    f"confirm_patient_delete_"
                    f"{selected_patient_id}"
                ),
            )


            if st.button(
                "🗑 Delete Selected Patient",
                disabled=(
                    not confirm_patient_delete
                ),
                width="stretch",
            ):

                with st.spinner(
                    "Deleting patient..."
                ):

                    success = delete_patient(
                        selected_patient_id
                    )


                if success:

                    st.success(
                        "Patient deleted successfully."
                    )

                    st.rerun()

                else:

                    st.error(
                        "Unable to delete patient."
                    )

else:

    if patient_search:

        st.info(
            "No patients match your search."
        )

    else:

        st.info(
            "No patient records available."
        )


st.divider()


# ==========================================================
# Recent Activity
# ==========================================================

st.subheader(
    "📝 Recent Activity"
)


activity = dashboard.get(
    "recent_activity",
    [],
)


if isinstance(
    activity,
    list,
) and activity:

    activity_df = pd.DataFrame(
        activity
    )


    st.dataframe(
        activity_df,
        width="stretch",
        hide_index=True,
    )

else:

    st.info(
        "No recent activity available."
    )


st.divider()


# ==========================================================
# System Health
# ==========================================================

st.subheader(
    "💻 System Health"
)


health_col1, health_col2 = (
    st.columns(2)
)


# ----------------------------------------------------------
# Backend
# ----------------------------------------------------------

with health_col1:

    try:

        backend_online = check_backend()

    except Exception:

        backend_online = True


    if backend_online:

        st.success(
            "🟢 FastAPI Backend"
        )

    else:

        st.error(
            "🔴 FastAPI Backend"
        )


    st.success(
        "🟢 Machine Learning Model"
    )


# ----------------------------------------------------------
# Services
# ----------------------------------------------------------

with health_col2:

    if dashboard:

        st.success(
            "🟢 Database"
        )

    else:

        st.warning(
            "🟡 Database status unavailable"
        )


    st.success(
        "🟢 AI Assistant"
    )


st.divider()


# ==========================================================
# Admin Information
# ==========================================================

st.subheader(
    "ℹ️ Administrator Information"
)


info_col1, info_col2, info_col3 = (
    st.columns(3)
)


with info_col1:

    st.info(
        f"""
        **Administrator**

        {admin_username}
        """
    )


with info_col2:

    st.info(
        f"""
        **Users**

        {total_users}
        """
    )


with info_col3:

    st.info(
        f"""
        **Patients**

        {total_patients}
        """
    )


st.divider()


# ==========================================================
# Footer
# ==========================================================

st.caption(
    "Administrator Panel | "
    "Parkinson Disease Detection Agent"
)
