"""Item related schemas for API requests and responses."""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, SQLModel


class ItemBase(SQLModel):
    """Shared properties for Item schemas."""
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=255)


class ItemCreate(ItemBase):
    """Properties to receive on item creation."""
    pass


class ItemUpdate(ItemBase):
    """Properties to receive on item update."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)  # type: ignore


class ItemPublic(ItemBase):
    """Properties to return via API, id is always required."""
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class ItemsPublic(SQLModel):
    """Schema for multiple items response."""
    data: List[ItemPublic]
    count: int
