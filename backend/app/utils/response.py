"""响应工具函数。"""

import json
import uuid
from typing import Any, Optional

from fastapi import HTTPException
from fastapi.responses import JSONResponse

from app.core.constants import BusinessCode, ResponseCode, get_code_message
from app.schemas.response import (
    ErrorResponse,
    ListResponse,
    SuccessResponse,
)


class CustomJSONResponse(JSONResponse):
    """自定义 JSON 响应，支持 UUID 序列化"""

    def render(self, content: Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            default=self._json_encoder,
        ).encode("utf-8")

    def _json_encoder(self, obj: Any) -> Any:
        """自定义 JSON 编码器"""
        if isinstance(obj, uuid.UUID):
            return str(obj)
        raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def success_response(
    data: Any = None,
    code: BusinessCode = BusinessCode.SUCCESS,
    message: Optional[str] = None,
    http_status: int = ResponseCode.SUCCESS.value,
) -> CustomJSONResponse:
    """创建成功响应"""
    response = SuccessResponse(data=data, code=code, message=message)
    return CustomJSONResponse(
        status_code=http_status,
        content=response.model_dump()
    )


def error_response(
    code: BusinessCode,
    message: Optional[str] = None,
    http_status: Optional[int] = None,
) -> CustomJSONResponse:
    """创建错误响应"""
    if http_status is None:
        # 根据业务状态码映射HTTP状态码
        http_status = _map_business_code_to_http_status(code)

    response = ErrorResponse(code=code, message=message)
    return CustomJSONResponse(
        status_code=http_status,
        content=response.model_dump()
    )


def list_response(
    items: list[Any],
    total: int,
    page: int = 1,
    page_size: int = 10,
    code: BusinessCode = BusinessCode.SUCCESS,
    message: Optional[str] = None,
) -> CustomJSONResponse:
    """创建列表响应"""
    list_data = ListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )
    return success_response(data=list_data.model_dump(), code=code, message=message)


def created_response(
    data: Any = None,
    message: Optional[str] = None,
) -> CustomJSONResponse:
    """创建资源成功响应"""
    return success_response(
        data=data,
        code=BusinessCode.CREATED,
        message=message,
        http_status=ResponseCode.CREATED.value,
    )


def updated_response(
    data: Any = None,
    message: Optional[str] = None,
) -> CustomJSONResponse:
    """更新资源成功响应"""
    return success_response(
        data=data,
        code=BusinessCode.UPDATED,
        message=message,
    )


def deleted_response(
    message: Optional[str] = None,
) -> CustomJSONResponse:
    """删除资源成功响应"""
    return success_response(
        data={"deleted": True},
        code=BusinessCode.DELETED,
        message=message,
    )


def not_found_response(
    message: Optional[str] = None,
) -> CustomJSONResponse:
    """资源不存在响应"""
    return error_response(
        code=BusinessCode.RESOURCE_NOT_FOUND,
        message=message,
    )


def permission_denied_response(
    message: Optional[str] = None,
) -> CustomJSONResponse:
    """权限不足响应"""
    return error_response(
        code=BusinessCode.PERMISSION_DENIED,
        message=message,
    )


def invalid_params_response(
    message: Optional[str] = None,
) -> CustomJSONResponse:
    """参数错误响应"""
    return error_response(
        code=BusinessCode.INVALID_PARAMS,
        message=message,
    )


def _map_business_code_to_http_status(code: BusinessCode) -> int:
    """将业务状态码映射到HTTP状态码"""
    mapping = {
        # 成功状态码
        BusinessCode.SUCCESS: ResponseCode.SUCCESS.value,
        BusinessCode.CREATED: ResponseCode.CREATED.value,
        BusinessCode.UPDATED: ResponseCode.SUCCESS.value,
        BusinessCode.DELETED: ResponseCode.SUCCESS.value,
        
        # 客户端错误
        BusinessCode.INVALID_PARAMS: ResponseCode.BAD_REQUEST.value,
        BusinessCode.RESOURCE_NOT_FOUND: ResponseCode.NOT_FOUND.value,
        BusinessCode.RESOURCE_ALREADY_EXISTS: ResponseCode.CONFLICT.value,
        BusinessCode.PERMISSION_DENIED: ResponseCode.FORBIDDEN.value,
        
        # 认证相关
        BusinessCode.AUTH_TOKEN_INVALID: ResponseCode.UNAUTHORIZED.value,
        BusinessCode.AUTH_TOKEN_EXPIRED: ResponseCode.UNAUTHORIZED.value,
        BusinessCode.AUTH_LOGIN_FAILED: ResponseCode.UNAUTHORIZED.value,
        BusinessCode.AUTH_PERMISSION_DENIED: ResponseCode.FORBIDDEN.value,
        BusinessCode.AUTH_USER_DISABLED: ResponseCode.FORBIDDEN.value,
        
        # 用户相关
        BusinessCode.USER_NOT_FOUND: ResponseCode.NOT_FOUND.value,
        BusinessCode.USER_ALREADY_EXISTS: ResponseCode.CONFLICT.value,
        BusinessCode.USER_PASSWORD_INCORRECT: ResponseCode.BAD_REQUEST.value,
        BusinessCode.USER_EMAIL_ALREADY_EXISTS: ResponseCode.CONFLICT.value,
        BusinessCode.USER_INACTIVE: ResponseCode.FORBIDDEN.value,
        
        # 项目相关
        BusinessCode.ITEM_NOT_FOUND: ResponseCode.NOT_FOUND.value,
        BusinessCode.ITEM_PERMISSION_DENIED: ResponseCode.FORBIDDEN.value,
        BusinessCode.ITEM_ALREADY_EXISTS: ResponseCode.CONFLICT.value,
        
        # 系统错误
        BusinessCode.SYSTEM_ERROR: ResponseCode.INTERNAL_SERVER_ERROR.value,
        BusinessCode.DATABASE_ERROR: ResponseCode.INTERNAL_SERVER_ERROR.value,
        BusinessCode.EXTERNAL_SERVICE_ERROR: ResponseCode.BAD_GATEWAY.value,
    }
    
    return mapping.get(code, ResponseCode.INTERNAL_SERVER_ERROR.value)


class ResponseException(HTTPException):
    """自定义响应异常"""
    
    def __init__(
        self,
        code: BusinessCode,
        message: Optional[str] = None,
        http_status: Optional[int] = None,
    ):
        self.business_code = code
        self.business_message = message or get_code_message(code)
        
        if http_status is None:
            http_status = _map_business_code_to_http_status(code)
        
        super().__init__(
            status_code=http_status,
            detail={
                "code": code.value,
                "message": self.business_message,
                "data": None,
            }
        )
