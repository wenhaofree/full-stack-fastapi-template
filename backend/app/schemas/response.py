"""统一响应格式定义。"""

import uuid
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

from app.core.constants import BusinessCode, get_code_message

# 泛型类型变量
DataType = TypeVar("DataType")


class BaseResponse(BaseModel, Generic[DataType]):
    """统一响应基类"""

    code: int = Field(..., description="业务状态码")
    message: str = Field(..., description="响应消息")
    data: Optional[DataType] = Field(None, description="响应数据")

    class Config:
        json_encoders = {
            uuid.UUID: str,  # UUID 序列化为字符串
        }


class SuccessResponse(BaseResponse[DataType]):
    """成功响应"""
    
    def __init__(
        self,
        data: Optional[DataType] = None,
        code: BusinessCode = BusinessCode.SUCCESS,
        message: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            code=code.value,
            message=message or get_code_message(code),
            data=data,
            **kwargs
        )


class ErrorResponse(BaseResponse[None]):
    """错误响应"""
    
    def __init__(
        self,
        code: BusinessCode,
        message: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            code=code.value,
            message=message or get_code_message(code),
            data=None,
            **kwargs
        )


class ListResponse(BaseModel):
    """列表响应数据结构"""
    
    items: list[Any] = Field(..., description="列表数据")
    total: int = Field(..., description="总数量")
    page: int = Field(1, description="当前页码")
    page_size: int = Field(10, description="每页数量")
    
    @property
    def total_pages(self) -> int:
        """总页数"""
        return (self.total + self.page_size - 1) // self.page_size


class PaginationParams(BaseModel):
    """分页参数"""
    
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")
    
    @property
    def skip(self) -> int:
        """跳过的记录数"""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """限制的记录数"""
        return self.page_size


# 常用响应类型别名
UserResponse = SuccessResponse[Any]
UsersResponse = SuccessResponse[ListResponse]
ItemResponse = SuccessResponse[Any]
ItemsResponse = SuccessResponse[ListResponse]
MessageResponse = SuccessResponse[dict[str, str]]
