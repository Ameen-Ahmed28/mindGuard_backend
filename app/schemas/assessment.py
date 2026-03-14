"""
Pydantic schemas for Assessment endpoints.
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from uuid import UUID


class AssessmentSubmit(BaseModel):
    """Schema for submitting an assessment."""
    user_id: UUID = Field(..., description="User's unique identifier")
    phq_score: int = Field(..., ge=0, le=27, description="Total PHQ-9 score (0-27)")
    emotion: Optional[str] = Field(None, description="Detected emotion from voice")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Emotion detection confidence")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "phq_score": 12,
            "emotion": "neutral",
            "confidence": 0.85
        }
    })


class AssessmentResponse(BaseModel):
    """Schema for assessment response."""
    assessment_id: str = Field(..., description="Assessment's unique identifier")
    severity: str = Field(..., description="Severity classification")
    risk_level: str = Field(..., description="Risk level classification")
    trend: str = Field(..., description="Trend analysis result")
    feedback_text: str = Field(..., description="AI-generated feedback")
    crisis_message: Optional[str] = Field(None, description="Crisis helpline message if high risk")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "assessment_id": "660e8400-e29b-41d4-a716-446655440000",
            "severity": "moderate",
            "risk_level": "moderate",
            "trend": "no_change",
            "feedback_text": "Based on your responses, you may be experiencing moderate symptoms...",
            "crisis_message": None
        }
    })


class AssessmentHistoryItem(BaseModel):
    """Schema for a single assessment in history."""
    id: str
    phq_score: int
    severity: str
    emotion: Optional[str]
    confidence: Optional[float]
    risk_level: str
    trend: Optional[str]
    created_at: datetime
    feedback: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class UserHistoryResponse(BaseModel):
    """Schema for user history response."""
    user: dict
    assessments: list[AssessmentHistoryItem]
    ratings: list[dict]
    
    model_config = ConfigDict(from_attributes=True)
