"""
Assessment router.
Handles PHQ-9 assessment submission and user history.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User
from app.models.assessment import Assessment
from app.models.feedback import FeedbackHistory
from app.models.rating import UserRating
from app.schemas.assessment import (
    AssessmentSubmit,
    AssessmentResponse,
    UserHistoryResponse,
    AssessmentHistoryItem
)
from app.services.phq9_service import phq9_service
from app.services.feedback_service import feedback_service
from app.services.trend_service import trend_service
from app.services.risk_service import risk_service
from app.utils.constants import get_crisis_message

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api", tags=["assessments"])


@router.post(
    "/submit-assessment",
    response_model=AssessmentResponse,
    summary="Submit PHQ-9 assessment",
    description="Submit a completed PHQ-9 assessment and receive AI-generated feedback"
)
async def submit_assessment(
    assessment_data: AssessmentSubmit,
    db: AsyncSession = Depends(get_db)
) -> AssessmentResponse:
    """
    Submit a PHQ-9 assessment.
    
    This endpoint:
    1. Validates the user exists
    2. Calculates severity and risk level
    3. Analyzes trend compared to previous assessment
    4. Generates AI feedback using Groq
    5. Saves assessment and feedback to database
    6. Returns results with optional crisis message
    
    Args:
        assessment_data: Assessment submission data
        db: Database session
        
    Returns:
        Assessment response with feedback
        
    Raises:
        HTTPException: If user not found or processing fails
    """
    # Verify user exists - convert UUID to string for comparison
    user_id_str = str(assessment_data.user_id)
    logger.info(f"Looking up user with ID: {user_id_str}")
    
    result = await db.execute(
        select(User).where(User.id == user_id_str)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        logger.warning(f"User not found with ID: {user_id_str}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        # Calculate severity and risk level
        severity = phq9_service.get_severity(assessment_data.phq_score)
        risk_level = phq9_service.get_risk_level(assessment_data.phq_score)
        
        # Calculate trend
        trend = await trend_service.calculate_user_trend(
            db, user_id_str, assessment_data.phq_score
        )
        
        # Generate AI feedback
        feedback_text = await feedback_service.generate_feedback(
            phq_score=assessment_data.phq_score,
            severity=severity,
            trend=trend,
            emotion=assessment_data.emotion
        )
        
        # Create assessment record
        assessment = Assessment(
            user_id=user_id_str,
            phq_score=assessment_data.phq_score,
            severity=severity,
            emotion=assessment_data.emotion,
            confidence=assessment_data.confidence,
            risk_level=risk_level,
            trend=trend
        )
        db.add(assessment)
        await db.flush()
        await db.refresh(assessment)
        
        # Create feedback history record
        feedback = FeedbackHistory(
            assessment_id=assessment.id,
            feedback_text=feedback_text
        )
        db.add(feedback)
        
        logger.info(f"Assessment created: {assessment.id} for user: {user.id}")
        
        # Get crisis message if high risk
        crisis_message = get_crisis_message(risk_level)
        
        return AssessmentResponse(
            assessment_id=assessment.id,
            severity=severity,
            risk_level=risk_level,
            trend=trend,
            feedback_text=feedback_text,
            crisis_message=crisis_message
        )
        
    except Exception as e:
        logger.error(f"Error submitting assessment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process assessment. Please try again."
        )


@router.get(
    "/user/{user_id}/history",
    response_model=UserHistoryResponse,
    summary="Get user assessment history",
    description="Retrieve all assessments and ratings for a user"
)
async def get_user_history(
    user_id: str,
    db: AsyncSession = Depends(get_db)
) -> UserHistoryResponse:
    """
    Get user's assessment history.
    
    Args:
        user_id: User's unique identifier
        db: Database session
        
    Returns:
        User history with assessments and ratings
        
    Raises:
        HTTPException: If user not found
    """
    # Get user
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get assessments with feedback (eagerly load the feedback relationship)
    result = await db.execute(
        select(Assessment)
        .options(selectinload(Assessment.feedback))
        .where(Assessment.user_id == user_id)
        .order_by(Assessment.created_at.desc())
    )
    assessments = result.scalars().all()
    
    # Get ratings
    result = await db.execute(
        select(UserRating).where(UserRating.user_id == user_id)
    )
    ratings = result.scalars().all()
    
    # Build assessment history items
    assessment_items = []
    for a in assessments:
        # Get feedback for this assessment
        feedback_text = None
        if a.feedback:
            feedback_text = a.feedback.feedback_text
        
        assessment_items.append(
            AssessmentHistoryItem(
                id=a.id,
                phq_score=a.phq_score,
                severity=a.severity,
                emotion=a.emotion,
                confidence=a.confidence,
                risk_level=a.risk_level,
                trend=a.trend,
                created_at=a.created_at,
                feedback=feedback_text
            )
        )
    
    # Build ratings list
    ratings_list = [
        {
            "assessment_id": r.assessment_id,
            "rating": r.rating,
            "comment": r.feedback_comment
        }
        for r in ratings
    ]
    
    return UserHistoryResponse(
        user={
            "id": user.id,
            "name": user.name,
            "created_at": user.created_at.isoformat() if user.created_at else None
        },
        assessments=assessment_items,
        ratings=ratings_list
    )
