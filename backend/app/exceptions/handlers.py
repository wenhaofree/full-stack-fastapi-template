"""Exception handlers for FastAPI application."""

import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from .base import AppException, ValidationError
from .auth import AuthenticationError, AuthorizationError
from .business import BusinessLogicError, ResourceNotFoundError

logger = logging.getLogger(__name__)


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup exception handlers for the FastAPI application."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        """Handle custom application exceptions."""
        logger.error(f"Application error: {exc.message}", extra={"details": exc.details})
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.message,
                "details": exc.details,
                "type": exc.__class__.__name__
            }
        )

    @app.exception_handler(PydanticValidationError)
    async def validation_exception_handler(
        request: Request, exc: PydanticValidationError
    ) -> JSONResponse:
        """Handle Pydantic validation errors."""
        logger.warning(f"Validation error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation failed",
                "details": exc.errors(),
                "type": "ValidationError"
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected exceptions."""
        logger.error(f"Unexpected error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "details": {},
                "type": "InternalServerError"
            }
        )
