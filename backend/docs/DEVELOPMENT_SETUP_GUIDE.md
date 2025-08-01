# 🚀 FastAPI 后端开发环境搭建指南

## 📋 目录
- [系统要求](#系统要求)
- [快速开始](#快速开始)
- [详细步骤](#详细步骤)
- [开发工具](#开发工具)
- [常见问题](#常见问题)
- [验证安装](#验证安装)

## 🔧 系统要求

### 必需软件
- **Python**: >= 3.10, < 4.0
- **uv**: Python 包管理器 (推荐) 或 pip
- **PostgreSQL**: >= 12.0 (数据库)
- **Git**: 版本控制

### 推荐软件
- **Docker**: 容器化部署 (可选)
- **VS Code**: 代码编辑器
- **Postman/Insomnia**: API 测试工具

## ⚡ 快速开始

```bash
# 1. 克隆项目
git clone <repository-url>
cd full-stack-fastapi-template/backend

# 2. 安装依赖
uv sync

# 3. 激活虚拟环境
source .venv/bin/activate

# 4. 配置环境变量
cp ../.env.example ../.env
vim ../.env  # 修改数据库配置

# 5. 初始化数据库
python app/initial_data.py

# 6. 启动开发服务器
fastapi dev app/main.py
```

## 📖 详细步骤

### 1. 项目克隆与目录结构

```bash
# 克隆项目
git clone <repository-url>
cd full-stack-fastapi-template

# 查看项目结构
tree -L 2
```

**项目结构说明:**
```
backend/
├── app/                    # 应用主目录
│   ├── core/              # 核心配置模块
│   ├── models/            # 数据库模型
│   ├── schemas/           # API 数据模式
│   ├── routes/            # 路由处理器
│   ├── services/          # 业务逻辑层
│   ├── dependencies/      # 依赖注入
│   ├── middleware/        # 中间件
│   ├── exceptions/        # 异常处理
│   └── tests/            # 测试文件
├── docs/                  # 项目文档
├── scripts/               # 脚本文件
├── logs/                  # 日志文件
└── pyproject.toml         # 项目配置
```

### 2. 环境配置

#### 2.1 Python 环境管理

**使用 uv (推荐):**
```bash
# 安装 uv (如果未安装)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 同步依赖
cd backend
uv sync

# 激活虚拟环境
source .venv/bin/activate
```

**使用 pip:**
```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -e .
```

#### 2.2 环境变量配置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
vim .env
```

**关键配置项:**
```bash
# 数据库配置
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=fastapi_db
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password

# 应用配置
SECRET_KEY=your-secret-key-here
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=your-admin-password

# 日志配置
LOG_LEVEL=DEBUG
LOG_REQUEST_DETAILS=true
LOG_FUNCTION_PARAMS=true
```

### 3. 数据库设置

#### 3.1 PostgreSQL 安装与配置

**macOS (使用 Homebrew):**
```bash
brew install postgresql
brew services start postgresql
createdb fastapi_db
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo -u postgres createdb fastapi_db
```

**Docker (推荐用于开发):**
```bash
docker run --name postgres-dev \
  -e POSTGRES_DB=fastapi_db \
  -e POSTGRES_USER=root \
  -e POSTGRES_PASSWORD=your_password \
  -p 5432:5432 \
  -d postgres:15
```

#### 3.2 数据库初始化

```bash
# 检查数据库连接
python app/backend_pre_start.py

# 运行数据库迁移
alembic upgrade head

# 创建初始数据
python app/initial_data.py

# 验证初始数据
python app/tests/integration/verify_initial_data.py
```

### 4. 开发服务器启动

#### 4.1 开发模式启动

```bash
# 使用 FastAPI CLI (推荐)
fastapi dev app/main.py

# 或使用 uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 4.2 生产模式启动

```bash
# 使用预启动脚本
bash scripts/prestart.sh

# 启动生产服务器
fastapi run app/main.py --port 8000
```

### 5. 验证安装

#### 5.1 健康检查

```bash
# API 健康检查
curl http://localhost:8000/api/v1/utils/health-check

# 预期响应
{"message": "OK"}
```

#### 5.2 API 文档访问

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

#### 5.3 运行测试

```bash
# 运行所有测试
bash scripts/test.sh

# 运行特定测试
pytest app/tests/test_main.py -v

# 运行集成测试
python app/tests/integration/verify_documentation.py
```

## 🛠️ 开发工具

### 代码质量工具

```bash
# 代码格式化
bash scripts/format.sh

# 代码检查
bash scripts/lint.sh

# 类型检查
mypy app/
```

### 数据库工具

```bash
# 创建新迁移
alembic revision --autogenerate -m "描述变更"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

### 日志查看

```bash
# 实时查看应用日志
tail -f logs/app.log

# 查看错误日志
tail -f logs/error.log

# 查看结构化日志
cat logs/app.log | jq '.'
```

## 🔍 常见问题

### 数据库连接问题

**问题**: `psycopg2.OperationalError: could not connect to server`

**解决方案**:
```bash
# 检查 PostgreSQL 服务状态
sudo systemctl status postgresql

# 检查端口占用
netstat -an | grep 5432

# 验证数据库配置
python -c "from app.core.db import engine; print(engine.url)"
```

### 依赖安装问题

**问题**: `uv sync` 失败

**解决方案**:
```bash
# 清理缓存
uv cache clean

# 重新同步
uv sync --refresh

# 或使用 pip 安装
pip install -e .
```

### 权限问题

**问题**: 无法创建日志文件

**解决方案**:
```bash
# 创建日志目录
mkdir -p logs

# 设置权限
chmod 755 logs
```

## 📚 下一步

1. **阅读架构文档**: [ARCHITECTURE.md](./ARCHITECTURE.md)
2. **了解开发规范**: [DEVELOPMENT_GUIDE.md](./DEVELOPMENT_GUIDE.md)
3. **查看 API 使用**: [API_USAGE.md](./API_USAGE.md)
4. **学习测试编写**: [TEST_STRUCTURE.md](./TEST_STRUCTURE.md)

## 🆘 获取帮助

- **项目文档**: `backend/docs/`
- **API 文档**: http://localhost:8000/docs
- **问题反馈**: 创建 GitHub Issue
- **开发讨论**: 项目 Discussions

---

**🎉 恭喜！你已经成功搭建了 FastAPI 开发环境！**
