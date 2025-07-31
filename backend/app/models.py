# This file will be deprecated - models are now split into models/ and schemas/ directories
# Import from new locations for backward compatibility

from app.models.user import User
from app.models.item import Item
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserRegister,
    UserUpdate,
    UserUpdateMe,
    UserPublic,
    UsersPublic,
    UpdatePassword,
)
from app.schemas.item import (
    ItemBase,
    ItemCreate,
    ItemUpdate,
    ItemPublic,
    ItemsPublic,
)
from app.schemas.auth import Token, TokenPayload, NewPassword
from app.schemas.common import Message

# Re-export for backward compatibility
__all__ = [
    # Models
    "User",
    "Item",
    # User schemas
    "UserBase",
    "UserCreate",
    "UserRegister",
    "UserUpdate",
    "UserUpdateMe",
    "UserPublic",
    "UsersPublic",
    "UpdatePassword",
    # Item schemas
    "ItemBase",
    "ItemCreate",
    "ItemUpdate",
    "ItemPublic",
    "ItemsPublic",
    # Auth schemas
    "Token",
    "TokenPayload",
    "NewPassword",
    # Common schemas
    "Message",
]
