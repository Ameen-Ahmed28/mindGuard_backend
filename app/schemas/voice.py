"""
Pydantic schemas for Voice analysis endpoints.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class VoiceAnalysisResponse(BaseModel):
    """Schema for voice emotion analysis response."""
    emotion: str = Field(..., description="Detected emotion label")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "emotion": "neutral",
            "confidence": 0.85
        }
    })
