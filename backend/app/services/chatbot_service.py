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
        Initialize chatbot service.

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

        # Store user message
        message = ChatMessage(
            role="user",
            content=request.message,
            timestamp=datetime.utcnow(),
        )

        self._history.setdefault(
            conversation_id,
            []
        ).append(message)

        # Store assistant response
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
        Generate an educational response based on
        the user's message.

        This is a rule-based chatbot.
        It does not provide diagnosis or prescribe treatment.
        """

        text = message.lower().strip()

        # =================================================
        # Greeting
        # =================================================

        if text in {
            "hi",
            "hello",
            "hey",
            "good morning",
            "good afternoon",
            "good evening",
        }:

            return (
                "Hello! 👋 I am the Parkinson Disease "
                "AI Health Assistant.\n\n"
                "I can provide educational information about "
                "Parkinson disease, symptoms, causes, risk factors, "
                "diagnosis, treatment, exercise, prediction results, "
                "and healthy habits.\n\n"
                "How can I help you?"
            )

        # =================================================
        # What is Parkinson Disease?
        # =================================================

        if (
            "what is parkinson" in text
            or "what's parkinson" in text
            or "define parkinson" in text
            or "about parkinson" in text
            or "parkinson disease" in text
            or "parkinson's disease" in text
        ):

            information = self.parkinson_information()

            return (
                f"{information.definition}\n\n"
                f"**Common symptoms:** "
                f"{', '.join(information.symptoms)}.\n\n"
                f"**Diagnosis:** "
                f"{', '.join(information.diagnosis)}.\n\n"
                f"{information.disclaimer}"
            )

        # =================================================
        # Symptoms
        # =================================================

        if (
            "symptom" in text
            or "signs" in text
            or "early signs" in text
            or "early symptoms" in text
        ):

            information = self.parkinson_information()

            return (
                "Common symptoms include:\n\n"
                + "\n".join(
                    f"• {symptom}"
                    for symptom in information.symptoms
                )
                + "\n\n"
                + information.disclaimer
            )

        # =================================================
        # Causes
        # =================================================

        if (
            "cause" in text
            or "causes" in text
            or "why does parkinson" in text
            or "what causes parkinson" in text
        ):

            information = self.parkinson_information()

            return (
                "Factors associated with Parkinson disease "
                "include:\n\n"
                + "\n".join(
                    f"• {cause}"
                    for cause in information.causes
                )
                + "\n\n"
                + information.disclaimer
            )

        # =================================================
        # Risk Factors
        # =================================================

        if (
            "risk factor" in text
            or "risk factors" in text
            or "who is at risk" in text
        ):

            information = self.parkinson_information()

            return (
                "Risk factors include:\n\n"
                + "\n".join(
                    f"• {risk}"
                    for risk in information.risk_factors
                )
                + "\n\n"
                + information.disclaimer
            )

        # =================================================
        # Diagnosis
        # =================================================

        if (
            "diagnos" in text
            or "diagnostic" in text
            or "how is parkinson diagnosed" in text
        ):

            information = self.parkinson_information()

            return (
                "The educational information lists "
                "the following approaches to diagnosis:\n\n"
                + "\n".join(
                    f"• {item}"
                    for item in information.diagnosis
                )
                + "\n\n"
                + information.disclaimer
            )

        # =================================================
        # Treatment
        # =================================================

        if (
            "treatment" in text
            or "treat parkinson" in text
            or "how is parkinson treated" in text
        ):

            information = self.parkinson_information()

            return (
                "The educational information includes:\n\n"
                + "\n".join(
                    f"• {item}"
                    for item in information.treatment
                )
                + "\n\n"
                + information.disclaimer
            )

        # =================================================
        # Exercise
        # =================================================

        if (
            "exercise" in text
            or "physical activity" in text
            or "workout" in text
            or "fitness" in text
        ):

            information = self.parkinson_information()

            return (
                "Exercise and healthy physical activity "
                "are included in the educational information.\n\n"
                + "\n".join(
                    f"• {item}"
                    for item in information.prevention
                )
                + "\n\n"
                + information.disclaimer
            )

        # =================================================
        # High Risk
        # =================================================

        if (
            "high risk" in text
            or "high-risk" in text
        ):

            return (
                "A high-risk prediction means the machine "
                "learning model found patterns associated "
                "with Parkinson disease.\n\n"
                "It is not a diagnosis. A qualified healthcare "
                "professional should evaluate the result "
                "clinically."
            )

        # =================================================
        # Medium Risk
        # =================================================

        if (
            "medium risk" in text
            or "moderate risk" in text
        ):

            return (
                "A medium-risk prediction means the machine "
                "learning model found some patterns associated "
                "with Parkinson disease.\n\n"
                "This result is not a diagnosis and should be "
                "discussed with a qualified healthcare professional."
            )

        # =================================================
        # Low Risk
        # =================================================

        if (
            "low risk" in text
        ):

            return (
                "A low-risk prediction means the machine "
                "learning model found fewer patterns associated "
                "with Parkinson disease.\n\n"
                "A low-risk result does not rule out disease "
                "and should not replace professional medical assessment."
            )

        # =================================================
        # Prediction
        # =================================================

        if (
            "prediction" in text
            or "model result" in text
            or "voice prediction" in text
            or "machine learning result" in text
        ):

            return (
                "The prediction is generated from 22 voice "
                "features using a trained machine learning model.\n\n"
                "The prediction is not a diagnosis and should "
                "be interpreted together with a qualified "
                "healthcare professional's clinical assessment."
            )

        # =================================================
        # Confidence / Accuracy
        # =================================================

        if (
            "confidence" in text
            or "accuracy" in text
            or "accurate" in text
            or "how accurate" in text
        ):

            return (
                "The prediction system reports a confidence "
                "value based on the machine learning model's "
                "output.\n\n"
                "Model confidence should not be interpreted "
                "as a medical diagnosis or as a guarantee that "
                "a person has or does not have Parkinson disease."
            )

        # =================================================
        # Healthy Habits / Prevention
        # =================================================

        if (
            "prevention" in text
            or "prevent parkinson" in text
            or "healthy habits" in text
            or "healthy lifestyle" in text
            or "lifestyle" in text
        ):

            information = self.parkinson_information()

            return (
                "The educational information lists:\n\n"
                + "\n".join(
                    f"• {item}"
                    for item in information.prevention
                )
                + "\n\n"
                + information.disclaimer
            )

        # =================================================
        # Report
        # =================================================

        if (
            "report" in text
            or "medical report" in text
        ):

            return (
                "A report can summarize prediction results, "
                "recommendations, and follow-up guidance.\n\n"
                "If you have questions about a specific medical "
                "report, a qualified healthcare professional should "
                "review and interpret it."
            )

        # =================================================
        # Help
        # =================================================

        if (
            "help" in text
            or "what can you do" in text
            or "what can you answer" in text
        ):

            return (
                "I can help with educational questions about:\n\n"
                "• Parkinson disease\n"
                "• Symptoms\n"
                "• Causes\n"
                "• Risk factors\n"
                "• Diagnosis\n"
                "• Treatment\n"
                "• Exercise\n"
                "• Prediction results\n"
                "• Model confidence\n"
                "• Healthy habits\n"
                "• Reports\n\n"
                "I cannot diagnose a disease or prescribe treatment."
            )

        # =================================================
        # Default Response
        # =================================================

        return (
            "I can answer educational questions about Parkinson "
            "disease, including its symptoms, causes, risk factors, "
            "diagnosis, treatment, exercise, prediction results, "
            "and healthy habits.\n\n"
            "Try asking:\n\n"
            "• What is Parkinson's Disease?\n"
            "• What are the early symptoms?\n"
            "• What causes Parkinson disease?\n"
            "• How is Parkinson disease diagnosed?\n"
            "• How accurate is the prediction?"
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
                len(messages)
                for messages in self._history.values()
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
                description=(
                    "Clinical evaluation and neurological examination."
                ),
                category="Diagnosis",
            ),
            EducationalTopic(
                title="Treatment",
                description=(
                    "Medication, exercise, and rehabilitation."
                ),
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
                "Parkinson disease is a progressive neurological "
                "disorder that primarily affects movement."
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
                "This information is educational and is not a "
                "substitute for professional medical advice."
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
