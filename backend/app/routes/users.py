"""标准化的用户路由 - 使用统一响应格式。"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import func, select

from app.core.constants import BusinessCode
from app.dependencies.auth import CurrentUser, get_current_active_superuser
from app.dependencies.database import SessionDep
from app.models.user import User
from app.schemas.response import PaginationParams
from app.schemas.user import (
    UpdatePassword,
    UserCreate,
    UserPublic,
    UserUpdate,
    UserUpdateMe,
)
from app.services.user_service import user_service
from app.utils.response import (
    ResponseException,
    created_response,
    deleted_response,
    list_response,
    success_response,
    updated_response,
)
from app.core.route_logging import log_route_debug, log_route_info

router = APIRouter()


@router.get("/")
# @log_route_debug(include_args=True, include_result=True, include_timing=True)  # 暂时禁用
async def read_users(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_active_superuser)],
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
):
    """获取用户列表（仅超级管理员）"""
    
    # 计算分页参数
    skip = (page - 1) * page_size
    
    # 获取总数
    count_statement = select(func.count()).select_from(User)
    total = session.exec(count_statement).one()
    
    # 获取用户列表
    statement = select(User).offset(skip).limit(page_size)
    users = session.exec(statement).all()
    
    # 转换为公开格式
    user_list = [UserPublic.model_validate(user) for user in users]

    return list_response(
        items=[user.model_dump(mode='json') for user in user_list],
        total=total,
        page=page,
        page_size=page_size,
        message="获取用户列表成功"
    )


@router.post("/")
# @log_route_debug(include_args=True, include_result=True, include_timing=True)  # 暂时禁用
async def create_user(
    *,
    session: SessionDep,
    user_in: UserCreate,
    current_user: Annotated[User, Depends(get_current_active_superuser)],
):
    """创建新用户（仅超级管理员）"""
    
    # 检查邮箱是否已存在
    existing_user = user_service.get_by_email(session=session, email=user_in.email)
    if existing_user:
        raise ResponseException(
            code=BusinessCode.USER_EMAIL_ALREADY_EXISTS,
            message=f"邮箱 {user_in.email} 已被使用"
        )
    
    # 创建用户
    user = user_service.create(session=session, obj_in=user_in)
    user_public = UserPublic.model_validate(user)
    
    return created_response(
        data=user_public.model_dump(mode='json'),
        message="用户创建成功"
    )


@router.get("/me")
async def read_user_me(current_user: CurrentUser):
    """获取当前用户信息"""
    
    user_public = UserPublic.model_validate(current_user)
    return success_response(
        data=user_public.model_dump(mode='json'),
        message="获取用户信息成功"
    )


@router.put("/me")
async def update_user_me(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    user_in: UserUpdateMe,
):
    """更新当前用户信息"""
    
    # 如果要更新邮箱，检查是否已存在
    if user_in.email and user_in.email != current_user.email:
        existing_user = user_service.get_by_email(session=session, email=user_in.email)
        if existing_user:
            raise ResponseException(
                code=BusinessCode.USER_EMAIL_ALREADY_EXISTS,
                message=f"邮箱 {user_in.email} 已被使用"
            )
    
    # 更新用户
    user = user_service.update(session=session, db_obj=current_user, obj_in=user_in)
    user_public = UserPublic.model_validate(user)
    
    return updated_response(
        data=user_public.model_dump(mode='json'),
        message="用户信息更新成功"
    )


@router.put("/me/password")
async def update_password(
    session: SessionDep,
    current_user: CurrentUser,
    update_password: UpdatePassword,
):
    """更新当前用户密码"""
    
    # 验证当前密码
    if not user_service.authenticate(
        session=session, 
        email=current_user.email, 
        password=update_password.current_password
    ):
        raise ResponseException(
            code=BusinessCode.USER_PASSWORD_INCORRECT,
            message="当前密码错误"
        )
    
    # 更新密码
    user_service.update(
        session=session,
        db_obj=current_user,
        obj_in={"password": update_password.new_password},
    )
    
    return updated_response(
        data={"password_updated": True},
        message="密码更新成功"
    )


@router.get("/{user_id}")
@log_route_debug(include_args=False, include_result=True, include_timing=True)
async def read_user_by_id(
    user_id: uuid.UUID,
    current_user: CurrentUser,
    session: SessionDep,
):
    """根据ID获取用户信息"""
    
    user = user_service.get(session=session, id=user_id)
    if not user:
        raise ResponseException(
            code=BusinessCode.USER_NOT_FOUND,
            message="用户不存在"
        )
    
    # 权限检查：只有超级管理员或用户本人可以查看
    if not user_service.is_superuser(current_user) and user.id != current_user.id:
        raise ResponseException(
            code=BusinessCode.AUTH_PERMISSION_DENIED,
            message="权限不足"
        )
    
    user_public = UserPublic.model_validate(user)
    return success_response(
        data=user_public.model_dump(mode='json'),
        message="获取用户信息成功"
    )


@router.put("/{user_id}")
async def update_user(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
    user_in: UserUpdate,
    current_user: Annotated[User, Depends(get_current_active_superuser)],
):
    """更新用户信息（仅超级管理员）"""
    
    user = user_service.get(session=session, id=user_id)
    if not user:
        raise ResponseException(
            code=BusinessCode.USER_NOT_FOUND,
            message="用户不存在"
        )
    
    # 如果要更新邮箱，检查是否已存在
    if user_in.email and user_in.email != user.email:
        existing_user = user_service.get_by_email(session=session, email=user_in.email)
        if existing_user:
            raise ResponseException(
                code=BusinessCode.USER_EMAIL_ALREADY_EXISTS,
                message=f"邮箱 {user_in.email} 已被使用"
            )
    
    # 更新用户
    user = user_service.update(session=session, db_obj=user, obj_in=user_in)
    user_public = UserPublic.model_validate(user)
    
    return updated_response(
        data=user_public.model_dump(mode='json'),
        message="用户信息更新成功"
    )


@router.delete("/{user_id}")
async def delete_user(
    session: SessionDep,
    user_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_superuser)],
):
    """删除用户（仅超级管理员）"""
    
    user = user_service.get(session=session, id=user_id)
    if not user:
        raise ResponseException(
            code=BusinessCode.USER_NOT_FOUND,
            message="用户不存在"
        )
    
    # 不能删除自己
    if user.id == current_user.id:
        raise ResponseException(
            code=BusinessCode.OPERATION_FAILED,
            message="不能删除自己的账户"
        )
    
    # 删除用户
    user_service.delete(session=session, id=user_id)
    
    return deleted_response(message="用户删除成功")
