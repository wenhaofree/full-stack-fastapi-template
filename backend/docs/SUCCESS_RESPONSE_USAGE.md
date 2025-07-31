# ✅ success_response 使用指南

## 概述

参考 `users.py` 的实现，在 `items.py` 中正确使用了 `success_response`，确保API响应格式的一致性。

## 📋 响应函数使用规则

### 1. list_response
**用途**: 返回列表数据，包含分页信息
**使用场景**: 
- 获取资源列表
- 需要分页的数据

```python
return list_response(
    items=[item.model_dump(mode='json') for item in item_list],
    total=total,
    page=page,
    page_size=page_size,
    message="获取物品列表成功"
)
```

### 2. success_response
**用途**: 返回单个资源或自定义数据结构
**使用场景**:
- 获取单个资源详情
- 获取当前用户的专属数据
- 返回自定义数据结构

```python
return success_response(
    data=item_public.model_dump(mode='json'),
    message="获取物品详情成功"
)
```

### 3. created_response
**用途**: 资源创建成功
```python
return created_response(
    data=item_public.model_dump(mode='json'),
    message="物品创建成功"
)
```

### 4. updated_response
**用途**: 资源更新成功
```python
return updated_response(
    data=item_public.model_dump(mode='json'),
    message="物品信息更新成功"
)
```

### 5. deleted_response
**用途**: 资源删除成功
```python
return deleted_response(
    message=f"物品 '{item_title}' 删除成功"
)
```

## 🔄 items.py 中的 success_response 使用

### 1. 获取单个物品详情
```python
@router.get("/{id}")
async def read_item(session: SessionDep, current_user: CurrentUser, id: uuid.UUID):
    """根据ID获取物品详情"""
    
    # ... 业务逻辑 ...
    
    item_public = ItemPublic.model_validate(item)
    return success_response(
        data=item_public.model_dump(mode='json'),
        message="获取物品详情成功"
    )
```

### 2. 获取当前用户的物品列表 (新增)
```python
@router.get("/me")
async def read_my_items(
    session: SessionDep,
    current_user: CurrentUser,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
):
    """获取当前用户的物品列表"""
    
    # ... 业务逻辑 ...
    
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
```

## 📊 响应格式对比

### users.py 中的使用
```python
# 获取用户列表 - list_response
@router.get("/")
return list_response(...)

# 获取当前用户信息 - success_response
@router.get("/me")
return success_response(...)

# 根据ID获取用户 - success_response
@router.get("/{user_id}")
return success_response(...)
```

### items.py 中的使用 (修改后)
```python
# 获取物品列表 - list_response
@router.get("/")
return list_response(...)

# 获取我的物品列表 - success_response
@router.get("/me")
return success_response(...)

# 根据ID获取物品 - success_response
@router.get("/{id}")
return success_response(...)
```

## 🎯 为什么 /me 路由使用 success_response？

### 1. 语义区别
- `/items/` - 获取所有物品（管理员）或用户物品（普通用户）
- `/items/me` - 明确获取当前用户的物品

### 2. 数据结构
- `list_response` 有固定的分页结构
- `success_response` 允许自定义数据结构，更灵活

### 3. 用户体验
- `/me` 路由通常返回用户专属数据
- 使用 `success_response` 可以包含更多个性化信息

## 📝 响应格式示例

### list_response 格式
```json
{
  "code": 10000,
  "message": "获取物品列表成功",
  "data": {
    "items": [...],
    "total": 10,
    "page": 1,
    "page_size": 10,
    "pages": 1
  },
  "timestamp": "2025-07-31T15:30:00.000000"
}
```

### success_response 格式 (单个资源)
```json
{
  "code": 10000,
  "message": "获取物品详情成功",
  "data": {
    "id": "uuid",
    "title": "物品标题",
    "description": "物品描述"
  },
  "timestamp": "2025-07-31T15:30:00.000000"
}
```

### success_response 格式 (自定义结构)
```json
{
  "code": 10000,
  "message": "获取我的物品列表成功",
  "data": {
    "items": [...],
    "total": 5,
    "page": 1,
    "page_size": 10,
    "pages": 1
  },
  "timestamp": "2025-07-31T15:30:00.000000"
}
```

## ✅ 最佳实践

### 1. 选择合适的响应函数
- 列表数据 → `list_response`
- 单个资源 → `success_response`
- 创建操作 → `created_response`
- 更新操作 → `updated_response`
- 删除操作 → `deleted_response`

### 2. 保持一致性
- 相同类型的操作使用相同的响应函数
- 参考现有路由的实现
- 遵循RESTful API设计原则

### 3. 消息友好性
- 使用中文友好的消息
- 包含具体的操作结果
- 提供有用的上下文信息

## 🎉 总结

通过参考 `users.py` 的实现，我们在 `items.py` 中正确使用了 `success_response`：

1. ✅ **获取单个物品** - 使用 `success_response`
2. ✅ **获取我的物品列表** - 使用 `success_response` (新增)
3. ✅ **获取物品列表** - 使用 `list_response`
4. ✅ **创建物品** - 使用 `created_response`
5. ✅ **更新物品** - 使用 `updated_response`
6. ✅ **删除物品** - 使用 `deleted_response`

现在 `items.py` 与 `users.py` 具有完全一致的响应格式和API设计风格！
