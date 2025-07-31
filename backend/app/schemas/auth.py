"""Authentication related schemas."""

from typing import Optional

from sqlmodel import Field, SQLModel


class Token(SQLModel):
    """JSON payload containing access token."""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    """Contents of JWT token."""
    sub: Optional[str] = None


class NewPassword(SQLModel):
    """Schema for password reset."""
    token: str
    new_password: str = Field(min_length=8, max_length=40)
