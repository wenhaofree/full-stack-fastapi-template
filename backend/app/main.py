"""Main FastAPI application."""

import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute

from app.core.config import settings
from app.core.logger_config import setup_professional_logging
from app.middleware import (
    setup_access_log_middleware,
    setup_cors_middleware,
    setup_error_middleware,
    setup_logging_middleware,
)
from app.routes import api_router


def custom_generate_unique_id(route: APIRoute) -> str:
    """Generate unique operation IDs for OpenAPI schema."""
    return f"{route.tags[0]}-{route.name}"


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Setup professional logging
    setup_professional_logging()

    # Initialize Sentry if configured
    if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
        sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

    # Create FastAPI app
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        generate_unique_id_function=custom_generate_unique_id,
    )

    # Setup middleware
    setup_cors_middleware(app)
    setup_access_log_middleware(app)  # 专业的访问日志
    setup_error_middleware(app)

    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app


# Create application instance
app = create_application()
