"""日志工具函数和装饰器。"""

import functools
import logging
import time
from typing import Any, Callable, Dict, Optional, TypeVar

from app.core.tracing import create_child_trace, get_trace_context

F = TypeVar('F', bound=Callable[..., Any])


def get_logger(name: str) -> logging.Logger:
    """获取日志记录器实例。"""
    return logging.getLogger(f"app.{name}")


def log_function_call(
    logger: Optional[logging.Logger] = None,
    level: int = logging.INFO,
    include_args: bool = False,
    include_result: bool = False,
    include_timing: bool = True,
) -> Callable[[F], F]:
    """函数调用日志装饰器。
    
    Args:
        logger: 日志记录器，如果为None则使用函数所在模块的logger
        level: 日志级别
        include_args: 是否记录函数参数
        include_result: 是否记录函数返回值
        include_timing: 是否记录执行时间
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 获取logger
            func_logger = logger or get_logger(func.__module__.split('.')[-1])
            
            # 创建子追踪上下文
            with create_child_trace():
                start_time = time.time()
                
                # 准备日志信息
                log_data = {
                    "function_name": func.__name__,
                    "function_module": func.__module__,
                }
                
                if include_args:
                    log_data.update({
                        "function_args": str(args) if args else None,
                        "function_kwargs": str(kwargs) if kwargs else None,
                    })
                
                # 记录函数开始
                func_logger.log(level, f"函数调用开始: {func.__name__}", extra=log_data)
                
                try:
                    # 执行函数
                    result = func(*args, **kwargs)
                    
                    # 计算执行时间
                    execution_time = time.time() - start_time
                    
                    # 准备完成日志
                    complete_log_data = log_data.copy()
                    if include_timing:
                        complete_log_data["execution_time"] = f"{execution_time:.3f}s"
                    if include_result:
                        complete_log_data["result"] = str(result)
                    
                    # 记录函数完成
                    func_logger.log(
                        level, 
                        f"函数调用完成: {func.__name__}", 
                        extra=complete_log_data
                    )
                    
                    return result
                    
                except Exception as e:
                    # 计算执行时间
                    execution_time = time.time() - start_time
                    
                    # 准备错误日志
                    error_log_data = log_data.copy()
                    error_log_data.update({
                        "execution_time": f"{execution_time:.3f}s",
                        "exception_type": type(e).__name__,
                        "exception_message": str(e),
                    })
                    
                    # 记录函数异常
                    func_logger.error(
                        f"函数调用异常: {func.__name__}", 
                        extra=error_log_data,
                        exc_info=True
                    )
                    
                    # 重新抛出异常
                    raise
        
        return wrapper
    return decorator


def log_async_function_call(
    logger: Optional[logging.Logger] = None,
    level: int = logging.INFO,
    include_args: bool = False,
    include_result: bool = False,
    include_timing: bool = True,
) -> Callable[[F], F]:
    """异步函数调用日志装饰器。"""
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # 获取logger
            func_logger = logger or get_logger(func.__module__.split('.')[-1])
            
            # 创建子追踪上下文
            with create_child_trace():
                start_time = time.time()
                
                # 准备日志信息
                log_data = {
                    "function_name": func.__name__,
                    "function_module": func.__module__,
                    "is_async": True,
                }
                
                if include_args:
                    log_data.update({
                        "function_args": str(args) if args else None,
                        "function_kwargs": str(kwargs) if kwargs else None,
                    })
                
                # 记录函数开始
                func_logger.log(level, f"异步函数调用开始: {func.__name__}", extra=log_data)
                
                try:
                    # 执行异步函数
                    result = await func(*args, **kwargs)
                    
                    # 计算执行时间
                    execution_time = time.time() - start_time
                    
                    # 准备完成日志
                    complete_log_data = log_data.copy()
                    if include_timing:
                        complete_log_data["execution_time"] = f"{execution_time:.3f}s"
                    if include_result:
                        complete_log_data["result"] = str(result)
                    
                    # 记录函数完成
                    func_logger.log(
                        level, 
                        f"异步函数调用完成: {func.__name__}", 
                        extra=complete_log_data
                    )
                    
                    return result
                    
                except Exception as e:
                    # 计算执行时间
                    execution_time = time.time() - start_time
                    
                    # 准备错误日志
                    error_log_data = log_data.copy()
                    error_log_data.update({
                        "execution_time": f"{execution_time:.3f}s",
                        "exception_type": type(e).__name__,
                        "exception_message": str(e),
                    })
                    
                    # 记录函数异常
                    func_logger.error(
                        f"异步函数调用异常: {func.__name__}", 
                        extra=error_log_data,
                        exc_info=True
                    )
                    
                    # 重新抛出异常
                    raise
        
        return wrapper
    return decorator


class StructuredLogger:
    """结构化日志记录器。"""
    
    def __init__(self, name: str):
        self.logger = get_logger(name)
        self.name = name
    
    def _log_with_context(
        self, 
        level: int, 
        message: str, 
        extra_data: Optional[Dict[str, Any]] = None,
        exc_info: bool = False
    ) -> None:
        """带上下文信息的日志记录。"""
        # 获取追踪上下文
        trace_context = get_trace_context()
        
        # 合并额外数据
        log_data = {}
        if extra_data:
            log_data.update(extra_data)
        
        # 添加追踪信息
        log_data.update({k: v for k, v in trace_context.items() if v})
        
        # 记录日志
        self.logger.log(level, message, extra=log_data, exc_info=exc_info)
    
    def debug(self, message: str, **kwargs) -> None:
        """记录DEBUG级别日志。"""
        self._log_with_context(logging.DEBUG, message, kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """记录INFO级别日志。"""
        self._log_with_context(logging.INFO, message, kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """记录WARNING级别日志。"""
        self._log_with_context(logging.WARNING, message, kwargs)
    
    def error(self, message: str, exc_info: bool = False, **kwargs) -> None:
        """记录ERROR级别日志。"""
        self._log_with_context(logging.ERROR, message, kwargs, exc_info=exc_info)
    
    def critical(self, message: str, exc_info: bool = False, **kwargs) -> None:
        """记录CRITICAL级别日志。"""
        self._log_with_context(logging.CRITICAL, message, kwargs, exc_info=exc_info)
    
    def exception(self, message: str, **kwargs) -> None:
        """记录异常日志（自动包含异常信息）。"""
        self._log_with_context(logging.ERROR, message, kwargs, exc_info=True)

    def log(self, level: int, message: str, **kwargs) -> None:
        """记录指定级别的日志。"""
        self._log_with_context(level, message, kwargs)


def get_structured_logger(name: str) -> StructuredLogger:
    """获取结构化日志记录器。"""
    return StructuredLogger(name)
