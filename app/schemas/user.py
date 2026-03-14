"""
Pydantic schemas for User endpoints.
"""

import re
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator
from datetime import datetime
from typing import Optional


class UserSignup(BaseModel):
    """Schema for user signup."""
    name: str = Field(..., min_length=1, max_length=100, description="User's display name")
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, max_length=100, description="User's password")
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets security requirements."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "securepassword123"
        }
    })


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=1, description="User's password")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "email": "john@example.com",
            "password": "securepassword123"
        }
    })


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: "UserResponse" = Field(..., description="User information")


class UserResponse(BaseModel):
    """Schema for user response."""
    id: str = Field(..., description="User's unique identifier")
    name: str = Field(..., description="User's display name")
    email: str = Field(..., description="User's email address")
    created_at: datetime = Field(..., description="Account creation timestamp")
    
    model_config = ConfigDict(from_attributes=True, json_schema_extra={
        "example": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "John Doe",
            "email": "john@example.com",
            "created_at": "2024-01-15T10:30:00"
        }
    })


# Legacy schema for backwards compatibility
class UserCreate(BaseModel):
    """Schema for creating a new user (legacy)."""
    name: str = Field(..., min_length=1, max_length=100, description="User's display name")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "John Doe"
        }
    })
