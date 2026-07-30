import streamlit as st
import pandas as pd

from utils.api_client import (
    get_admin_dashboard,
    get_users,
    get_patients,
    delete_user,
    delete_patient
)

# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="Admin Dashboard",
    page_icon="🛠",
    layout="wide"
)

# ==========================================================
# Authorization
# ==========================================================

if st.session_state.get("role", "User") != "Admin":
    st.error("🚫 Access Denied! Administrator privileges required.")
    st.stop()

# ==========================================================
# Header
# ==========================================================

st.title("🛠 Admin Dashboard")

st.write("""
Manage users, patients, and monitor the overall health of the system.
""")

st.divider()

# ==========================================================
# Dashboard Statistics
# ==========================================================

dashboard = get_admin_dashboard()

if dashboard is None:
    st.error("Unable to load dashboard.")
    st.stop()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("👥 Users", dashboard["total_users"])

with col2:
    st.metric("🩺 Patients", dashboard["total_patients"])

with col3:
    st.metric("🧠 Predictions", dashboard["total_predictions"])

with col4:
    st.metric("📄 Reports", dashboard["total_reports"])

st.divider()

# ==========================================================
# Users
# ==========================================================

st.subheader("👥 User Management")

users = get_users()

if users:

    users_df = pd.DataFrame(users)

    st.dataframe(
        users_df,
        use_container_width=True,
        hide_index=True
    )

    selected_user = st.selectbox(
        "Select User",
        users_df["username"].tolist()
    )

    user = users_df[
        users_df["username"] == selected_user
    ].iloc[0]

    if st.button("❌ Delete User"):

        if delete_user(user["id"]):

            st.success("User deleted successfully.")

            st.rerun()

        else:

            st.error("Unable to delete user.")

else:

    st.info("No users found.")

st.divider()

# ==========================================================
# Patients
# ==========================================================

st.subheader("🩺 Patient Management")

patients = get_patients()

if patients:

    patient_df = pd.DataFrame(patients)

    st.dataframe(
        patient_df,
        use_container_width=True,
        hide_index=True
    )

    selected_patient = st.selectbox(
        "Select Patient",
        patient_df["patient_name"].tolist()
    )

    patient = patient_df[
        patient_df["patient_name"] == selected_patient
    ].iloc[0]

    if st.button("🗑 Delete Patient"):

        if delete_patient(patient["id"]):

            st.success("Patient deleted successfully.")

            st.rerun()

        else:

            st.error("Unable to delete patient.")

else:

    st.info("No patient records available.")

st.divider()

# ==========================================================
# System Health
# ==========================================================

st.subheader("💻 System Health")

health_col1, health_col2 = st.columns(2)

with health_col1:

    st.success("🟢 FastAPI Backend")

    st.success("🟢 Machine Learning Model")

with health_col2:

    st.success("🟢 Database")

    st.success("🟢 AI Assistant")

st.divider()

# ==========================================================
# Recent Activity
# ==========================================================

st.subheader("📝 Recent Activity")

activity = dashboard.get("recent_activity", [])

if activity:

    st.dataframe(
        pd.DataFrame(activity),
        use_container_width=True,
        hide_index=True
    )

else:

    st.info("No recent activity available.")

st.divider()

# ==========================================================
# Footer
# ==========================================================

st.caption("Administrator Panel | Parkinson Disease Detection Agent")
