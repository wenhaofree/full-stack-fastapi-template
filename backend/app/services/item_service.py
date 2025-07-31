"""Item service for business logic operations."""

import uuid
from typing import Any

from sqlmodel import Session, func, select

from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate
from .base import BaseService


class ItemService(BaseService[Item, ItemCreate, ItemUpdate]):
    """Item service with business logic."""

    def __init__(self):
        super().__init__(Item)

    def create_with_owner(
        self, session: Session, *, obj_in: ItemCreate, owner_id: uuid.UUID
    ) -> Item:
        """Create a new item with owner."""
        db_obj = Item.model_validate(obj_in, update={"owner_id": owner_id})
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def get_multi_by_owner(
        self,
        session: Session,
        *,
        owner_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> list[Item]:
        """Get multiple items by owner with pagination."""
        statement = (
            select(Item)
            .where(Item.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
        )
        return list(session.exec(statement).all())

    def get_count_by_owner(self, session: Session, *, owner_id: uuid.UUID) -> int:
        """Get count of items by owner."""
        statement = select(func.count()).select_from(Item).where(Item.owner_id == owner_id)
        return session.exec(statement).one()

    def get_total_count(self, session: Session) -> int:
        """Get total count of all items."""
        statement = select(func.count()).select_from(Item)
        return session.exec(statement).one()

    def is_owner(self, item: Item, user_id: uuid.UUID) -> bool:
        """Check if user is the owner of the item."""
        return item.owner_id == user_id


# Create a singleton instance
item_service = ItemService()
