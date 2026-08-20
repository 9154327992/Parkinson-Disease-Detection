import streamlit as st
import pandas as pd

from utils.api_client import (
    get_admin_dashboard,
    get_users,
    get_admin_patients,
    delete_user,
    delete_patient,
)

from utils.session import (
    initialize_session,
)


# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="Admin Dashboard",
    page_icon="🛠️",
    layout="wide",
)


# ==========================================================
# Session
# ==========================================================

initialize_session()


# ==========================================================
# Access
# ==========================================================

st.session_state["logged_in"] = True
st.session_state["role"] = "Administrator"


# ==========================================================
# Helper Functions
# ==========================================================

def safe_list(
    value,
    keys=None,
):
    """
    Normalize common API list responses.
    """

    if isinstance(
        value,
        list,
    ):

        return value


    if isinstance(
        value,
        dict,
    ):

        search_keys = (
            keys
            or [
                "data",
                "items",
                "records",
                "users",
                "patients",
            ]
        )


        for key in search_keys:

            result = value.get(
                key
            )

            if isinstance(
                result,
                list,
            ):

                return result


    return []


def get_value(
    record,
    keys,
    default=None,
):
    """
    Return the first available field.
    """

    if not isinstance(
        record,
        dict,
    ):

        return default


    for key in keys:

        value = record.get(
            key
        )

        if value is not None:

            return value


    return default


def patient_name(
    patient,
):
    """
    Safely build patient display name.
    """

    name = get_value(
        patient,
        [
            "patient_name",
            "name",
            "full_name",
        ],
        None,
    )


    if name:

        return str(
            name
        )


    first_name = get_value(
        patient,
        [
            "first_name",
            "firstName",
        ],
        "",
    )


    last_name = get_value(
        patient,
        [
            "last_name",
            "lastName",
        ],
        "",
    )


    result = (
        f"{first_name} "
        f"{last_name}"
    ).strip()


    return result or "Unknown"


# ==========================================================
# Header
# ==========================================================

st.title(
    "🛠️ Admin Dashboard"
)

st.write(
    """
Manage users and patients and monitor the overall
system status.
"""
)


st.success(
    "Administrator access granted: "
    f"{st.session_state.get('username', 'Administrator')}"
)


st.divider()


# ==========================================================
# Load Dashboard
# ==========================================================

with st.spinner(
    "Loading administrator dashboard..."
):

    dashboard = get_admin_dashboard()


# ==========================================================
# Validate Dashboard
# ==========================================================

if dashboard is None:

    st.error(
        "Unable to load the administrator dashboard."
    )

    st.warning(
        """
The backend rejected the administrator request
or the Admin API is unavailable.

Make sure you are logged in with an administrator
account and that the backend is available.
"""
    )

    st.stop()


if not isinstance(
    dashboard,
    dict,
):

    st.error(
        "Invalid dashboard response from backend."
    )

    st.stop()


# ==========================================================
# Dashboard Metrics
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


# ==========================================================
# System Overview
# ==========================================================

st.subheader(
    "📊 System Overview"
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
# User Roles
# ==========================================================

st.subheader(
    "👥 User Roles"
)


user_roles = dashboard.get(
    "user_roles",
    {},
)


if not isinstance(
    user_roles,
    dict,
):

    user_roles = {}


role1, role2, role3 = (
    st.columns(3)
)


with role1:

    st.metric(
        "🛡️ Administrators",
        user_roles.get(
            "admins",
            0,
        ),
    )


with role2:

    st.metric(
        "👨‍⚕️ Doctors",
        user_roles.get(
            "doctors",
            0,
        ),
    )


with role3:

    st.metric(
        "👤 Users",
        user_roles.get(
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

    users_response = get_users()


if users_response is None:

    st.error(
        "Unable to load users."
    )

    users = []

else:

    users = safe_list(
        users_response,
        [
            "users",
            "data",
            "records",
        ],
    )


# ==========================================================
# Users Table
# ==========================================================

if users:

    user_rows = []


    for user in users:

        user_rows.append(
            {
                "ID":
                    get_value(
                        user,
                        [
                            "id",
                            "user_id",
                        ],
                        "N/A",
                    ),

                "Username":
                    get_value(
                        user,
                        [
                            "username",
                        ],
                        "N/A",
                    ),

                "Full Name":
                    get_value(
                        user,
                        [
                            "full_name",
                            "name",
                        ],
                        "N/A",
                    ),

                "Role":
                    get_value(
                        user,
                        [
                            "role",
                            "user_role",
                        ],
                        "User",
                    ),

                "Active":
                    get_value(
                        user,
                        [
                            "is_active",
                            "active",
                        ],
                        True,
                    ),

                "Created":
                    get_value(
                        user,
                        [
                            "created_at",
                            "created",
                        ],
                        "N/A",
                    ),
            }
        )


    st.dataframe(
        pd.DataFrame(
            user_rows
        ),
        use_container_width=True,
        hide_index=True,
    )


else:

    st.info(
        "No users found."
    )


# ==========================================================
# Delete User
# ==========================================================

if users:

    st.write(
        "### 🗑️ Delete User"
    )


    selectable_users = []


    for user in users:

        user_id = get_value(
            user,
            [
                "id",
                "user_id",
            ],
            None,
        )


        username = get_value(
            user,
            [
                "username",
            ],
            f"User {user_id}",
        )


        if user_id is not None:

            selectable_users.append(
                (
                    str(username),
                    user_id,
                )
            )


    if selectable_users:

        labels = [
            item[0]
            for item in selectable_users
        ]


        selected_username = st.selectbox(
            "Select User",
            labels,
            key="admin_delete_user",
        )


        selected_user_id = next(
            user_id
            for username, user_id
            in selectable_users
            if username
            == selected_username
        )


        current_username = (
            st.session_state.get(
                "username"
            )
        )


        if (
            selected_username
            == current_username
        ):

            st.warning(
                "You cannot delete the currently logged-in administrator."
            )


        confirm = st.checkbox(
            "I understand this action cannot be undone.",
            key="confirm_delete_user",
        )


        if st.button(
            "❌ Delete Selected User",
            disabled=(
                not confirm
                or selected_username
                == current_username
            ),
            use_container_width=True,
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

    patients_response = (
        get_admin_patients()
    )


if patients_response is None:

    st.error(
        "Unable to load administrator patients."
    )

    patients = []

else:

    patients = safe_list(
        patients_response,
        [
            "patients",
            "data",
            "records",
        ],
    )


# ==========================================================
# Patient Table
# ==========================================================

if patients:

    patient_rows = []


    for patient in patients:

        patient_rows.append(
            {
                "ID":
                    get_value(
                        patient,
                        [
                            "id",
                            "patient_id",
                        ],
                        "N/A",
                    ),

                "Patient Name":
                    patient_name(
                        patient
                    ),

                "Age":
                    get_value(
                        patient,
                        [
                            "age",
                        ],
                        "N/A",
                    ),

                "Gender":
                    get_value(
                        patient,
                        [
                            "gender",
                        ],
                        "N/A",
                    ),
            }
        )


    st.dataframe(
        pd.DataFrame(
            patient_rows
        ),
        use_container_width=True,
        hide_index=True,
    )


else:

    st.info(
        "No patient records found."
    )


# ==========================================================
# Delete Patient
# ==========================================================

if patients:

    st.write(
        "### 🗑️ Delete Patient"
    )


    selectable_patients = []


    for patient in patients:

        patient_id = get_value(
            patient,
            [
                "id",
                "patient_id",
            ],
            None,
        )


        name = patient_name(
            patient
        )


        if patient_id is not None:

            selectable_patients.append(
                (
                    f"{name} "
                    f"(ID: {patient_id})",
                    patient_id,
                )
            )


    if selectable_patients:

        labels = [
            item[0]
            for item in selectable_patients
        ]


        selected_patient = st.selectbox(
            "Select Patient",
            labels,
            key="admin_delete_patient",
        )


        selected_patient_id = next(
            patient_id
            for label, patient_id
            in selectable_patients
            if label
            == selected_patient
        )


        confirm_patient = st.checkbox(
            "I understand this action cannot be undone.",
            key="confirm_delete_patient",
        )


        if st.button(
            "🗑️ Delete Selected Patient",
            disabled=not confirm_patient,
            use_container_width=True,
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


st.divider()


# ==========================================================
# Recent Users
# ==========================================================

st.subheader(
    "📝 Recent Users"
)


recent_users = dashboard.get(
    "recent_users",
    [],
)


if (
    isinstance(
        recent_users,
        list,
    )
    and recent_users
):

    recent_rows = []


    for user in recent_users:

        if not isinstance(
            user,
            dict,
        ):

            continue


        recent_rows.append(
            {
                "Username":
                    user.get(
                        "username",
                        "N/A",
                    ),

                "Full Name":
                    user.get(
                        "full_name",
                        "N/A",
                    ),

                "Role":
                    user.get(
                        "role",
                        "N/A",
                    ),

                "Created":
                    user.get(
                        "created_at",
                        "N/A",
                    ),
            }
        )


    if recent_rows:

        st.dataframe(
            pd.DataFrame(
                recent_rows
            ),
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "No recent users available."
        )

else:

    st.info(
        "No recent users available."
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


if (
    isinstance(
        activity,
        list,
    )
    and activity
):

    activity_rows = []


    for item in activity:

        if not isinstance(
            item,
            dict,
        ):

            continue


        activity_rows.append(
            {
                "Type":
                    item.get(
                        "type",
                        "Activity",
                    ),

                "Description":
                    item.get(
                        "description",
                        item.get(
                            "message",
                            "",
                        ),
                    ),

                "Created":
                    item.get(
                        "created_at",
                        item.get(
                            "timestamp",
                            "N/A",
                        ),
                    ),
            }
        )


    if activity_rows:

        st.dataframe(
            pd.DataFrame(
                activity_rows
            ),
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "No recent activity available."
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

from utils.api_client import check_backend


backend_ok = check_backend()


health1, health2 = st.columns(2)


with health1:

    if backend_ok:

        st.success(
            "🟢 FastAPI Backend: Connected"
        )

    else:

        st.error(
            "🔴 FastAPI Backend: Unavailable"
        )


with health2:

    if backend_ok:

        st.success(
            "🟢 Database: Connected"
        )

    else:

        st.error(
            "🔴 Database: Unavailable"
        )


health3, health4 = st.columns(2)


with health3:

    if backend_ok:

        st.success(
            "🟢 Machine Learning Model: Available"
        )

    else:

        st.error(
            "🔴 Machine Learning Model: Unavailable"
        )


with health4:

    if backend_ok:

        st.success(
            "🟢 AI Assistant: Available"
        )

    else:

        st.error(
            "🔴 AI Assistant: Unavailable"
        )


# ==========================================================
# Refresh
# ==========================================================

if st.button(
    "🔄 Refresh Dashboard",
    use_container_width=True,
):

    st.rerun()


# ==========================================================
# Footer
# ==========================================================

st.caption(
    "Administrator Panel | "
    "Parkinson Disease Detection Agent"
)
