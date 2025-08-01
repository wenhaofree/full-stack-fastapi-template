"""Item service for business logic operations."""

import uuid
from typing import Any

from sqlmodel import Session, func, select

from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate
from .base import SoftDeleteService


class ItemService(SoftDeleteService[Item, ItemCreate, ItemUpdate]):
    """Item service with business logic and soft delete functionality."""

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
        limit: int = 100,
        include_deleted: bool = False
    ) -> list[Item]:
        """Get multiple items by owner with pagination, optionally including deleted items."""
        statement = select(Item).where(Item.owner_id == owner_id)

        if not include_deleted:
            statement = statement.where(Item.deleted_at.is_(None))

        statement = statement.offset(skip).limit(limit)
        return list(session.exec(statement).all())

    def get_count_by_owner(self, session: Session, *, owner_id: uuid.UUID, include_deleted: bool = False) -> int:
        """Get count of items by owner, optionally including deleted items."""
        statement = select(func.count()).select_from(Item).where(Item.owner_id == owner_id)

        if not include_deleted:
            statement = statement.where(Item.deleted_at.is_(None))

        return session.exec(statement).one()

    def get_total_count(self, session: Session, *, include_deleted: bool = False) -> int:
        """Get total count of all items, optionally including deleted items."""
        statement = select(func.count()).select_from(Item)

        if not include_deleted:
            statement = statement.where(Item.deleted_at.is_(None))

        return session.exec(statement).one()

    def is_owner(self, item: Item, user_id: uuid.UUID) -> bool:
        """Check if user is the owner of the item."""
        return item.owner_id == user_id


# Create a singleton instance
item_service = ItemService()
