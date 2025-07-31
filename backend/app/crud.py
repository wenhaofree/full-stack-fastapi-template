# This file will be deprecated - CRUD operations are now in services/
# Import from new services for backward compatibility

import uuid
from typing import Any

from sqlmodel import Session

from app.models import Item, User
from app.schemas.item import ItemCreate
from app.schemas.user import UserCreate, UserUpdate
from app.services.item_service import item_service
from app.services.user_service import user_service


def create_user(*, session: Session, user_create: UserCreate) -> User:
    """Create user - delegates to user service."""
    return user_service.create(session=session, obj_in=user_create)


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    """Update user - delegates to user service."""
    return user_service.update(session=session, db_obj=db_user, obj_in=user_in)


def get_user_by_email(*, session: Session, email: str) -> User | None:
    """Get user by email - delegates to user service."""
    return user_service.get_by_email(session=session, email=email)


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    """Authenticate user - delegates to user service."""
    return user_service.authenticate(session=session, email=email, password=password)


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    """Create item - delegates to item service."""
    return item_service.create_with_owner(session=session, obj_in=item_in, owner_id=owner_id)
