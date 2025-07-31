"""专业的日志配置模块。"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Dict, Any

from pythonjsonlogger import jsonlogger

from app.core.config import settings
from app.core.tracing import get_trace_context


class TraceContextFilter(logging.Filter):
    """添加追踪上下文信息到日志记录。"""
    
    def filter(self, record):
        """为日志记录添加追踪信息。"""
        trace_context = get_trace_context()
        record.trace_id = trace_context.get('trace_id') or 'N/A'
        record.request_id = trace_context.get('request_id') or 'N/A'
        record.user_id = trace_context.get('user_id') or 'N/A'
        return True


class ColoredConsoleFormatter(logging.Formatter):
    """彩色控制台格式化器。"""
    
    # ANSI 颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
        'RESET': '\033[0m'        # 重置
    }
    
    def __init__(self, use_colors: bool = True):
        super().__init__()
        self.use_colors = use_colors and self._supports_color()
    
    def _supports_color(self) -> bool:
        """检查终端是否支持颜色。"""
        return (
            hasattr(sys.stderr, "isatty") and sys.stderr.isatty() and
            os.getenv('TERM') != 'dumb'
        )
    
    def format(self, record):
        """格式化日志记录。"""
        # 基础格式
        if hasattr(record, 'trace_id'):
            log_format = "%(asctime)s | %(levelname)-8s | %(trace_id)s | %(name)s | %(message)s"
        else:
            log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

        formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")
        formatted = formatter.format(record)

        # 添加颜色
        if self.use_colors:
            level_color = self.COLORS.get(record.levelname, '')
            if level_color:
                formatted = formatted.replace(
                    record.levelname,
                    f"{level_color}{record.levelname}{self.COLORS['RESET']}"
                )

        # 添加路由相关的详细信息（仅对路由日志）
        if hasattr(record, 'input_parameters') or hasattr(record, 'output_result'):
            details = []

            # 添加入参信息
            if hasattr(record, 'input_parameters') and record.input_parameters:
                params_str = str(record.input_parameters)
                if len(params_str) > 200:
                    params_str = params_str[:200] + "..."
                details.append(f"📥 入参: {params_str}")

            # 添加出参信息
            if hasattr(record, 'output_result') and record.output_result is not None:
                result_str = str(record.output_result)
                if len(result_str) > 200:
                    result_str = result_str[:200] + "..."
                details.append(f"📤 出参: {result_str}")

            # 添加执行时间
            if hasattr(record, 'execution_time'):
                details.append(f"⏱️  耗时: {record.execution_time}")

            if details:
                formatted += "\n    " + " | ".join(details)

        return formatted


class JSONFormatter(jsonlogger.JsonFormatter):
    """自定义JSON格式化器。"""
    
    def add_fields(self, log_record, record, message_dict):
        """添加自定义字段到JSON日志。"""
        super().add_fields(log_record, record, message_dict)
        
        # 添加追踪信息
        if hasattr(record, 'trace_id'):
            log_record['trace_id'] = record.trace_id
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id
        if hasattr(record, 'user_id') and record.user_id != 'N/A':
            log_record['user_id'] = record.user_id
        
        # 添加环境信息
        log_record['environment'] = settings.ENVIRONMENT
        
        # 重新组织字段顺序
        ordered_record = {
            'timestamp': log_record.get('asctime'),
            'level': log_record.get('levelname'),
            'logger': log_record.get('name'),
            'message': log_record.get('message'),
            'trace_id': log_record.get('trace_id'),
            'request_id': log_record.get('request_id'),
            'user_id': log_record.get('user_id'),
            'environment': log_record.get('environment'),
        }
        
        # 添加其他字段
        for key, value in log_record.items():
            if key not in ordered_record:
                ordered_record[key] = value
        
        # 清空原记录并添加有序字段
        log_record.clear()
        log_record.update({k: v for k, v in ordered_record.items() if v is not None})


def ensure_log_directory():
    """确保日志目录存在。"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    return log_dir


def get_log_level() -> int:
    """获取日志级别。"""
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
    }
    return level_map.get(settings.LOG_LEVEL, logging.INFO)


def create_console_handler() -> logging.Handler:
    """创建控制台处理器。"""
    handler = logging.StreamHandler(sys.stdout)
    
    if settings.LOG_FORMAT in ["console", "both"]:
        # 开发环境使用彩色格式
        formatter = ColoredConsoleFormatter(use_colors=settings.ENVIRONMENT == "local")
    else:
        # JSON格式
        formatter = JSONFormatter()
    
    handler.setFormatter(formatter)
    handler.addFilter(TraceContextFilter())
    return handler


def create_file_handler() -> logging.Handler:
    """创建文件处理器（带轮转）。"""
    if not settings.LOG_FILE_ENABLED:
        return None
    
    log_dir = ensure_log_directory()
    log_file = log_dir / "app.log"
    
    # 使用时间和大小轮转
    handler = logging.handlers.TimedRotatingFileHandler(
        filename=str(log_file),
        when="midnight",
        interval=1,
        backupCount=settings.LOG_FILE_BACKUP_COUNT,
        encoding="utf-8"
    )
    
    # 同时限制文件大小
    handler.maxBytes = settings.LOG_FILE_MAX_SIZE * 1024 * 1024  # MB to bytes
    
    # 文件始终使用JSON格式
    formatter = JSONFormatter()
    handler.setFormatter(formatter)
    handler.addFilter(TraceContextFilter())
    
    return handler


def create_error_file_handler() -> logging.Handler:
    """创建错误日志文件处理器。"""
    if not settings.LOG_FILE_ENABLED:
        return None
    
    log_dir = ensure_log_directory()
    error_log_file = log_dir / "error.log"
    
    handler = logging.handlers.TimedRotatingFileHandler(
        filename=str(error_log_file),
        when="midnight",
        interval=1,
        backupCount=settings.LOG_FILE_BACKUP_COUNT,
        encoding="utf-8"
    )
    
    handler.setLevel(logging.ERROR)
    handler.maxBytes = settings.LOG_FILE_MAX_SIZE * 1024 * 1024
    
    formatter = JSONFormatter()
    handler.setFormatter(formatter)
    handler.addFilter(TraceContextFilter())
    
    return handler


def setup_professional_logging():
    """设置专业的日志配置。"""
    # 获取根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(get_log_level())
    
    # 清除现有处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 添加控制台处理器
    console_handler = create_console_handler()
    console_handler.setLevel(get_log_level())
    root_logger.addHandler(console_handler)
    
    # 添加文件处理器
    if settings.LOG_FILE_ENABLED:
        file_handler = create_file_handler()
        if file_handler:
            file_handler.setLevel(get_log_level())
            root_logger.addHandler(file_handler)
        
        # 添加错误文件处理器
        error_handler = create_error_file_handler()
        if error_handler:
            root_logger.addHandler(error_handler)
    
    # 配置特定日志记录器
    configure_specific_loggers()
    
    # 记录日志系统启动信息
    logger = logging.getLogger("app.logging")
    logger.info(
        "日志系统已启动",
        extra={
            "environment": settings.ENVIRONMENT,
            "log_level": settings.LOG_LEVEL,
            "log_format": settings.LOG_FORMAT,
            "file_enabled": settings.LOG_FILE_ENABLED,
        }
    )


def configure_specific_loggers():
    """配置特定的日志记录器。"""
    log_level = get_log_level()
    
    # 应用日志
    app_logger = logging.getLogger("app")
    app_logger.setLevel(log_level)
    
    # FastAPI/Uvicorn日志
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(logging.INFO if log_level == logging.DEBUG else logging.WARNING)
    
    # SQLAlchemy日志
    sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
    if log_level == logging.DEBUG:
        sqlalchemy_logger.setLevel(logging.INFO)  # 显示SQL查询
    else:
        sqlalchemy_logger.setLevel(logging.WARNING)
    
    # 禁用一些噪音日志
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
