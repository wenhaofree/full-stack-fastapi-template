"""Base service class with common CRUD operations."""

from typing import Any, Generic, TypeVar
import uuid

from sqlmodel import Session, SQLModel, select

from app.models.base import SoftDeleteModel

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=SQLModel)
SoftDeleteModelType = TypeVar("SoftDeleteModelType", bound=SoftDeleteModel)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base service class with common CRUD operations."""

    def __init__(self, model: type[ModelType]):
        """Initialize the service with a model class."""
        self.model = model

    def get(self, session: Session, id: uuid.UUID) -> ModelType | None:
        """Get a single record by ID."""
        return session.get(self.model, id)

    def get_multi(
        self, session: Session, *, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        """Get multiple records with pagination."""
        statement = select(self.model).offset(skip).limit(limit)
        return list(session.exec(statement).all())

    def create(self, session: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record."""
        db_obj = self.model.model_validate(obj_in)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def update(
        self,
        session: Session,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        """Update an existing record."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        db_obj.sqlmodel_update(update_data)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def delete(self, session: Session, *, id: uuid.UUID) -> ModelType | None:
        """Delete a record by ID."""
        obj = session.get(self.model, id)
        if obj:
            session.delete(obj)
            session.commit()
        return obj


class SoftDeleteService(Generic[SoftDeleteModelType, CreateSchemaType, UpdateSchemaType]):
    """Base service class with soft delete functionality."""

    def __init__(self, model: type[SoftDeleteModelType]):
        """Initialize the service with a soft delete model class."""
        self.model = model

    def get(self, session: Session, id: uuid.UUID, *, include_deleted: bool = False) -> SoftDeleteModelType | None:
        """Get a single record by ID, optionally including deleted records."""
        obj = session.get(self.model, id)
        if obj and not include_deleted and obj.is_deleted:
            return None
        return obj

    def get_multi(
        self,
        session: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False
    ) -> list[SoftDeleteModelType]:
        """Get multiple records with pagination, optionally including deleted records."""
        statement = select(self.model)

        if not include_deleted:
            statement = statement.where(self.model.deleted_at.is_(None))

        statement = statement.offset(skip).limit(limit)
        return list(session.exec(statement).all())

    def create(self, session: Session, *, obj_in: CreateSchemaType) -> SoftDeleteModelType:
        """Create a new record."""
        db_obj = self.model.model_validate(obj_in)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def update(
        self,
        session: Session,
        *,
        db_obj: SoftDeleteModelType,
        obj_in: UpdateSchemaType | dict[str, Any]
    ) -> SoftDeleteModelType:
        """Update an existing record."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        db_obj.sqlmodel_update(update_data)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def soft_delete(self, session: Session, *, id: uuid.UUID) -> SoftDeleteModelType | None:
        """Soft delete a record by ID."""
        obj = self.get(session, id, include_deleted=False)
        if obj:
            obj.soft_delete()
            session.add(obj)
            session.commit()
            session.refresh(obj)
        return obj

    def restore(self, session: Session, *, id: uuid.UUID) -> SoftDeleteModelType | None:
        """Restore a soft deleted record by ID."""
        obj = session.get(self.model, id)
        if obj and obj.is_deleted:
            obj.restore()
            session.add(obj)
            session.commit()
            session.refresh(obj)
        return obj

    def delete(self, session: Session, *, id: uuid.UUID) -> SoftDeleteModelType | None:
        """Permanently delete a record by ID."""
        obj = session.get(self.model, id)
        if obj:
            session.delete(obj)
            session.commit()
        return obj
