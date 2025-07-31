"""Authentication service for business logic operations."""

from datetime import timedelta

from app.core.config import settings
from app.core.security import create_access_token
from app.schemas.auth import Token
from .user_service import user_service


class AuthService:
    """Authentication service with business logic."""

    def create_access_token_for_user(self, user_id: str) -> Token:
        """Create access token for user."""
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=user_id, expires_delta=access_token_expires
        )
        return Token(access_token=access_token)


# Create a singleton instance
auth_service = AuthService()
