"""User database model."""

import uuid
from typing import TYPE_CHECKING, List, Optional

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .item import Item


class UserBase(SQLModel):
    """Shared properties for User model."""
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = Field(default=None, max_length=255)


class User(UserBase, table=True):
    """User database model."""
    __tablename__ = "user"  # Explicitly set table name

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: List["Item"] = Relationship(back_populates="owner", cascade_delete=True)
