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
    Rule-based AI Health Assistant.

    Provides educational information about:
    - Parkinson disease
    - Symptoms
    - Causes
    - Risk factors
    - Diagnosis
    - Treatment
    - Exercise
    - Nutrition
    - Stress
    - Speech and voice
    - Prediction results
    - Model confidence
    - Reports
    """

    def __init__(self):
        """
        Initialize chatbot service.

        In production this can be replaced or extended with:
        - LLM integration
        - Vector database
        - Medical knowledge base
        - Persistent conversation storage
        """

        self._history = {}

    # ==========================================================
    # Chat
    # ==========================================================

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

        # ------------------------------------------------------
        # Store user message
        # ------------------------------------------------------

        user_message = ChatMessage(
            role="user",
            content=request.message,
            timestamp=datetime.utcnow(),
        )

        self._history.setdefault(
            conversation_id,
            []
        ).append(user_message)

        # ------------------------------------------------------
        # Store assistant response
        # ------------------------------------------------------

        assistant_message = ChatMessage(
            role="assistant",
            content=answer,
            timestamp=datetime.utcnow(),
        )

        self._history[conversation_id].append(
            assistant_message
        )

        # ------------------------------------------------------
        # Response
        # ------------------------------------------------------

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
    # Generate Response
    # ==========================================================

    def _generate_response(
        self,
        message: str,
    ) -> str:
        """
        Generate an educational response.

        This is a rule-based chatbot.
        It does not diagnose disease or prescribe medication.
        """

        text = message.lower().strip()

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
                "prediction results, and healthy habits.\n\n"
                "How can I help you?"
            )

        # ======================================================
        # What is Parkinson Disease?
        # ======================================================

        if (
            "what is parkinson" in text
            or "what's parkinson" in text
            or "define parkinson" in text
            or "about parkinson" in text
            or "tell me about parkinson" in text
            or "parkinson disease" in text
            or "parkinson's disease" in text
        ):

            information = self.parkinson_information()

            return (
                f"{information.definition}\n\n"
                "**Common symptoms:**\n"
                + "\n".join(
                    f"• {symptom}"
                    for symptom in information.symptoms
                )
                + "\n\n"
                f"{information.disclaimer}"
            )

        # ======================================================
        # Hand Tremor / Tremor
        # ======================================================

        if (
            "hand tremor" in text
            or "hand tremors" in text
            or "my hands shake" in text
            or "hands shake" in text
            or "shaking hands" in text
            or "tremor" in text
            or "tremors" in text
            or "shaking" in text
        ):

            return (
                "Hand tremors can have several possible causes. "
                "They may occur with conditions such as Parkinson "
                "disease or essential tremor, and can also be "
                "associated with medication effects, stress or "
                "anxiety, caffeine use, or other medical or "
                "neurological conditions.\n\n"
                "A tremor by itself does not establish a diagnosis. "
                "If a tremor is persistent, worsening, or interfering "
                "with daily activities, it should be evaluated by "
                "a qualified healthcare professional.\n\n"
                "This information is educational and is not a "
                "substitute for professional medical advice."
            )

        # ======================================================
        # Early Symptoms
        # ======================================================

        if (
            "early symptom" in text
            or "early signs" in text
            or "first symptoms" in text
            or "initial symptoms" in text
            or "symptoms of parkinson" in text
        ):

            information = self.parkinson_information()

            return (
                "Common symptoms associated with Parkinson "
                "disease include:\n\n"
                + "\n".join(
                    f"• {symptom}"
                    for symptom in information.symptoms
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

        if (
            "bradykinesia" in text
            or "slow movement" in text
            or "slowness of movement" in text
            or "what is bradykinesia" in text
            or "explain bradykinesia" in text
        ):

            return (
                "Bradykinesia means slowness of movement. "
                "It is one of the movement-related features "
                "associated with Parkinson disease.\n\n"
                "It can make everyday activities take longer "
                "and may affect walking, getting up, dressing, "
                "writing, or other fine-motor activities.\n\n"
                "Bradykinesia can have causes other than Parkinson "
                "disease, so its presence alone does not establish "
                "a diagnosis.\n\n"
                "A healthcare professional should evaluate "
                "persistent movement changes."
            )

        # ======================================================
        # Rigidity / Muscle Stiffness
        # ======================================================

        if (
            "rigidity" in text
            or "muscle stiffness" in text
            or "muscle stiff" in text
            or "stiff muscles" in text
            or "stiffness" in text
        ):

            return (
                "Rigidity refers to stiffness or resistance when "
                "a limb or joint is moved. It can occur as a "
                "motor symptom in Parkinson disease.\n\n"
                "People may notice stiffness in the arms, legs, "
                "neck, or other parts of the body.\n\n"
                "Stiffness can have many possible causes, so "
                "persistent symptoms should be assessed by a "
                "qualified healthcare professional."
            )

        # ======================================================
        # Balance / Postural Instability
        # ======================================================

        if (
            "balance problem" in text
            or "balance problems" in text
            or "postural instability" in text
            or "falling" in text
            or "falls" in text
        ):

            return (
                "Balance difficulties can occur in Parkinson "
                "disease, particularly as the condition progresses. "
                "They may increase the risk of falls.\n\n"
                "Balance problems can also have many other causes. "
                "A healthcare professional can evaluate the cause "
                "and recommend appropriate exercises or support."
            )

        # ======================================================
        # Walking Problems
        # ======================================================

        if (
            "walking problem" in text
            or "walking problems" in text
            or "difficulty walking" in text
            or "walking difficulty" in text
            or "freezing" in text
            or "shuffling" in text
        ):

            return (
                "Parkinson disease can affect walking and movement. "
                "Some people may experience slower walking, "
                "shorter steps, shuffling, or episodes of "
                "freezing of gait.\n\n"
                "Walking difficulties can have other causes as well. "
                "A healthcare professional or physical therapist "
                "can help assess persistent mobility problems."
            )

        # ======================================================
        # Voice Disorders / Speech
        # ======================================================

        if (
            "voice disorder" in text
            or "voice disorders" in text
            or "voice problem" in text
            or "voice problems" in text
            or "speech problem" in text
            or "speech problems" in text
            or "voice change" in text
            or "voice changes" in text
            or "soft voice" in text
            or "speech changes" in text
        ):

            return (
                "Voice and speech changes can occur in Parkinson "
                "disease. Some people may experience a softer voice, "
                "less variation in pitch, reduced vocal intensity, "
                "or changes in speech clarity.\n\n"
                "Voice measurements can also be used as one type "
                "of input in machine-learning research related to "
                "Parkinson disease detection.\n\n"
                "Persistent voice or speech changes should be "
                "evaluated by an appropriate healthcare professional."
            )

        # ======================================================
        # Causes of Parkinson Disease
        # ======================================================

        if (
            "what causes parkinson" in text
            or "what cause parkinson" in text
            or "causes of parkinson" in text
            or "cause of parkinson" in text
            or "why does parkinson happen" in text
            or "why do people get parkinson" in text
        ):

            information = self.parkinson_information()

            return (
                "Factors associated with Parkinson disease include:\n\n"
                + "\n".join(
                    f"• {cause}"
                    for cause in information.causes
                )
                + "\n\n"
                + information.disclaimer
            )

        # ======================================================
        # Risk Factors
        # ======================================================

        if (
            "risk factor" in text
            or "risk factors" in text
            or "who is at risk" in text
            or "risk of parkinson" in text
        ):

            information = self.parkinson_information()

            return (
                "Risk factors associated with Parkinson disease "
                "include:\n\n"
                + "\n".join(
                    f"• {risk}"
                    for risk in information.risk_factors
                )
                + "\n\n"
                + information.disclaimer
            )

        # ======================================================
        # Diagnosis
        # ======================================================

        if (
            "how is parkinson diagnosed" in text
            or "how to diagnose parkinson" in text
            or "diagnosis of parkinson" in text
            or "diagnose parkinson" in text
            or "diagnostic test" in text
            or "parkinson diagnosis" in text
        ):

            information = self.parkinson_information()

            return (
                "The educational information lists the following "
                "approaches to Parkinson disease diagnosis:\n\n"
                + "\n".join(
                    f"• {item}"
                    for item in information.diagnosis
                )
                + "\n\n"
                "Diagnosis should be performed by an appropriate "
                "healthcare professional based on the person's "
                "clinical history and examination.\n\n"
                + information.disclaimer
            )

        # ======================================================
        # Is Parkinson Curable?
        # ======================================================

        if (
            "is parkinson curable" in text
            or "can parkinson be cured" in text
            or "can parkinson's be cured" in text
            or "cure for parkinson" in text
            or "cure for parkinson's" in text
            or "does parkinson have a cure" in text
            or "is there a cure for parkinson" in text
        ):

            return (
                "Parkinson disease currently does not have a "
                "definitive cure. Treatment and rehabilitation "
                "approaches can help manage symptoms and support "
                "quality of life.\n\n"
                "Treatment decisions should be made with qualified "
                "healthcare professionals based on the individual's "
                "condition."
            )

        # ======================================================
        # Treatment
        # ======================================================

        if (
            "treatment for parkinson" in text
            or "treat parkinson" in text
            or "how is parkinson treated" in text
            or "parkinson treatment" in text
            or "treatments for parkinson" in text
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

        # ======================================================
        # Medication
        # ======================================================

        if (
            "medication" in text
            or "medications" in text
            or "medicine" in text
            or "medicines" in text
            or "drug for parkinson" in text
            or "drugs for parkinson" in text
        ):

            return (
                "Medication can be part of Parkinson disease "
                "management, but the appropriate medication and "
                "dose depend on the individual.\n\n"
                "Medication should only be started, stopped, "
                "or changed under the guidance of a qualified "
                "healthcare professional."
            )

        # ======================================================
        # Food / Nutrition
        # ======================================================

        if (
            "food" in text
            or "foods" in text
            or "diet" in text
            or "nutrition" in text
            or "what should i eat" in text
            or "what can i eat" in text
            or "recommended food" in text
        ):

            return (
                "A balanced and nutritious diet can support "
                "general health.\n\n"
                "A healthy diet can include a variety of "
                "nutrient-rich foods, adequate hydration, "
                "and appropriate amounts of fruits, vegetables, "
                "whole grains, and protein according to individual "
                "needs.\n\n"
                "People with Parkinson disease may have individual "
                "dietary considerations, especially when taking "
                "medications. Specific dietary changes should be "
                "discussed with a qualified healthcare professional "
                "or dietitian."
            )

        # ======================================================
        # Exercise
        # ======================================================

        if (
            "exercise" in text
            or "physical activity" in text
            or "workout" in text
            or "fitness" in text
            or "which exercises" in text
            or "beneficial exercise" in text
        ):

            return (
                "Regular physical activity can support mobility "
                "and general health.\n\n"
                "Examples of activities that may be included "
                "in an appropriate exercise program include:\n\n"
                "• Walking\n"
                "• Stretching\n"
                "• Balance exercises\n"
                "• Strength exercises\n"
                "• Physical therapy exercises\n\n"
                "The appropriate exercise program depends on "
                "the person's abilities and health status. "
                "A healthcare professional or physical therapist "
                "can provide individualized guidance."
            )

        # ======================================================
        # Stress / Anxiety
        # ======================================================

        if (
            "stress" in text
            or "anxiety" in text
            or "how can stress" in text
            or "reduce stress" in text
            or "manage stress" in text
            or "relax" in text
        ):

            return (
                "Stress management can include:\n\n"
                "• Regular physical activity\n"
                "• Adequate rest and sleep\n"
                "• Relaxation or breathing exercises\n"
                "• Social support\n"
                "• Maintaining regular daily routines\n"
                "• Speaking with a healthcare professional "
                "when stress or anxiety becomes difficult to manage\n\n"
                "If anxiety or stress significantly affects daily "
                "life, professional support may be appropriate."
            )

        # ======================================================
        # Sleep
        # ======================================================

        if (
            "sleep" in text
            or "insomnia" in text
            or "sleep problem" in text
            or "sleep problems" in text
            or "difficulty sleeping" in text
        ):

            return (
                "Sleep problems can occur in people with Parkinson "
                "disease, although sleep difficulties can have many "
                "other causes.\n\n"
                "Maintaining a regular sleep schedule, creating a "
                "comfortable sleep environment, and discussing "
                "persistent sleep problems with a healthcare "
                "professional may be helpful."
            )

        # ======================================================
        # Non-Motor Symptoms
        # ======================================================

        if (
            "non motor symptom" in text
            or "non-motor symptom" in text
            or "non motor symptoms" in text
            or "non-motor symptoms" in text
        ):

            return (
                "Parkinson disease can involve symptoms beyond "
                "movement. These may include changes involving "
                "sleep, mood, thinking, speech, or other functions.\n\n"
                "Non-motor symptoms can vary considerably between "
                "individuals and should be discussed with a "
                "healthcare professional when persistent or "
                "concerning."
            )

        # ======================================================
        # Motor Symptoms
        # ======================================================

        if (
            "motor symptom" in text
            or "motor symptoms" in text
            or "movement symptom" in text
            or "movement symptoms" in text
        ):

            information = self.parkinson_information()

            return (
                "Common movement-related symptoms associated "
                "with Parkinson disease include:\n\n"
                + "\n".join(
                    f"• {symptom}"
                    for symptom in information.symptoms
                )
                + "\n\n"
                + information.disclaimer
            )

        # ======================================================
        # Dopamine
        # ======================================================

        if (
            "dopamine" in text
            or "what is dopamine" in text
            or "dopamine in parkinson" in text
        ):

            return (
                "Dopamine is a chemical messenger in the brain "
                "that plays an important role in movement and "
                "other functions.\n\n"
                "Parkinson disease is associated with loss of "
                "dopamine-producing neurons, which contributes "
                "to movement-related symptoms."
            )

        # ======================================================
        # High Risk
        # ======================================================

        if (
            "high risk" in text
            or "high-risk" in text
        ):

            return (
                "A high-risk prediction means the machine learning "
                "model found patterns associated with Parkinson "
                "disease.\n\n"
                "It is not a diagnosis. A qualified healthcare "
                "professional should evaluate the result clinically."
            )

        # ======================================================
        # Medium Risk
        # ======================================================

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

        # ======================================================
        # Low Risk
        # ======================================================

        if "low risk" in text:

            return (
                "A low-risk prediction means the machine learning "
                "model found fewer patterns associated with "
                "Parkinson disease.\n\n"
                "A low-risk result does not rule out disease and "
                "should not replace professional medical assessment."
            )

        # ======================================================
        # Prediction
        # ======================================================

        if (
            "prediction" in text
            or "model result" in text
            or "voice prediction" in text
            or "machine learning result" in text
            or "prediction result" in text
        ):

            return (
                "The prediction is generated from 22 voice "
                "features using a trained machine learning model.\n\n"
                "The prediction is not a diagnosis and should "
                "be interpreted together with a qualified "
                "healthcare professional's clinical assessment."
            )

        # ======================================================
        # Confidence / Accuracy
        # ======================================================

        if (
            "confidence" in text
            or "accuracy" in text
            or "accurate" in text
            or "how accurate" in text
            or "model accuracy" in text
        ):

            return (
                "The prediction system reports a confidence value "
                "based on the machine learning model's output.\n\n"
                "Confidence should not be interpreted as a medical "
                "diagnosis or as a guarantee that a person does "
                "or does not have Parkinson disease."
            )

        # ======================================================
        # Report
        # ======================================================

        if (
            "report" in text
            or "medical report" in text
            or "prediction report" in text
        ):

            return (
                "A prediction report can summarize prediction "
                "results, confidence, risk level, recommendations, "
                "and related information.\n\n"
                "A report from this system should not replace "
                "professional medical evaluation."
            )

        # ======================================================
        # Healthy Lifestyle
        # ======================================================

        if (
            "healthy habits" in text
            or "healthy lifestyle" in text
            or "lifestyle" in text
            or "healthy living" in text
        ):

            information = self.parkinson_information()

            return (
                "Healthy lifestyle practices mentioned in the "
                "educational information include:\n\n"
                + "\n".join(
                    f"• {item}"
                    for item in information.prevention
                )
                + "\n\n"
                + information.disclaimer
            )

        # ======================================================
        # Prevention / Risk Reduction
        # ======================================================

        if (
            "prevent" in text
            or "prevention" in text
            or "reduce the risk" in text
            or "lower the risk" in text
            or "avoid parkinson" in text
            or "avoid parkinson's" in text
            or "how to prevent" in text
            or "how can i prevent" in text
            or "how can we prevent" in text
            or "can parkinson be prevented" in text
            or "is parkinson preventable" in text
        ):

            information = self.parkinson_information()

            return (
                "There is currently no guaranteed way to prevent "
                "Parkinson disease. However, some healthy lifestyle "
                "practices may support overall health and may help "
                "reduce certain risk factors.\n\n"

                "**Healthy practices include:**\n\n"

                + "\n".join(
                    f"• {item}"
                    for item in information.prevention
                )

                + "\n\n"

                "These measures do not guarantee that Parkinson "
                "disease will be prevented.\n\n"

                + information.disclaimer
            )

        # ======================================================
        # Help
        # ======================================================

        if (
            "help" in text
            or "what can you do" in text
            or "what can you answer" in text
            or "topics" in text
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
                "• Diagnosis\n"
                "• Treatment\n"
                "• Medication\n"
                "• Nutrition\n"
                "• Exercise\n"
                "• Stress and anxiety\n"
                "• Sleep\n"
                "• Prediction results\n"
                "• Model confidence\n"
                "• Reports\n\n"
                "I cannot diagnose a disease or prescribe "
                "individual treatment."
            )

        # ======================================================
        # Default
        # ======================================================

        return (
            "I can answer educational questions about Parkinson "
            "disease, including symptoms, causes, risk factors, "
            "diagnosis, treatment, exercise, nutrition, stress, "
            "sleep, voice changes, prediction results, and "
            "healthy habits.\n\n"
            "Try asking:\n\n"
            "• What is Parkinson's Disease?\n"
            "• What causes hand tremors?\n"
            "• What are the early symptoms?\n"
            "• Is Parkinson curable?\n"
            "• How is Parkinson diagnosed?\n"
            "• What foods are recommended?\n"
            "• Which exercises are beneficial?\n"
            "• How can stress be reduced?\n"
            "• Explain Bradykinesia.\n"
            "• Explain Voice Disorders."
        )

    # ==========================================================
    # Conversation History
    # ==========================================================

    def get_history(
        self,
    ) -> ChatHistoryResponse:
        """
        Return conversation history.
        """

        conversations = []

        for conversation_id, messages in self._history.items():

            conversations.append(
                ConversationHistory(
                    conversation_id=conversation_id,
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

    # ==========================================================
    # Clear History
    # ==========================================================

    def clear_history(
        self,
    ) -> ClearChatResponse:
        """
        Clear all conversation history.
        """

        self._history.clear()

        return ClearChatResponse(
            message="Conversation history cleared."
        )

    # ==========================================================
    # Suggested Questions
    # ==========================================================

    def suggested_questions(
        self,
    ) -> list[SuggestedQuestion]:
        """
        Return suggested questions.
        """

        return [
            SuggestedQuestion(
                id=1,
                question="What is Parkinson's Disease?",
                category="General",
            ),
            SuggestedQuestion(
                id=2,
                question="What causes hand tremors?",
                category="Symptoms",
            ),
            SuggestedQuestion(
                id=3,
                question="What are the early symptoms?",
                category="Symptoms",
            ),
            SuggestedQuestion(
                id=4,
                question="Is Parkinson curable?",
                category="Treatment",
            ),
            SuggestedQuestion(
                id=5,
                question="How is Parkinson diagnosed?",
                category="Diagnosis",
            ),
            SuggestedQuestion(
                id=6,
                question="What foods are recommended?",
                category="Nutrition",
            ),
            SuggestedQuestion(
                id=7,
                question="Which exercises are beneficial?",
                category="Exercise",
            ),
            SuggestedQuestion(
                id=8,
                question="How can stress be reduced?",
                category="Lifestyle",
            ),
            SuggestedQuestion(
                id=9,
                question="Explain Bradykinesia.",
                category="Symptoms",
            ),
            SuggestedQuestion(
                id=10,
                question="Explain Voice Disorders.",
                category="Symptoms",
            ),
        ]

    # ==========================================================
    # Frequently Asked Questions
    # ==========================================================

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
                    "No. The system provides a machine-learning "
                    "prediction that should be evaluated by a "
                    "qualified healthcare professional."
                ),
            ),
            FAQItem(
                question="How accurate is the prediction?",
                answer=(
                    "The system reports model confidence, but "
                    "confidence should not be interpreted as a "
                    "medical diagnosis."
                ),
            ),
            FAQItem(
                question="What symptoms can occur in Parkinson disease?",
                answer=(
                    "Common movement-related symptoms include "
                    "tremor, rigidity, slowed movement, and "
                    "balance problems."
                ),
            ),
            FAQItem(
                question="Is Parkinson disease curable?",
                answer=(
                    "Parkinson disease currently does not have "
                    "a definitive cure, although treatments can "
                    "help manage symptoms."
                ),
            ),
        ]

    # ==========================================================
    # Educational Topics
    # ==========================================================

    def educational_topics(
        self,
    ) -> list[EducationalTopic]:
        """
        Return educational topics.
        """

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
            EducationalTopic(
                title="Exercise",
                description=(
                    "Physical activity and mobility."
                ),
                category="Lifestyle",
            ),
            EducationalTopic(
                title="Voice Disorders",
                description=(
                    "Speech and voice changes."
                ),
                category="Symptoms",
            ),
        ]

    # ==========================================================
    # Prediction Explanation
    # ==========================================================

    def explain_prediction(
        self,
        prediction_id: int,
    ) -> PredictionExplanation:
        """
        Explain a prediction.
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

    # ==========================================================
    # Report Explanation
    # ==========================================================

    def explain_report(
        self,
        report_id: int,
    ) -> ReportExplanation:
        """
        Explain a generated report.
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

    # ==========================================================
    # Parkinson Information
    # ==========================================================

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

    # ==========================================================
    # Status
    # ==========================================================

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
