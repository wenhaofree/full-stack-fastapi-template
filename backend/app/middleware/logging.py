"""增强的日志中间件配置。"""

import json
import logging
import time
from typing import Callable, Optional

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse

from app.core.config import settings
from app.core.tracing import (
    TraceContext,
    generate_request_id,
    generate_trace_id,
    get_trace_id,
    set_user_id,
)

logger = logging.getLogger("app.middleware.logging")


class LoggingMiddleware(BaseHTTPMiddleware):
    """增强的请求/响应日志中间件。"""

    def __init__(self, app, log_request_body: bool = True, log_response_body: bool = True):
        super().__init__(app)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        # 敏感字段列表，不记录这些字段的值
        self.sensitive_fields = {
            'password', 'token', 'secret', 'key', 'authorization',
            'passwd', 'pwd', 'auth', 'credential', 'api_key'
        }

    async def _read_request_body(self, request: Request) -> Optional[str]:
        """安全地读取请求体。"""
        try:
            if not self.log_request_body:
                return None

            # 只记录JSON和表单数据
            content_type = request.headers.get("content-type", "")
            if not any(ct in content_type.lower() for ct in ["application/json", "application/x-www-form-urlencoded"]):
                return f"<{content_type}>"

            body = await request.body()
            if not body:
                return None

            # 尝试解析JSON
            if "application/json" in content_type.lower():
                try:
                    body_data = json.loads(body.decode('utf-8'))
                    # 过滤敏感字段
                    filtered_data = self._filter_sensitive_data(body_data)
                    return json.dumps(filtered_data, ensure_ascii=False)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    return "<invalid_json>"
            else:
                # 表单数据
                body_str = body.decode('utf-8')
                if len(body_str) > 1000:  # 限制长度
                    body_str = body_str[:1000] + "..."
                return body_str

        except Exception as e:
            logger.warning(f"读取请求体失败: {e}")
            return None

    def _filter_sensitive_data(self, data):
        """过滤敏感数据。"""
        if isinstance(data, dict):
            filtered = {}
            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in self.sensitive_fields):
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

    async def _capture_response_body(self, response: Response) -> tuple[Response, Optional[str]]:
        """捕获响应体内容。"""
        try:
            if not self.log_response_body:
                return response, None

            # 只处理JSON响应
            content_type = response.headers.get("content-type", "")
            if "application/json" not in content_type.lower():
                return response, f"<{content_type}>"

            # 对于StreamingResponse，我们需要特殊处理
            if isinstance(response, StreamingResponse):
                return response, "<streaming_response>"

            # 读取响应体
            if hasattr(response, 'body') and response.body:
                body_str = response.body.decode('utf-8')
                # 限制响应体长度
                if len(body_str) > 2000:
                    body_str = body_str[:2000] + "..."
                return response, body_str

            return response, None

        except Exception as e:
            logger.warning(f"捕获响应体失败: {e}")
            return response, None

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并记录日志。"""
        # 从请求头中获取或生成追踪ID
        trace_id = request.headers.get("X-Trace-ID") or generate_trace_id()
        request_id = generate_request_id()

        # 创建追踪上下文
        with TraceContext(trace_id=trace_id, request_id=request_id):
            # 将追踪信息添加到请求状态
            request.state.trace_id = trace_id
            request.state.request_id = request_id

            start_time = time.time()

            # 提取用户信息（如果有认证信息）
            user_id = await self._extract_user_id(request)
            if user_id:
                set_user_id(user_id)

            # 读取请求体（DEBUG级别）
            request_body = None
            if logger.isEnabledFor(logging.DEBUG):
                request_body = await self._read_request_body(request)

            # 记录请求开始
            log_data = {
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "query_params": str(request.query_params) if request.query_params else None,
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
                "content_type": request.headers.get("content-type"),
                "content_length": request.headers.get("content-length"),
                "user_id": user_id,
            }

            # DEBUG级别添加请求体
            if request_body is not None:
                log_data["request_body"] = request_body
                logger.debug("请求开始（含请求体）", extra=log_data)
            else:
                logger.info("请求开始", extra=log_data)

            try:
                # 处理请求
                response = await call_next(request)

                process_time = time.time() - start_time

                # 捕获响应体（DEBUG级别）
                response_body = None
                if logger.isEnabledFor(logging.DEBUG):
                    response, response_body = await self._capture_response_body(response)

                # 记录请求完成
                log_data = {
                    "method": request.method,
                    "url": str(request.url),
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "process_time": f"{process_time:.3f}s",
                    "response_size": response.headers.get("content-length"),
                    "user_id": user_id,
                }

                # DEBUG级别添加响应体
                if response_body is not None:
                    log_data["response_body"] = response_body
                    logger.debug("请求完成（含响应体）", extra=log_data)
                else:
                    logger.info("请求完成", extra=log_data)

                # 添加追踪信息到响应头
                response.headers["X-Trace-ID"] = trace_id
                response.headers["X-Request-ID"] = request_id

                return response

            except Exception as e:
                process_time = time.time() - start_time

                # 记录请求异常
                logger.error(
                    f"请求处理异常: {str(e)}",
                    extra={
                        "method": request.method,
                        "url": str(request.url),
                        "path": request.url.path,
                        "process_time": f"{process_time:.3f}s",
                        "exception_type": type(e).__name__,
                        "user_id": user_id,
                    },
                    exc_info=True
                )

                # 重新抛出异常
                raise

    async def _extract_user_id(self, request: Request) -> Optional[str]:
        """从请求中提取用户ID。"""
        try:
            # 尝试从Authorization头中提取用户信息
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                # 这里可以解析JWT token获取用户ID
                # 为了避免循环导入，这里只是示例
                # 实际实现中可以调用认证服务
                return None

            # 也可以从其他地方获取用户ID，比如session
            return None

        except Exception:
            # 如果提取用户ID失败，不影响主流程
            return None


def setup_logging_middleware(app: FastAPI) -> None:
    """Setup logging middleware for the FastAPI application."""
    from app.core.config import settings

    # 根据配置决定是否记录详细信息
    log_request_body = settings.LOG_REQUEST_DETAILS
    log_response_body = settings.LOG_REQUEST_DETAILS

    app.add_middleware(
        LoggingMiddleware,
        log_request_body=log_request_body,
        log_response_body=log_response_body
    )
