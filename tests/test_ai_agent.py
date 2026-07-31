"""
Unit Tests for AI Agent Module
"""

import pytest

from app.ai_agent.health_assistant import HealthAssistant
from app.ai_agent.symptom_explainer import SymptomExplainer
from app.ai_agent.recommendation import RecommendationAgent
from app.ai_agent.exercise_planner import ExercisePlanner
from app.ai_agent.medication_reminder import MedicationReminder
from app.ai_agent.prompt_templates import PromptTemplates


# ==========================================================
# Fixtures
# ==========================================================

@pytest.fixture
def assistant():
    return HealthAssistant()


@pytest.fixture
def symptom():
    return SymptomExplainer()


@pytest.fixture
def recommendation():
    return RecommendationAgent()


@pytest.fixture
def exercise():
    return ExercisePlanner()


@pytest.fixture
def reminder():
    return MedicationReminder()


@pytest.fixture
def prompts():
    return PromptTemplates()


# ==========================================================
# Health Assistant
# ==========================================================

def test_greeting(assistant):

    message = assistant.greeting()

    assert isinstance(message, str)
    assert len(message) > 0


def test_health_tip(assistant):

    tip = assistant.health_tip()

    assert isinstance(tip, str)


def test_disclaimer(assistant):

    disclaimer = assistant.disclaimer()

    assert "doctor" in disclaimer.lower()


def test_dashboard(assistant):

    dashboard = assistant.dashboard()

    assert isinstance(dashboard, dict)


def test_status(assistant):

    status = assistant.status()

    assert status["status"] == "Online"


# ==========================================================
# Symptom Explainer
# ==========================================================

def test_explain_known_symptom(symptom):

    result = symptom.explain("tremor")

    assert isinstance(result, str)
    assert len(result) > 0


def test_explain_unknown_symptom(symptom):

    result = symptom.explain("unknown_symptom")

    assert isinstance(result, str)


def test_search_symptoms(symptom):

    results = symptom.search("speech")

    assert isinstance(results, list)


def test_available_symptoms(symptom):

    symptoms = symptom.available_symptoms()

    assert isinstance(symptoms, list)


# ==========================================================
# Recommendation Agent
# ==========================================================

def test_lifestyle_recommendation(recommendation):

    result = recommendation.lifestyle()

    assert isinstance(result, list)


def test_diet_recommendation(recommendation):

    result = recommendation.diet()

    assert isinstance(result, list)


def test_followup_recommendation(recommendation):

    result = recommendation.follow_up()

    assert isinstance(result, str)


def test_wellness_tips(recommendation):

    result = recommendation.wellness()

    assert isinstance(result, list)


# ==========================================================
# Exercise Planner
# ==========================================================

def test_daily_plan(exercise):

    plan = exercise.daily_plan()

    assert isinstance(plan, dict)


def test_weekly_plan(exercise):

    plan = exercise.weekly_plan()

    assert isinstance(plan, dict)


def test_categories(exercise):

    categories = exercise.exercise_categories()

    assert isinstance(categories, list)


def test_safety_tips(exercise):

    tips = exercise.safety_tips()

    assert isinstance(tips, list)


# ==========================================================
# Medication Reminder
# ==========================================================

def test_create_reminder(reminder):

    result = reminder.create_reminder(
        medication="Levodopa",
        time="09:00",
    )

    assert isinstance(result, dict)


def test_schedule(reminder):

    schedule = reminder.schedule()

    assert isinstance(schedule, list)


def test_adherence_summary(reminder):

    summary = reminder.adherence_summary()

    assert isinstance(summary, dict)


def test_missed_dose(reminder):

    advice = reminder.missed_dose_guidance()

    assert isinstance(advice, str)


# ==========================================================
# Prompt Templates
# ==========================================================

def test_system_prompt(prompts):

    prompt = prompts.system_prompt()

    assert isinstance(prompt, str)
    assert len(prompt) > 20


def test_prediction_prompt(prompts):

    prompt = prompts.prediction_prompt()

    assert isinstance(prompt, str)


def test_symptom_prompt(prompts):

    prompt = prompts.symptom_prompt()

    assert isinstance(prompt, str)


def test_report_prompt(prompts):

    prompt = prompts.report_prompt()

    assert isinstance(prompt, str)


def test_followup_prompt(prompts):

    prompt = prompts.followup_prompt()

    assert isinstance(prompt, str)


# ==========================================================
# Integration
# ==========================================================

def test_patient_summary(assistant):

    summary = assistant.patient_summary(
        patient_name="John Doe",
        prediction="Positive",
        risk_level="Moderate",
    )

    assert isinstance(summary, str)


def test_prediction_explanation(assistant):

    explanation = assistant.prediction_explanation(
        prediction="Positive"
    )

    assert isinstance(explanation, str)


# ==========================================================
# Invalid Inputs
# ==========================================================

def test_empty_symptom(symptom):

    result = symptom.explain("")

    assert isinstance(result, str)


def test_none_symptom(symptom):

    result = symptom.explain(None)

    assert isinstance(result, str)


# ==========================================================
# Module Health
# ==========================================================

def test_ai_agent_status(assistant):

    status = assistant.status()

    assert status["status"] == "Online"
