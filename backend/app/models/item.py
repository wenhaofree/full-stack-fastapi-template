"""Item database model."""

import uuid
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from .base import SoftDeleteModel

if TYPE_CHECKING:
    from .user import User


class ItemBase(SQLModel):
    """Shared properties for Item model."""
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=255)


class Item(ItemBase, SoftDeleteModel, table=True):
    """Item database model with soft delete functionality."""
    __tablename__ = "item"  # Explicitly set table name

    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: Optional["User"] = Relationship(back_populates="items")
