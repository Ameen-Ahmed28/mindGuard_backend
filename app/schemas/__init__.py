"""
Pydantic schemas package.
Exports all schemas for easy importing.
"""

from app.schemas.user import UserCreate, UserResponse
from app.schemas.assessment import (
    AssessmentSubmit,
    AssessmentResponse,
    AssessmentHistoryItem,
    UserHistoryResponse
)
from app.schemas.voice import VoiceAnalysisResponse
from app.schemas.rating import RatingSubmit, RatingResponse, AverageRatingResponse

__all__ = [
    "UserCreate",
    "UserResponse",
    "AssessmentSubmit",
    "AssessmentResponse",
    "AssessmentHistoryItem",
    "UserHistoryResponse",
    "VoiceAnalysisResponse",
    "RatingSubmit",
    "RatingResponse",
    "AverageRatingResponse"
]
