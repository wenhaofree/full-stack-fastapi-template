"""Base model classes for database models."""

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

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


class SoftDeleteModel(BaseModel):
    """Base model with soft delete functionality."""

    deleted_at: Optional[datetime] = Field(default=None, description="软删除时间，有值表示已删除")

    def soft_delete(self) -> None:
        """执行软删除操作。"""
        self.deleted_at = datetime.now(timezone.utc)
        self.update_timestamp()

    def restore(self) -> None:
        """恢复软删除的记录。"""
        self.deleted_at = None
        self.update_timestamp()

    @property
    def is_deleted(self) -> bool:
        """检查记录是否已被软删除。"""
        return self.deleted_at is not None

    @property
    def is_active_record(self) -> bool:
        """检查记录是否为活跃状态（未删除）。"""
        return self.deleted_at is None
