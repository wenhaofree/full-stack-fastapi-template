"""Base model classes for database models."""

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlmodel import Field, SQLModel


class BaseModel(SQLModel):
    """Base model with common fields for all database models."""
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(timezone.utc)

    def sqlmodel_update(self, update_data: dict[str, Any], *, update: dict[str, Any] | None = None) -> None:
        """Override to automatically update timestamp."""
        super().sqlmodel_update(update_data, update=update)
        self.update_timestamp()
