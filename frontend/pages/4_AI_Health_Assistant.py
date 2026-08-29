import streamlit as st
from pathlib import Path

from utils.api_client import ask_ai_assistant


# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="AI Health Assistant",
    page_icon="🤖",
    layout="wide",
)


# ==========================================================
# Paths
# ==========================================================

FRONTEND_DIR = Path(
    __file__
).resolve().parents[1]

IMAGE_PATH = (
    FRONTEND_DIR
    / "assets"
    / "images"
    / "chatbot_banner.png"
)


# ==========================================================
# Session State
# ==========================================================

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


if "ai_error" not in st.session_state:
    st.session_state.ai_error = None


# ==========================================================
# Banner
# ==========================================================

if IMAGE_PATH.exists():

    st.image(
        str(IMAGE_PATH),
        use_container_width=True,
    )

else:

    st.warning(
        "Chatbot banner image was not found."
    )


# ==========================================================
# Header
# ==========================================================

st.title(
    "🤖 AI Health Assistant"
)

st.markdown(
    """
Ask questions about **Parkinson's disease, symptoms,
diagnosis, exercise, nutrition, medication, voice
changes, and healthy lifestyle practices.**
"""
)

st.caption(
    "AI-assisted educational health information"
)

st.divider()


# ==========================================================
# Suggested Questions
# ==========================================================

st.subheader(
    "💡 Suggested Questions"
)

st.markdown(
    "Choose a question or type your own below."
)


suggested_questions = [

    "What is Parkinson's disease?",

    "What are the early symptoms of Parkinson's disease?",

    "How can the risk of Parkinson's disease be reduced?",

    "How is Parkinson's disease diagnosed?",

    "Is Parkinson's disease curable?",

    "What exercises may be beneficial for people with Parkinson's?",

    "What foods are recommended for a healthy lifestyle?",

    "What causes tremors and slowed movement?",

    "What is bradykinesia?",

    "What are Parkinson's-related voice changes?",

]


# ==========================================================
# Suggested Question Buttons
# ==========================================================

question_columns = st.columns(2)


for index, question_text in enumerate(
    suggested_questions
):

    column = question_columns[
        index % 2
    ]

    with column:

        if st.button(
            question_text,
            key=f"question_{index}",
            use_container_width=True,
        ):

            st.session_state[
                "pending_question"
            ] = question_text

            st.rerun()


st.divider()


# ==========================================================
# AI Request Function
# ==========================================================

def ask_question(
    question: str,
):
    """
    Send a question to the FastAPI AI assistant
    and store the response in chat history.
    """

    question = str(
        question
    ).strip()

    if not question:
        return


    # ------------------------------------------------------
    # Clear previous error
    # ------------------------------------------------------

    st.session_state.ai_error = None


    # ------------------------------------------------------
    # Store User Message
    # ------------------------------------------------------

    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": question,
        }
    )


    # ------------------------------------------------------
    # Call Backend
    # ------------------------------------------------------

    response = None

    with st.spinner(
        "🤖 AI Health Assistant is thinking..."
    ):

        try:

            response = ask_ai_assistant(
                question
            )

        except Exception as exc:

            st.session_state.ai_error = (
                "Unable to connect to the AI Health "
                "Assistant."
            )

            response = None


    # ------------------------------------------------------
    # Handle No Response
    # ------------------------------------------------------

    if response is None:

        answer = (
            "I could not get a response from the "
            "AI Health Assistant. Please check the "
            "backend connection and try again."
        )


    # ------------------------------------------------------
    # Handle Dictionary Response
    # ------------------------------------------------------

    elif isinstance(
        response,
        dict,
    ):

        answer = (
            response.get("answer")
            or response.get("response")
            or response.get("message")
            or response.get("content")
            or ""
        )

        answer = str(
            answer
        ).strip()


        if not answer:

            answer = (
                "The AI Health Assistant returned "
                "an empty response."
            )

            st.session_state.ai_error = (
                "The backend returned no answer."
            )


        # --------------------------------------------------
        # Backend explicitly reported failure
        # --------------------------------------------------

        if response.get(
            "success"
        ) is False:

            st.session_state.ai_error = (
                response.get("error")
                or response.get("message")
                or "AI Assistant request failed."
            )


    # ------------------------------------------------------
    # Handle String Response
    # ------------------------------------------------------

    elif isinstance(
        response,
        str,
    ):

        answer = response.strip()


        if not answer:

            answer = (
                "The AI Health Assistant returned "
                "an empty response."
            )


    # ------------------------------------------------------
    # Unexpected Response
    # ------------------------------------------------------

    else:

        answer = (
            "The AI Health Assistant returned "
            "an unexpected response."
        )

        st.session_state.ai_error = (
            "Unexpected backend response type: "
            f"{type(response).__name__}"
        )


    # ------------------------------------------------------
    # Store Assistant Response
    # ------------------------------------------------------

    st.session_state.chat_history.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )


# ==========================================================
# Process Suggested Question
# ==========================================================

if "pending_question" in st.session_state:

    pending_question = (
        st.session_state.pop(
            "pending_question"
        )
    )

    ask_question(
        pending_question
    )

    st.rerun()


# ==========================================================
# Error Display
# ==========================================================

if st.session_state.ai_error:

    st.error(
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
        👋 Welcome to the AI Health Assistant.

        Ask a question about Parkinson's disease,
        symptoms, diagnosis, exercise, nutrition,
        medication, voice changes, or healthy living.
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
    "Ask your health question..."
)


if question:

    ask_question(
        question
    )

    st.rerun()


# ==========================================================
# Conversation Controls
# ==========================================================

if st.session_state.chat_history:

    st.divider()

    control_col1, control_col2 = (
        st.columns(2)
    )


    with control_col1:

        if st.button(
            "🗑 Clear Conversation",
            use_container_width=True,
        ):

            st.session_state.chat_history = []

            st.session_state.ai_error = None

            st.rerun()


    with control_col2:

        if st.button(
            "🔄 Start New Conversation",
            use_container_width=True,
        ):

            st.session_state.chat_history = []

            st.session_state.ai_error = None

            st.rerun()


# ==========================================================
# Health Assistant Guidance
# ==========================================================

st.divider()

with st.expander(
    "ℹ️ What can I ask?"
):

    st.markdown(
        """
### Parkinson's Disease

- What is Parkinson's disease?
- What are the common symptoms?
- What are early warning signs?
- How is Parkinson's diagnosed?
- Is Parkinson's curable?

### Lifestyle

- What exercises may help?
- What foods support a healthy lifestyle?
- How can sleep be improved?
- How can stress be managed?

### Voice and Movement

- What is bradykinesia?
- What causes tremors?
- Why can Parkinson's affect speech?
- What are common voice changes?

### General Health

You can also ask about general health topics,
but the assistant provides **educational information**
and cannot provide a personal diagnosis.
"""
    )


# ==========================================================
# Medical Disclaimer
# ==========================================================

st.divider()

st.warning(
    """
⚠️ **Medical Disclaimer**

The AI Health Assistant provides general educational
information. It is not a substitute for professional
medical advice, diagnosis, or treatment.

The assistant cannot diagnose Parkinson's disease or
determine an individual's medical condition.

If you have persistent, worsening, or concerning
symptoms, consult a qualified healthcare professional.
"""
)


# ==========================================================
# Footer
# ==========================================================

st.caption(
    "Parkinson Disease Detection Agent "
    "• AI Health Assistant"
)
