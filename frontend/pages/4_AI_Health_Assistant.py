import streamlit as st


from utils.api_client import (
    ask_ai_assistant,
)


# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="AI Health Assistant",
    page_icon="🤖",
    layout="wide",
)


# ==========================================================
# Session State
# ==========================================================

if "chat_history" not in st.session_state:

    st.session_state.chat_history = []


if "ai_error" not in st.session_state:

    st.session_state.ai_error = None


# ==========================================================
# Header
# ==========================================================

st.title(
    "🤖 AI Health Assistant"
)


st.write(
    """
    Ask questions about Parkinson's Disease, symptoms,
    diagnosis, exercise, medication, nutrition, and
    healthy lifestyle recommendations.
    """
)


st.divider()


# ==========================================================
# Ask AI
# ==========================================================

def ask_question(
    question: str,
):
    """
    Send a question to the FastAPI chatbot.

    Handles dictionary, string, None, and unexpected
    API responses safely.
    """

    question = str(
        question
    ).strip()


    if not question:

        return


    # ------------------------------------------------------
    # Add User Message
    # ------------------------------------------------------

    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": question,
        }
    )


    st.session_state.ai_error = None


    # ------------------------------------------------------
    # Ask Backend
    # ------------------------------------------------------

    with st.spinner(
        "🤖 AI is thinking..."
    ):

        try:

            response = ask_ai_assistant(
                question
            )

        except Exception as exc:

            response = None

            st.session_state.ai_error = (
                f"AI Assistant request failed: {exc}"
            )


    # ------------------------------------------------------
    # Handle No Response
    # ------------------------------------------------------

    if response is None:

        answer = (
            "Unable to connect to the AI Health "
            "Assistant. Please try again."
        )


        if not st.session_state.ai_error:

            st.session_state.ai_error = (
                "The backend did not return a response."
            )


    # ------------------------------------------------------
    # Dictionary Response
    # ------------------------------------------------------

    elif isinstance(
        response,
        dict,
    ):

        # Our api_client may return "answer".
        # The backend may return "response".

        answer = (
            response.get("answer")
            or response.get("response")
            or response.get("message")
            or ""
        )


        if not answer:

            answer = (
                "The AI Assistant returned an "
                "empty response."
            )


            st.session_state.ai_error = (
                "The AI Assistant returned no answer."
            )


        # --------------------------------------------------
        # Backend failure
        # --------------------------------------------------

        if response.get(
            "success"
        ) is False:

            st.session_state.ai_error = (
                response.get(
                    "answer"
                )
                or response.get(
                    "response"
                )
                or "AI Assistant request failed."
            )


    # ------------------------------------------------------
    # Plain Text Response
    # ------------------------------------------------------

    elif isinstance(
        response,
        str,
    ):

        answer = response.strip()


        if not answer:

            answer = (
                "The AI Assistant returned "
                "an empty response."
            )


    # ------------------------------------------------------
    # Unexpected Response
    # ------------------------------------------------------

    else:

        answer = (
            "The AI Assistant returned an "
            "unexpected response."
        )


        st.session_state.ai_error = (
            f"Unexpected response type: "
            f"{type(response).__name__}"
        )


    # ------------------------------------------------------
    # Save AI Response
    # ------------------------------------------------------

    st.session_state.chat_history.append(
        {
            "role": "assistant",
            "content": str(
                answer
            ),
        }
    )


# ==========================================================
# Suggested Questions
# ==========================================================

st.subheader(
    "💡 Suggested Questions"
)


# ==========================================================
# Default Questions
# ==========================================================

suggested_questions = [
    "What is Parkinson's Disease?",
    "What causes hand tremors?",
    "What are the early symptoms?",
    "Is Parkinson curable?",
    "How is Parkinson diagnosed?",
    "What foods are recommended?",
    "Which exercises are beneficial?",
    "How can stress be reduced?",
    "Explain Bradykinesia.",
    "Explain Voice Disorders.",
]


# ----------------------------------------------------------
# Limit displayed questions
# ----------------------------------------------------------

suggested_questions = (
    suggested_questions[:10]
)


# ==========================================================
# Suggested Question Buttons
# ==========================================================

col1, col2 = st.columns(
    2
)


for index, question in enumerate(
    suggested_questions
):

    column = (
        col1
        if index % 2 == 0
        else col2
    )


    with column:

        if st.button(
            question,
            key=(
                f"suggested_question_"
                f"{index}"
            ),
            width="stretch",
        ):

            ask_question(
                question
            )

            st.rerun()


st.divider()


# ==========================================================
# Error Information
# ==========================================================

if st.session_state.ai_error:

    st.warning(
        "⚠️ "
        + str(
            st.session_state.ai_error
        )
    )


# ==========================================================
# Conversation
# ==========================================================

st.subheader(
    "💬 Conversation"
)


if not st.session_state.chat_history:

    st.info(
        """
        Select a suggested question above
        or type your own question below.
        """
    )


else:

    for message in (
        st.session_state.chat_history
    ):

        if not isinstance(
            message,
            dict,
        ):

            continue


        role = message.get(
            "role",
            "assistant",
        )


        content = message.get(
            "content",
            "",
        )


        if role not in (
            "user",
            "assistant",
        ):

            role = "assistant"


        with st.chat_message(
            role
        ):

            st.markdown(
                str(
                    content
                )
            )


# ==========================================================
# User Input
# ==========================================================

question = st.chat_input(
    "Ask your medical question..."
)


# ==========================================================
# Process User Input
# ==========================================================

if question:

    ask_question(
        question
    )

    st.rerun()


# ==========================================================
# Clear Conversation
# ==========================================================

st.divider()


if st.button(
    "🗑 Clear Conversation",
    width="stretch",
):

    st.session_state.chat_history = []

    st.session_state.ai_error = None

    st.rerun()


# ==========================================================
# Medical Disclaimer
# ==========================================================

st.divider()


st.warning(
    """
    ⚠️ **Medical Disclaimer**

    The AI Health Assistant provides general
    educational information and is not a substitute
    for professional medical advice, diagnosis,
    or treatment.

    Always consult a qualified healthcare professional
    for personal medical decisions.
    """
)


# ==========================================================
# Footer
# ==========================================================

st.caption(
    "Parkinson Disease Detection Agent "
    "• AI Health Assistant"
)
