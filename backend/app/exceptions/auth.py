"""Authentication and authorization exceptions."""

from .base import AppException


class AuthenticationError(AppException):
    """Authentication failed exception."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message=message, status_code=401)


class AuthorizationError(AppException):
    """Authorization failed exception."""
    
    def __init__(self, message: str = "Not enough permissions"):
        super().__init__(message=message, status_code=403)
