import streamlit as st
import pandas as pd

from utils.api_client import get_patient_history


# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="Patient History",
    page_icon="📋",
    layout="wide",
)


# ==========================================================
# Header
# ==========================================================

st.title(
    "📋 Patient History"
)

st.write(
    """
    View previously analyzed patients and their
    Parkinson's disease prediction results.
    """
)

st.divider()


# ==========================================================
# Load History
# ==========================================================

with st.spinner(
    "Loading patient history..."
):

    history = get_patient_history()


# ==========================================================
# Validate Response
# ==========================================================

if history is None:

    st.error(
        "Unable to fetch prediction history."
    )

    st.info(
        """
        The backend did not return prediction history.
        Please check your connection and try again.
        """
    )

    if st.button(
        "🔄 Retry",
        width="stretch",
    ):

        st.rerun()

    st.stop()


if not isinstance(
    history,
    list,
):

    history = []


# ==========================================================
# Empty State
# ==========================================================

if not history:

    st.info(
        """
        📭 No prediction history is available yet.

        Create a prediction from the Prediction page
        and it will appear here.
        """
    )

    if st.button(
        "🩺 Create New Prediction",
        width="stretch",
    ):

        st.switch_page(
            "pages/2_Prediction.py"
        )

    st.stop()


# ==========================================================
# Convert to DataFrame
# ==========================================================

df = pd.DataFrame(
    history
)


# ==========================================================
# Normalize Columns
# ==========================================================

if (
    "patient_name"
    not in df.columns
):

    if (
        "first_name"
        in df.columns
    ):

        df[
            "patient_name"
        ] = (
            df[
                "first_name"
            ]
            .fillna("")
            .astype(str)
            + " "
            + df.get(
                "last_name",
                "",
            )
            .fillna("")
            .astype(str)
        ).str.strip()

    else:

        df[
            "patient_name"
        ] = "Unknown"


if (
    "diagnosis"
    not in df.columns
):

    if (
        "prediction"
        in df.columns
    ):

        df[
            "diagnosis"
        ] = df[
            "prediction"
        ]

    elif (
        "prediction_result"
        in df.columns
    ):

        df[
            "diagnosis"
        ] = df[
            "prediction_result"
        ]

    else:

        df[
            "diagnosis"
        ] = "Unknown"


if (
    "risk_level"
    not in df.columns
):

    df[
        "risk_level"
    ] = "Unknown"


if (
    "risk_score"
    not in df.columns
):

    df[
        "risk_score"
    ] = None


# ==========================================================
# Summary
# ==========================================================

st.subheader(
    "📊 History Summary"
)


total_records = len(
    df
)


high_risk_count = 0
medium_risk_count = 0
low_risk_count = 0


if "risk_level" in df.columns:

    risk_values = (
        df[
            "risk_level"
        ]
        .fillna("")
        .astype(str)
        .str.lower()
    )


    high_risk_count = int(
        risk_values.str.contains(
            "high"
        ).sum()
    )


    medium_risk_count = int(
        risk_values.str.contains(
            "medium"
        ).sum()
    )


    low_risk_count = int(
        risk_values.str.contains(
            "low"
        ).sum()
    )


summary_col1, summary_col2, summary_col3, summary_col4 = (
    st.columns(4)
)


with summary_col1:

    st.metric(
        "🧠 Total Predictions",
        total_records,
    )


with summary_col2:

    st.metric(
        "🔴 High Risk",
        high_risk_count,
    )


with summary_col3:

    st.metric(
        "🟠 Medium Risk",
        medium_risk_count,
    )


with summary_col4:

    st.metric(
        "🟢 Low Risk",
        low_risk_count,
    )


st.divider()


# ==========================================================
# Search
# ==========================================================

st.subheader(
    "🔎 Search Predictions"
)


search = st.text_input(
    "Search",
    placeholder=(
        "Search by patient name, "
        "diagnosis, risk level, or ID..."
    ),
)


filtered_df = df.copy()


if search:

    search_text = (
        search
        .strip()
        .lower()
    )


    mask = (
        filtered_df
        .astype(str)
        .apply(
            lambda column:
            column.str.lower()
            .str.contains(
                search_text,
                na=False,
            )
        )
        .any(
            axis=1
        )
    )


    filtered_df = filtered_df[
        mask
    ]


# ==========================================================
# Results Count
# ==========================================================

st.caption(
    f"Showing {len(filtered_df)} "
    f"of {len(df)} prediction records."
)


# ==========================================================
# Display History
# ==========================================================

display_columns = [
    "id",
    "patient_name",
    "diagnosis",
    "risk_level",
    "risk_score",
    "created_at",
]


available_columns = [
    column
    for column in display_columns
    if column in filtered_df.columns
]


if available_columns:

    display_df = filtered_df[
        available_columns
    ].copy()

else:

    display_df = filtered_df.copy()


display_df = display_df.rename(
    columns={
        "id": "ID",
        "patient_name": "Patient",
        "diagnosis": "Diagnosis",
        "risk_level": "Risk Level",
        "risk_score": "Risk Score",
        "created_at": "Date",
    }
)


st.dataframe(
    display_df,
    width="stretch",
    hide_index=True,
)


st.divider()


# ==========================================================
# Select Prediction
# ==========================================================

st.subheader(
    "🔍 Prediction Details"
)


record_options = []


for index, record in filtered_df.iterrows():

    patient_name = record.get(
        "patient_name",
        "Unknown",
    )


    diagnosis = record.get(
        "diagnosis",
        "Unknown",
    )


    risk_level = record.get(
        "risk_level",
        "Unknown",
    )


    record_id = record.get(
        "id",
        index,
    )


    label = (
        f"{patient_name} | "
        f"{diagnosis} | "
        f"{risk_level} | "
        f"ID: {record_id}"
    )


    record_options.append(
        (
            index,
            label,
        )
    )


if record_options:

    selected_index = st.selectbox(
        "Select a prediction",
        [
            item[0]
            for item in record_options
        ],
        format_func=lambda index: next(
            (
                label
                for item_index, label
                in record_options
                if item_index == index
            ),
            str(index),
        ),
    )


    selected = filtered_df.loc[
        selected_index
    ]


    # ======================================================
    # Selected Details
    # ======================================================

    detail_col1, detail_col2, detail_col3 = (
        st.columns(3)
    )


    with detail_col1:

        st.write(
            f"**Patient:** "
            f"{selected.get('patient_name', 'N/A')}"
        )

        st.write(
            f"**Age:** "
            f"{selected.get('age', 'N/A')}"
        )

        st.write(
            f"**Gender:** "
            f"{selected.get('gender', 'N/A')}"
        )


    with detail_col2:

        st.write(
            f"**Diagnosis:** "
            f"{selected.get('diagnosis', 'N/A')}"
        )

        st.write(
            f"**Risk Level:** "
            f"{selected.get('risk_level', 'N/A')}"
        )

        st.write(
            f"**Risk Score:** "
            f"{selected.get('risk_score', 'N/A')}"
        )


    with detail_col3:

        st.write(
            f"**Prediction ID:** "
            f"{selected.get('id', 'N/A')}"
        )

        st.write(
            f"**Date:** "
            f"{selected.get('created_at', 'N/A')}"
        )

        st.write(
            f"**Confidence:** "
            f"{selected.get('confidence', 'N/A')}"
        )


    st.divider()


    # ======================================================
    # Recommendation
    # ======================================================

    recommendation = selected.get(
        "recommendation"
    )


    if recommendation:

        st.subheader(
            "💡 Recommendation"
        )

        st.info(
            str(
                recommendation
            )
        )


    # ======================================================
    # Raw Record
    # ======================================================

    with st.expander(
        "🔎 View Complete Prediction Record"
    ):

        st.json(
            selected.to_dict()
        )


# ==========================================================
# Export
# ==========================================================

st.divider()

st.subheader(
    "⬇️ Export History"
)


csv_data = filtered_df.to_csv(
    index=False
)


st.download_button(
    label="📥 Download Prediction History",
    data=csv_data,
    file_name="prediction_history.csv",
    mime="text/csv",
    width="stretch",
)


# ==========================================================
# Navigation
# ==========================================================

st.divider()

nav1, nav2 = st.columns(2)


with nav1:

    if st.button(
        "🩺 New Prediction",
        width="stretch",
    ):

        st.switch_page(
            "pages/2_Prediction.py"
        )


with nav2:

    if st.button(
        "📄 View Reports",
        width="stretch",
    ):

        st.switch_page(
            "pages/5_Reports.py"
        )


# ==========================================================
# Medical Disclaimer
# ==========================================================

st.divider()

st.warning(
    """
    ⚠️ **Medical Disclaimer**

    Prediction history is provided for AI-assisted
    screening and educational purposes. It does not
    constitute a medical diagnosis or treatment plan.
    """
)


# ==========================================================
# Footer
# ==========================================================

st.caption(
    "Parkinson Disease Detection Agent • Patient History"
)
