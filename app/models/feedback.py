"""
FeedbackHistory model for storing AI-generated feedback.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database import Base


class FeedbackHistory(Base):
    """FeedbackHistory model for storing AI-generated feedback for assessments."""
    
    __tablename__ = "feedback_history"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id = Column(String(36), ForeignKey("assessments.id"), nullable=False, unique=True)
    feedback_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    assessment = relationship("Assessment", back_populates="feedback")
    
    def __repr__(self):
        return f"<FeedbackHistory(id={self.id}, assessment_id={self.assessment_id})>"
    
    def to_dict(self):
        """Convert feedback to dictionary."""
        return {
            "id": self.id,
            "assessment_id": self.assessment_id,
            "feedback_text": self.feedback_text,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
