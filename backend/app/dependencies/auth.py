"""Authentication dependencies."""

import uuid
from typing import Annotated, Optional

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError

from app.core import security
from app.core.config import settings
from app.core.constants import BusinessCode
from app.exceptions.auth import AuthenticationError, AuthorizationError
from app.models.user import User
from app.schemas.auth import TokenPayload
from app.services.user_service import user_service
from app.utils.response import ResponseException
from .database import SessionDep

class CustomOAuth2PasswordBearer(OAuth2PasswordBearer):
    """自定义OAuth2PasswordBearer，使用统一响应格式"""

    async def __call__(self, request: Request) -> Optional[str]:
        authorization = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise ResponseException(
                    code=BusinessCode.AUTH_TOKEN_INVALID,
                    message="缺少认证令牌"
                )
            else:
                return None
        return param


reusable_oauth2 = CustomOAuth2PasswordBearer(
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
        raise ResponseException(
            code=BusinessCode.AUTH_TOKEN_INVALID,
            message="令牌无效或已过期"
        )

    if not token_data.sub:
        raise ResponseException(
            code=BusinessCode.AUTH_TOKEN_INVALID,
            message="令牌格式错误"
        )

    user = user_service.get(session=session, id=uuid.UUID(token_data.sub))
    if not user:
        raise ResponseException(
            code=BusinessCode.USER_NOT_FOUND,
            message="用户不存在"
        )
    if not user_service.is_active(user):
        raise ResponseException(
            code=BusinessCode.USER_INACTIVE,
            message="用户已被禁用"
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    """Get current active superuser."""
    if not user_service.is_superuser(current_user):
        raise ResponseException(
            code=BusinessCode.AUTH_PERMISSION_DENIED,
            message="权限不足，需要超级管理员权限"
        )
    return current_user
