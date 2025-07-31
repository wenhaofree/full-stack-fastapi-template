"""Item database model."""

import uuid
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .user import User


class ItemBase(SQLModel):
    """Shared properties for Item model."""
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=255)


class Item(ItemBase, table=True):
    """Item database model."""
    __tablename__ = "item"  # Explicitly set table name

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: Optional["User"] = Relationship(back_populates="items")
