"""
Chatbot Service

AI Health Assistant for Parkinson Disease Detection System.

This service provides educational information only.
It does NOT diagnose diseases or prescribe treatments.
"""

from datetime import datetime
from uuid import uuid4

from app.schemas.chatbot import (
    ChatRequest,
    ChatResponse,
    ChatMessage,
    ConversationHistory,
    SuggestedQuestion,
    FAQItem,
    EducationalTopic,
    PredictionExplanation,
    ReportExplanation,
    ChatHistoryResponse,
    ClearChatResponse,
    ChatbotStatus,
    ParkinsonInformation,
)


class ChatbotService:
    """
    AI Health Assistant.
    """

    def __init__(self):
        """
        In production integrate with:

        - OpenAI / Local LLM
        - Vector Database
        - Medical Knowledge Base
        - Database conversation storage
        """

        self._history = {}

    # =====================================================
    # Chat
    # =====================================================

    def chat(
        self,
        request: ChatRequest,
    ) -> ChatResponse:
        """
        Process a user message.
        """

        conversation_id = (
            request.conversation_id
            or str(uuid4())
        )

        answer = self._generate_response(
            request.message
        )

        message = ChatMessage(
            role="user",
            content=request.message,
            timestamp=datetime.utcnow(),
        )

        self._history.setdefault(
            conversation_id,
            []
        ).append(message)

        self._history[conversation_id].append(
            ChatMessage(
                role="assistant",
                content=answer,
                timestamp=datetime.utcnow(),
            )
        )

        return ChatResponse(
            conversation_id=conversation_id,
            response=answer,
            sources=[
                "Parkinson Foundation",
                "World Health Organization",
            ],
            suggestions=[
                "What are the early symptoms?",
                "Explain my prediction.",
                "How accurate is the model?",
            ],
            timestamp=datetime.utcnow(),
        )

    # =====================================================
    # Generate Response
    # =====================================================

    def _generate_response(
        self,
        message: str,
    ) -> str:
        """
        Simple rule-based chatbot.

        Replace with an LLM in production.
        """

        text = message.lower()

        if "symptom" in text:
            return (
                "Common symptoms include tremor, stiffness, "
                "slowed movement, and balance difficulties. "
                "Consult a healthcare professional for diagnosis."
            )

        if "high risk" in text:
            return (
                "A high-risk prediction means the machine learning "
                "model found patterns associated with Parkinson disease. "
                "It is not a diagnosis."
            )

        if "prediction" in text:
            return (
                "The prediction is generated from 22 voice features "
                "using a trained machine learning model."
            )

        if "exercise" in text:
            return (
                "Regular walking, stretching, balance exercises, "
                "and strength training may help maintain mobility."
            )

        return (
            "I can answer educational questions about Parkinson disease, "
            "prediction results, reports, exercise, and healthy habits."
        )

    # =====================================================
    # Conversation History
    # =====================================================

    def get_history(
        self,
    ) -> ChatHistoryResponse:
        """
        Return conversation history.
        """

        conversations = []

        for cid, messages in self._history.items():

            conversations.append(
                ConversationHistory(
                    conversation_id=cid,
                    messages=messages,
                )
            )

        return ChatHistoryResponse(
            total_messages=sum(
                len(m)
                for m in self._history.values()
            ),
            conversations=conversations,
        )

    # =====================================================
    # Clear History
    # =====================================================

    def clear_history(
        self,
    ) -> ClearChatResponse:
        """
        Remove conversation history.
        """

        self._history.clear()

        return ClearChatResponse(
            message="Conversation history cleared."
        )

    # =====================================================
    # Suggested Questions
    # =====================================================

    def suggested_questions(
        self,
    ) -> list[SuggestedQuestion]:
        """
        Suggested questions.
        """

        return [
            SuggestedQuestion(
                id=1,
                question="What are early symptoms?",
                category="Symptoms",
            ),
            SuggestedQuestion(
                id=2,
                question="Explain my prediction.",
                category="Prediction",
            ),
            SuggestedQuestion(
                id=3,
                question="How accurate is the model?",
                category="Model",
            ),
        ]

    # =====================================================
    # Frequently Asked Questions
    # =====================================================

    def faq(
        self,
    ) -> list[FAQItem]:
        """
        Frequently asked questions.
        """

        return [
            FAQItem(
                question="Can this system diagnose Parkinson disease?",
                answer=(
                    "No. It provides a prediction that should be "
                    "confirmed by a qualified healthcare professional."
                ),
            ),
            FAQItem(
                question="How accurate is the prediction?",
                answer=(
                    "Accuracy depends on the trained machine learning "
                    "model and should not replace clinical assessment."
                ),
            ),
        ]

    # =====================================================
    # Educational Topics
    # =====================================================

    def educational_topics(
        self,
    ) -> list[EducationalTopic]:
        """
        Parkinson educational topics.
        """

        return [
            EducationalTopic(
                title="Symptoms",
                description="Motor and non-motor symptoms.",
                category="Disease",
            ),
            EducationalTopic(
                title="Diagnosis",
                description="Clinical evaluation and neurological examination.",
                category="Diagnosis",
            ),
            EducationalTopic(
                title="Treatment",
                description="Medication, exercise, and rehabilitation.",
                category="Treatment",
            ),
        ]

    # =====================================================
    # Prediction Explanation
    # =====================================================

    def explain_prediction(
        self,
        prediction_id: int,
    ) -> PredictionExplanation:
        """
        Explain prediction.
        """

        return PredictionExplanation(
            prediction_id=prediction_id,
            prediction="Parkinson Detected",
            confidence=97.8,
            risk_level="High Risk",
            explanation=(
                "The prediction is based on patterns identified "
                "from voice measurements using a machine learning model."
            ),
        )

    # =====================================================
    # Report Explanation
    # =====================================================

    def explain_report(
        self,
        report_id: int,
    ) -> ReportExplanation:
        """
        Explain generated report.
        """

        return ReportExplanation(
            report_id=report_id,
            summary=(
                "The report summarizes prediction results, "
                "recommendations, and follow-up guidance."
            ),
            recommendations=[
                "Consult a neurologist.",
                "Maintain regular exercise.",
                "Follow up as recommended.",
            ],
        )

    # =====================================================
    # Parkinson Information
    # =====================================================

    def parkinson_information(
        self,
    ) -> ParkinsonInformation:
        """
        Educational Parkinson information.
        """

        return ParkinsonInformation(
            definition=(
                "Parkinson disease is a progressive neurological disorder "
                "that primarily affects movement."
            ),
            symptoms=[
                "Tremor",
                "Rigidity",
                "Slowed movement",
                "Balance problems",
            ],
            causes=[
                "Loss of dopamine-producing neurons",
                "Genetic factors",
                "Environmental influences",
            ],
            risk_factors=[
                "Increasing age",
                "Family history",
                "Environmental exposure",
            ],
            diagnosis=[
                "Neurological examination",
                "Medical history",
                "Clinical assessment",
            ],
            treatment=[
                "Medication",
                "Physical therapy",
                "Speech therapy",
                "Exercise",
            ],
            prevention=[
                "Regular physical activity",
                "Healthy diet",
                "Routine medical care",
            ],
            disclaimer=(
                "This information is educational and is not a substitute "
                "for professional medical advice."
            ),
        )

    # =====================================================
    # Status
    # =====================================================

    def status(
        self,
    ) -> ChatbotStatus:
        """
        Return chatbot status.
        """

        return ChatbotStatus(
            status="Online",
            model_name="Parkinson AI Assistant",
            version="1.0.0",
            knowledge_base="Medical Knowledge Base",
        )
