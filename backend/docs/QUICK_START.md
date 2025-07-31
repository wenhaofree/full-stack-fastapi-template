# 🚀 FastAPI 快速开发指南

## 5分钟创建新功能

### 1️⃣ 创建模型 (`app/models/your_model.py`)

```python
from sqlmodel import Field, SQLModel
import uuid

class YourModelBase(SQLModel):
    name: str = Field(max_length=255)
    description: str | None = None

class YourModel(YourModelBase, table=True):
    __tablename__ = "your_table"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
```

### 2️⃣ 创建 Schemas (`app/schemas/your_model.py`)

```python
from sqlmodel import SQLModel
import uuid

class YourModelCreate(YourModelBase):
    pass

class YourModelUpdate(SQLModel):
    name: str | None = None
    description: str | None = None

class YourModelPublic(YourModelBase):
    id: uuid.UUID
```

### 3️⃣ 创建服务 (`app/services/your_model_service.py`)

```python
from app.services.base import BaseService
from app.models.your_model import YourModel
from app.schemas.your_model import YourModelCreate, YourModelUpdate

class YourModelService(BaseService[YourModel, YourModelCreate, YourModelUpdate]):
    def __init__(self):
        super().__init__(YourModel)

your_model_service = YourModelService()
```

### 4️⃣ 创建路由 (`app/routes/your_models.py`)

```python
from fastapi import APIRouter
from app.dependencies.database import SessionDep
from app.schemas.your_model import YourModelCreate, YourModelPublic
from app.services.your_model_service import your_model_service

router = APIRouter()

@router.post("/", response_model=YourModelPublic)
async def create_item(*, session: SessionDep, item_in: YourModelCreate):
    return your_model_service.create(session=session, obj_in=item_in)

@router.get("/{id}", response_model=YourModelPublic)
async def read_item(session: SessionDep, id: uuid.UUID):
    item = your_model_service.get(session=session, id=id)
    if not item:
        raise ResourceNotFoundError("Item not found")
    return item
```

### 5️⃣ 注册路由 (`app/routes/api.py`)

```python
from . import your_models

api_router.include_router(your_models.router, prefix="/your-models", tags=["your-models"])
```

### 6️⃣ 更新导入

在 `app/models/__init__.py`:
```python
from .your_model import YourModel
__all__ = [..., "YourModel"]
```

在 `app/schemas/__init__.py`:
```python
from .your_model import YourModelCreate, YourModelPublic, YourModelUpdate
__all__ = [..., "YourModelCreate", "YourModelPublic", "YourModelUpdate"]
```

## 📁 目录结构速览

```
app/
├── models/         # 数据库模型
├── schemas/        # API 数据结构  
├── services/       # 业务逻辑
├── routes/         # 路由定义
├── dependencies/   # 依赖注入
├── exceptions/     # 异常处理
├── middleware/     # 中间件
├── core/          # 核心配置
└── main.py        # 应用入口
```

## 🔧 常用命令

```bash
# 开发服务器
fastapi run app/main.py --reload

# 测试
pytest

# 格式化代码
ruff format .

# 数据库迁移
alembic revision --autogenerate -m "Add your_table"
alembic upgrade head

# 初始化数据
python app/initial_data.py
```

## 💡 开发技巧

1. **复制现有模块**: 从 `user.py` 或 `item.py` 复制并修改
2. **使用类型提示**: 所有函数都要有类型注解
3. **异常处理**: 使用 `app/exceptions/` 中的自定义异常
4. **认证**: 需要认证的路由添加 `CurrentUser` 依赖
5. **测试**: 在 `app/tests/` 中添加对应测试

## 🎯 下一步

- 阅读完整的 [DEVELOPMENT_GUIDE.md](./DEVELOPMENT_GUIDE.md)
- 查看现有的 `user.py` 和 `item.py` 示例
- 运行测试确保一切正常工作
