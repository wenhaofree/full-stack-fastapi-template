"""User service for business logic operations."""

from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from .base import BaseService


class UserService(BaseService[User, UserCreate, UserUpdate]):
    """User service with business logic."""

    def __init__(self):
        super().__init__(User)

    def get_by_email(self, session: Session, *, email: str) -> User | None:
        """Get user by email address."""
        statement = select(User).where(User.email == email)
        return session.exec(statement).first()

    def create(self, session: Session, *, obj_in: UserCreate) -> User:
        """Create a new user with hashed password."""
        db_obj = User.model_validate(
            obj_in, update={"hashed_password": get_password_hash(obj_in.password)}
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def update(
        self,
        session: Session,
        *,
        db_obj: User,
        obj_in: UserUpdate | dict[str, Any]
    ) -> User:
        """Update user with password hashing if needed."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        # Hash password if provided
        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        
        db_obj.sqlmodel_update(update_data)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def authenticate(self, session: Session, *, email: str, password: str) -> User | None:
        """Authenticate user with email and password."""
        user = self.get_by_email(session=session, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        """Check if user is active."""
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        """Check if user is superuser."""
        return user.is_superuser

    def _get_password_hash(self, password: str) -> str:
        """Get password hash (for internal use)."""
        from app.core.security import get_password_hash
        return get_password_hash(password)


# Create a singleton instance
user_service = UserService()
