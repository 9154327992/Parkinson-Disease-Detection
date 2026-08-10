import streamlit as st

from utils.api_client import ask_ai_assistant


# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="AI Health Assistant",
    page_icon="🤖",
    layout="wide"
)


# ==========================================================
# Session State
# ==========================================================

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ==========================================================
# Header
# ==========================================================

st.title("🤖 AI Health Assistant")

st.write(
    """
Ask questions about Parkinson's Disease, symptoms, diagnosis,
exercise, medication, nutrition, and healthy lifestyle
recommendations.
"""
)

st.divider()


# ==========================================================
# Function: Ask AI
# ==========================================================

def ask_question(question: str):

    question = question.strip()

    if not question:
        return

    # ------------------------------------------------------
    # Add user question to conversation
    # ------------------------------------------------------

    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": question
        }
    )

    # ------------------------------------------------------
    # Ask Backend
    # ------------------------------------------------------

    with st.spinner("AI is thinking..."):

        response = ask_ai_assistant(
            question
        )

    # ------------------------------------------------------
    # Handle Backend Error
    # ------------------------------------------------------

    if response is None:

        answer = (
            "Unable to connect to the AI Assistant."
        )

        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        return

    # ------------------------------------------------------
    # Get AI Response
    # ------------------------------------------------------

    answer = response.get(
        "response",
        "No response received from the AI Assistant."
    )

    # ------------------------------------------------------
    # Save Assistant Response
    # ------------------------------------------------------

    st.session_state.chat_history.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": response.get(
                "sources",
                []
            )
        }
    )


# ==========================================================
# Suggested Questions
# ==========================================================

st.subheader("💡 Suggested Questions")

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
    "Explain Voice Disorders."
]


# ==========================================================
# Suggested Question Buttons
# ==========================================================

col1, col2 = st.columns(2)

for index, question in enumerate(
    suggested_questions
):

    column = col1 if index % 2 == 0 else col2

    with column:

        if st.button(
            question,
            key=f"suggested_question_{index}",
            use_container_width=True
        ):

            ask_question(question)

            st.rerun()


st.divider()


# ==========================================================
# Chat Messages
# ==========================================================

st.subheader("💬 Conversation")

if not st.session_state.chat_history:

    st.info(
        "Select a suggested question or type your "
        "own question below."
    )

else:

    for message in st.session_state.chat_history:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )

            # --------------------------------------------------
            # Sources
            # --------------------------------------------------

            if message["role"] == "assistant":

                sources = message.get(
                    "sources",
                    []
                )

                if sources:

                    st.caption(
                        "Sources: "
                        + ", ".join(sources)
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

    ask_question(question)

    st.rerun()


# ==========================================================
# Clear Chat
# ==========================================================

st.divider()

if st.button(
    "🗑 Clear Conversation",
    use_container_width=True
):

    st.session_state.chat_history = []

    st.rerun()
