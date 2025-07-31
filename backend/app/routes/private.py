"""Private routes for development environment only."""

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.dependencies.database import SessionDep
from app.models.user import User
from app.schemas.user import UserPublic
from app.services.user_service import user_service

router = APIRouter()


class PrivateUserCreate(BaseModel):
    """Schema for creating users in development environment."""
    email: str
    password: str
    full_name: str
    is_verified: bool = False


@router.post("/users/", response_model=UserPublic)
async def create_user(user_in: PrivateUserCreate, session: SessionDep) -> Any:
    """Create a new user (development only)."""
    # Create user directly without validation for development purposes
    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=user_service._get_password_hash(user_in.password),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user
