"""Error handling middleware."""

import logging
import time
from typing import Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.exceptions.handlers import setup_exception_handlers

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for handling errors and logging."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and handle errors."""
        start_time = time.time()
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log successful requests
            logger.info(
                f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s"
            )
            
            return response
            
        except Exception as exc:
            process_time = time.time() - start_time
            
            # Log error
            logger.error(
                f"{request.method} {request.url.path} - Error: {exc} - {process_time:.3f}s",
                exc_info=True
            )
            
            # Re-raise to let exception handlers deal with it
            raise exc


def setup_error_middleware(app: FastAPI) -> None:
    """Setup error handling middleware and exception handlers."""
    # Add error handling middleware
    app.add_middleware(ErrorHandlingMiddleware)
    
    # Setup exception handlers
    setup_exception_handlers(app)
