"""User routes."""

import uuid
from typing import Any, Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

from app.dependencies.auth import CurrentUser, get_current_active_superuser
from app.dependencies.database import SessionDep
from app.exceptions.auth import AuthenticationError, AuthorizationError
from app.exceptions.business import BusinessLogicError, ResourceNotFoundError
from app.models.item import Item
from app.models.user import User
from app.schemas.common import Message
from app.schemas.user import (
    UpdatePassword,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)
from app.services.user_service import user_service
from app.utils import generate_new_account_email, send_email

router = APIRouter()


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
)
async def read_users(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """Retrieve users."""
    count_statement = select(func.count()).select_from(User)
    count = session.exec(count_statement).one()

    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()

    return UsersPublic(data=users, count=count)


@router.post("/", response_model=UserPublic)
async def create_user(
    *,
    session: SessionDep,
    user_in: UserCreate,
    current_user: Annotated[User, Depends(get_current_active_superuser)],
) -> Any:
    """Create new user."""
    user = user_service.get_by_email(session=session, email=user_in.email)
    if user:
        raise BusinessLogicError(
            message="The user with this email already exists in the system"
        )
    
    user = user_service.create(session=session, obj_in=user_in)
    return user


@router.get("/me", response_model=UserPublic)
async def read_user_me(current_user: CurrentUser) -> Any:
    """Get current user."""
    return current_user


@router.put("/me", response_model=UserPublic)
async def update_user_me(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    user_in: UserUpdateMe,
) -> Any:
    """Update own user."""
    user = user_service.update(session=session, db_obj=current_user, obj_in=user_in)
    return user


@router.put("/me/password", response_model=Message)
async def update_password(
    session: SessionDep,
    current_user: CurrentUser,
    update_password: UpdatePassword,
) -> Any:
    """Update own password."""
    if not user_service.authenticate(
        session=session, 
        email=current_user.email, 
        password=update_password.current_password
    ):
        raise AuthenticationError(message="Invalid current password")
    
    user_service.update(
        session=session,
        db_obj=current_user,
        obj_in={"password": update_password.new_password},
    )
    return Message(message="Password updated successfully")


@router.get("/{user_id}", response_model=UserPublic)
async def read_user_by_id(
    user_id: uuid.UUID,
    current_user: CurrentUser,
    session: SessionDep,
) -> Any:
    """Get a specific user by id."""
    user = user_service.get(session=session, id=user_id)
    if not user:
        raise ResourceNotFoundError(message="User not found")
    
    if not user_service.is_superuser(current_user) and user.id != current_user.id:
        raise AuthorizationError(message="Not enough permissions")
    
    return user


@router.put("/{user_id}", response_model=UserPublic)
async def update_user(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
    user_in: UserUpdate,
    current_user: Annotated[User, Depends(get_current_active_superuser)],
) -> Any:
    """Update a user."""
    user = user_service.get(session=session, id=user_id)
    if not user:
        raise ResourceNotFoundError(message="User not found")
    
    user = user_service.update(session=session, db_obj=user, obj_in=user_in)
    return user
