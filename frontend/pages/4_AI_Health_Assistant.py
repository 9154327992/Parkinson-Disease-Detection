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
exercise, medication, and healthy lifestyle recommendations.
"""
)

st.divider()

# ==========================================================
# Suggested Questions
# ==========================================================

st.subheader("💡 Suggested Questions")

col1, col2 = st.columns(2)

with col1:

    st.markdown("""
- What is Parkinson's Disease?

- What causes hand tremors?

- What are the early symptoms?

- Is Parkinson curable?

- How is Parkinson diagnosed?
""")

with col2:

    st.markdown("""
- What foods are recommended?

- Which exercises are beneficial?

- How can stress be reduced?

- Explain Bradykinesia.

- Explain Voice Disorders.
""")

st.divider()

# ==========================================================
# Chat Messages
# ==========================================================

st.subheader("💬 Conversation")

for message in st.session_state.chat_history:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

# ==========================================================
# User Input
# ==========================================================

question = st.chat_input(
    "Ask your medical question..."
)

# ==========================================================
# AI Response
# ==========================================================

if question:

    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.spinner("AI is thinking..."):

        response = ask_ai_assistant(question)

    if response is None:

        answer = (
            "Unable to connect to the AI Assistant."
        )

    else:

        answer = response["response"]

    st.session_state.chat_history.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    with st.chat_message("assistant"):
        st.markdown(answer)

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
