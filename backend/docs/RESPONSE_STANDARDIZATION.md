# 📋 API 响应格式标准化文档

## 概述

本文档描述了 FastAPI 项目中统一的 API 响应格式标准，包括成功响应、错误响应、状态码管理等。

## 🎯 标准化目标

1. **统一响应格式** - 所有 API 返回相同的数据结构
2. **业务状态码分离** - 区分 HTTP 状态码和业务状态码
3. **错误处理标准化** - 统一的错误信息格式
4. **国际化支持** - 支持多语言错误消息
5. **前端友好** - 便于前端统一处理

## 📊 响应格式规范

### 统一响应结构

所有 API 响应都遵循以下格式：

```json
{
  "code": 10000,           // 业务状态码
  "message": "操作成功",    // 响应消息
  "data": {}              // 响应数据（可为 null）
}
```

### 字段说明

- **code**: 业务状态码，用于标识具体的业务结果
- **message**: 人类可读的响应消息，支持国际化
- **data**: 实际的响应数据，成功时包含数据，失败时为 null

## 🔢 状态码体系

### 业务状态码分类

#### 成功状态码 (1xxxx)
- `10000` - 操作成功
- `10001` - 创建成功
- `10002` - 更新成功
- `10003` - 删除成功

#### 客户端错误 (2xxxx)
- `20001` - 参数错误
- `20002` - 资源不存在
- `20003` - 资源已存在
- `20004` - 权限不足
- `20005` - 操作失败

#### 认证相关 (3xxxx)
- `30001` - 令牌无效
- `30002` - 令牌已过期
- `30003` - 登录失败
- `30004` - 权限不足
- `30005` - 用户已禁用

#### 用户相关 (4xxxx)
- `40001` - 用户不存在
- `40002` - 用户已存在
- `40003` - 密码错误
- `40004` - 邮箱已存在
- `40005` - 用户未激活

#### 项目相关 (5xxxx)
- `50001` - 项目不存在
- `50002` - 项目权限不足
- `50003` - 项目已存在

#### 系统错误 (9xxxx)
- `90001` - 系统错误
- `90002` - 数据库错误
- `90003` - 外部服务错误

### HTTP 状态码映射

业务状态码会自动映射到相应的 HTTP 状态码：

| 业务状态码范围 | HTTP 状态码 | 说明 |
|---------------|-------------|------|
| 1xxxx | 200/201 | 成功 |
| 2xxxx | 400/404/409/422 | 客户端错误 |
| 3xxxx | 401/403 | 认证授权错误 |
| 4xxxx | 400/404/409 | 用户相关错误 |
| 5xxxx | 400/403/404 | 业务相关错误 |
| 9xxxx | 500/502 | 服务器错误 |

## 📝 响应示例

### 成功响应

#### 获取单个资源
```json
{
  "code": 10000,
  "message": "获取用户信息成功",
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "full_name": "张三",
    "is_active": true
  }
}
```

#### 获取列表资源
```json
{
  "code": 10000,
  "message": "获取用户列表成功",
  "data": {
    "items": [
      {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "email": "user@example.com",
        "full_name": "张三"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 10,
    "total_pages": 1
  }
}
```

#### 创建资源
```json
{
  "code": 10001,
  "message": "用户创建成功",
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "newuser@example.com",
    "full_name": "新用户"
  }
}
```

#### 删除资源
```json
{
  "code": 10003,
  "message": "用户删除成功",
  "data": {
    "deleted": true
  }
}
```

### 错误响应

#### 认证错误
```json
{
  "code": 30001,
  "message": "缺少认证令牌",
  "data": null
}
```

#### 权限错误
```json
{
  "code": 30004,
  "message": "权限不足，需要超级管理员权限",
  "data": null
}
```

#### 资源不存在
```json
{
  "code": 40001,
  "message": "用户不存在",
  "data": null
}
```

#### 参数验证错误
```json
{
  "code": 20001,
  "message": "参数验证失败",
  "data": null
}
```

#### 业务逻辑错误
```json
{
  "code": 40004,
  "message": "邮箱 user@example.com 已被使用",
  "data": null
}
```

## 🛠️ 实现方式

### 核心组件

1. **常量定义** (`app/core/constants.py`)
   - 业务状态码枚举
   - 状态码消息映射
   - HTTP 状态码映射

2. **响应模型** (`app/schemas/response.py`)
   - 统一响应基类
   - 成功响应类
   - 错误响应类
   - 分页响应类

3. **响应工具** (`app/utils/response.py`)
   - 响应创建函数
   - 自定义异常类
   - 状态码映射函数

4. **异常处理** (`app/exceptions/handlers.py`)
   - 全局异常处理器
   - 统一错误响应格式

### 使用方法

#### 在路由中使用

```python
from app.utils.response import success_response, created_response, ResponseException
from app.core.constants import BusinessCode

@router.get("/users/me")
async def get_current_user(current_user: CurrentUser):
    """获取当前用户信息"""
    return success_response(
        data=current_user.model_dump(),
        message="获取用户信息成功"
    )

@router.post("/users/")
async def create_user(user_in: UserCreate, session: SessionDep):
    """创建用户"""
    # 检查邮箱是否已存在
    if existing_user:
        raise ResponseException(
            code=BusinessCode.USER_EMAIL_ALREADY_EXISTS,
            message=f"邮箱 {user_in.email} 已被使用"
        )
    
    user = user_service.create(session=session, obj_in=user_in)
    return created_response(
        data=user.model_dump(),
        message="用户创建成功"
    )
```

#### 自定义异常

```python
from app.utils.response import ResponseException
from app.core.constants import BusinessCode

# 抛出业务异常
raise ResponseException(
    code=BusinessCode.USER_NOT_FOUND,
    message="用户不存在"
)

# 自定义消息
raise ResponseException(
    code=BusinessCode.USER_EMAIL_ALREADY_EXISTS,
    message=f"邮箱 {email} 已被使用"
)
```

## 🎯 前端集成

### JavaScript/TypeScript 示例

```typescript
interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T | null;
}

// 统一的 API 请求处理
async function apiRequest<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, options);
  const result: ApiResponse<T> = await response.json();
  
  if (result.code >= 20000) {
    // 业务错误
    throw new Error(result.message);
  }
  
  return result.data;
}

// 使用示例
try {
  const user = await apiRequest<User>('/api/v1/v2/users/me');
  console.log('用户信息:', user);
} catch (error) {
  console.error('获取用户信息失败:', error.message);
}
```

## 📋 最佳实践

1. **一致性** - 所有 API 都使用相同的响应格式
2. **语义化** - 业务状态码要有明确的语义
3. **国际化** - 错误消息支持多语言
4. **文档化** - 在 API 文档中明确说明状态码含义
5. **向后兼容** - 新增状态码时保持向后兼容

## 🔄 迁移指南

### 从旧格式迁移

1. **更新路由** - 使用新的响应工具函数
2. **替换异常** - 使用 `ResponseException` 替代 `HTTPException`
3. **更新测试** - 验证新的响应格式
4. **前端适配** - 更新前端代码以处理新格式

### 兼容性处理

在迁移期间，可以同时支持新旧格式：

```python
# 新路由使用标准格式
@router.get("/v2/users/")
async def get_users_v2():
    return success_response(data=users, message="获取成功")

# 旧路由保持兼容
@router.get("/users/")
async def get_users():
    return {"data": users, "count": len(users)}  # 旧格式
```

这种标准化确保了 API 的一致性和可维护性，为前后端协作提供了清晰的规范。
