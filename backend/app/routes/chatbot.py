"""
AI Health Assistant Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_current_user

from app.schemas.chatbot import (
    ChatRequest,
    ChatResponse,
)

from app.services.chatbot_service import ChatbotService


router = APIRouter(
    prefix="/chatbot",
    tags=["AI Health Assistant"]
)

chatbot_service = ChatbotService()


# ==========================================================
# Chat with AI Assistant
# ==========================================================

@router.post(
    "/",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
)
def chat(
    request: ChatRequest,
    current_user=Depends(get_current_user)
):
    """
    Chat with the AI Health Assistant.
    """

    try:

        return chatbot_service.chat(
            request=request,
            user=current_user
        )

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chatbot error: {str(e)}"
        )


# ==========================================================
# Suggested Questions
# ==========================================================

@router.get("/suggestions")
def suggestions(
    current_user=Depends(get_current_user)
):
    """
    Return suggested questions.
    """

    return chatbot_service.suggestions()


# ==========================================================
# Chat History
# ==========================================================

@router.get("/history")
def history(
    current_user=Depends(get_current_user)
):
    """
    Return chat history.
    """

    return chatbot_service.history(
        current_user["id"]
    )


# ==========================================================
# Clear Chat History
# ==========================================================

@router.delete("/history")
def clear_history(
    current_user=Depends(get_current_user)
):
    """
    Clear chat history.
    """

    chatbot_service.clear_history(
        current_user["id"]
    )

    return {
        "message": "Chat history cleared."
    }


# ==========================================================
# Explain Prediction
# ==========================================================

@router.get("/prediction/{prediction_id}")
def explain_prediction(
    prediction_id: int,
    current_user=Depends(get_current_user)
):
    """
    Explain a prediction result in
    patient-friendly language.
    """

    explanation = chatbot_service.explain_prediction(
        prediction_id
    )

    if explanation is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found."
        )

    return explanation


# ==========================================================
# Explain Report
# ==========================================================

@router.get("/report/{report_id}")
def explain_report(
    report_id: int,
    current_user=Depends(get_current_user)
):
    """
    Explain a patient's report.
    """

    explanation = chatbot_service.explain_report(
        report_id
    )

    if explanation is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found."
        )

    return explanation


# ==========================================================
# Parkinson Disease Information
# ==========================================================

@router.get("/parkinson")
def parkinson_information():
    """
    Educational information about
    Parkinson Disease.
    """

    return chatbot_service.parkinson_information()


# ==========================================================
# Frequently Asked Questions
# ==========================================================

@router.get("/faq")
def faq():
    """
    Frequently asked questions.
    """

    return chatbot_service.faq()
