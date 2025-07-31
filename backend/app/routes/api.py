"""Main API router that includes all route modules."""

from fastapi import APIRouter

from app.core.config import settings
from . import auth, health, items, users

api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router, tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])  # 标准化用户路由
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(health.router, prefix="/health", tags=["health"])

# Include development-only routes
if settings.ENVIRONMENT == "local":
    from . import private
    api_router.include_router(private.router, prefix="/private", tags=["private"])
