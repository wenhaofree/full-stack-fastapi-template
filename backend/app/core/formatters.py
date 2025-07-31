"""自定义日志格式化器。"""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional

from app.core.tracing import get_trace_context


class ColorCodes:
    """ANSI 颜色代码。"""
    
    # 重置
    RESET = '\033[0m'
    
    # 前景色
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # 亮色
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # 背景色
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    
    # 样式
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器。"""
    
    # 日志级别颜色映射
    LEVEL_COLORS = {
        'DEBUG': ColorCodes.BRIGHT_BLUE,
        'INFO': ColorCodes.BRIGHT_GREEN,
        'WARNING': ColorCodes.BRIGHT_YELLOW,
        'ERROR': ColorCodes.BRIGHT_RED,
        'CRITICAL': ColorCodes.BG_RED + ColorCodes.BRIGHT_WHITE,
    }
    
    def __init__(
        self, 
        fmt: Optional[str] = None, 
        datefmt: Optional[str] = None,
        use_colors: bool = True
    ):
        super().__init__(fmt, datefmt)
        self.use_colors = use_colors and self._supports_color()
    
    def _supports_color(self) -> bool:
        """检查终端是否支持颜色输出。"""
        # 检查是否在支持颜色的终端中
        return (
            hasattr(sys.stderr, "isatty") and sys.stderr.isatty() and
            sys.platform != "win32"  # Windows 需要特殊处理
        )
    
    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录。"""
        # 添加追踪上下文信息
        trace_context = get_trace_context()
        for key, value in trace_context.items():
            if value:
                setattr(record, key, value)
        
        # 格式化基础消息
        formatted = super().format(record)
        
        if not self.use_colors:
            return formatted
        
        # 应用颜色
        level_color = self.LEVEL_COLORS.get(record.levelname, '')
        if level_color:
            # 为日志级别添加颜色
            formatted = formatted.replace(
                record.levelname,
                f"{level_color}{record.levelname}{ColorCodes.RESET}"
            )
            
            # 为追踪ID添加颜色
            if hasattr(record, 'trace_id') and record.trace_id:
                formatted = formatted.replace(
                    record.trace_id,
                    f"{ColorCodes.CYAN}{record.trace_id}{ColorCodes.RESET}"
                )
        
        return formatted


class StructuredFormatter(logging.Formatter):
    """结构化日志格式化器（JSON格式）。"""
    
    def __init__(self, include_trace: bool = True):
        super().__init__()
        self.include_trace = include_trace
    
    def format(self, record: logging.LogRecord) -> str:
        """格式化为JSON格式。"""
        # 基础日志信息
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # 添加追踪信息
        if self.include_trace:
            trace_context = get_trace_context()
            log_data.update({k: v for k, v in trace_context.items() if v})
        
        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # 添加额外字段
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)
        
        # 从record中提取其他自定义字段
        reserved_fields = {
            'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
            'filename', 'module', 'exc_info', 'exc_text', 'stack_info',
            'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
            'thread', 'threadName', 'processName', 'process', 'getMessage',
            'extra_fields', 'message', 'asctime'
        }

        for key, value in record.__dict__.items():
            if key not in reserved_fields and not key.startswith('_'):
                log_data[key] = value
        
        return json.dumps(log_data, ensure_ascii=False, default=str)


class TraceFormatter(logging.Formatter):
    """带追踪信息的格式化器。"""
    
    def __init__(
        self, 
        fmt: Optional[str] = None, 
        datefmt: Optional[str] = None,
        include_trace: bool = True
    ):
        # 如果没有提供格式，使用默认的带追踪信息的格式
        if fmt is None and include_trace:
            fmt = (
                "%(asctime)s | %(levelname)-8s | "
                "%(trace_id)s | %(request_id)s | "
                "%(name)s | %(message)s"
            )
        elif fmt is None:
            fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        
        super().__init__(fmt, datefmt)
        self.include_trace = include_trace
    
    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录，添加追踪信息。"""
        if self.include_trace:
            # 添加追踪上下文信息
            trace_context = get_trace_context()
            
            # 设置默认值以避免格式化错误
            record.trace_id = trace_context.get('trace_id') or 'N/A'
            record.request_id = trace_context.get('request_id') or 'N/A'
            record.user_id = trace_context.get('user_id') or 'N/A'
        
        return super().format(record)


class DevelopmentFormatter(ColoredFormatter, TraceFormatter):
    """开发环境格式化器，结合彩色输出和追踪信息。"""
    
    def __init__(self):
        # 开发环境的详细格式
        fmt = (
            "%(asctime)s | %(levelname)-8s | "
            "%(trace_id)s | %(name)s:%(lineno)d | %(message)s"
        )
        ColoredFormatter.__init__(self, fmt=fmt, use_colors=True)
        TraceFormatter.__init__(self, fmt=fmt, include_trace=True)
    
    def format(self, record: logging.LogRecord) -> str:
        """结合追踪信息和彩色输出。"""
        # 先添加追踪信息
        TraceFormatter.format(self, record)
        # 再应用彩色格式
        return ColoredFormatter.format(self, record)


class ProductionFormatter(StructuredFormatter):
    """生产环境格式化器，使用JSON格式。"""
    
    def __init__(self):
        super().__init__(include_trace=True)
