# 使用说明：
```shell
git clone 
cd 
uv sync
source .venv/bin/activate

# 初始化数据库
vim .env # 修改数据库密码等配置
python app/initial_data.py
python app/tests/integration/verify_initial_data.py  # 验证数据是否初始化成功
python app/tests/integration/verify_documentation.py # 验证文档是否齐全

```

# TODO:
更新为标准的后端框架结构，后续作为统一使用的模版；

1. 统一返回状态码✅
2. 异常统一处理-待验证
3. aop日志路由接口入参和出参-todo
4. 认证和授权功能确认✅
5. 模块解耦 + 依赖注入=目录结构优化；✅
7. 接口幂等性与重复请求处理-后续接入redis处理
8. API 鉴权 + RBAC 权限系统- todo
9. 日志追踪与链路标识+彩色日志和追踪ID✅
10. 异步任务与事件解耦
11. 统一分页规范	page/limit/total/default size 等结构一致-待验证
12. 版本控制	API 使用 /v1/ 路由，支持未来版本演进-待验证
13. 时间字段增加✅


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