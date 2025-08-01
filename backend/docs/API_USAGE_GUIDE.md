# 📡 API 使用指南

## 📋 目录
- [API 概览](#api-概览)
- [认证授权](#认证授权)
- [用户管理](#用户管理)
- [物品管理](#物品管理)
- [响应格式](#响应格式)
- [错误处理](#错误处理)
- [最佳实践](#最佳实践)

## 🌐 API 概览

### 基础信息
- **Base URL**: `http://localhost:8000/api/v1`
- **认证方式**: JWT Bearer Token
- **数据格式**: JSON
- **字符编码**: UTF-8

### API 文档
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🔐 认证授权

### 1. 用户登录

```bash
POST /api/v1/login/access-token
Content-Type: application/x-www-form-urlencoded

username=admin@example.com&password=changethis
```

**响应示例:**
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer"
  },
  "timestamp": "2025-08-01T16:30:00Z",
  "request_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### 2. 使用 Token

```bash
# 在请求头中添加 Authorization
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### 3. 获取当前用户信息

```bash
GET /api/v1/users/me
Authorization: Bearer <token>
```

## 👥 用户管理

### 1. 创建用户 (仅超级管理员)

```bash
POST /api/v1/users/
Authorization: Bearer <admin-token>
Content-Type: application/json

{
  "email": "newuser@example.com",
  "password": "securepassword123",
  "full_name": "New User",
  "is_active": true,
  "is_superuser": false
}
```

### 2. 获取用户列表 (仅超级管理员)

```bash
GET /api/v1/users/?page=1&page_size=10&include_deleted=false
Authorization: Bearer <admin-token>
```

**查询参数:**
- `page`: 页码 (默认: 1)
- `page_size`: 每页数量 (默认: 10, 最大: 100)
- `include_deleted`: 是否包含已删除用户 (默认: false)

### 3. 获取特定用户

```bash
GET /api/v1/users/{user_id}
Authorization: Bearer <token>
```

### 4. 更新用户信息

```bash
PUT /api/v1/users/{user_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "full_name": "Updated Name",
  "email": "updated@example.com"
}
```

### 5. 软删除用户

```bash
DELETE /api/v1/users/{user_id}
Authorization: Bearer <admin-token>
```

### 6. 恢复已删除用户

```bash
POST /api/v1/users/{user_id}/restore
Authorization: Bearer <admin-token>
```

### 7. 永久删除用户

```bash
DELETE /api/v1/users/{user_id}/permanent
Authorization: Bearer <admin-token>
```

## 📦 物品管理

### 1. 创建物品

```bash
POST /api/v1/items/
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "我的新物品",
  "description": "这是一个很棒的物品"
}
```

### 2. 获取物品列表

```bash
# 获取所有物品 (超级管理员)
GET /api/v1/items/?page=1&page_size=10&include_deleted=false
Authorization: Bearer <admin-token>

# 获取我的物品
GET /api/v1/items/me?page=1&page_size=10&include_deleted=false
Authorization: Bearer <token>
```

### 3. 获取特定物品

```bash
GET /api/v1/items/{item_id}
Authorization: Bearer <token>
```

### 4. 更新物品

```bash
PUT /api/v1/items/{item_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "更新的标题",
  "description": "更新的描述"
}
```

### 5. 软删除物品

```bash
DELETE /api/v1/items/{item_id}
Authorization: Bearer <token>
```

### 6. 恢复已删除物品

```bash
POST /api/v1/items/{item_id}/restore
Authorization: Bearer <token>
```

### 7. 永久删除物品

```bash
DELETE /api/v1/items/{item_id}/permanent
Authorization: Bearer <token>
```

## 📄 响应格式

### 统一响应结构

所有 API 响应都遵循统一的格式：

```json
{
  "code": 200,
  "message": "操作成功",
  "data": { /* 具体数据 */ },
  "timestamp": "2025-08-01T16:30:00Z",
  "request_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### 分页响应格式

```json
{
  "code": 200,
  "message": "获取列表成功",
  "data": {
    "items": [/* 数据列表 */],
    "total": 100,
    "page": 1,
    "page_size": 10,
    "total_pages": 10
  },
  "timestamp": "2025-08-01T16:30:00Z",
  "request_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### 时间戳字段

所有实体都包含以下时间戳字段：

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "created_at": "2025-08-01T16:30:00Z",
  "updated_at": "2025-08-01T16:35:00Z",
  "deleted_at": null
}
```

## ❌ 错误处理

### HTTP 状态码

- `200`: 成功
- `201`: 创建成功
- `400`: 请求参数错误
- `401`: 未认证
- `403`: 权限不足
- `404`: 资源不存在
- `422`: 数据验证失败
- `500`: 服务器内部错误

### 错误响应格式

```json
{
  "code": 400,
  "message": "请求参数错误",
  "data": {
    "detail": "具体错误信息",
    "errors": [
      {
        "field": "email",
        "message": "邮箱格式不正确"
      }
    ]
  },
  "timestamp": "2025-08-01T16:30:00Z",
  "request_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### 常见错误码

| 业务码 | 说明 |
|--------|------|
| 1001 | 用户不存在 |
| 1002 | 密码错误 |
| 1003 | 用户已存在 |
| 2001 | 物品不存在 |
| 2002 | 权限不足 |
| 9001 | 系统错误 |

## 🎯 最佳实践

### 1. 请求头设置

```bash
Content-Type: application/json
Authorization: Bearer <token>
Accept: application/json
User-Agent: YourApp/1.0
```

### 2. 分页查询

```bash
# 推荐的分页参数
GET /api/v1/items/?page=1&page_size=20

# 避免过大的 page_size
# ❌ page_size=1000  (太大)
# ✅ page_size=50    (合适)
```

### 3. 错误处理

```javascript
// JavaScript 示例
async function apiCall() {
  try {
    const response = await fetch('/api/v1/users/me', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    const result = await response.json();
    
    if (result.code === 200) {
      return result.data;
    } else {
      throw new Error(result.message);
    }
  } catch (error) {
    console.error('API 调用失败:', error);
    throw error;
  }
}
```

### 4. 软删除处理

```bash
# 获取活跃数据 (默认)
GET /api/v1/items/

# 获取包含已删除的数据
GET /api/v1/items/?include_deleted=true

# 恢复已删除的数据
POST /api/v1/items/{id}/restore
```

### 5. 请求追踪

每个 API 响应都包含 `request_id` 字段，用于请求追踪和问题排查：

```json
{
  "request_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

在日志中可以通过 `request_id` 查找相关的请求记录。

## 🔧 调试技巧

### 1. 使用 curl 测试

```bash
# 登录获取 token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=changethis" | \
  jq -r '.data.access_token')

# 使用 token 调用 API
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/users/me"
```

### 2. 查看请求日志

```bash
# 实时查看 API 请求日志
tail -f logs/app.log | grep "REQUEST\|RESPONSE"
```

### 3. API 测试工具

推荐使用以下工具测试 API：
- **Postman**: 图形化 API 测试
- **Insomnia**: 轻量级 API 客户端
- **HTTPie**: 命令行 HTTP 客户端
- **curl**: 通用命令行工具

---

**📚 更多信息请参考 [Swagger 文档](http://localhost:8000/docs)**
