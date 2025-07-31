"""Business logic exceptions."""

from .base import AppException


class BusinessLogicError(AppException):
    """Business logic error exception."""
    
    def __init__(self, message: str = "Business logic error"):
        super().__init__(message=message, status_code=400)


class ResourceNotFoundError(AppException):
    """Resource not found exception."""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message=message, status_code=404)
