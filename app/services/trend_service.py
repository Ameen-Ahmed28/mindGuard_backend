"""
Trend Service for analyzing PHQ-9 score trends over time.
"""

import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.assessment import Assessment
from app.utils.constants import calculate_trend

# Configure logging
logger = logging.getLogger(__name__)


class TrendService:
    """Service for analyzing PHQ-9 score trends."""
    
    @staticmethod
    async def get_previous_score(db: AsyncSession, user_id: str) -> Optional[int]:
        """
        Get the previous PHQ-9 score for a user.
        
        Args:
            db: Database session
            user_id: User's unique identifier
            
        Returns:
            Previous PHQ-9 score or None if no previous assessment
        """
        try:
            # Get the most recent assessment before the current one
            result = await db.execute(
                select(Assessment)
                .where(Assessment.user_id == user_id)
                .order_by(Assessment.created_at.desc())
                .limit(1)
            )
            previous_assessment = result.scalar_one_or_none()
            
            if previous_assessment:
                return previous_assessment.phq_score
            return None
            
        except Exception as e:
            logger.error(f"Error fetching previous score: {e}")
            return None
    
    @staticmethod
    async def calculate_user_trend(
        db: AsyncSession,
        user_id: str,
        current_score: int
    ) -> str:
        """
        Calculate trend for a user based on current and previous scores.
        
        Args:
            db: Database session
            user_id: User's unique identifier
            current_score: Current PHQ-9 score
            
        Returns:
            Trend string
        """
        previous_score = await TrendService.get_previous_score(db, user_id)
        return calculate_trend(current_score, previous_score)
    
    @staticmethod
    async def get_score_history(
        db: AsyncSession,
        user_id: str,
        limit: int = 10
    ) -> list[dict]:
        """
        Get PHQ-9 score history for a user.
        
        Args:
            db: Database session
            user_id: User's unique identifier
            limit: Maximum number of records to return
            
        Returns:
            List of score history records
        """
        try:
            result = await db.execute(
                select(Assessment)
                .where(Assessment.user_id == user_id)
                .order_by(Assessment.created_at.desc())
                .limit(limit)
            )
            assessments = result.scalars().all()
            
            return [
                {
                    "score": a.phq_score,
                    "severity": a.severity,
                    "date": a.created_at.isoformat() if a.created_at else None
                }
                for a in assessments
            ]
            
        except Exception as e:
            logger.error(f"Error fetching score history: {e}")
            return []


# Create singleton instance
trend_service = TrendService()
