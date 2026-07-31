"""
Recommendation Schemas
"""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ==========================================================
# Recommendation Request
# ==========================================================

class RecommendationRequest(BaseModel):
    """
    Request model for generating recommendations.
    """

    patient_id: int = Field(..., gt=0)

    prediction: str

    risk_level: str

    confidence: float = Field(
        ...,
        ge=0,
        le=100
    )

    age: int = Field(
        ...,
        ge=1,
        le=120
    )

    medical_history: Optional[str] = None


# ==========================================================
# Lifestyle Recommendation
# ==========================================================

class LifestyleRecommendation(BaseModel):
    """
    Lifestyle recommendations.
    """

    title: str

    description: str


# ==========================================================
# Diet Recommendation
# ==========================================================

class DietRecommendation(BaseModel):
    """
    Diet recommendations.
    """

    title: str

    description: str


# ==========================================================
# Exercise Recommendation
# ==========================================================

class ExerciseRecommendation(BaseModel):
    """
    Exercise recommendation.
    """

    name: str

    duration: str

    frequency: str

    description: str


# ==========================================================
# Follow-up Recommendation
# ==========================================================

class FollowUpRecommendation(BaseModel):
    """
    Follow-up schedule.
    """

    next_visit: str

    specialist: str

    notes: str


# ==========================================================
# Medication Guidance
# ==========================================================

class MedicationGuidance(BaseModel):
    """
    Educational medication guidance.
    """

    note: str

    disclaimer: str


# ==========================================================
# Recommendation Response
# ==========================================================

class RecommendationResponse(BaseModel):
    """
    Complete recommendation response.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    patient_id: int

    risk_level: str

    recommendation: str

    lifestyle: List[LifestyleRecommendation]

    diet: List[DietRecommendation]

    exercises: List[ExerciseRecommendation]

    follow_up: FollowUpRecommendation

    medication: MedicationGuidance

    warning: str


# ==========================================================
# Recommendation Summary
# ==========================================================

class RecommendationSummary(BaseModel):
    """
    Short recommendation summary.
    """

    patient_id: int

    risk_level: str

    recommendation: str


# ==========================================================
# Recommendation History
# ==========================================================

class RecommendationHistory(BaseModel):
    """
    Recommendation history.
    """

    patient_id: int

    prediction_id: int

    recommendation: str

    risk_level: str

    created_at: str
