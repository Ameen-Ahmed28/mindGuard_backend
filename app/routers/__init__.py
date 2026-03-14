"""
Routers package.
Exports all API routers.
"""

from app.routers.users import router as users_router
from app.routers.voice import router as voice_router
from app.routers.assessments import router as assessments_router
from app.routers.ratings import router as ratings_router

__all__ = [
    "users_router",
    "voice_router",
    "assessments_router",
    "ratings_router"
]
