"""Base service class with common CRUD operations."""

from typing import Any, Generic, TypeVar
import uuid

from sqlmodel import Session, SQLModel, select

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=SQLModel)


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
