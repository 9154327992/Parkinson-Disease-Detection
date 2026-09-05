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

        history = self._history.get(
            conversation_id,
            [],
        )

        answer = self._generate_response(
            message=request.message,
            history=history,
        )

        user_message = ChatMessage(
            role="user",
            content=request.message,
            timestamp=datetime.utcnow(),
        )

        assistant_message = ChatMessage(
            role="assistant",
            content=answer,
            timestamp=datetime.utcnow(),
        )

        self._history.setdefault(
            conversation_id,
            [],
        )

        self._history[
            conversation_id
        ].append(
            user_message
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
                "What is Parkinson's disease?",
                "What are the early symptoms?",
                "How can Parkinson risk be reduced?",
                "Is Parkinson's disease curable?",
                "How is Parkinson's disease diagnosed?",
                "What foods support a healthy lifestyle?",
                "Which exercises may be beneficial?",
                "How can stress be managed?",
                "What is bradykinesia?",
                "What are Parkinson's-related voice changes?",
            ],
            timestamp=datetime.utcnow(),
        )

    # ==========================================================
    # Context
    # ==========================================================

    def _get_context(
        self,
        history,
    ) -> str:

        if not history:
            return ""

        messages = []

        for message in history[-10:]:

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
    # Helpers
    # ==========================================================

    def _contains_any(
        self,
        text: str,
        keywords,
    ) -> bool:

        return any(
            keyword in text
            for keyword in keywords
        )

    def _disclaimer(
        self,
    ) -> str:

        return (
            "This information is educational and is not a "
            "substitute for professional medical advice."
        )

    # ==========================================================
    # Response Generation
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
                "Please enter a question about Parkinson's disease "
                "or another supported health topic."
            )

        # ======================================================
        # Greeting
        # ======================================================

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
                "Parkinson's disease, symptoms, causes, risk "
                "factors, diagnosis, treatment, exercise, "
                "nutrition, sleep, stress, movement, and "
                "voice changes.\n\n"
                "How can I help you?"
            )

        # ======================================================
        # CURABILITY
        #
        # IMPORTANT:
        # This must appear BEFORE the generic Parkinson rule.
        # ======================================================

        if self._contains_any(
            text,
            [
                "curable",
                "cure parkinson",
                "cure for parkinson",
                "can parkinson be cured",
                "is there a cure",
            ],
        ):

            return (
                "**Parkinson's disease currently does not have "
                "a definitive cure.**\n\n"
                "However, treatments and rehabilitation can help "
                "manage symptoms and support quality of life. "
                "Treatment may include medication, exercise, "
                "physical therapy, speech therapy, and other "
                "support depending on the individual's needs.\n\n"
                + self._disclaimer()
            )

        # ======================================================
        # PREVENTION / RISK REDUCTION
        # ======================================================

        if self._contains_any(
            text,
            [
                "prevent",
                "prevention",
                "preventing",
                "reduce risk",
                "reduce the risk",
                "risk be reduced",
                "lower risk",
                "avoid parkinson",
                "avoid the disease",
                "how can i avoid",
                "how to avoid",
                "how can i prevent",
                "how to prevent",
                "can it be prevented",
                "can parkinson be prevented",
                "is parkinson preventable",
                "prevent it",
                "avoid it",
                "reduce its risk",
            ],
        ):

            return (
                "There is currently **no guaranteed way to prevent "
                "Parkinson's disease**. However, healthy lifestyle "
                "practices can support overall health and may help "
                "reduce certain risk factors.\n\n"

                "**Healthy practices include:**\n\n"

                "• **Regular physical activity** — supports "
                "general health, mobility, and physical fitness.\n\n"

                "• **A balanced diet** — supports overall health "
                "and nutritional well-being.\n\n"

                "• **Good sleep** — healthy sleep habits support "
                "general physical and mental well-being.\n\n"

                "• **Stress management** — relaxation, exercise, "
                "and social support may help manage stress.\n\n"

                "• **Routine medical care** — regular healthcare "
                "visits can help identify health concerns.\n\n"

                "These practices do not guarantee that Parkinson's "
                "disease will be prevented.\n\n"

                + self._disclaimer()
            )

        # ======================================================
        # DIAGNOSIS
        # ======================================================

        if self._contains_any(
            text,
            [
                "diagnosed",
                "diagnosis",
                "diagnose parkinson",
                "diagnostic test",
                "how is parkinson diagnosed",
            ],
        ):

            return (
                "Parkinson's disease is generally diagnosed through "
                "a clinical evaluation rather than one single test.\n\n"

                "**The assessment may include:**\n\n"

                "• Medical history\n"
                "• Review of symptoms\n"
                "• Neurological examination\n"
                "• Assessment of movement and balance\n"
                "• Additional tests when needed to rule out "
                "other conditions\n\n"

                "Diagnosis should be made by a qualified healthcare "
                "professional.\n\n"

                + self._disclaimer()
            )

        # ======================================================
        # EARLY SYMPTOMS
        # ======================================================

        if self._contains_any(
            text,
            [
                "early symptom",
                "early symptoms",
                "early sign",
                "early signs",
                "first symptoms",
                "warning signs",
            ],
        ):

            return (
                "**Early symptoms associated with Parkinson's "
                "disease may include:**\n\n"

                "• Tremor or shaking\n"
                "• Slowed movement\n"
                "• Muscle stiffness or rigidity\n"
                "• Changes in walking or posture\n"
                "• Reduced facial expression\n"
                "• Softer voice or speech changes\n"
                "• Changes in handwriting\n\n"

                "Symptoms vary between individuals and these "
                "symptoms can also occur with other conditions.\n\n"

                + self._disclaimer()
            )

        # ======================================================
        # CAUSES
        # ======================================================

        if self._contains_any(
            text,
            [
                "what causes parkinson",
                "causes of parkinson",
                "cause of parkinson",
                "why does parkinson happen",
                "why do people get parkinson",
            ],
        ):

            return (
                "The exact cause of Parkinson's disease is not "
                "fully understood. It is thought to involve a "
                "combination of factors.\n\n"

                "**Factors associated with Parkinson's disease "
                "may include:**\n\n"

                "• Changes involving dopamine-producing neurons\n"
                "• Genetic factors\n"
                "• Environmental influences\n"
                "• Increasing age\n\n"

                "Having a risk factor does not mean a person will "
                "develop Parkinson's disease.\n\n"

                + self._disclaimer()
            )

        # ======================================================
        # RISK FACTORS
        # ======================================================

        if self._contains_any(
            text,
            [
                "risk factor",
                "risk factors",
                "who is at risk",
                "risk of parkinson",
            ],
        ):

            return (
                "Factors associated with a higher risk of "
                "Parkinson's disease can include:\n\n"

                "• Increasing age\n"
                "• Family history in some cases\n"
                "• Certain environmental influences\n\n"

                "Risk factors do not guarantee that a person will "
                "develop the disease.\n\n"

                + self._disclaimer()
            )

        # ======================================================
        # TREATMENT
        # ======================================================

        if self._contains_any(
            text,
            [
                "treatment for parkinson",
                "treatments for parkinson",
                "how is parkinson treated",
                "parkinson treatment",
            ],
        ):

            return (
                "Parkinson's disease management may include a "
                "combination of approaches depending on the "
                "individual's symptoms and needs.\n\n"

                "**Approaches may include:**\n\n"

                "• Medication\n"
                "• Physical therapy\n"
                "• Exercise and movement programs\n"
                "• Speech and communication therapy\n"
                "• Occupational therapy\n"
                "• Other supportive care\n\n"

                "Treatment should be planned with qualified "
                "healthcare professionals."
            )

        # ======================================================
        # MEDICATION
        # ======================================================

        if self._contains_any(
            text,
            [
                "medication",
                "medications",
                "medicine",
                "medicines",
            ],
        ):

            return (
                "Medication can be an important part of managing "
                "Parkinson's disease symptoms. The appropriate "
                "medication and dose depend on the individual.\n\n"

                "Do not start, stop, or change medication without "
                "guidance from a qualified healthcare professional."
            )

        # ======================================================
        # TREMORS
        # ======================================================

        if self._contains_any(
            text,
            [
                "tremor",
                "tremors",
                "hand shake",
                "hands shake",
                "shaking hands",
            ],
        ):

            return (
                "Tremors can have several possible causes. They may "
                "occur with Parkinson's disease or other conditions "
                "and can also be associated with stress, anxiety, "
                "caffeine, medication effects, or other medical "
                "conditions.\n\n"

                "A tremor alone does not establish a diagnosis. "
                "Persistent or worsening tremors should be evaluated "
                "by a healthcare professional.\n\n"

                + self._disclaimer()
            )

        # ======================================================
        # BRADYKINESIA
        # ======================================================

        if self._contains_any(
            text,
            [
                "bradykinesia",
                "slow movement",
                "slowness of movement",
            ],
        ):

            return (
                "**Bradykinesia** means slowness of movement. "
                "It is one of the movement-related features "
                "associated with Parkinson's disease.\n\n"

                "It may affect activities such as walking, getting "
                "up, dressing, writing, and other everyday tasks.\n\n"

                + self._disclaimer()
            )

        # ======================================================
        # RIGIDITY
        # ======================================================

        if self._contains_any(
            text,
            [
                "rigidity",
                "muscle stiffness",
                "stiff muscles",
            ],
        ):

            return (
                "Rigidity refers to increased muscle stiffness or "
                "resistance during movement. It can occur as a "
                "movement-related symptom associated with "
                "Parkinson's disease.\n\n"

                "Persistent stiffness can have many causes and "
                "should be assessed by a healthcare professional."
            )

        # ======================================================
        # WALKING / BALANCE
        # ======================================================

        if self._contains_any(
            text,
            [
                "balance problem",
                "balance problems",
                "walking problem",
                "walking problems",
                "difficulty walking",
                "freezing",
                "shuffling",
                "falling",
                "falls",
            ],
        ):

            return (
                "Parkinson's disease can affect walking and balance. "
                "Some people may experience slower movement, shorter "
                "steps, shuffling, freezing of gait, or balance "
                "difficulties.\n\n"

                "Persistent balance or mobility problems should be "
                "evaluated by a healthcare professional."
            )

        # ======================================================
        # VOICE / SPEECH
        # ======================================================

        if self._contains_any(
            text,
            [
                "voice",
                "speech",
                "voice disorder",
                "voice changes",
                "soft voice",
            ],
        ):

            return (
                "Parkinson's disease can sometimes affect voice and "
                "speech. Changes may include reduced vocal volume, "
                "a softer voice, or changes in speech clarity.\n\n"

                "Persistent voice or speech changes should be "
                "evaluated by an appropriate healthcare professional."
            )

        # ======================================================
        # EXERCISE
        # ======================================================

        if self._contains_any(
            text,
            [
                "exercise",
                "exercises",
                "physical activity",
                "workout",
                "fitness",
            ],
        ):

            return (
                "Regular physical activity can support general "
                "health and mobility.\n\n"

                "**Examples may include:**\n\n"

                "• Walking\n"
                "• Stretching\n"
                "• Balance exercises\n"
                "• Strength exercises\n"
                "• Physical therapy exercises\n\n"

                "The most suitable exercise program depends on the "
                "person's health and physical abilities."
            )

        # ======================================================
        # FOOD / NUTRITION
        # ======================================================

        if self._contains_any(
            text,
            [
                "food",
                "foods",
                "diet",
                "nutrition",
                "eat",
            ],
        ):

            return (
                "A balanced and nutritious diet can support general "
                "health.\n\n"

                "Healthy eating may include a variety of:\n\n"

                "• Fruits and vegetables\n"
                "• Whole grains\n"
                "• Protein-rich foods\n"
                "• Adequate fluids\n\n"

                "Specific dietary advice should be discussed with a "
                "qualified healthcare professional or dietitian."
            )

        # ======================================================
        # STRESS
        # ======================================================

        if self._contains_any(
            text,
            [
                "stress",
                "anxiety",
                "relax",
                "reduce stress",
                "manage stress",
            ],
        ):

            return (
                "General stress-management strategies may include:\n\n"

                "• Regular physical activity\n"
                "• Adequate sleep\n"
                "• Relaxation or breathing exercises\n"
                "• Maintaining routines\n"
                "• Social support\n\n"

                "Professional support may be helpful when stress or "
                "anxiety significantly affects daily life."
            )

        # ======================================================
        # SLEEP
        # ======================================================

        if self._contains_any(
            text,
            [
                "sleep",
                "insomnia",
                "difficulty sleeping",
            ],
        ):

            return (
                "Sleep difficulties can occur for many reasons.\n\n"

                "General healthy sleep practices may include keeping "
                "a regular sleep schedule and discussing persistent "
                "sleep problems with a healthcare professional."
            )

        # ======================================================
        # PREDICTION
        # ======================================================

        if self._contains_any(
            text,
            [
                "prediction",
                "model result",
                "voice prediction",
                "machine learning",
            ],
        ):

            return (
                "The prediction in this system is generated from "
                "voice measurements using a machine-learning model.\n\n"

                "It is not a medical diagnosis and should be "
                "interpreted together with appropriate clinical "
                "evaluation."
            )

        # ======================================================
        # GENERIC "WHAT IS PARKINSON?"
        #
        # This is intentionally near the end so that specific
        # questions are handled first.
        # ======================================================

        if (
            "what is parkinson" in text
            or "what's parkinson" in text
            or "define parkinson" in text
            or text in {
                "parkinson",
                "parkinson disease",
                "parkinson's disease",
            }
        ):

            return (
                "Parkinson's disease is a progressive neurological "
                "disorder that primarily affects movement.\n\n"

                "**Common symptoms can include:**\n\n"

                "• Tremor\n"
                "• Rigidity or muscle stiffness\n"
                "• Slowed movement\n"
                "• Balance problems\n"
                "• Changes in walking\n"
                "• Voice or speech changes\n\n"

                + self._disclaimer()
            )

        # ======================================================
        # HELP
        # ======================================================

        if self._contains_any(
            text,
            [
                "help",
                "what can you do",
                "what can you answer",
                "topics",
            ],
        ):

            return (
                "I can help with educational questions about:\n\n"

                "• Parkinson's disease\n"
                "• Symptoms and early signs\n"
                "• Tremors and bradykinesia\n"
                "• Causes and risk factors\n"
                "• Prevention and healthy habits\n"
                "• Diagnosis and treatment\n"
                "• Exercise and nutrition\n"
                "• Stress and sleep\n"
                "• Voice and speech changes\n"
                "• Prediction results"
            )

        # ======================================================
        # DEFAULT
        # ======================================================

        return (
            "I can provide educational information about "
            "Parkinson's disease and related topics.\n\n"

            "**You can ask about:**\n\n"

            "• Symptoms\n"
            "• Causes and risk factors\n"
            "• Prevention and healthy habits\n"
            "• Diagnosis\n"
            "• Treatment\n"
            "• Exercise\n"
            "• Nutrition\n"
            "• Stress and sleep\n"
            "• Voice and speech changes\n\n"

            "For example: **Is Parkinson's disease curable?**"
        )

    # ==========================================================
    # History
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
    # Suggestions
    # ==========================================================

    def suggested_questions(
        self,
    ) -> list[SuggestedQuestion]:

        questions = [
            (
                "What is Parkinson's disease?",
                "General",
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
                "Is Parkinson's disease curable?",
                "Treatment",
            ),
            (
                "How is Parkinson's disease diagnosed?",
                "Diagnosis",
            ),
            (
                "What foods support a healthy lifestyle?",
                "Nutrition",
            ),
            (
                "Which exercises may be beneficial?",
                "Exercise",
            ),
            (
                "How can stress be managed?",
                "Lifestyle",
            ),
            (
                "What is bradykinesia?",
                "Symptoms",
            ),
            (
                "What are Parkinson's-related voice changes?",
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
                    "Can this system diagnose Parkinson's disease?"
                ),
                answer=(
                    "No. The system provides educational "
                    "information and machine-learning predictions. "
                    "It does not replace professional medical "
                    "evaluation."
                ),
            ),
            FAQItem(
                question=(
                    "Can Parkinson's disease be prevented?"
                ),
                answer=(
                    "There is currently no guaranteed way to "
                    "prevent Parkinson's disease. Healthy lifestyle "
                    "practices can support overall health."
                ),
            ),
            FAQItem(
                question=(
                    "Is Parkinson's disease curable?"
                ),
                answer=(
                    "Parkinson's disease currently does not have a "
                    "definitive cure, although treatment can help "
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
                title="Parkinson's Disease",
                description=(
                    "General educational information about "
                    "Parkinson's disease."
                ),
                category="Disease",
            ),
            EducationalTopic(
                title="Symptoms",
                description=(
                    "Movement-related and other symptoms."
                ),
                category="Disease",
            ),
            EducationalTopic(
                title="Prevention",
                description=(
                    "Healthy lifestyle practices and risk reduction."
                ),
                category="Lifestyle",
            ),
            EducationalTopic(
                title="Diagnosis",
                description=(
                    "Clinical and neurological assessment."
                ),
                category="Diagnosis",
            ),
            EducationalTopic(
                title="Treatment",
                description=(
                    "Treatment and rehabilitation approaches."
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
                "with the actual patient record and appropriate "
                "clinical assessment."
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
                "The report summarizes prediction results and "
                "related recommendations."
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
                "Parkinson's disease is a progressive neurological "
                "disorder that primarily affects movement."
            ),
            symptoms=[
                "Tremor",
                "Rigidity",
                "Slowed movement",
                "Balance problems",
            ],
            causes=[
                "Changes involving dopamine-producing neurons",
                "Genetic factors",
                "Environmental influences",
            ],
            risk_factors=[
                "Increasing age",
                "Family history",
                "Environmental influences",
            ],
            diagnosis=[
                "Medical history",
                "Neurological examination",
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
                "Balanced diet",
                "Good sleep",
                "Stress management",
                "Routine medical care",
            ],
            disclaimer=self._disclaimer(),
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
            version="1.2.0",
            knowledge_base="Medical Knowledge Base",
        )
