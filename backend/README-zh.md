# 🚀 FastAPI 后端项目

## 📋 项目简介

这是一个基于 FastAPI 的现代化后端项目模板，集成了完整的用户管理、物品管理、认证授权、日志系统等功能。项目采用现代化的架构设计，遵循最佳实践，可作为企业级应用的基础模板。

## ⚡ 快速开始

### 环境要求
- Python >= 3.10
- PostgreSQL >= 12.0
- uv (推荐) 或 pip

### 安装步骤

```bash
# 1. 克隆项目
git clone <repository-url>
cd full-stack-fastapi-template/backend

# 2. 安装依赖
uv sync
source .venv/bin/activate

# 3. 配置环境变量
cp ../.env.example ../.env
vim ../.env  # 修改数据库配置等

# 4. 初始化数据库
python app/initial_data.py

# 5. 验证安装
python app/tests/integration/verify_initial_data.py
python app/tests/integration/verify_documentation.py

# 6. 启动开发服务器
fastapi dev app/main.py
```

### 访问地址
- **API 文档**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/api/v1/utils/health-check

## 📚 完整文档

详细的开发和部署文档请参考：

### 🎯 新手必读
- **[开发环境搭建指南](./docs/DEVELOPMENT_SETUP_GUIDE.md)** - 完整的环境搭建步骤
- **[API 使用指南](./docs/API_USAGE_GUIDE.md)** - API 接口使用说明
- **[快速开始](./docs/QUICK_START.md)** - 5分钟快速上手

### 🏗️ 架构文档
- **[系统架构](./docs/ARCHITECTURE.md)** - 详细的架构设计
- **[开发指南](./docs/DEVELOPMENT_GUIDE.md)** - 开发规范和最佳实践
- **[部署指南](./docs/DEPLOYMENT_GUIDE.md)** - 生产环境部署

### 📖 完整文档索引
- **[完整文档索引](./docs/COMPLETE_DOCUMENTATION_INDEX.md)** - 所有文档的导航

## ✅ 已实现功能

### 🔐 认证授权
- ✅ JWT Token 认证
- ✅ 用户注册/登录
- ✅ 权限控制 (普通用户/超级管理员)
- ✅ 密码加密存储

### 👥 用户管理
- ✅ 用户 CRUD 操作
- ✅ 用户软删除/恢复
- ✅ 用户信息更新
- ✅ 时间戳字段 (创建/更新/删除时间)

### 📦 物品管理
- ✅ 物品 CRUD 操作
- ✅ 物品软删除/恢复
- ✅ 所有者权限控制
- ✅ 时间戳字段

### � 响应标准化
- ✅ 统一响应格式
- ✅ 统一错误处理
- ✅ 请求追踪 ID
- ✅ 分页响应规范

### 📝 日志系统
- ✅ 结构化日志记录
- ✅ 请求/响应日志
- ✅ 路由参数日志
- ✅ SQL 查询日志
- ✅ 彩色控制台输出
- ✅ 文件日志轮转

### 🧪 测试体系
- ✅ 单元测试框架
- ✅ 集成测试
- ✅ API 测试
- ✅ 测试数据管理

### 🔧 开发工具
- ✅ 代码格式化 (Ruff)
- ✅ 类型检查 (MyPy)
- ✅ 代码检查 (Ruff)
- ✅ 预提交钩子

## 🎯 技术特性

### 🏗️ 架构设计
- **分层架构**: Models → Services → Routes
- **依赖注入**: FastAPI 原生依赖系统
- **模块化设计**: 清晰的目录结构
- **软删除**: 数据安全删除和恢复

### 🔒 安全特性
- **JWT 认证**: 安全的用户认证
- **密码加密**: bcrypt 密码哈希
- **权限控制**: 基于角色的访问控制
- **输入验证**: Pydantic 数据验证

### 📈 性能优化
- **异步处理**: 全异步 API 设计
- **数据库优化**: SQLModel ORM
- **连接池**: 数据库连接池管理
- **缓存策略**: 响应缓存机制

## 🚀 生产就绪

### 🐳 容器化部署
- Docker 支持
- Docker Compose 配置
- 多阶段构建优化

### 📊 监控运维
- 健康检查端点
- 结构化日志
- 错误追踪
- 性能监控

### 🔧 配置管理
- 环境变量配置
- 多环境支持
- 敏感信息保护