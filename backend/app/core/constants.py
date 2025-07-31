"""应用常量定义，包括状态码、错误码等。"""

from enum import Enum
from typing import Dict, Any


class ResponseCode(Enum):
    """统一响应状态码"""
    
    # 成功状态码 (2xx)
    SUCCESS = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    
    # 客户端错误 (4xx)
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS = 429
    
    # 服务器错误 (5xx)
    INTERNAL_SERVER_ERROR = 500
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504


class BusinessCode(Enum):
    """业务状态码"""
    
    # 通用成功
    SUCCESS = 10000
    CREATED = 10001
    UPDATED = 10002
    DELETED = 10003
    
    # 通用错误
    INVALID_PARAMS = 20001
    RESOURCE_NOT_FOUND = 20002
    RESOURCE_ALREADY_EXISTS = 20003
    PERMISSION_DENIED = 20004
    OPERATION_FAILED = 20005
    
    # 认证相关
    AUTH_TOKEN_INVALID = 30001
    AUTH_TOKEN_EXPIRED = 30002
    AUTH_LOGIN_FAILED = 30003
    AUTH_PERMISSION_DENIED = 30004
    AUTH_USER_DISABLED = 30005
    
    # 用户相关
    USER_NOT_FOUND = 40001
    USER_ALREADY_EXISTS = 40002
    USER_PASSWORD_INCORRECT = 40003
    USER_EMAIL_ALREADY_EXISTS = 40004
    USER_INACTIVE = 40005
    
    # 项目相关
    ITEM_NOT_FOUND = 50001
    ITEM_PERMISSION_DENIED = 50002
    ITEM_ALREADY_EXISTS = 50003
    
    # 系统错误
    SYSTEM_ERROR = 90001
    DATABASE_ERROR = 90002
    EXTERNAL_SERVICE_ERROR = 90003


# 状态码对应的消息
CODE_MESSAGES: Dict[BusinessCode, str] = {
    # 通用成功
    BusinessCode.SUCCESS: "操作成功",
    BusinessCode.CREATED: "创建成功",
    BusinessCode.UPDATED: "更新成功",
    BusinessCode.DELETED: "删除成功",
    
    # 通用错误
    BusinessCode.INVALID_PARAMS: "参数错误",
    BusinessCode.RESOURCE_NOT_FOUND: "资源不存在",
    BusinessCode.RESOURCE_ALREADY_EXISTS: "资源已存在",
    BusinessCode.PERMISSION_DENIED: "权限不足",
    BusinessCode.OPERATION_FAILED: "操作失败",
    
    # 认证相关
    BusinessCode.AUTH_TOKEN_INVALID: "令牌无效",
    BusinessCode.AUTH_TOKEN_EXPIRED: "令牌已过期",
    BusinessCode.AUTH_LOGIN_FAILED: "登录失败",
    BusinessCode.AUTH_PERMISSION_DENIED: "权限不足",
    BusinessCode.AUTH_USER_DISABLED: "用户已禁用",
    
    # 用户相关
    BusinessCode.USER_NOT_FOUND: "用户不存在",
    BusinessCode.USER_ALREADY_EXISTS: "用户已存在",
    BusinessCode.USER_PASSWORD_INCORRECT: "密码错误",
    BusinessCode.USER_EMAIL_ALREADY_EXISTS: "邮箱已存在",
    BusinessCode.USER_INACTIVE: "用户未激活",
    
    # 项目相关
    BusinessCode.ITEM_NOT_FOUND: "项目不存在",
    BusinessCode.ITEM_PERMISSION_DENIED: "项目权限不足",
    BusinessCode.ITEM_ALREADY_EXISTS: "项目已存在",
    
    # 系统错误
    BusinessCode.SYSTEM_ERROR: "系统错误",
    BusinessCode.DATABASE_ERROR: "数据库错误",
    BusinessCode.EXTERNAL_SERVICE_ERROR: "外部服务错误",
}


def get_code_message(code: BusinessCode) -> str:
    """获取状态码对应的消息"""
    return CODE_MESSAGES.get(code, "未知错误")


# 成功状态码集合
SUCCESS_CODES = {
    BusinessCode.SUCCESS,
    BusinessCode.CREATED,
    BusinessCode.UPDATED,
    BusinessCode.DELETED,
}


def is_success_code(code: BusinessCode) -> bool:
    """判断是否为成功状态码"""
    return code in SUCCESS_CODES
