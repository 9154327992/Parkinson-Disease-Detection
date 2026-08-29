import streamlit as st
from pathlib import Path


# ==========================================================
# Paths
# ==========================================================

FRONTEND_DIR = (
    Path(__file__).resolve().parents[1]
)

ASSETS_DIR = (
    FRONTEND_DIR
    / "assets"
)

LOGO_PATH = (
    ASSETS_DIR
    / "logo.png"
)


# ==========================================================
# Sidebar
# ==========================================================

def render_sidebar():
    """
    Render the application sidebar.

    Displays:
    - Application logo
    - Application title
    - Navigation information
    - User information when available
    """


    # ------------------------------------------------------
    # Sidebar container
    # ------------------------------------------------------

    with st.sidebar:

        # --------------------------------------------------
        # Logo
        # --------------------------------------------------

        if LOGO_PATH.exists():

            st.image(
                str(LOGO_PATH),
                width=180,
            )

        else:

            st.markdown(
                """
                <div style="
                    text-align:center;
                    font-size:48px;
                    margin-bottom:10px;
                ">
                    🧠
                </div>
                """,
                unsafe_allow_html=True,
            )


        # --------------------------------------------------
        # Application title
        # --------------------------------------------------

        st.markdown(
            """
            <div style="
                text-align:center;
                margin-bottom:15px;
            ">

            <h2 style="
                margin-bottom:2px;
            ">
                Parkinson Disease
            </h2>

            <p style="
                margin-top:0;
                font-size:14px;
                opacity:0.75;
            ">
                Detection Agent
            </p>

            </div>
            """,
            unsafe_allow_html=True,
        )


        st.divider()


        # --------------------------------------------------
        # Navigation
        # --------------------------------------------------

        st.markdown(
            "### 🧭 Navigation"
        )

        st.markdown(
            """
            Use the navigation menu above to access:

            🏠 **Home**  
            🎙️ **Prediction**  
            📋 **Patient History**  
            🤖 **AI Health Assistant**  
            📄 **Reports**  
            📊 **Analytics**  
            ⚙️ **Settings**
            """
        )


        st.divider()


        # --------------------------------------------------
        # Platform information
        # --------------------------------------------------

        with st.expander(
            "ℹ️ About the Platform"
        ):

            st.markdown(
                """
                **Parkinson Disease Detection Agent**

                An AI-powered healthcare application
                designed to support Parkinson's disease
                risk assessment using voice analysis.

                **Main capabilities:**

                - 🎙️ Voice-based analysis
                - 🤖 Machine-learning prediction
                - 📊 Risk assessment
                - 📋 Patient history
                - 📄 Automated reports
                - 📈 Analytics
                - 💬 AI Health Assistant

                **Important:** Prediction results are
                educational/model-based assessments and
                are not a medical diagnosis.
                """
            )


        # --------------------------------------------------
        # Security information
        # --------------------------------------------------

        with st.expander(
            "🔐 Privacy & Security"
        ):

            st.markdown(
                """
                Your application data should be handled
                according to the security and privacy
                configuration of the deployed system.

                Do not use prediction results as a
                substitute for professional medical advice.
                """
            )


        # --------------------------------------------------
        # Footer
        # --------------------------------------------------

        st.divider()

        st.caption(
            "Parkinson Disease Detection Agent"
        )

        st.caption(
            "AI-powered • Educational • Not a diagnosis"
        )


# ==========================================================
# Automatic Sidebar Rendering
# ==========================================================

render_sidebar()
