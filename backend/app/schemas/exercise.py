from typing import List, Optional
from pydantic import BaseModel, Field


class ExerciseRequest(BaseModel):
    age: int = Field(..., ge=1, le=120)
    gender: Optional[str] = None
    diagnosis: Optional[str] = None
    severity: Optional[str] = "mild"
    mobility_level: Optional[str] = "moderate"
    duration_per_day: Optional[int] = 30


class ExerciseItem(BaseModel):
    name: str
    description: str
    duration: str
    frequency: str


class ExercisePlan(BaseModel):
    title: str
    description: str
    exercises: List[ExerciseItem]
    precautions: List[str] = []
    notes: Optional[str] = None
