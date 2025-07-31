# 使用说明：
```shell
git clone 
cd 
uv sync
source .venv/bin/activate

# 初始化数据库
vim .env # 修改数据库密码等配置
python app/initial_data.py
python verify_initial_data.py # 验证数据是否初始化成功
python verify_documentation.py # 验证文档是否齐全

```

# TODO:
更新为标准的后端框架结构，后续作为统一使用的模版；

1. 统一返回状态码
2. 异常统一处理
3. aop日志入参和出参
4. 认证和授权功能确认
5. 目录结构优化；
backend/
├── app/
│   ├── models/              # 数据库模型
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user.py
│   │   └── item.py
│   ├── schemas/             # API数据结构
│   │   ├── __init__.py
│   │   ├── common.py
│   │   ├── auth.py
│   │   ├── user.py
│   │   └── item.py
│   ├── services/            # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   └── item_service.py
│   ├── routes/              # 路由定义
│   │   ├── __init__.py
│   │   ├── api.py
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── items.py
│   │   └── health.py
│   ├── dependencies/        # 依赖注入
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── database.py
│   │   └── common.py
│   ├── exceptions/          # 异常处理
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── auth.py
│   │   ├── business.py
│   │   └── handlers.py
│   ├── middleware/          # 中间件
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── logging.py
│   │   ├── cors.py
│   │   └── error.py
│   ├── core/               # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   └── logging.py
│   ├── utils/              # 工具函数
│   │   ├── __init__.py
│   │   ├── email.py
│   │   ├── security.py
│   │   └── helpers.py
│   ├── alembic/            # 数据库迁移
│   ├── tests/              # 测试
│   └── main.py             # 应用入口
├── scripts/                # 脚本文件
├── pyproject.toml          # 项目配置
├── uv.lock                 # 依赖锁定
├── Dockerfile
└── README.md


🚀 实施优先级建议
高优先级（立即实施）：
统一错误处理机制
完善类型注解
添加基础监控和日志
实现CRUD基类

中优先级（短期实施）：
异步数据库操作
缓存层实现
安全性增强
测试覆盖率提升

🎯 实施步骤建议
第一阶段（立即实施）：
分离 models 和 schemas
重构 CRUD 为 services
移动和重组路由结构
添加统一异常处理

第二阶段（1-2周内）：
添加中间件层
优化依赖注入
完善测试结构
添加日志系统