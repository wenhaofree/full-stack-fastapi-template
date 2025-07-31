"""路由函数日志装饰器。"""

import functools
import inspect
import json
import logging
from typing import Any, Callable, Dict, Optional, TypeVar

from fastapi import Request, Response
from pydantic import BaseModel

from app.core.logger import get_structured_logger
from app.core.tracing import create_child_trace

F = TypeVar('F', bound=Callable[..., Any])


class RouteLogger:
    """路由日志记录器。"""
    
    def __init__(self, logger_name: str = "app.route"):
        self.logger = get_structured_logger(logger_name)
        # 敏感字段列表
        self.sensitive_fields = {
            'password', 'token', 'secret', 'key', 'authorization',
            'passwd', 'pwd', 'auth', 'credential', 'api_key', 'refresh_token'
        }
    
    def _filter_sensitive_data(self, data: Any) -> Any:
        """过滤敏感数据。"""
        if isinstance(data, dict):
            filtered = {}
            for key, value in data.items():
                if any(sensitive in str(key).lower() for sensitive in self.sensitive_fields):
                    filtered[key] = "***FILTERED***"
                elif isinstance(value, (dict, list)):
                    filtered[key] = self._filter_sensitive_data(value)
                else:
                    filtered[key] = value
            return filtered
        elif isinstance(data, list):
            return [self._filter_sensitive_data(item) for item in data]
        elif isinstance(data, BaseModel):
            # 处理Pydantic模型
            return self._filter_sensitive_data(data.model_dump())
        else:
            return data
    
    def _serialize_value(self, value: Any) -> Any:
        """序列化值为可JSON化的格式。"""
        try:
            if isinstance(value, BaseModel):
                return value.model_dump()
            elif isinstance(value, (str, int, float, bool, type(None))):
                return value
            elif isinstance(value, (list, tuple)):
                return [self._serialize_value(item) for item in value]
            elif isinstance(value, dict):
                return {k: self._serialize_value(v) for k, v in value.items()}
            elif self._is_response_object(value):
                # 处理FastAPI Response对象
                return self._serialize_response(value)
            elif hasattr(value, '__dict__'):
                # 对于其他有__dict__的对象，尝试序列化其属性
                try:
                    obj_dict = {}
                    for k, v in value.__dict__.items():
                        if not k.startswith('_'):  # 跳过私有属性
                            obj_dict[k] = self._serialize_value(v)
                    return obj_dict if obj_dict else f"<{type(value).__name__}>"
                except:
                    return f"<{type(value).__name__}>"
            else:
                return str(value)
        except Exception:
            return f"<{type(value).__name__}>"

    def _is_response_object(self, value: Any) -> bool:
        """检查是否是Response对象。"""
        return (
            hasattr(value, 'status_code') and
            hasattr(value, 'headers') and
            (hasattr(value, 'body') or hasattr(value, 'content'))
        )

    def _serialize_response(self, response: Any) -> Dict[str, Any]:
        """序列化Response对象。"""
        try:
            result = {
                "type": type(response).__name__,
                "status_code": getattr(response, 'status_code', None),
                "headers": dict(getattr(response, 'headers', {})),
            }

            # 尝试获取响应体内容
            if hasattr(response, 'body'):
                body = response.body
                if isinstance(body, bytes):
                    try:
                        # 尝试解码为JSON
                        import json
                        body_str = body.decode('utf-8')
                        if body_str.strip().startswith(('{', '[')):
                            result["body"] = json.loads(body_str)
                        else:
                            result["body"] = body_str
                    except:
                        result["body"] = f"<bytes: {len(body)} bytes>"
                else:
                    result["body"] = str(body)
            elif hasattr(response, 'content'):
                content = response.content
                if isinstance(content, (str, dict, list)):
                    result["content"] = content
                else:
                    result["content"] = str(content)

            return result
        except Exception as e:
            return {
                "type": type(response).__name__,
                "error": f"序列化失败: {str(e)}"
            }

    def _extract_route_info(self, func: Callable) -> Dict[str, Any]:
        """提取路由函数信息。"""
        return {
            "function_name": func.__name__,
            "function_module": func.__module__,
            "function_file": inspect.getfile(func) if hasattr(func, '__code__') else None,
        }
    
    def _extract_parameters(self, func: Callable, args: tuple, kwargs: dict) -> Dict[str, Any]:
        """提取函数参数。"""
        try:
            # 获取函数签名
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # 序列化参数
            parameters = {}
            for name, value in bound_args.arguments.items():
                # 跳过Request和Response对象
                if isinstance(value, (Request, Response)):
                    parameters[name] = f"<{type(value).__name__}>"
                else:
                    serialized_value = self._serialize_value(value)
                    parameters[name] = self._filter_sensitive_data(serialized_value)
            
            return parameters
        except Exception as e:
            self.logger.warning(f"提取函数参数失败: {e}")
            return {"error": f"参数提取失败: {str(e)}"}
    
    def log_route(
        self,
        include_args: bool = True,
        include_result: bool = True,
        include_timing: bool = True,
        log_level: int = logging.DEBUG,
    ) -> Callable[[F], F]:
        """路由函数日志装饰器。
        
        Args:
            include_args: 是否记录函数参数
            include_result: 是否记录函数返回值
            include_timing: 是否记录执行时间
            log_level: 日志级别
        """
        def decorator(func: F) -> F:
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                # 创建子追踪上下文
                with create_child_trace():
                    import time
                    start_time = time.time()
                    
                    # 提取路由信息
                    route_info = self._extract_route_info(func)
                    
                    # 提取参数信息
                    parameters = {}
                    if include_args:
                        parameters = self._extract_parameters(func, args, kwargs)
                    
                    # 记录函数开始
                    log_data = {
                        **route_info,
                        "operation": "route_start",
                        "is_async": True,
                    }
                    
                    if parameters:
                        log_data["parameters"] = parameters
                    
                    self.logger.log(
                        log_level,
                        f"路由函数开始: {func.__name__}",
                        **log_data
                    )
                    
                    try:
                        # 执行函数
                        result = await func(*args, **kwargs)
                        
                        # 计算执行时间
                        execution_time = time.time() - start_time
                        
                        # 准备完成日志
                        complete_log_data = {
                            **route_info,
                            "operation": "route_complete",
                            "is_async": True,
                        }

                        if include_timing:
                            complete_log_data["execution_time"] = f"{execution_time:.3f}s"

                        # 添加入参信息（如果启用）
                        if include_args and parameters:
                            complete_log_data["input_parameters"] = parameters

                        # 添加出参信息（如果启用）
                        if include_result:
                            serialized_result = self._serialize_value(result)
                            filtered_result = self._filter_sensitive_data(serialized_result)
                            complete_log_data["output_result"] = filtered_result
                        
                        # 记录函数完成
                        self.logger.log(
                            log_level,
                            f"路由函数完成: {func.__name__}",
                            **complete_log_data
                        )
                        
                        return result
                        
                    except Exception as e:
                        # 计算执行时间
                        execution_time = time.time() - start_time
                        
                        # 准备错误日志
                        error_log_data = {
                            **route_info,
                            "operation": "route_error",
                            "is_async": True,
                            "execution_time": f"{execution_time:.3f}s",
                            "exception_type": type(e).__name__,
                            "exception_message": str(e),
                        }

                        # 添加入参信息到错误日志（便于调试）
                        if include_args and parameters:
                            error_log_data["input_parameters"] = parameters
                        
                        # 记录函数异常
                        self.logger.error(
                            f"路由函数异常: {func.__name__}",
                            exc_info=True,
                            **error_log_data
                        )
                        
                        # 重新抛出异常
                        raise
            
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                # 创建子追踪上下文
                with create_child_trace():
                    import time
                    start_time = time.time()
                    
                    # 提取路由信息
                    route_info = self._extract_route_info(func)
                    
                    # 提取参数信息
                    parameters = {}
                    if include_args:
                        parameters = self._extract_parameters(func, args, kwargs)
                    
                    # 记录函数开始
                    log_data = {
                        **route_info,
                        "operation": "route_start",
                        "is_async": False,
                    }
                    
                    if parameters:
                        log_data["parameters"] = parameters
                    
                    self.logger.log(
                        log_level,
                        f"路由函数开始: {func.__name__}",
                        **log_data
                    )
                    
                    try:
                        # 执行函数
                        result = func(*args, **kwargs)
                        
                        # 计算执行时间
                        execution_time = time.time() - start_time
                        
                        # 准备完成日志
                        complete_log_data = {
                            **route_info,
                            "operation": "route_complete",
                            "is_async": False,
                        }
                        
                        if include_timing:
                            complete_log_data["execution_time"] = f"{execution_time:.3f}s"
                        
                        if include_result:
                            serialized_result = self._serialize_value(result)
                            filtered_result = self._filter_sensitive_data(serialized_result)
                            complete_log_data["result"] = filtered_result
                        
                        # 记录函数完成
                        self.logger.log(
                            log_level,
                            f"路由函数完成: {func.__name__}",
                            **complete_log_data
                        )
                        
                        return result
                        
                    except Exception as e:
                        # 计算执行时间
                        execution_time = time.time() - start_time
                        
                        # 准备错误日志
                        error_log_data = {
                            **route_info,
                            "operation": "route_error",
                            "is_async": False,
                            "execution_time": f"{execution_time:.3f}s",
                            "exception_type": type(e).__name__,
                            "exception_message": str(e),
                        }
                        
                        # 记录函数异常
                        self.logger.error(
                            f"路由函数异常: {func.__name__}",
                            exc_info=True,
                            **error_log_data
                        )
                        
                        # 重新抛出异常
                        raise
            
            # 根据函数类型返回相应的包装器
            if inspect.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator


# 创建默认的路由日志记录器实例
default_route_logger = RouteLogger()

# 便捷的装饰器函数
def log_route_debug(
    include_args: Optional[bool] = None,
    include_result: Optional[bool] = None,
    include_timing: bool = True,
) -> Callable[[F], F]:
    """DEBUG级别的路由日志装饰器。"""
    from app.core.config import settings

    # 如果没有明确指定，则使用配置文件的设置
    if include_args is None:
        include_args = settings.LOG_FUNCTION_PARAMS
    if include_result is None:
        include_result = settings.LOG_FUNCTION_PARAMS

    return default_route_logger.log_route(
        include_args=include_args,
        include_result=include_result,
        include_timing=include_timing,
        log_level=logging.DEBUG,
    )


def log_route_info(
    include_args: bool = False,
    include_result: bool = False,
    include_timing: bool = True,
) -> Callable[[F], F]:
    """INFO级别的路由日志装饰器。"""
    return default_route_logger.log_route(
        include_args=include_args,
        include_result=include_result,
        include_timing=include_timing,
        log_level=logging.INFO,
    )
