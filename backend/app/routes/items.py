"""标准化的物品路由 - 使用统一响应格式。"""

import uuid

from fastapi import APIRouter, Query
from sqlmodel import func, select

from app.dependencies.auth import CurrentUser
from app.dependencies.database import SessionDep
from app.core.constants import BusinessCode
from app.models import Item
from app.schemas import ItemCreate, ItemPublic, ItemUpdate
from app.services.item_service import item_service
from app.utils.response import (
    ResponseException,
    created_response,
    deleted_response,
    list_response,
    success_response,
    updated_response,
)
from app.core.route_logging import log_route_debug, log_route_info  # 暂时禁用

router = APIRouter()


@router.get("/")
@log_route_debug(include_args=True, include_result=True, include_timing=True)  # 暂时禁用
async def read_items(
    session: SessionDep,
    current_user: CurrentUser,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    include_deleted: bool = Query(False, description="是否包含已删除的物品"),
):
    """获取物品列表"""

    # 计算分页参数
    skip = (page - 1) * page_size

    if current_user.is_superuser:
        # 超级管理员可以查看所有物品
        total = item_service.get_total_count(session=session, include_deleted=include_deleted)
        items = item_service.get_multi(session=session, skip=skip, limit=page_size, include_deleted=include_deleted)
    else:
        # 普通用户只能查看自己的物品
        total = item_service.get_count_by_owner(session=session, owner_id=current_user.id, include_deleted=include_deleted)
        items = item_service.get_multi_by_owner(
            session=session,
            owner_id=current_user.id,
            skip=skip,
            limit=page_size,
            include_deleted=include_deleted
        )

    # 转换为公开格式
    item_list = [ItemPublic.model_validate(item) for item in items]

    return list_response(
        items=[item.model_dump(mode='json') for item in item_list],
        total=total,
        page=page,
        page_size=page_size,
        message=f"获取物品列表成功{'（包含已删除物品）' if include_deleted else ''}"
    )


@router.get("/me")
# @log_route_debug(include_args=True, include_result=True, include_timing=True)  # 暂时禁用
async def read_my_items(
    session: SessionDep,
    current_user: CurrentUser,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    include_deleted: bool = Query(False, description="是否包含已删除的物品"),
):
    """获取当前用户的物品列表"""

    # 计算分页参数
    skip = (page - 1) * page_size

    # 获取当前用户的物品
    total = item_service.get_count_by_owner(
        session=session,
        owner_id=current_user.id,
        include_deleted=include_deleted
    )

    items = item_service.get_multi_by_owner(
        session=session,
        owner_id=current_user.id,
        skip=skip,
        limit=page_size,
        include_deleted=include_deleted
    )

    # 转换为公开格式
    item_list = [ItemPublic.model_validate(item) for item in items]

    return success_response(
        data={
            "items": [item.model_dump(mode='json') for item in item_list],
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        },
        message="获取我的物品列表成功"
    )


@router.get("/{id}")
# @log_route_debug(include_args=True, include_result=True, include_timing=True)  # 暂时禁用
async def read_item(session: SessionDep, current_user: CurrentUser, id: uuid.UUID):
    """根据ID获取物品详情"""

    item = session.get(Item, id)
    if not item:
        raise ResponseException(
            code=BusinessCode.RESOURCE_NOT_FOUND,
            message=f"物品 {id} 不存在"
        )

    # 权限检查：超级管理员或物品所有者
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise ResponseException(
            code=BusinessCode.PERMISSION_DENIED,
            message="没有权限访问此物品"
        )

    item_public = ItemPublic.model_validate(item)
    return success_response(
        data=item_public.model_dump(mode='json'),
        message="获取物品详情成功"
    )


@router.post("/")
# @log_route_debug(include_args=True, include_result=True, include_timing=True)  # 暂时禁用
async def create_item(
    *, session: SessionDep, current_user: CurrentUser, item_in: ItemCreate
):
    """创建新物品"""

    # 创建物品，设置当前用户为所有者
    item = Item.model_validate(item_in, update={"owner_id": current_user.id})
    session.add(item)
    session.commit()
    session.refresh(item)

    item_public = ItemPublic.model_validate(item)
    return created_response(
        data=item_public.model_dump(mode='json'),
        message="物品创建成功"
    )


@router.put("/{id}")
# @log_route_debug(include_args=True, include_result=True, include_timing=True)  # 暂时禁用
async def update_item(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    item_in: ItemUpdate,
):
    """更新物品信息"""

    item = session.get(Item, id)
    if not item:
        raise ResponseException(
            code=BusinessCode.RESOURCE_NOT_FOUND,
            message=f"物品 {id} 不存在"
        )

    # 权限检查：超级管理员或物品所有者
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise ResponseException(
            code=BusinessCode.PERMISSION_DENIED,
            message="没有权限修改此物品"
        )

    # 更新物品信息
    update_dict = item_in.model_dump(exclude_unset=True)
    item.sqlmodel_update(update_dict)
    session.add(item)
    session.commit()
    session.refresh(item)

    item_public = ItemPublic.model_validate(item)
    return updated_response(
        data=item_public.model_dump(mode='json'),
        message="物品信息更新成功"
    )


@router.delete("/{id}")
# @log_route_debug(include_args=True, include_result=True, include_timing=True)  # 暂时禁用
async def delete_item(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
):
    """软删除物品"""

    item = item_service.get(session=session, id=id, include_deleted=False)
    if not item:
        raise ResponseException(
            code=BusinessCode.RESOURCE_NOT_FOUND,
            message=f"物品 {id} 不存在或已被删除"
        )

    # 权限检查：超级管理员或物品所有者
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise ResponseException(
            code=BusinessCode.PERMISSION_DENIED,
            message="没有权限删除此物品"
        )

    # 保存物品信息用于返回
    item_title = item.title

    # 软删除物品
    item_service.soft_delete(session=session, id=id)

    return deleted_response(
        message=f"物品 '{item_title}' 删除成功"
    )


@router.post("/{id}/restore")
# @log_route_debug(include_args=True, include_result=True, include_timing=True)  # 暂时禁用
async def restore_item(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
):
    """恢复已删除的物品"""

    item = item_service.restore(session=session, id=id)
    if not item:
        raise ResponseException(
            code=BusinessCode.RESOURCE_NOT_FOUND,
            message=f"物品 {id} 不存在或未被删除"
        )

    # 权限检查：超级管理员或物品所有者
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise ResponseException(
            code=BusinessCode.PERMISSION_DENIED,
            message="没有权限恢复此物品"
        )

    item_public = ItemPublic.model_validate(item)
    return success_response(
        data=item_public.model_dump(mode='json'),
        message=f"物品 '{item.title}' 恢复成功"
    )


@router.delete("/{id}/permanent")
# @log_route_debug(include_args=True, include_result=True, include_timing=True)  # 暂时禁用
async def permanently_delete_item(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
):
    """永久删除物品（谨慎使用）"""

    item = item_service.get(session=session, id=id, include_deleted=True)
    if not item:
        raise ResponseException(
            code=BusinessCode.RESOURCE_NOT_FOUND,
            message=f"物品 {id} 不存在"
        )

    # 权限检查：超级管理员或物品所有者
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise ResponseException(
            code=BusinessCode.PERMISSION_DENIED,
            message="没有权限永久删除此物品"
        )

    # 保存物品信息用于返回
    item_title = item.title

    # 永久删除物品
    item_service.delete(session=session, id=id)

    return deleted_response(
        message=f"物品 '{item_title}' 永久删除成功"
    )
