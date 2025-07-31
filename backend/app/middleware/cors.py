"""CORS middleware configuration."""

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.core.config import settings


def setup_cors_middleware(app: FastAPI) -> None:
    """Setup CORS middleware for the FastAPI application."""
    if settings.all_cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.all_cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
