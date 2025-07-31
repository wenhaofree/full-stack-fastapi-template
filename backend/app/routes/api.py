"""Main API router that includes all route modules."""

from fastapi import APIRouter

from app.core.config import settings
from . import auth, health, items, users, debug_example

api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router, tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])  # 标准化用户路由
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(health.router, prefix="/health", tags=["health"])

# DEBUG路由（仅在开发环境启用）
from app.core.config import settings
if settings.ENVIRONMENT == "local":
    api_router.include_router(debug_example.router, tags=["debug"])

# Include development-only routes
if settings.ENVIRONMENT == "local":
    from . import private
    api_router.include_router(private.router, prefix="/private", tags=["private"])
