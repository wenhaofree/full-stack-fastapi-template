"""Health check and utility routes."""

from fastapi import APIRouter, Depends
from pydantic.networks import EmailStr

from app.dependencies.auth import get_current_active_superuser
from app.schemas.common import Message
from app.utils import generate_test_email, send_email

router = APIRouter()


@router.get("/")
async def health_check() -> dict[str, str]:
    """Basic health check endpoint."""
    return {"status": "healthy"}


@router.get("/detailed")
async def detailed_health_check() -> dict[str, str]:
    """Detailed health check endpoint."""
    # TODO: Add database connectivity check, external service checks, etc.
    return {
        "status": "healthy",
        "database": "connected",
        "version": "1.0.0"
    }


@router.post(
    "/test-email/",
    dependencies=[Depends(get_current_active_superuser)],
    status_code=201,
    response_model=Message,
)
async def test_email(email_to: EmailStr) -> Message:
    """Test email functionality."""
    email_data = generate_test_email(email_to=email_to)
    send_email(
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Test email sent")
