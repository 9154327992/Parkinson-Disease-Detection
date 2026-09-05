from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_current_user

from app.schemas.chatbot import (
    ChatRequest,
    ChatResponse,
)

from app.services.chatbot_service import ChatbotService


router = APIRouter(
    prefix="/chatbot",
    tags=["AI Health Assistant"],
)


chatbot_service = ChatbotService()


# ==========================================================
# Chat
# ==========================================================

@router.post(
    "/",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
)
def chat(
    request: ChatRequest,
    current_user=Depends(get_current_user),
):

    try:

        return chatbot_service.chat(
            request=request
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chatbot error: {str(exc)}",
        )


# ==========================================================
# Suggestions
# ==========================================================

@router.get("/suggestions")
def suggestions(
    current_user=Depends(get_current_user),
):

    return chatbot_service.suggestions()


# ==========================================================
# History
# ==========================================================

@router.get("/history")
def history(
    current_user=Depends(get_current_user),
):

    user_id = None

    if isinstance(
        current_user,
        dict,
    ):

        user_id = current_user.get(
            "id"
        )

    return chatbot_service.history(
        user_id
    )


# ==========================================================
# Clear History
# ==========================================================

@router.delete("/history")
def clear_history(
    current_user=Depends(get_current_user),
):

    user_id = None

    if isinstance(
        current_user,
        dict,
    ):

        user_id = current_user.get(
            "id"
        )

    return chatbot_service.clear_history(
        user_id
    )


# ==========================================================
# Explain Prediction
# ==========================================================

@router.get(
    "/prediction/{prediction_id}"
)
def explain_prediction(
    prediction_id: int,
    current_user=Depends(get_current_user),
):

    explanation = (
        chatbot_service.explain_prediction(
            prediction_id
        )
    )

    if explanation is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found.",
        )

    return explanation


# ==========================================================
# Explain Report
# ==========================================================

@router.get(
    "/report/{report_id}"
)
def explain_report(
    report_id: int,
    current_user=Depends(get_current_user),
):

    explanation = (
        chatbot_service.explain_report(
            report_id
        )
    )

    if explanation is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found.",
        )

    return explanation


# ==========================================================
# Parkinson Information
# ==========================================================

@router.get("/parkinson")
def parkinson_information():

    return chatbot_service.parkinson_information()


# ==========================================================
# FAQ
# ==========================================================

@router.get("/faq")
def faq():

    return chatbot_service.faq()


# ==========================================================
# Educational Topics
# ==========================================================

@router.get("/topics")
def educational_topics():

    return chatbot_service.educational_topics()


# ==========================================================
# Status
# ==========================================================

@router.get("/status")
def chatbot_status():

    return chatbot_service.status()
