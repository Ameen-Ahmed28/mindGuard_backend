"""
Main FastAPI application entry point.
Multimodal AI Mental Health Monitoring System.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers import (
    users_router,
    voice_router,
    assessments_router,
    ratings_router
)
from app.utils.constants import PHQ9_QUESTIONS

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting up Mental Health Monitoring System...")
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Mental Health Monitoring System...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    ## Multimodal AI Mental Health Monitoring System
    
    A comprehensive mental health screening system that combines:
    
    - **PHQ-9 Questionnaire**: Validated depression screening tool
    - **Voice Emotion Detection**: AI-powered emotion analysis from audio
    - **AI-Generated Feedback**: Personalized supportive feedback using Groq LLM
    - **Trend Analysis**: Track mental health changes over time
    
    ### Important Disclaimer
    ⚠️ This tool is for screening purposes only and is NOT a clinical diagnosis.
    If you're in crisis, please contact the KIRAN Mental Health Helpline: 1800-599-0019
    
    ### Assessment Flow
    1. Register as a user
    2. Complete the PHQ-9 questionnaire
    3. Optionally record voice for emotion detection
    4. Receive AI-generated supportive feedback
    5. Rate the feedback quality
    """,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)

# Add security headers middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # Prevent clickjacking (but allow for docs)
        if not request.url.path.startswith("/docs"):
            response.headers["X-Frame-Options"] = "DENY"
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        # XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # Content Security Policy - relaxed for Swagger UI docs
        if request.url.path.startswith("/docs") or request.url.path.startswith("/redoc"):
            # Allow Swagger UI resources
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https://fastapi.tiangolo.com; "
                "font-src 'self' https://cdn.jsdelivr.net;"
            )
        else:
            # Strict CSP for API endpoints
            response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response


app.add_middleware(SecurityHeadersMiddleware)

# Include routers
app.include_router(users_router)
app.include_router(voice_router)
app.include_router(assessments_router)
app.include_router(ratings_router)


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "documentation": "/docs"
    }


# Health check endpoint
@app.get("/api/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app_version
    }


# Get PHQ-9 questions endpoint
@app.get("/api/phq9-questions", tags=["phq9"])
async def get_phq9_questions():
    """
    Get PHQ-9 questionnaire questions.
    
    Returns the 9 validated PHQ-9 questions with response options.
    """
    return {
        "questions": PHQ9_QUESTIONS,
        "scoring": {
            "min_score": 0,
            "max_score": 27,
            "response_options": [
                {"value": 0, "label": "Not at all"},
                {"value": 1, "label": "Several days"},
                {"value": 2, "label": "More than half the days"},
                {"value": 3, "label": "Nearly every day"}
            ]
        },
        "severity_levels": [
            {"range": "0-4", "severity": "minimal"},
            {"range": "5-9", "severity": "mild"},
            {"range": "10-14", "severity": "moderate"},
            {"range": "15-19", "severity": "moderately_severe"},
            {"range": "20-27", "severity": "severe"}
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
