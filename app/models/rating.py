"""
UserRating model for storing user feedback ratings.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database import Base


class UserRating(Base):
    """UserRating model for storing user ratings of AI feedback."""
    
    __tablename__ = "user_ratings"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    assessment_id = Column(String(36), ForeignKey("assessments.id"), nullable=False, unique=True)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    feedback_comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="ratings")
    assessment = relationship("Assessment", back_populates="rating")
    
    def __repr__(self):
        return f"<UserRating(id={self.id}, rating={self.rating})>"
    
    def to_dict(self):
        """Convert rating to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "assessment_id": self.assessment_id,
            "rating": self.rating,
            "feedback_comment": self.feedback_comment,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
