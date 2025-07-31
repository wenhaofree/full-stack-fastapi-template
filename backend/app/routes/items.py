"""Item routes."""

import uuid
from typing import Any

from fastapi import APIRouter

from app.dependencies.auth import CurrentUser
from app.dependencies.database import SessionDep
from app.exceptions.auth import AuthorizationError
from app.exceptions.business import ResourceNotFoundError
from app.schemas.common import Message
from app.schemas.item import ItemCreate, ItemPublic, ItemsPublic, ItemUpdate
from app.services.item_service import item_service
from app.services.user_service import user_service

router = APIRouter()


@router.get("/", response_model=ItemsPublic)
async def read_items(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """Retrieve items."""
    if user_service.is_superuser(current_user):
        # Superuser can see all items
        count = item_service.get_total_count(session=session)
        items = item_service.get_multi(session=session, skip=skip, limit=limit)
    else:
        # Regular user can only see their own items
        count = item_service.get_count_by_owner(session=session, owner_id=current_user.id)
        items = item_service.get_multi_by_owner(
            session=session, owner_id=current_user.id, skip=skip, limit=limit
        )

    return ItemsPublic(data=items, count=count)


@router.get("/{id}", response_model=ItemPublic)
async def read_item(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """Get item by ID."""
    item = item_service.get(session=session, id=id)
    if not item:
        raise ResourceNotFoundError(message="Item not found")
    
    if not user_service.is_superuser(current_user) and not item_service.is_owner(item, current_user.id):
        raise AuthorizationError(message="Not enough permissions")
    
    return item


@router.post("/", response_model=ItemPublic)
async def create_item(
    *, session: SessionDep, current_user: CurrentUser, item_in: ItemCreate
) -> Any:
    """Create new item."""
    item = item_service.create_with_owner(
        session=session, obj_in=item_in, owner_id=current_user.id
    )
    return item


@router.put("/{id}", response_model=ItemPublic)
async def update_item(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    item_in: ItemUpdate,
) -> Any:
    """Update an item."""
    item = item_service.get(session=session, id=id)
    if not item:
        raise ResourceNotFoundError(message="Item not found")
    
    if not user_service.is_superuser(current_user) and not item_service.is_owner(item, current_user.id):
        raise AuthorizationError(message="Not enough permissions")
    
    item = item_service.update(session=session, db_obj=item, obj_in=item_in)
    return item


@router.delete("/{id}", response_model=Message)
async def delete_item(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """Delete an item."""
    item = item_service.get(session=session, id=id)
    if not item:
        raise ResourceNotFoundError(message="Item not found")
    
    if not user_service.is_superuser(current_user) and not item_service.is_owner(item, current_user.id):
        raise AuthorizationError(message="Not enough permissions")
    
    item_service.delete(session=session, id=id)
    return Message(message="Item deleted successfully")
