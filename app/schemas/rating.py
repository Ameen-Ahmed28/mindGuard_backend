"""
Pydantic schemas for Rating endpoints.
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from uuid import UUID


class RatingSubmit(BaseModel):
    """Schema for submitting a rating."""
    user_id: UUID = Field(..., description="User's unique identifier")
    assessment_id: UUID = Field(..., description="Assessment's unique identifier")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5 stars")
    feedback_comment: Optional[str] = Field(None, max_length=500, description="Optional feedback comment")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "assessment_id": "660e8400-e29b-41d4-a716-446655440000",
            "rating": 4,
            "feedback_comment": "Very helpful feedback!"
        }
    })


class RatingResponse(BaseModel):
    """Schema for rating response."""
    id: str = Field(..., description="Rating's unique identifier")
    rating: int = Field(..., description="Rating value (1-5)")
    created_at: datetime = Field(..., description="Rating timestamp")
    
    model_config = ConfigDict(from_attributes=True, json_schema_extra={
        "example": {
            "id": "770e8400-e29b-41d4-a716-446655440000",
            "rating": 4,
            "created_at": "2024-01-15T10:30:00"
        }
    })


class AverageRatingResponse(BaseModel):
    """Schema for average rating response."""
    average_rating: float = Field(..., description="Average rating across all submissions")
    total_ratings: int = Field(..., description="Total number of ratings")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "average_rating": 4.2,
            "total_ratings": 150
        }
    })
