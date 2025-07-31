"""Authentication dependencies."""

import uuid
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError

from app.core import security
from app.core.config import settings
from app.exceptions.auth import AuthenticationError, AuthorizationError
from app.models.user import User
from app.schemas.auth import TokenPayload
from app.services.user_service import user_service
from .database import SessionDep

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    """Get current authenticated user."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise AuthenticationError("Could not validate credentials")
    
    if not token_data.sub:
        raise AuthenticationError("Invalid token payload")

    user = user_service.get(session=session, id=uuid.UUID(token_data.sub))
    if not user:
        raise AuthenticationError("User not found")
    if not user_service.is_active(user):
        raise AuthenticationError("Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    """Get current active superuser."""
    if not user_service.is_superuser(current_user):
        raise AuthorizationError("The user doesn't have enough privileges")
    return current_user
