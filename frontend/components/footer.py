import streamlit as st
from datetime import datetime


def render_footer():
    """
    Render the application footer.
    """

    st.divider()

    current_year = datetime.now().year

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        st.caption(
            f"© {current_year} Parkinson Disease Detection Agent"
        )

    with col2:
        st.caption(
            "Powered by Streamlit • FastAPI • Scikit-learn"
        )

    with col3:
        st.caption("Version 1.0.0")
