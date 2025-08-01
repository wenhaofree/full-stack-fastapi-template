"""User database model."""

import uuid
from typing import TYPE_CHECKING, List, Optional

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

from .base import SoftDeleteModel

if TYPE_CHECKING:
    from .item import Item


class UserBase(SQLModel):
    """Shared properties for User model."""
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = Field(default=None, max_length=255)


class User(UserBase, SoftDeleteModel, table=True):
    """User database model with soft delete functionality."""
    __tablename__ = "user"  # Explicitly set table name

    hashed_password: str
    items: List["Item"] = Relationship(back_populates="owner", cascade_delete=True)
