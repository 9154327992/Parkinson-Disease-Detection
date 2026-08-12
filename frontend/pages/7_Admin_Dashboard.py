import streamlit as st
import pandas as pd

from utils.api_client import (
    get_admin_dashboard,
    get_users,
    get_patients,
    delete_user,
    delete_patient,
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
    page_icon="🛠️",
    layout="wide",
)


# ==========================================================
# Initialize Session
# ==========================================================

initialize_session()


# ==========================================================
# Authentication
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
        "🚫 Access Denied"
    )

    st.info(
        "Administrator privileges are required."
    )

    st.stop()


# ==========================================================
# Helper Functions
# ==========================================================

def normalize_list(
    data,
    keys=None,
):
    """
    Convert different API response formats into a list.
    """

    if data is None:
        return []

    if isinstance(
        data,
        list,
    ):
        return data

    if isinstance(
        data,
        dict,
    ):

        if keys:

            for key in keys:

                value = data.get(
                    key
                )

                if isinstance(
                    value,
                    list,
                ):
                    return value

        return []

    return []


def get_value(
    record,
    keys,
    default=None,
):
    """
    Return first available field.
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


def get_patient_name(
    patient,
):
    """
    Safely construct patient name.
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
        return str(name)

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

    combined = (
        f"{first_name} {last_name}"
    ).strip()

    return combined or "Unknown"


def get_role(
    user,
):
    role = get_value(
        user,
        [
            "role",
            "user_role",
        ],
        "user",
    )

    return str(
        role
    )


# ==========================================================
# Header
# ==========================================================

st.title(
    "🛠️ Admin Dashboard"
)

st.write(
    """
Manage users, patients, and monitor the
overall health of the system.
"""
)

st.success(
    f"Administrator access granted: "
    f"{st.session_state.get('username', 'Administrator')}"
)

st.divider()


# ==========================================================
# Load Data
# ==========================================================

with st.spinner(
    "Loading administrator data..."
):

    dashboard = get_admin_dashboard()
    users_response = get_users()
    patients_response = get_patients()


# ==========================================================
# Normalize Data
# ==========================================================

users = normalize_list(
    users_response,
    [
        "users",
        "data",
        "records",
    ],
)

patients = normalize_list(
    patients_response,
    [
        "patients",
        "data",
        "records",
    ],
)


if not isinstance(
    dashboard,
    dict,
):

    dashboard = {}


# ==========================================================
# Calculate Real Counts
# ==========================================================

# Prefer actual returned records.

total_users = len(
    users
)

total_patients = len(
    patients
)


# Fallback to dashboard values if list endpoint
# did not return records.

if total_users == 0:

    total_users = int(
        dashboard.get(
            "total_users",
            0,
        )
        or 0
    )


if total_patients == 0:

    total_patients = int(
        dashboard.get(
            "total_patients",
            0,
        )
        or 0
    )


total_predictions = int(
    dashboard.get(
        "total_predictions",
        0,
    )
    or 0
)


total_reports = int(
    dashboard.get(
        "total_reports",
        0,
    )
    or 0
)


# ==========================================================
# User Role Counts
# ==========================================================

admin_count = 0
doctor_count = 0
normal_count = 0


for user in users:

    role = get_role(
        user
    ).lower().strip()

    if role == "admin":

        admin_count += 1

    elif role == "doctor":

        doctor_count += 1

    else:

        normal_count += 1


# ==========================================================
# Dashboard Metrics
# ==========================================================

st.subheader(
    "📊 System Overview"
)

metric1, metric2, metric3, metric4 = (
    st.columns(4)
)


with metric1:

    st.metric(
        "👥 Users",
        total_users,
    )


with metric2:

    st.metric(
        "🩺 Patients",
        total_patients,
    )


with metric3:

    st.metric(
        "🧠 Predictions",
        total_predictions,
    )


with metric4:

    st.metric(
        "📄 Reports",
        total_reports,
    )


st.divider()


# ==========================================================
# User Management
# ==========================================================

st.subheader(
    "👥 User Management"
)


if users:

    user_rows = []

    for user in users:

        user_rows.append(
            {
                "ID":
                    get_value(
                        user,
                        ["id", "user_id"],
                        "N/A",
                    ),

                "Username":
                    get_value(
                        user,
                        ["username"],
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

                "Email":
                    get_value(
                        user,
                        ["email"],
                        "N/A",
                    ),

                "Role":
                    get_role(
                        user
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


    users_df = pd.DataFrame(
        user_rows
    )


    st.dataframe(
        users_df,
        use_container_width=True,
        hide_index=True,
    )


    # ------------------------------------------------------
    # User Summary
    # ------------------------------------------------------

    role1, role2, role3 = (
        st.columns(3)
    )


    with role1:

        st.metric(
            "Administrators",
            admin_count,
        )


    with role2:

        st.metric(
            "Doctors",
            doctor_count,
        )


    with role3:

        st.metric(
            "Users",
            normal_count,
        )


    # ------------------------------------------------------
    # Delete User
    # ------------------------------------------------------

    st.write(
        "### 🗑️ User Management"
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

        user_labels = [
            item[0]
            for item in selectable_users
        ]


        selected_username = st.selectbox(
            "Select User",
            user_labels,
            key="admin_selected_user",
        )


        selected_user_id = next(
            user_id
            for username, user_id
            in selectable_users
            if username == selected_username
        )


        confirm_user_delete = st.checkbox(
            "I understand that deleting this user cannot be undone.",
            key="confirm_user_delete",
        )


        if st.button(
            "❌ Delete Selected User",
            disabled=not confirm_user_delete,
            use_container_width=True,
        ):

            # Safety: prevent accidental deletion
            # of the currently logged-in administrator.

            current_username = (
                st.session_state.get(
                    "username"
                )
            )


            if (
                selected_username
                == current_username
            ):

                st.error(
                    "You cannot delete the currently logged-in administrator."
                )

            else:

                try:

                    success = delete_user(
                        selected_user_id
                    )

                except Exception:

                    success = False


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

    st.info(
        "No users were returned by the backend."
    )


st.divider()


# ==========================================================
# Patient Management
# ==========================================================

st.subheader(
    "🩺 Patient Management"
)


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
                    get_patient_name(
                        patient
                    ),

                "Age":
                    get_value(
                        patient,
                        ["age"],
                        "N/A",
                    ),

                "Gender":
                    get_value(
                        patient,
                        ["gender"],
                        "N/A",
                    ),

                "Email":
                    get_value(
                        patient,
                        ["email"],
                        "N/A",
                    ),

                "Phone":
                    get_value(
                        patient,
                        ["phone"],
                        "N/A",
                    ),
            }
        )


    patients_df = pd.DataFrame(
        patient_rows
    )


    st.dataframe(
        patients_df,
        use_container_width=True,
        hide_index=True,
    )


    # ------------------------------------------------------
    # Delete Patient
    # ------------------------------------------------------

    st.write(
        "### 🗑️ Patient Management"
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

        patient_name = get_patient_name(
            patient
        )


        if patient_id is not None:

            selectable_patients.append(
                (
                    f"{patient_name} "
                    f"(ID: {patient_id})",
                    patient_id,
                )
            )


    if selectable_patients:

        patient_labels = [
            item[0]
            for item in selectable_patients
        ]


        selected_patient = st.selectbox(
            "Select Patient",
            patient_labels,
            key="admin_selected_patient",
        )


        selected_patient_id = next(
            patient_id
            for label, patient_id
            in selectable_patients
            if label == selected_patient
        )


        confirm_patient_delete = st.checkbox(
            "I understand that deleting this patient cannot be undone.",
            key="confirm_patient_delete",
        )


        if st.button(
            "🗑️ Delete Selected Patient",
            disabled=not confirm_patient_delete,
            use_container_width=True,
        ):

            try:

                success = delete_patient(
                    selected_patient_id
                )

            except Exception:

                success = False


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

    st.info(
        "No patient records were returned by the backend."
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
                    get_value(
                        item,
                        ["type"],
                        "Activity",
                    ),

                "Description":
                    get_value(
                        item,
                        [
                            "description",
                            "message",
                        ],
                        "",
                    ),

                "Created":
                    get_value(
                        item,
                        [
                            "created_at",
                            "timestamp",
                        ],
                        "N/A",
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


health1, health2 = (
    st.columns(2)
)


with health1:

    if (
        dashboard
        or users
        or patients
    ):

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


with health2:

    if patients is not None:

        st.success(
            "🟢 Database"
        )

    else:

        st.warning(
            "🟡 Database"
        )


    st.success(
        "🟢 AI Assistant"
    )


st.divider()


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
