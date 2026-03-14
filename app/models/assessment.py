"""
Assessment model for storing PHQ-9 assessment results.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Assessment(Base):
    """Assessment model representing a PHQ-9 assessment result."""
    
    __tablename__ = "assessments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    phq_score = Column(Integer, nullable=False)
    severity = Column(String(30), nullable=False)
    emotion = Column(String(50), nullable=True)
    confidence = Column(Float, nullable=True)
    risk_level = Column(String(20), nullable=False)
    trend = Column(String(30), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="assessments")
    feedback = relationship("FeedbackHistory", back_populates="assessment", uselist=False, cascade="all, delete-orphan")
    rating = relationship("UserRating", back_populates="assessment", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Assessment(id={self.id}, user_id={self.user_id}, phq_score={self.phq_score})>"
    
    def to_dict(self):
        """Convert assessment to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "phq_score": self.phq_score,
            "severity": self.severity,
            "emotion": self.emotion,
            "confidence": self.confidence,
            "risk_level": self.risk_level,
            "trend": self.trend,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
