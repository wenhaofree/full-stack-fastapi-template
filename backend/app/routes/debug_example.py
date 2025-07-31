"""DEBUG级别日志示例路由。"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.route_logging import log_route_debug, log_route_info
from app.dependencies.auth import CurrentUser

router = APIRouter()


class UserCreateRequest(BaseModel):
    """用户创建请求模型。"""
    email: str = Field(..., description="用户邮箱")
    password: str = Field(..., min_length=8, description="用户密码")
    full_name: Optional[str] = Field(None, description="用户全名")
    age: Optional[int] = Field(None, ge=0, le=150, description="用户年龄")


class UserResponse(BaseModel):
    """用户响应模型。"""
    id: str = Field(..., description="用户ID")
    email: str = Field(..., description="用户邮箱")
    full_name: Optional[str] = Field(None, description="用户全名")
    age: Optional[int] = Field(None, description="用户年龄")
    is_active: bool = Field(..., description="是否激活")


class SearchRequest(BaseModel):
    """搜索请求模型。"""
    keyword: str = Field(..., description="搜索关键词")
    category: Optional[str] = Field(None, description="搜索分类")
    limit: int = Field(10, ge=1, le=100, description="返回数量限制")


@router.post("/debug/users", response_model=UserResponse, tags=["debug"])
@log_route_debug(include_args=True, include_result=True, include_timing=True)
async def create_debug_user(user_data: UserCreateRequest) -> UserResponse:
    """创建用户（DEBUG日志示例）。
    
    这个接口会记录详细的入参和出参信息，包括：
    - 请求体内容（过滤敏感字段）
    - 函数参数
    - 返回值
    - 执行时间
    """
    # 模拟用户创建逻辑
    import uuid
    import time
    
    # 模拟一些处理时间
    await asyncio.sleep(0.1)
    
    # 模拟业务逻辑
    if user_data.email == "test@error.com":
        raise HTTPException(status_code=400, detail="测试错误情况")
    
    # 返回创建的用户
    return UserResponse(
        id=str(uuid.uuid4()),
        email=user_data.email,
        full_name=user_data.full_name,
        age=user_data.age,
        is_active=True
    )


@router.get("/debug/users/{user_id}", response_model=UserResponse, tags=["debug"])
@log_route_debug(include_args=True, include_result=True)
async def get_debug_user(user_id: str) -> UserResponse:
    """获取用户信息（DEBUG日志示例）。"""
    import uuid
    
    # 模拟查询逻辑
    if user_id == "not-found":
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return UserResponse(
        id=user_id,
        email=f"user_{user_id}@example.com",
        full_name=f"User {user_id}",
        age=25,
        is_active=True
    )


@router.post("/debug/search", tags=["debug"])
@log_route_debug(include_args=True, include_result=True)
async def search_debug(search_data: SearchRequest) -> dict:
    """搜索接口（DEBUG日志示例）。"""
    import time
    
    # 模拟搜索处理
    await asyncio.sleep(0.05)
    
    # 模拟搜索结果
    results = []
    for i in range(min(search_data.limit, 5)):
        results.append({
            "id": f"item_{i}",
            "title": f"{search_data.keyword} 结果 {i+1}",
            "category": search_data.category or "default",
            "score": 0.9 - i * 0.1
        })
    
    return {
        "keyword": search_data.keyword,
        "category": search_data.category,
        "total": len(results),
        "results": results,
        "search_time": "0.050s"
    }


@router.get("/debug/users", response_model=List[UserResponse], tags=["debug"])
@log_route_debug(include_args=True, include_result=True)
async def list_debug_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    is_active: Optional[bool] = Query(None, description="是否激活")
) -> List[UserResponse]:
    """获取用户列表（DEBUG日志示例）。"""
    import uuid
    
    # 模拟查询逻辑
    users = []
    for i in range(page_size):
        user_id = str(uuid.uuid4())
        users.append(UserResponse(
            id=user_id,
            email=f"user_{i}@example.com",
            full_name=f"User {i}" if keyword is None else f"{keyword} User {i}",
            age=20 + i,
            is_active=is_active if is_active is not None else (i % 2 == 0)
        ))
    
    return users


@router.put("/debug/users/{user_id}", response_model=UserResponse, tags=["debug"])
@log_route_debug(include_args=True, include_result=True)
async def update_debug_user(
    user_id: str,
    user_data: UserCreateRequest
) -> UserResponse:
    """更新用户信息（DEBUG日志示例）。"""
    # 模拟更新逻辑
    if user_id == "not-found":
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return UserResponse(
        id=user_id,
        email=user_data.email,
        full_name=user_data.full_name,
        age=user_data.age,
        is_active=True
    )


@router.delete("/debug/users/{user_id}", tags=["debug"])
@log_route_debug(include_args=True, include_result=True)
async def delete_debug_user(user_id: str) -> dict:
    """删除用户（DEBUG日志示例）。"""
    # 模拟删除逻辑
    if user_id == "not-found":
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {
        "message": f"用户 {user_id} 已删除",
        "deleted_id": user_id,
        "success": True
    }


class LoginRequest(BaseModel):
    """登录请求模型。"""
    email: str = Field(..., description="用户邮箱")
    password: str = Field(..., description="用户密码")


@router.post("/debug/login", tags=["debug"])
@log_route_debug(include_args=True, include_result=True)
async def debug_login(login_data: LoginRequest) -> dict:
    """登录接口（DEBUG日志示例，会过滤密码字段）。"""
    import time
    
    # 模拟登录验证
    await asyncio.sleep(0.02)
    
    if login_data.email == "admin@example.com" and login_data.password == "admin123":
        return {
            "access_token": "fake_jwt_token_here",
            "token_type": "bearer",
            "expires_in": 3600,
            "user_id": "admin_user_id"
        }
    else:
        raise HTTPException(status_code=401, detail="邮箱或密码错误")


@router.get("/debug/protected", tags=["debug"])
@log_route_debug(include_args=True, include_result=True)
async def debug_protected_route(current_user: CurrentUser) -> dict:
    """受保护的路由（DEBUG日志示例）。"""
    return {
        "message": "这是受保护的路由",
        "user_id": str(current_user.id),
        "user_email": current_user.email,
        "timestamp": time.time()
    }


# 添加一些INFO级别的路由示例
@router.get("/debug/health", tags=["debug"])
@log_route_info(include_timing=True)
async def debug_health() -> dict:
    """健康检查（INFO级别日志）。"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    }


@router.get("/debug/stats", tags=["debug"])
@log_route_info(include_result=True, include_timing=True)
async def debug_stats() -> dict:
    """系统统计（INFO级别日志）。"""
    import time

    return {
        "cpu_percent": 15.5,  # 模拟CPU使用率
        "memory_percent": 45.2,  # 模拟内存使用率
        "timestamp": time.time()
    }


# 导入asyncio和time
import asyncio
import time
