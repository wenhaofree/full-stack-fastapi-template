"""Authentication routes."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.dependencies.auth import get_current_user
from app.dependencies.database import SessionDep
from app.exceptions.auth import AuthenticationError
from app.exceptions.business import ResourceNotFoundError
from app.schemas.auth import NewPassword, Token
from app.schemas.common import Message
from app.schemas.user import UserPublic
from app.services.auth_service import auth_service
from app.services.user_service import user_service
from app.utils import (
    generate_password_reset_token,
    generate_reset_password_email,
    send_email,
    verify_password_reset_token,
)

router = APIRouter()


@router.post("/login/access-token", response_model=Token)
async def login_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """OAuth2 compatible token login, get an access token for future requests."""
    user = user_service.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise AuthenticationError("Incorrect email or password")
    if not user.is_active:
        raise AuthenticationError("Inactive user")
    
    return auth_service.create_access_token_for_user(str(user.id))


@router.post("/login/test-token", response_model=UserPublic)
async def test_token(current_user: Annotated[UserPublic, Depends(get_current_user)]) -> Any:
    """Test access token."""
    return current_user


@router.post("/password-recovery/{email}", response_model=Message)
async def recover_password(email: str, session: SessionDep) -> Message:
    """Password Recovery."""
    user = user_service.get_by_email(session=session, email=email)
    if not user:
        raise ResourceNotFoundError("The user with this email does not exist in the system.")
    
    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )
    send_email(
        email_to=user.email,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Password recovery email sent")


@router.post("/reset-password/", response_model=Message)
async def reset_password(session: SessionDep, body: NewPassword) -> Message:
    """Reset password."""
    email = verify_password_reset_token(token=body.token)
    if not email:
        raise AuthenticationError("Invalid token")
    
    user = user_service.get_by_email(session=session, email=email)
    if not user:
        raise ResourceNotFoundError("The user with this email does not exist in the system.")
    if not user.is_active:
        raise AuthenticationError("Inactive user")
    
    # Update password using service
    user_service.update(
        session=session, 
        db_obj=user, 
        obj_in={"password": body.new_password}
    )
    return Message(message="Password updated successfully")
