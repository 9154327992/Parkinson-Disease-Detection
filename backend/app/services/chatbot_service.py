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

    def __init__(self):
        self._history = {}

    # ==========================================================
    # Chat
    # ==========================================================

    def chat(
        self,
        request: ChatRequest,
    ) -> ChatResponse:

        conversation_id = (
            request.conversation_id
            or str(uuid4())
        )

        conversation_history = self._history.get(
            conversation_id,
            [],
        )

        answer = self._generate_response(
            message=request.message,
            history=conversation_history,
        )

        user_message = ChatMessage(
            role="user",
            content=request.message,
            timestamp=datetime.utcnow(),
        )

        self._history.setdefault(
            conversation_id,
            [],
        ).append(
            user_message
        )

        assistant_message = ChatMessage(
            role="assistant",
            content=answer,
            timestamp=datetime.utcnow(),
        )

        self._history[
            conversation_id
        ].append(
            assistant_message
        )

        return ChatResponse(
            conversation_id=conversation_id,
            response=answer,
            sources=[
                "Parkinson Foundation",
                "World Health Organization",
            ],
            suggestions=[
                "What is Parkinson's Disease?",
                "What causes hand tremors?",
                "What are the early symptoms?",
                "How can Parkinson risk be reduced?",
                "Is Parkinson curable?",
                "How is Parkinson diagnosed?",
                "What foods are recommended?",
                "Which exercises are beneficial?",
                "How can stress be reduced?",
                "Explain Bradykinesia.",
                "Explain Voice Disorders.",
            ],
            timestamp=datetime.utcnow(),
        )

    # ==========================================================
    # Conversation Context
    # ==========================================================

    def _get_context(
        self,
        history,
    ) -> str:

        messages = []

        for message in history[-8:]:

            content = getattr(
                message,
                "content",
                "",
            )

            if content:

                messages.append(
                    str(content).lower()
                )

        return " ".join(
            messages
        )

    # ==========================================================
    # Generate Response
    # ==========================================================

    def _generate_response(
        self,
        message: str,
        history=None,
    ) -> str:

        text = str(
            message or ""
        ).lower().strip()

        history = history or []

        context = self._get_context(
            history
        )

        if not text:

            return (
                "Please enter a question about Parkinson disease "
                "or another supported health topic."
            )

        # ======================================================
        # Greeting
        # ======================================================

        if text in {
            "hi",
            "hello",
            "hey",
            "hiya",
            "good morning",
            "good afternoon",
            "good evening",
        }:

            return (
                "Hello! 👋 I am the Parkinson Disease "
                "AI Health Assistant.\n\n"
                "I can provide educational information about "
                "Parkinson disease, symptoms, causes, risk factors, "
                "diagnosis, treatment, exercise, nutrition, "
                "stress, sleep, voice changes, and healthy habits.\n\n"
                "How can I help you?"
            )

        # ======================================================
        # Prevention / Risk Reduction
        # ======================================================

        prevention_keywords = [

            "prevent",
            "prevention",
            "preventing",

            "avoid parkinson",
            "avoid the disease",
            "avoid it",

            "reduce risk",
            "reduce the risk",

            "lower risk",
            "lower the risk",

            "how to avoid",
            "how can i avoid",

            "how to prevent",
            "how can i prevent",

            "can it be prevented",
            "can this be prevented",

            "can parkinson be prevented",
            "is parkinson preventable",

            "how to prevent it",
            "how can i prevent it",

            "what can i do to prevent",
        ]

        if any(
            keyword in text
            for keyword in prevention_keywords
        ):

            information = (
                self.parkinson_information()
            )

            return (
                "There is currently no guaranteed way to prevent "
                "Parkinson disease. However, healthy lifestyle "
                "practices can support overall health and may help "
                "reduce some risk factors.\n\n"

                "**Healthy practices include:**\n\n"

                "• **Regular physical activity**\n"
                "  Regular movement and exercise can support "
                "general health and mobility.\n\n"

                "• **A balanced diet**\n"
                "  Eating a varied and nutritious diet can support "
                "overall health.\n\n"

                "• **Good sleep and stress management**\n"
                "  Maintaining healthy sleep habits and managing "
                "stress can support general well-being.\n\n"

                "• **Routine medical care**\n"
                "  Regular healthcare visits can help identify and "
                "address health concerns.\n\n"

                "These measures do not guarantee that Parkinson "
                "disease will be prevented.\n\n"

                + information.disclaimer
            )

        # ======================================================
        # Follow-up prevention question
        # ======================================================

        if (
            "parkinson" in context
            and (
                "prevent it" in text
                or "avoid it" in text
                or "reduce its risk" in text
            )
        ):

            information = (
                self.parkinson_information()
            )

            return (
                "If you are referring to Parkinson disease, there "
                "is currently no guaranteed way to prevent it. "
                "However, regular exercise, a balanced diet, "
                "healthy sleep habits, stress management, and "
                "routine medical care can support overall health.\n\n"

                "These practices do not guarantee prevention.\n\n"

                + information.disclaimer
            )

        # ======================================================
        # What is Parkinson Disease?
        # ======================================================

        if (
            "what is parkinson" in text
            or "what's parkinson" in text
            or "define parkinson" in text
            or "tell me about parkinson" in text
            or (
                (
                    "parkinson disease" in text
                    or "parkinson's disease" in text
                )
                and len(text.split()) <= 7
            )
        ):

            information = (
                self.parkinson_information()
            )

            return (
                f"{information.definition}\n\n"

                "**Common symptoms:**\n"

                + "\n".join(
                    f"• {symptom}"
                    for symptom
                    in information.symptoms
                )

                + "\n\n"

                + information.disclaimer
            )

        # ======================================================
        # Tremors
        # ======================================================

        if any(
            keyword in text
            for keyword in [
                "hand tremor",
                "hand tremors",
                "my hands shake",
                "hands shake",
                "shaking hands",
                "tremor",
                "tremors",
                "shaking",
            ]
        ):

            return (
                "Hand tremors can have several possible causes. "
                "They may occur with conditions such as Parkinson "
                "disease or essential tremor and can also be "
                "associated with medication effects, stress, "
                "anxiety, caffeine use, or other medical conditions.\n\n"

                "A tremor alone does not establish a diagnosis. "
                "Persistent or worsening tremors should be evaluated "
                "by a qualified healthcare professional.\n\n"

                "This information is educational and is not a "
                "substitute for professional medical advice."
            )

        # ======================================================
        # Early Symptoms
        # ======================================================

        if any(
            keyword in text
            for keyword in [
                "early symptom",
                "early symptoms",
                "early signs",
                "first symptoms",
                "initial symptoms",
                "symptoms of parkinson",
            ]
        ):

            information = (
                self.parkinson_information()
            )

            return (
                "Common symptoms associated with Parkinson "
                "disease include:\n\n"

                + "\n".join(
                    f"• {symptom}"
                    for symptom
                    in information.symptoms
                )

                + "\n\n"

                "Symptoms can vary between individuals. "
                "Persistent or concerning symptoms should be "
                "evaluated by a healthcare professional.\n\n"

                + information.disclaimer
            )

        # ======================================================
        # Bradykinesia
        # ======================================================

        if any(
            keyword in text
            for keyword in [
                "bradykinesia",
                "slow movement",
                "slowness of movement",
            ]
        ):

            return (
                "**Bradykinesia** means slowness of movement. "
                "It is one of the movement-related features "
                "associated with Parkinson disease.\n\n"

                "It can make everyday activities take longer and "
                "may affect walking, getting up, dressing, writing, "
                "or other fine-motor activities.\n\n"

                "Persistent movement changes should be evaluated "
                "by a qualified healthcare professional."
            )

        # ======================================================
        # Rigidity
        # ======================================================

        if any(
            keyword in text
            for keyword in [
                "rigidity",
                "muscle stiffness",
                "stiff muscles",
                "stiffness",
            ]
        ):

            return (
                "Rigidity refers to stiffness or resistance when "
                "a limb or joint is moved. It can occur as a "
                "movement-related symptom in Parkinson disease.\n\n"

                "Persistent stiffness can have many causes and "
                "should be evaluated by a healthcare professional."
            )

        # ======================================================
        # Balance
        # ======================================================

        if any(
            keyword in text
            for keyword in [
                "balance problem",
                "balance problems",
                "postural instability",
                "falling",
                "falls",
            ]
        ):

            return (
                "Balance difficulties can occur in Parkinson "
                "disease and may increase the risk of falls.\n\n"

                "Balance problems can also have many other causes. "
                "A healthcare professional can help evaluate "
                "persistent balance difficulties."
            )

        # ======================================================
        # Walking
        # ======================================================

        if any(
            keyword in text
            for keyword in [
                "walking problem",
                "walking problems",
                "difficulty walking",
                "walking difficulty",
                "freezing",
                "shuffling",
            ]
        ):

            return (
                "Parkinson disease can affect walking and movement. "
                "Some people may experience slower walking, shorter "
                "steps, shuffling, or freezing of gait.\n\n"

                "Persistent mobility problems should be assessed "
                "by a healthcare professional."
            )

        # ======================================================
        # Voice / Speech
        # ======================================================

        if any(
            keyword in text
            for keyword in [
                "voice disorder",
                "voice disorders",
                "voice problem",
                "voice problems",
                "speech problem",
                "speech problems",
                "voice change",
                "voice changes",
                "soft voice",
                "speech changes",
            ]
        ):

            return (
                "Voice and speech changes can occur in Parkinson "
                "disease. Some people may experience a softer voice, "
                "reduced vocal intensity, or changes in speech clarity.\n\n"

                "Persistent voice or speech changes should be "
                "evaluated by an appropriate healthcare professional."
            )

        # ======================================================
        # Causes
        # ======================================================

        if any(
            keyword in text
            for keyword in [
                "what causes parkinson",
                "causes of parkinson",
                "cause of parkinson",
                "why does parkinson happen",
                "why do people get parkinson",
            ]
        ):

            information = (
                self.parkinson_information()
            )

            return (
                "Factors associated with Parkinson disease include:\n\n"

                + "\n".join(
                    f"• {cause}"
                    for cause
                    in information.causes
                )

                + "\n\n"

                + information.disclaimer
            )

        # ======================================================
        # Risk Factors
        # ======================================================

        if any(
            keyword in text
            for keyword in [
                "risk factor",
                "risk factors",
                "who is at risk",
                "risk of parkinson",
            ]
        ):

            information = (
                self.parkinson_information()
            )

            return (
                "Risk factors associated with Parkinson disease "
                "include:\n\n"

                + "\n".join(
                    f"• {risk}"
                    for risk
                    in information.risk_factors
                )

                + "\n\n"

                + information.disclaimer
            )

        # ======================================================
        # Diagnosis
        # ======================================================

        if any(
            keyword in text
            for keyword in [
                "how is parkinson diagnosed",
                "how to diagnose parkinson",
                "diagnosis of parkinson",
                "diagnose parkinson",
                "diagnostic test",
                "parkinson diagnosis",
            ]
        ):

            information = (
                self.parkinson_information()
            )

            return (
                "Parkinson disease diagnosis generally involves:\n\n"

                + "\n".join(
                    f"• {item}"
                    for item
                    in information.diagnosis
                )

                + "\n\n"

                "Diagnosis should be performed by a qualified "
                "healthcare professional.\n\n"

                + information.disclaimer
            )

        # ======================================================
        # Cure
        # ======================================================

        if any(
            keyword in text
            for keyword in [
                "is parkinson curable",
                "can parkinson be cured",
                "can parkinson's be cured",
                "cure for parkinson",
                "is there a cure for parkinson",
            ]
        ):

            return (
                "Parkinson disease currently does not have a "
                "definitive cure. However, treatment and "
                "rehabilitation can help manage symptoms and "
                "support quality of life.\n\n"

                "Treatment decisions should be made with qualified "
                "healthcare professionals."
            )

        # ======================================================
        # Treatment
        # ======================================================

        if any(
            keyword in text
            for keyword in [
                "treatment for parkinson",
                "treat parkinson",
                "how is parkinson treated",
                "parkinson treatment",
                "treatments for parkinson",
            ]
        ):

            information = (
                self.parkinson_information()
            )

            return (
                "Educational treatment approaches include:\n\n"

                + "\n".join(
                    f"• {item}"
                    for item
                    in information.treatment
                )

                + "\n\n"

                + information.disclaimer
            )

        # ======================================================
        # Medication
        # ======================================================

        if any(
            keyword in text
            for keyword in [
                "medication",
                "medications",
                "medicine",
                "medicines",
            ]
        ):

            return (
                "Medication can be part of Parkinson disease "
                "management, but the appropriate medication and "
                "dose depend on the individual.\n\n"

                "Medication should only be started, stopped, or "
                "changed under the guidance of a qualified "
                "healthcare professional."
            )

        # ======================================================
        # Food / Nutrition
        # ======================================================

        if any(
            keyword in text
            for keyword in [
                "food",
                "foods",
                "diet",
                "nutrition",
                "what should i eat",
                "what can i eat",
            ]
        ):

            return (
                "A balanced and nutritious diet can support "
                "general health.\n\n"

                "Healthy eating can include a variety of "
                "nutrient-rich foods, fruits, vegetables, whole "
                "grains, protein, and adequate hydration.\n\n"

                "Specific dietary changes should be discussed with "
                "a qualified healthcare professional or dietitian."
            )

        # ======================================================
        # Exercise
        # ======================================================

        if any(
            keyword in text
            for keyword in [
                "exercise",
                "physical activity",
                "workout",
                "fitness",
                "which exercises",
            ]
        ):

            return (
                "Regular physical activity can support mobility "
                "and general health.\n\n"

                "Examples may include:\n\n"

                "• Walking\n"
                "• Stretching\n"
                "• Balance exercises\n"
                "• Strength exercises\n"
                "• Physical therapy exercises\n\n"

                "The most appropriate exercise program depends on "
                "the person's health and abilities."
            )

        # ======================================================
        # Stress
        # ======================================================

        if any(
            keyword in text
            for keyword in [
                "stress",
                "anxiety",
                "reduce stress",
                "manage stress",
                "relax",
            ]
        ):

            return (
                "Stress management may include:\n\n"

                "• Regular physical activity\n"
                "• Adequate sleep\n"
                "• Relaxation or breathing exercises\n"
                "• Social support\n"
                "• Maintaining regular routines\n\n"

                "Professional support may be helpful when stress "
                "or anxiety significantly affects daily life."
            )

        # ======================================================
        # Sleep
        # ======================================================

        if any(
            keyword in text
            for keyword in [
                "sleep",
                "insomnia",
                "sleep problem",
                "sleep problems",
                "difficulty sleeping",
            ]
        ):

            return (
                "Sleep difficulties can occur for many reasons.\n\n"

                "Helpful general practices may include maintaining "
                "a regular sleep schedule and discussing persistent "
                "sleep problems with a healthcare professional."
            )

        # ======================================================
        # Prediction
        # ======================================================

        if any(
            keyword in text
            for keyword in [
                "prediction",
                "model result",
                "voice prediction",
                "machine learning result",
            ]
        ):

            return (
                "The prediction is generated from voice features "
                "using a trained machine-learning model.\n\n"

                "The prediction is not a medical diagnosis and "
                "should be interpreted with appropriate clinical "
                "assessment."
            )

        # ======================================================
        # Confidence
        # ======================================================

        if any(
            keyword in text
            for keyword in [
                "confidence",
                "accuracy",
                "accurate",
                "how accurate",
            ]
        ):

            return (
                "The prediction system reports a confidence value "
                "based on the machine-learning model output.\n\n"

                "Confidence should not be interpreted as a medical "
                "diagnosis or a guarantee."
            )

        # ======================================================
        # Help
        # ======================================================

        if any(
            keyword in text
            for keyword in [
                "help",
                "what can you do",
                "what can you answer",
                "topics",
            ]
        ):

            return (
                "I can help with educational questions about:\n\n"

                "• Parkinson disease\n"
                "• Tremors\n"
                "• Early symptoms\n"
                "• Bradykinesia\n"
                "• Rigidity\n"
                "• Balance and walking\n"
                "• Voice and speech changes\n"
                "• Causes and risk factors\n"
                "• Prevention and healthy habits\n"
                "• Diagnosis\n"
                "• Treatment\n"
                "• Medication\n"
                "• Nutrition\n"
                "• Exercise\n"
                "• Stress and anxiety\n"
                "• Sleep\n"
                "• Prediction results"
            )

        # ======================================================
        # Follow-up question
        # ======================================================

        if (
            any(
                word in text
                for word in [
                    "it",
                    "this",
                    "that",
                ]
            )
            and "parkinson" in context
        ):

            return (
                "I understand you may be referring to Parkinson "
                "disease. Please tell me what you would like to "
                "know about it.\n\n"

                "For example:\n"
                "• Symptoms\n"
                "• Prevention\n"
                "• Causes\n"
                "• Diagnosis\n"
                "• Treatment\n"
                "• Exercise or diet"
            )

        # ======================================================
        # Default
        # ======================================================

        return (
            "I can answer educational questions about Parkinson "
            "disease, including symptoms, causes, risk factors, "
            "prevention, diagnosis, treatment, exercise, nutrition, "
            "stress, sleep, and voice changes.\n\n"

            "Try asking:\n\n"

            "• What is Parkinson's Disease?\n"
            "• What are the early symptoms?\n"
            "• How can Parkinson risk be reduced?\n"
            "• Is Parkinson curable?\n"
            "• How is Parkinson diagnosed?"
        )

    # ==========================================================
    # Conversation History
    # ==========================================================

    def get_history(
        self,
        user_id=None,
    ) -> ChatHistoryResponse:

        conversations = []

        for conversation_id, messages in (
            self._history.items()
        ):

            conversations.append(
                ConversationHistory(
                    conversation_id=conversation_id,
                    messages=messages,
                )
            )

        return ChatHistoryResponse(
            total_messages=sum(
                len(messages)
                for messages
                in self._history.values()
            ),
            conversations=conversations,
        )

    def history(
        self,
        user_id=None,
    ) -> ChatHistoryResponse:

        return self.get_history(
            user_id=user_id
        )

    # ==========================================================
    # Clear History
    # ==========================================================

    def clear_history(
        self,
        user_id=None,
    ) -> ClearChatResponse:

        self._history.clear()

        return ClearChatResponse(
            message="Chat history cleared."
        )

    # ==========================================================
    # Suggested Questions
    # ==========================================================

    def suggested_questions(
        self,
    ) -> list[SuggestedQuestion]:

        questions = [

            (
                "What is Parkinson's Disease?",
                "General",
            ),

            (
                "What causes hand tremors?",
                "Symptoms",
            ),

            (
                "What are the early symptoms?",
                "Symptoms",
            ),

            (
                "How can Parkinson risk be reduced?",
                "Prevention",
            ),

            (
                "Is Parkinson curable?",
                "Treatment",
            ),

            (
                "How is Parkinson diagnosed?",
                "Diagnosis",
            ),

            (
                "What foods are recommended?",
                "Nutrition",
            ),

            (
                "Which exercises are beneficial?",
                "Exercise",
            ),

            (
                "How can stress be reduced?",
                "Lifestyle",
            ),

            (
                "Explain Bradykinesia.",
                "Symptoms",
            ),
        ]

        return [

            SuggestedQuestion(
                id=index,
                question=question,
                category=category,
            )

            for index, (
                question,
                category,
            ) in enumerate(
                questions,
                start=1,
            )
        ]

    def suggestions(
        self,
    ) -> list[SuggestedQuestion]:

        return self.suggested_questions()

    # ==========================================================
    # FAQ
    # ==========================================================

    def faq(
        self,
    ) -> list[FAQItem]:

        return [

            FAQItem(
                question=(
                    "Can this system diagnose Parkinson disease?"
                ),
                answer=(
                    "No. The system provides a machine-learning "
                    "prediction and does not replace professional "
                    "medical evaluation."
                ),
            ),

            FAQItem(
                question=(
                    "Can Parkinson disease be prevented?"
                ),
                answer=(
                    "There is currently no guaranteed way to prevent "
                    "Parkinson disease. Healthy lifestyle practices "
                    "may support overall health."
                ),
            ),

            FAQItem(
                question=(
                    "Is Parkinson disease curable?"
                ),
                answer=(
                    "Parkinson disease currently does not have a "
                    "definitive cure, although treatments can help "
                    "manage symptoms."
                ),
            ),
        ]

    # ==========================================================
    # Educational Topics
    # ==========================================================

    def educational_topics(
        self,
    ) -> list[EducationalTopic]:

        return [

            EducationalTopic(
                title="Parkinson Disease",
                description=(
                    "General information about Parkinson disease."
                ),
                category="Disease",
            ),

            EducationalTopic(
                title="Symptoms",
                description=(
                    "Motor and non-motor symptoms."
                ),
                category="Disease",
            ),

            EducationalTopic(
                title="Prevention",
                description=(
                    "Risk reduction and healthy lifestyle practices."
                ),
                category="Lifestyle",
            ),

            EducationalTopic(
                title="Diagnosis",
                description=(
                    "Clinical evaluation and neurological assessment."
                ),
                category="Diagnosis",
            ),

            EducationalTopic(
                title="Treatment",
                description=(
                    "Medication, rehabilitation, and exercise."
                ),
                category="Treatment",
            ),
        ]

    # ==========================================================
    # Prediction Explanation
    # ==========================================================

    def explain_prediction(
        self,
        prediction_id: int,
    ) -> PredictionExplanation:

        return PredictionExplanation(
            prediction_id=prediction_id,
            prediction="Prediction Result",
            confidence=0.0,
            risk_level="Unknown",
            explanation=(
                "The prediction should be interpreted together "
                "with the actual patient record and clinical "
                "assessment."
            ),
        )

    # ==========================================================
    # Report Explanation
    # ==========================================================

    def explain_report(
        self,
        report_id: int,
    ) -> ReportExplanation:

        return ReportExplanation(
            report_id=report_id,
            summary=(
                "The report summarizes prediction results, "
                "recommendations, and follow-up guidance."
            ),
            recommendations=[
                "Consult a qualified healthcare professional.",
                "Maintain healthy lifestyle practices.",
                "Follow up as medically recommended.",
            ],
        )

    # ==========================================================
    # Parkinson Information
    # ==========================================================

    def parkinson_information(
        self,
    ) -> ParkinsonInformation:

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
                "Good sleep and stress management",
                "Routine medical care",
            ],

            disclaimer=(
                "This information is educational and is not a "
                "substitute for professional medical advice."
            ),
        )

    # ==========================================================
    # Status
    # ==========================================================

    def status(
        self,
    ) -> ChatbotStatus:

        return ChatbotStatus(
            status="Online",
            model_name="Parkinson AI Assistant",
            version="1.1.0",
            knowledge_base="Medical Knowledge Base",
        )
