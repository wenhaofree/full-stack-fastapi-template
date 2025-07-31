"""增强的日志配置系统。"""

import logging
import logging.config
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Any, Dict

from app.core.config import settings
from app.core.formatters import (
    DevelopmentFormatter,
    ProductionFormatter,
    StructuredFormatter,
    TraceFormatter,
)


def ensure_log_directory() -> None:
    """确保日志目录存在。"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)


def get_log_level_from_config() -> str:
    """从配置中获取日志级别。"""
    return settings.LOG_LEVEL


def get_log_config() -> dict:
    """根据环境获取日志配置。"""
    ensure_log_directory()

    # 从配置获取日志级别
    log_level = get_log_level_from_config()

    # 基础配置
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {},
        "handlers": {},
        "loggers": {},
        "root": {
            "level": log_level,
            "handlers": ["console"],
        },
    }

    if settings.ENVIRONMENT == "local":
        # 开发环境：彩色输出 + 详细信息
        config["formatters"] = {
            "development": {
                "()": DevelopmentFormatter,
            },
            "structured": {
                "()": StructuredFormatter,
                "include_trace": True,
            },
        }

        config["handlers"] = {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "development",
                "stream": sys.stdout,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "structured",
                "filename": "logs/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf-8",
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "structured",
                "filename": "logs/error.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf-8",
            },
        }

        config["loggers"] = {
            "app": {
                "level": log_level,
                "handlers": ["console", "file", "error_file"],
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO" if log_level == "DEBUG" else log_level,
                "handlers": ["console"],
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "level": "INFO" if log_level == "DEBUG" else "WARNING",
                "handlers": ["console"],
                "propagate": False,
            },
            "sqlalchemy.pool": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False,
            },
        }

    elif settings.ENVIRONMENT == "production":
        # 生产环境：JSON格式 + 性能优化
        config["formatters"] = {
            "production": {
                "()": ProductionFormatter,
            },
            "simple": {
                "()": TraceFormatter,
                "fmt": "%(asctime)s | %(levelname)s | %(trace_id)s | %(name)s | %(message)s",
                "include_trace": True,
            },
        }

        # 生产环境默认使用INFO级别，除非明确设置了其他级别
        prod_log_level = log_level if log_level in ["WARNING", "ERROR", "CRITICAL"] else "INFO"

        config["handlers"] = {
            "console": {
                "class": "logging.StreamHandler",
                "level": prod_log_level,
                "formatter": "simple",
                "stream": sys.stdout,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": prod_log_level,
                "formatter": "production",
                "filename": "logs/app.log",
                "maxBytes": 52428800,  # 50MB
                "backupCount": 10,
                "encoding": "utf-8",
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "production",
                "filename": "logs/error.log",
                "maxBytes": 52428800,  # 50MB
                "backupCount": 10,
                "encoding": "utf-8",
            },
        }

        config["loggers"] = {
            "app": {
                "level": prod_log_level,
                "handlers": ["console", "file", "error_file"],
                "propagate": False,
            },
            "uvicorn": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False,
            },
            "sqlalchemy": {
                "level": "WARNING",
                "handlers": ["file"],
                "propagate": False,
            },
        }

    else:
        # 测试/其他环境：简单格式
        config["formatters"] = {
            "simple": {
                "()": TraceFormatter,
                "fmt": "%(asctime)s | %(levelname)s | %(trace_id)s | %(name)s | %(message)s",
                "include_trace": True,
            },
        }

        config["handlers"] = {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "simple",
                "stream": sys.stdout,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "simple",
                "filename": "logs/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf-8",
            },
        }

        config["loggers"] = {
            "app": {
                "level": log_level,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "uvicorn": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False,
            },
            "sqlalchemy": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False,
            },
        }

    return config


def setup_logging() -> None:
    """设置日志配置。"""
    config = get_log_config()
    logging.config.dictConfig(config)

    # 记录日志系统启动信息
    logger = get_logger("logging")
    logger.info(f"日志系统已启动 - 环境: {settings.ENVIRONMENT}")
    logger.debug(f"日志配置: {config}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(f"app.{name}")
