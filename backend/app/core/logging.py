"""Logging configuration."""

import logging
import logging.config
import sys
from typing import Any

from app.core.config import settings


def setup_logging() -> None:
    """Setup logging configuration."""
    
    # Define log format
    log_format = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },

        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "default",
                "stream": sys.stdout,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "detailed",
                "filename": "logs/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
        },
        "loggers": {
            "app": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "sqlalchemy": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False,
            },
        },
        "root": {
            "level": "INFO",
            "handlers": ["console"],
        },
    }
    
    # Adjust log level based on environment
    if settings.ENVIRONMENT == "local":
        log_format["handlers"]["console"]["level"] = "DEBUG"
        log_format["loggers"]["app"]["level"] = "DEBUG"
        log_format["loggers"]["sqlalchemy"]["level"] = "INFO"
    
    # Apply logging configuration
    logging.config.dictConfig(log_format)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(f"app.{name}")
