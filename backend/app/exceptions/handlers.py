"""Exception handlers for FastAPI application."""

import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from app.core.constants import BusinessCode
from app.utils.response import ResponseException, error_response
from .base import AppException, ValidationError
from .auth import AuthenticationError, AuthorizationError
from .business import BusinessLogicError, ResourceNotFoundError

logger = logging.getLogger(__name__)


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup exception handlers for the FastAPI application."""

    @app.exception_handler(ResponseException)
    async def response_exception_handler(request: Request, exc: ResponseException) -> JSONResponse:
        """Handle custom response exceptions."""
        logger.error(f"Business error: {exc.business_message}", extra={"code": exc.business_code.value})
        return error_response(
            code=exc.business_code,
            message=exc.business_message,
        )

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        """Handle custom application exceptions."""
        logger.error(f"Application error: {exc.message}", extra={"details": exc.details})

        # 映射到统一响应格式
        if isinstance(exc, AuthenticationError):
            return error_response(BusinessCode.AUTH_LOGIN_FAILED, exc.message)
        elif isinstance(exc, AuthorizationError):
            return error_response(BusinessCode.AUTH_PERMISSION_DENIED, exc.message)
        elif isinstance(exc, ResourceNotFoundError):
            return error_response(BusinessCode.RESOURCE_NOT_FOUND, exc.message)
        elif isinstance(exc, BusinessLogicError):
            return error_response(BusinessCode.OPERATION_FAILED, exc.message)
        else:
            return error_response(BusinessCode.SYSTEM_ERROR, exc.message)

    @app.exception_handler(PydanticValidationError)
    async def validation_exception_handler(
        request: Request, exc: PydanticValidationError
    ) -> JSONResponse:
        """Handle Pydantic validation errors."""
        logger.warning(f"Validation error: {exc}")
        return error_response(
            code=BusinessCode.INVALID_PARAMS,
            message="参数验证失败",
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected exceptions."""
        logger.error(f"Unexpected error: {exc}", exc_info=True)
        return error_response(
            code=BusinessCode.SYSTEM_ERROR,
            message="系统内部错误",
        )
