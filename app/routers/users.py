"""
User management router.
Handles user creation, authentication, and retrieval.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserSignup, UserLogin, TokenResponse
from app.utils.security import hash_password, verify_password, create_access_token

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api", tags=["users"])


@router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with name, email, and password"
)
async def signup(
    user_data: UserSignup,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Register a new user.
    
    Args:
        user_data: User signup data with name, email, and password
        db: Database session
        
    Returns:
        JWT token and user information
        
    Raises:
        HTTPException: If email already exists or signup fails
    """
    try:
        # Check if email already exists
        result = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user with hashed password
        hashed_password = hash_password(user_data.password)
        user = User(
            name=user_data.name,
            email=user_data.email,
            password_hash=hashed_password
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
        
        # Generate access token
        access_token = create_access_token(
            data={"sub": user.id, "email": user.email}
        )
        
        logger.info(f"Created user: {user.id}")
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=user.id,
                name=user.name,
                email=user.email,
                created_at=user.created_at
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login user",
    description="Authenticate user with email and password"
)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Login user.
    
    Args:
        credentials: User login credentials with email and password
        db: Database session
        
    Returns:
        JWT token and user information
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by email
    result = await db.execute(
        select(User).where(User.email == credentials.email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    # Generate access token
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email}
    )
    
    logger.info(f"User logged in: {user.id}")
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            created_at=user.created_at
        )
    )


@router.post(
    "/create-user",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user (legacy)",
    description="Create a new user account with a display name (legacy endpoint)",
    deprecated=True
)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Create a new user (legacy endpoint for backwards compatibility).
    
    Args:
        user_data: User creation data with name
        db: Database session
        
    Returns:
        Created user information
        
    Raises:
        HTTPException: If user creation fails
    """
    try:
        # Create new user with placeholder email and password
        # This is deprecated - use /signup instead
        import uuid
        placeholder_email = f"user_{uuid.uuid4().hex[:8]}@placeholder.local"
        placeholder_password = uuid.uuid4().hex
        
        user = User(
            name=user_data.name,
            email=placeholder_email,
            password_hash=hash_password(placeholder_password)
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
        
        logger.info(f"Created user (legacy): {user.id}")
        
        return UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            created_at=user.created_at
        )
        
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.get(
    "/user/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Retrieve user information by their unique identifier"
)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Get user by ID.
    
    Args:
        user_id: User's unique identifier
        db: Database session
        
    Returns:
        User information
        
    Raises:
        HTTPException: If user not found
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        created_at=user.created_at
    )
