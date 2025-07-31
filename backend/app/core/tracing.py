"""链路追踪系统实现。"""

import contextvars
import uuid
from typing import Optional


# 创建上下文变量来存储追踪ID
trace_id_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    'trace_id', 
    default=None
)

request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    'request_id', 
    default=None
)

user_id_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    'user_id', 
    default=None
)


def generate_trace_id() -> str:
    """生成新的追踪ID。"""
    return str(uuid.uuid4())


def generate_request_id() -> str:
    """生成新的请求ID。"""
    return str(uuid.uuid4())


def set_trace_id(trace_id: str) -> None:
    """设置当前上下文的追踪ID。"""
    trace_id_var.set(trace_id)


def get_trace_id() -> Optional[str]:
    """获取当前上下文的追踪ID。"""
    return trace_id_var.get(None)


def set_request_id(request_id: str) -> None:
    """设置当前上下文的请求ID。"""
    request_id_var.set(request_id)


def get_request_id() -> Optional[str]:
    """获取当前上下文的请求ID。"""
    return request_id_var.get(None)


def set_user_id(user_id: str) -> None:
    """设置当前上下文的用户ID。"""
    user_id_var.set(user_id)


def get_user_id() -> Optional[str]:
    """获取当前上下文的用户ID。"""
    return user_id_var.get(None)


def get_trace_context() -> dict[str, Optional[str]]:
    """获取完整的追踪上下文信息。"""
    return {
        "trace_id": get_trace_id(),
        "request_id": get_request_id(),
        "user_id": get_user_id(),
    }


class TraceContext:
    """追踪上下文管理器。"""
    
    def __init__(
        self, 
        trace_id: Optional[str] = None,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        self.trace_id = trace_id or generate_trace_id()
        self.request_id = request_id or generate_request_id()
        self.user_id = user_id
        
        # 保存之前的值以便恢复
        self._previous_trace_id = None
        self._previous_request_id = None
        self._previous_user_id = None
    
    def __enter__(self):
        """进入上下文时设置追踪信息。"""
        self._previous_trace_id = get_trace_id()
        self._previous_request_id = get_request_id()
        self._previous_user_id = get_user_id()
        
        set_trace_id(self.trace_id)
        set_request_id(self.request_id)
        if self.user_id:
            set_user_id(self.user_id)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时恢复之前的追踪信息。"""
        if self._previous_trace_id:
            set_trace_id(self._previous_trace_id)
        if self._previous_request_id:
            set_request_id(self._previous_request_id)
        if self._previous_user_id:
            set_user_id(self._previous_user_id)
    
    def get_context_dict(self) -> dict[str, Optional[str]]:
        """获取上下文字典。"""
        return {
            "trace_id": self.trace_id,
            "request_id": self.request_id,
            "user_id": self.user_id,
        }


def create_child_trace(parent_trace_id: Optional[str] = None) -> TraceContext:
    """创建子追踪上下文，继承父追踪ID。"""
    parent_trace_id = parent_trace_id or get_trace_id()
    return TraceContext(
        trace_id=parent_trace_id,
        request_id=generate_request_id(),
        user_id=get_user_id()
    )
