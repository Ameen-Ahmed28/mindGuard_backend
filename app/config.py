"""
Application configuration module.
Handles environment variables and application settings.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "Mental Health Monitoring System"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False, alias="DEBUG")
    
    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./mental_health.db",
        alias="DATABASE_URL"
    )
    
    # Groq API
    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    groq_model: str = Field(default="openai/gpt-oss-20b", alias="GROQ_MODEL")
    
    # HuggingFace
    huggingface_token: Optional[str] = Field(default=None, alias="HUGGINGFACE_TOKEN")
    emotion_model: str = Field(
        default="prithivMLmods/Speech-Emotion-Classification",
        alias="EMOTION_MODEL"
    )
    
    # CORS - should be set via environment variable for production
    cors_origins: str = Field(
        default="",
        alias="CORS_ORIGINS"
    )
    
    # Crisis Helpline
    crisis_helpline: str = "1800-599-0019"
    crisis_helpline_name: str = "KIRAN Mental Health Helpline"
    
    # JWT Authentication
    jwt_secret: str = Field(default="", alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_expiration_hours: int = Field(default=24, alias="JWT_EXPIRATION_HOURS")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Validate critical secrets are set
        if not self.jwt_secret:
            import secrets
            # Generate a secure random key for development
            self.jwt_secret = secrets.token_urlsafe(32)
            import warnings
            warnings.warn(
                "JWT_SECRET not set in environment. Using generated key for development. "
                "Set JWT_SECRET environment variable for production!",
                UserWarning
            )
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Create global settings instance
settings = Settings()
