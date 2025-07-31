"""Base exception classes."""

from typing import Any


class AppException(Exception):
    """Base application exception."""
    
    def __init__(
        self,
        message: str = "An error occurred",
        status_code: int = 500,
        details: dict[str, Any] | None = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(AppException):
    """Validation error exception."""
    
    def __init__(self, message: str = "Validation failed", details: dict[str, Any] | None = None):
        super().__init__(message=message, status_code=422, details=details)
