"""User related schemas for API requests and responses."""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    """Shared properties for User schemas."""
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = Field(default=None, max_length=255)


class UserCreate(UserBase):
    """Properties to receive via API on user creation."""
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    """Properties for user registration."""
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


class UserUpdate(UserBase):
    """Properties to receive via API on user update, all are optional."""
    email: Optional[EmailStr] = Field(default=None, max_length=255)  # type: ignore
    password: Optional[str] = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    """Properties for user self-update."""
    full_name: Optional[str] = Field(default=None, max_length=255)
    email: Optional[EmailStr] = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    """Schema for password update."""
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


class UserPublic(UserBase):
    """Properties to return via API, id is always required."""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class UsersPublic(SQLModel):
    """Schema for multiple users response."""
    data: List[UserPublic]
    count: int
