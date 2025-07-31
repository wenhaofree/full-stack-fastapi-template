"""专业的访问日志中间件。"""

import json
import logging
import time
from typing import Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.tracing import (
    TraceContext,
    generate_request_id,
    generate_trace_id,
    set_user_id,
)

# 创建专门的访问日志记录器
access_logger = logging.getLogger("app.access")


class AccessLogMiddleware(BaseHTTPMiddleware):
    """专业的访问日志中间件。"""
    
    def __init__(self, app, log_request_body: bool = True, log_response_body: bool = True):
        super().__init__(app)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        # 敏感字段列表
        self.sensitive_fields = {
            'password', 'token', 'secret', 'key', 'authorization',
            'passwd', 'pwd', 'auth', 'credential', 'api_key', 'refresh_token'
        }
        # 不记录请求体的路径
        self.skip_body_paths = {
            '/docs', '/redoc', '/openapi.json', '/favicon.ico'
        }
    
    def _should_log_body(self, path: str) -> bool:
        """判断是否应该记录请求体。"""
        return path not in self.skip_body_paths
    
    def _filter_sensitive_data(self, data):
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
        else:
            return data
    
    async def _read_request_body(self, request: Request) -> Optional[str]:
        """安全地读取请求体。"""
        try:
            if not self.log_request_body or not self._should_log_body(request.url.path):
                return None

            content_type = request.headers.get("content-type", "")
            if not any(ct in content_type.lower() for ct in ["application/json", "application/x-www-form-urlencoded"]):
                return f"<{content_type}>"

            body = await request.body()
            if not body:
                return None

            if "application/json" in content_type.lower():
                try:
                    body_data = json.loads(body.decode('utf-8'))
                    filtered_data = self._filter_sensitive_data(body_data)
                    return json.dumps(filtered_data, ensure_ascii=False)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    return "<invalid_json>"
            else:
                body_str = body.decode('utf-8')
                if len(body_str) > 1000:
                    body_str = body_str[:1000] + "..."
                return body_str

        except Exception as e:
            access_logger.warning(f"读取请求体失败: {e}")
            return None

    async def _capture_response_body(self, response) -> tuple:
        """捕获响应体内容。"""
        try:
            if not self.log_response_body:
                return response, None

            # 对于某些响应类型，直接返回不处理
            if hasattr(response, 'body_iterator'):
                # 流式响应或大文件响应，不捕获内容
                return response, "<streaming_response>"

            # 检查响应类型
            content_type = response.headers.get("content-type", "")
            if not any(ct in content_type.lower() for ct in ["application/json", "text/"]):
                return response, f"<{content_type}>"

            # 尝试获取响应体内容
            response_body = None
            if hasattr(response, 'body') and response.body:
                response_body = response.body
            elif hasattr(response, 'content') and response.content:
                response_body = response.content
            else:
                return response, "<no_body>"

            if not response_body:
                return response, None

            # 确保是bytes类型
            if isinstance(response_body, str):
                response_body = response_body.encode('utf-8')

            # 解析响应体
            if "application/json" in content_type.lower():
                try:
                    body_data = json.loads(response_body.decode('utf-8'))
                    filtered_data = self._filter_sensitive_data(body_data)
                    body_str = json.dumps(filtered_data, ensure_ascii=False)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    body_str = "<invalid_json>"
            else:
                body_str = response_body.decode('utf-8', errors='ignore')
                if len(body_str) > 2000:
                    body_str = body_str[:2000] + "..."

            return response, body_str

        except Exception as e:
            access_logger.warning(f"捕获响应体失败: {e}")
            return response, None
    
    async def _extract_user_id(self, request: Request) -> Optional[str]:
        """从请求中提取用户ID。"""
        try:
            # 尝试从Authorization头中提取用户信息
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                # 这里可以解析JWT token获取用户ID
                # 为了避免循环导入，这里只是示例
                return None
            return None
        except Exception:
            return None
    
    def _get_client_ip(self, request: Request) -> str:
        """获取客户端真实IP。"""
        # 优先从代理头中获取真实IP
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并记录访问日志。"""
        # 从请求头中获取或生成追踪ID
        trace_id = request.headers.get("X-Trace-ID") or generate_trace_id()
        request_id = generate_request_id()

        # 创建追踪上下文
        with TraceContext(trace_id=trace_id, request_id=request_id):
            # 将追踪信息添加到请求状态
            request.state.trace_id = trace_id
            request.state.request_id = request_id

            start_time = time.time()

            # 提取用户信息
            user_id = await self._extract_user_id(request)
            if user_id:
                set_user_id(user_id)

            # 读取请求体（仅在DEBUG级别）
            request_body = None
            if access_logger.isEnabledFor(logging.DEBUG) and self.log_request_body:
                request_body = await self._read_request_body(request)

            # 准备请求日志数据
            request_log_data = {
                "event": "request_start",
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "query_params": str(request.query_params) if request.query_params else None,
                "client_ip": self._get_client_ip(request),
                "user_agent": request.headers.get("user-agent"),
                "content_type": request.headers.get("content-type"),
                "content_length": request.headers.get("content-length"),
                "user_id": user_id,
            }

            # DEBUG级别添加请求体
            if request_body is not None:
                request_log_data["request_body"] = request_body
                access_logger.debug("➡️ 请求开始（含请求体）", extra=request_log_data)
            else:
                access_logger.info("➡️ 请求开始", extra=request_log_data)

            try:
                # 处理请求
                response = await call_next(request)

                process_time = time.time() - start_time

                # 准备响应日志数据
                response_log_data = {
                    "event": "request_complete",
                    "method": request.method,
                    "url": str(request.url),
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "process_time": f"{process_time:.3f}s",
                    "response_size": response.headers.get("content-length"),
                    "user_id": user_id,
                }

                # 根据状态码决定日志级别
                if response.status_code >= 500:
                    log_level = logging.ERROR
                    log_message = "⬅️ 请求完成（服务器错误）"
                elif response.status_code >= 400:
                    log_level = logging.WARNING
                    log_message = "⬅️ 请求完成（客户端错误）"
                else:
                    log_level = logging.INFO
                    log_message = "⬅️ 请求完成"

                access_logger.log(log_level, log_message, extra=response_log_data)

                # 添加追踪信息到响应头
                response.headers["X-Trace-ID"] = trace_id
                response.headers["X-Request-ID"] = request_id

                return response

            except Exception as e:
                process_time = time.time() - start_time

                # 记录请求异常
                error_log_data = {
                    "event": "request_error",
                    "method": request.method,
                    "url": str(request.url),
                    "path": request.url.path,
                    "process_time": f"{process_time:.3f}s",
                    "exception_type": type(e).__name__,
                    "exception_message": str(e),
                    "user_id": user_id,
                }

                access_logger.error("💥 请求处理异常", extra=error_log_data, exc_info=True)

                # 重新抛出异常
                raise


def setup_access_log_middleware(app):
    """设置访问日志中间件。"""
    # 根据配置决定是否记录详细信息
    log_request_body = settings.LOG_REQUEST_DETAILS
    log_response_body = False  # 暂时禁用响应体记录以避免阻塞

    app.add_middleware(
        AccessLogMiddleware,
        log_request_body=log_request_body,
        log_response_body=log_response_body
    )


def setup_access_log_middleware(app):
    """设置访问日志中间件。"""
    # 根据配置决定是否记录详细信息
    log_request_body = settings.LOG_REQUEST_DETAILS
    log_response_body = settings.LOG_REQUEST_DETAILS
    
    app.add_middleware(
        AccessLogMiddleware,
        log_request_body=log_request_body,
        log_response_body=log_response_body
    )
