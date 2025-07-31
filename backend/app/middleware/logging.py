"""Logging middleware configuration."""

import logging
import time
import uuid
from typing import Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with logging."""
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            }
        )
        
        # Process request
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Request completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "process_time": f"{process_time:.3f}s",
            }
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response


def setup_logging_middleware(app: FastAPI) -> None:
    """Setup logging middleware for the FastAPI application."""
    app.add_middleware(LoggingMiddleware)
