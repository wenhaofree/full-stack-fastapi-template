# 🏗️ FastAPI 项目架构文档

## 架构概览

本项目采用分层架构设计，遵循现代化 FastAPI 最佳实践，实现了关注点分离和高内聚低耦合的设计原则。

## 🔄 请求流程

```
HTTP Request
    ↓
Middleware (CORS, Logging, Error Handling)
    ↓
Routes (API Endpoints)
    ↓
Dependencies (Auth, Database)
    ↓
Services (Business Logic)
    ↓
Models (Database Operations)
    ↓
Database
```

## 📁 分层架构详解

### 1. 表示层 (Presentation Layer)

**位置**: `app/routes/`

**职责**:
- 处理 HTTP 请求和响应
- 参数验证和序列化
- 路由定义和文档

**文件结构**:
```
routes/
├── api.py          # 主路由聚合器
├── auth.py         # 认证相关路由
├── users.py        # 用户管理路由
├── items.py        # 项目管理路由
├── health.py       # 健康检查路由
└── private.py      # 开发环境专用路由
```

### 2. 业务逻辑层 (Business Logic Layer)

**位置**: `app/services/`

**职责**:
- 实现业务规则和逻辑
- 数据处理和转换
- 跨模型的复杂操作

**文件结构**:
```
services/
├── base.py         # 基础服务类 (通用 CRUD)
├── auth_service.py # 认证业务逻辑
├── user_service.py # 用户业务逻辑
└── item_service.py # 项目业务逻辑
```

### 3. 数据访问层 (Data Access Layer)

**位置**: `app/models/`

**职责**:
- 数据库模型定义
- 数据库表结构
- 关系映射

**文件结构**:
```
models/
├── base.py         # 基础模型类
├── user.py         # 用户数据模型
└── item.py         # 项目数据模型
```

### 4. 数据传输层 (Data Transfer Layer)

**位置**: `app/schemas/`

**职责**:
- API 请求/响应数据结构
- 数据验证规则
- 序列化/反序列化

**文件结构**:
```
schemas/
├── common.py       # 通用 schemas
├── auth.py         # 认证相关 schemas
├── user.py         # 用户相关 schemas
└── item.py         # 项目相关 schemas
```

## 🔧 横切关注点 (Cross-cutting Concerns)

### 依赖注入 (`app/dependencies/`)

```
dependencies/
├── auth.py         # 认证依赖
└── database.py     # 数据库依赖
```

**作用**:
- 管理组件间的依赖关系
- 提供可重用的依赖项
- 支持测试和模拟

### 异常处理 (`app/exceptions/`)

```
exceptions/
├── base.py         # 基础异常类
├── auth.py         # 认证异常
├── business.py     # 业务异常
└── handlers.py     # 全局异常处理器
```

**作用**:
- 统一错误处理机制
- 结构化错误响应
- 错误日志记录

### 中间件 (`app/middleware/`)

```
middleware/
├── cors.py         # 跨域处理
├── logging.py      # 请求日志
└── error.py        # 错误处理
```

**作用**:
- 请求/响应预处理
- 横切功能实现
- 性能监控

### 核心配置 (`app/core/`)

```
core/
├── config.py       # 应用配置
├── database.py     # 数据库配置
├── security.py     # 安全配置
└── logging.py      # 日志配置
```

**作用**:
- 集中配置管理
- 环境变量处理
- 核心组件初始化

## 🔄 数据流向

### 1. 创建资源流程

```
POST /api/v1/items/
    ↓
routes/items.py::create_item()
    ↓
dependencies/auth.py::get_current_user()
    ↓
services/item_service.py::create_with_owner()
    ↓
models/item.py::Item
    ↓
Database
```

### 2. 查询资源流程

```
GET /api/v1/items/{id}
    ↓
routes/items.py::read_item()
    ↓
services/item_service.py::get()
    ↓
models/item.py::Item
    ↓
Database
    ↓
schemas/item.py::ItemPublic
```

## 🎯 设计原则

### 1. 单一职责原则 (SRP)
- 每个模块只负责一个功能领域
- 路由只处理 HTTP 相关逻辑
- 服务只处理业务逻辑
- 模型只定义数据结构

### 2. 依赖倒置原则 (DIP)
- 高层模块不依赖低层模块
- 通过依赖注入管理依赖关系
- 使用抽象接口而非具体实现

### 3. 开闭原则 (OCP)
- 对扩展开放，对修改关闭
- 通过继承和组合扩展功能
- 插件化的中间件系统

### 4. 接口隔离原则 (ISP)
- 客户端不应依赖不需要的接口
- 细粒度的 schema 定义
- 专用的服务接口

## 🔒 安全架构

### 认证流程

```
Client Request
    ↓
middleware/auth.py (JWT Token Validation)
    ↓
dependencies/auth.py::get_current_user()
    ↓
services/user_service.py::authenticate()
    ↓
Route Handler
```

### 授权检查

```
Route Handler
    ↓
dependencies/auth.py::get_current_active_superuser()
    ↓
Business Logic (Permission Check)
    ↓
Resource Access
```

## 📊 性能考虑

### 1. 数据库优化
- 使用连接池管理数据库连接
- 实现查询优化和索引策略
- 支持读写分离

### 2. 缓存策略
- 服务层缓存业务数据
- 路由层缓存响应结果
- 数据库查询结果缓存

### 3. 异步处理
- 使用 async/await 处理 I/O 操作
- 非阻塞的数据库操作
- 异步中间件处理

## 🧪 测试架构

### 测试分层

```
tests/
├── unit/           # 单元测试 (Services, Utils)
├── integration/    # 集成测试 (Database, External APIs)
├── api/           # API 测试 (Routes)
└── e2e/           # 端到端测试
```

### 测试策略
- **单元测试**: 测试业务逻辑和工具函数
- **集成测试**: 测试数据库操作和外部服务
- **API 测试**: 测试路由和中间件
- **端到端测试**: 测试完整的用户场景

## 🚀 部署架构

### 容器化部署

```
Docker Container
├── FastAPI Application
├── uv (Package Manager)
├── PostgreSQL Client
└── Application Dependencies
```

### 环境配置
- **开发环境**: 自动重载，详细日志
- **测试环境**: 模拟数据，集成测试
- **生产环境**: 性能优化，安全加固

这种架构设计确保了代码的可维护性、可扩展性和可测试性，为团队协作和项目长期发展提供了坚实的基础。
