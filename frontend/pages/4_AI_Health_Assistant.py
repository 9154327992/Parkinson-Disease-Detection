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


# Used to trigger scrolling after an assistant response.
if "scroll_to_answer" not in st.session_state:
    st.session_state.scroll_to_answer = False


# Used for suggested-question buttons.
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


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
changes, sleep, stress, and healthy lifestyle practices.**
"""
)

st.caption(
    "AI-assisted educational health information"
)

st.divider()


# ==========================================================
# Ask Question
# ==========================================================

def ask_question(
    question: str,
):
    """
    Send a question to the FastAPI AI assistant.

    The response is stored in Streamlit session state.
    """

    question = str(
        question
    ).strip()

    if not question:
        return


    # ------------------------------------------------------
    # Reset error
    # ------------------------------------------------------

    st.session_state.ai_error = None


    # ------------------------------------------------------
    # Add user message
    # ------------------------------------------------------

    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": question,
        }
    )


    # ------------------------------------------------------
    # Ask backend
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
    # No response
    # ------------------------------------------------------

    if response is None:

        answer = (
            "I could not get a response from the "
            "AI Health Assistant. Please check the "
            "backend connection and try again."
        )


    # ------------------------------------------------------
    # Dictionary response
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
        # Backend failure
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
    # String response
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
    # Unexpected response
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
    # Add assistant response
    # ------------------------------------------------------

    st.session_state.chat_history.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )


    # ------------------------------------------------------
    # Tell page to scroll to latest answer
    # ------------------------------------------------------

    st.session_state.scroll_to_answer = True


# ==========================================================
# Suggested Questions
# ==========================================================

st.subheader(
    "💡 Suggested Questions"
)

st.markdown(
    "Choose a question or type your own question below."
)


suggested_questions = [

    "What is Parkinson's disease?",

    "What are the early symptoms of Parkinson's disease?",

    "How can the risk of Parkinson's disease be reduced?",

    "How is Parkinson's disease diagnosed?",

    "Is Parkinson's disease curable?",

    "What exercises may be beneficial for Parkinson's?",

    "What foods are recommended for a healthy lifestyle?",

    "What causes tremors and slowed movement?",

    "What is bradykinesia?",

    "What are Parkinson's-related voice changes?",

]


# ==========================================================
# Suggested Question Buttons
# ==========================================================

col1, col2 = st.columns(2)


for index, question_text in enumerate(
    suggested_questions
):

    column = (
        col1
        if index % 2 == 0
        else col2
    )

    with column:

        if st.button(
            question_text,
            key=f"suggested_question_{index}",
            use_container_width=True,
        ):

            st.session_state.pending_question = (
                question_text
            )

            st.rerun()


# ==========================================================
# Process Suggested Question
# ==========================================================

if st.session_state.pending_question:

    pending_question = (
        st.session_state.pending_question
    )

    st.session_state.pending_question = None

    ask_question(
        pending_question
    )

    st.rerun()


# ==========================================================
# Error Information
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

st.divider()

st.subheader(
    "💬 Conversation"
)


if not st.session_state.chat_history:

    st.info(
        """
        👋 Welcome to the AI Health Assistant.

        Ask a question about Parkinson's disease,
        symptoms, diagnosis, exercise, nutrition,
        medication, voice changes, sleep, stress,
        or healthy living.
        """
    )

else:

    for index, message in enumerate(
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


        # --------------------------------------------------
        # Latest assistant answer marker
        # --------------------------------------------------

        is_latest_assistant = (
            index
            == len(
                st.session_state.chat_history
            ) - 1
            and role == "assistant"
        )


        if is_latest_assistant:

            st.markdown(
                """
                <div id="latest-answer"></div>
                """,
                unsafe_allow_html=True,
            )


        # --------------------------------------------------
        # Chat message
        # --------------------------------------------------

        with st.chat_message(
            role
        ):

            st.markdown(
                str(
                    content
                )
            )


# ==========================================================
# Automatic Scroll To Latest Answer
# ==========================================================

if (
    st.session_state.scroll_to_answer
    and st.session_state.chat_history
):

    st.session_state.scroll_to_answer = False

    import streamlit.components.v1 as components

    components.html(
        """
        <script>
        setTimeout(function() {

            try {

                const parentDocument =
                    window.parent.document;

                const messages =
                    parentDocument.querySelectorAll(
                        '[data-testid="stChatMessage"]'
                    );

                if (messages.length > 0) {

                    const lastMessage =
                        messages[messages.length - 1];

                    lastMessage.scrollIntoView({
                        behavior: "smooth",
                        block: "center"
                    });

                } else {

                    window.parent.scrollTo({
                        top: document.body.scrollHeight,
                        behavior: "smooth"
                    });

                }

            } catch (error) {

                console.log(
                    "Automatic scroll failed:",
                    error
                );

            }

        }, 800);
        </script>
        """,
        height=0,
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
            width="stretch",
        ):

            st.session_state.chat_history = []

            st.session_state.ai_error = None

            st.session_state.pop(
                "chat_conversation_id",
                None,
            )

            st.rerun()


    with control_col2:

        if st.button(
            "🔄 New Conversation",
            use_container_width=True,
        ):

            st.session_state.chat_history = []

            st.session_state.ai_error = None

            st.session_state.scroll_to_answer = False

            st.session_state.pending_question = None

            st.session_state.pop(
                "chat_conversation_id",
                None,
            )

            st.rerun()


# ==========================================================
# What Can I Ask?
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
- What are the early warning signs?
- How is Parkinson's disease diagnosed?
- Is Parkinson's disease curable?
- How can the risk be reduced?

### Lifestyle

- What exercises may be beneficial?
- What foods support a healthy lifestyle?
- How can sleep be improved?
- How can stress be managed?

### Movement and Voice

- What is bradykinesia?
- What causes tremors?
- Why can Parkinson's affect speech?
- What are common Parkinson's-related voice changes?

### General Health

You can ask general educational health questions,
but the assistant cannot provide a personal diagnosis
or replace a healthcare professional.
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
