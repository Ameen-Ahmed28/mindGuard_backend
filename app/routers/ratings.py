"""
Rating router.
Handles user feedback ratings for assessments.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.user import User
from app.models.assessment import Assessment
from app.models.rating import UserRating
from app.schemas.rating import (
    RatingSubmit,
    RatingResponse,
    AverageRatingResponse
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api", tags=["ratings"])


@router.post(
    "/submit-rating",
    response_model=RatingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit assessment rating",
    description="Submit a rating (1-5 stars) for an assessment's AI feedback"
)
async def submit_rating(
    rating_data: RatingSubmit,
    db: AsyncSession = Depends(get_db)
) -> RatingResponse:
    """
    Submit a rating for an assessment.
    
    Args:
        rating_data: Rating submission data
        db: Database session
        
    Returns:
        Created rating information
        
    Raises:
        HTTPException: If user or assessment not found, or rating already exists
    """
    # Verify user exists - convert to string for comparison
    user_id_str = str(rating_data.user_id)
    logger.info(f"Looking up user for rating with ID: {user_id_str}")
    
    result = await db.execute(
        select(User).where(User.id == user_id_str)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        logger.warning(f"User not found for rating: {user_id_str}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify assessment exists - convert to string for comparison
    assessment_id_str = str(rating_data.assessment_id)
    logger.info(f"Looking up assessment for rating with ID: {assessment_id_str}")
    
    result = await db.execute(
        select(Assessment).where(Assessment.id == assessment_id_str)
    )
    assessment = result.scalar_one_or_none()
    
    if not assessment:
        logger.warning(f"Assessment not found for rating: {assessment_id_str}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found"
        )
    
    try:
        # Create rating (unique constraint on assessment_id prevents duplicates)
        rating = UserRating(
            user_id=user_id_str,
            assessment_id=assessment_id_str,
            rating=rating_data.rating,
            feedback_comment=rating_data.feedback_comment
        )
        db.add(rating)
        await db.flush()
        await db.refresh(rating)
        
        logger.info(f"Rating submitted: {rating.id} for assessment: {rating_data.assessment_id}")
        
        return RatingResponse(
            id=rating.id,
            rating=rating.rating,
            created_at=rating.created_at
        )
        
    except IntegrityError:
        # Handle duplicate rating (race condition caught by unique constraint)
        logger.warning(f"Duplicate rating attempt for assessment: {rating_data.assessment_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating already submitted for this assessment"
        )
    except Exception as e:
        logger.error(f"Error submitting rating: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit rating"
        )


@router.get(
    "/analytics/average-rating",
    response_model=AverageRatingResponse,
    summary="Get average rating",
    description="Get the average rating across all submitted ratings"
)
async def get_average_rating(
    db: AsyncSession = Depends(get_db)
) -> AverageRatingResponse:
    """
    Get average rating across all submissions.
    
    Args:
        db: Database session
        
    Returns:
        Average rating and total count
    """
    try:
        # Calculate average rating
        result = await db.execute(
            select(
                func.avg(UserRating.rating).label("average"),
                func.count(UserRating.id).label("total")
            )
        )
        row = result.one()
        
        average = row.average if row.average else 0.0
        total = row.total if row.total else 0
        
        return AverageRatingResponse(
            average_rating=round(float(average), 2),
            total_ratings=total
        )
        
    except Exception as e:
        logger.error(f"Error calculating average rating: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate average rating"
        )
