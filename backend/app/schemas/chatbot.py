"""
Chatbot Schemas
"""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


# ==========================================================
# Chat Request
# ==========================================================

class ChatRequest(BaseModel):
    """
    User chat request.
    """

    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User question"
    )

    patient_id: Optional[int] = Field(
        default=None,
        gt=0
    )

    prediction_id: Optional[int] = Field(
        default=None,
        gt=0
    )

    conversation_id: Optional[str] = None


# ==========================================================
# Chat Message
# ==========================================================

class ChatMessage(BaseModel):
    """
    Individual chat message.
    """

    role: Literal["user", "assistant"]

    content: str

    timestamp: datetime


# ==========================================================
# Chat Response
# ==========================================================

class ChatResponse(BaseModel):
    """
    AI assistant response.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    conversation_id: str

    response: str

    sources: List[str] = []

    suggestions: List[str] = []

    timestamp: datetime


# ==========================================================
# Conversation History
# ==========================================================

class ConversationHistory(BaseModel):
    """
    Conversation history.
    """

    conversation_id: str

    messages: List[ChatMessage]


# ==========================================================
# Suggested Question
# ==========================================================

class SuggestedQuestion(BaseModel):
    """
    Suggested question.
    """

    id: int

    question: str

    category: str


# ==========================================================
# FAQ Item
# ==========================================================

class FAQItem(BaseModel):
    """
    Frequently asked question.
    """

    question: str

    answer: str


# ==========================================================
# Educational Topic
# ==========================================================

class EducationalTopic(BaseModel):
    """
    Educational information about Parkinson disease.
    """

    title: str

    description: str

    category: str


# ==========================================================
# Prediction Explanation
# ==========================================================

class PredictionExplanation(BaseModel):
    """
    Explanation of prediction result.
    """

    prediction_id: int

    prediction: str

    confidence: float

    risk_level: str

    explanation: str


# ==========================================================
# Report Explanation
# ==========================================================

class ReportExplanation(BaseModel):
    """
    Explanation of generated report.
    """

    report_id: int

    summary: str

    recommendations: List[str]


# ==========================================================
# Chat History Response
# ==========================================================

class ChatHistoryResponse(BaseModel):
    """
    Chat history response.
    """

    total_messages: int

    conversations: List[ConversationHistory]


# ==========================================================
# Clear Chat Response
# ==========================================================

class ClearChatResponse(BaseModel):
    """
    Response after clearing history.
    """

    message: str


# ==========================================================
# Chatbot Status
# ==========================================================

class ChatbotStatus(BaseModel):
    """
    AI assistant status.
    """

    status: str

    model_name: str

    version: str

    knowledge_base: str


# ==========================================================
# Parkinson Information
# ==========================================================

class ParkinsonInformation(BaseModel):
    """
    Educational Parkinson disease information.
    """

    definition: str

    symptoms: List[str]

    causes: List[str]

    risk_factors: List[str]

    diagnosis: List[str]

    treatment: List[str]

    prevention: List[str]

    disclaimer: str
