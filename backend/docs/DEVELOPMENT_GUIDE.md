# FastAPI 项目开发指南

本文档介绍重构后的 FastAPI 项目结构和开发流程，帮助新手快速上手开发。

## 📁 项目结构

```
backend/app/
├── models/              # 数据库模型
│   ├── __init__.py
│   ├── base.py         # 基础模型类
│   ├── user.py         # 用户模型
│   └── item.py         # 项目模型
├── schemas/            # API 数据结构
│   ├── __init__.py
│   ├── common.py       # 通用 schemas
│   ├── auth.py         # 认证相关 schemas
│   ├── user.py         # 用户相关 schemas
│   └── item.py         # 项目相关 schemas
├── services/           # 业务逻辑层
│   ├── __init__.py
│   ├── base.py         # 基础服务类
│   ├── auth_service.py # 认证服务
│   ├── user_service.py # 用户服务
│   └── item_service.py # 项目服务
├── routes/             # 路由定义
│   ├── __init__.py
│   ├── api.py          # 主路由聚合
│   ├── auth.py         # 认证路由
│   ├── users.py        # 用户路由
│   ├── items.py        # 项目路由
│   ├── health.py       # 健康检查路由
│   └── private.py      # 开发环境专用路由
├── dependencies/       # 依赖注入
│   ├── __init__.py
│   ├── auth.py         # 认证依赖
│   └── database.py     # 数据库依赖
├── exceptions/         # 异常处理
│   ├── __init__.py
│   ├── base.py         # 基础异常类
│   ├── auth.py         # 认证异常
│   ├── business.py     # 业务异常
│   └── handlers.py     # 异常处理器
├── middleware/         # 中间件
│   ├── __init__.py
│   ├── cors.py         # CORS 中间件
│   ├── logging.py      # 日志中间件
│   └── error.py        # 错误处理中间件
├── core/               # 核心配置
│   ├── __init__.py
│   ├── config.py       # 应用配置
│   ├── database.py     # 数据库配置
│   ├── security.py     # 安全配置
│   └── logging.py      # 日志配置
├── utils/              # 工具函数
│   ├── __init__.py
│   └── ...
├── tests/              # 测试
│   └── ...
├── alembic/            # 数据库迁移
│   └── ...
└── main.py             # 应用入口
```

## 🚀 新手开发指南：从表到路由

### 步骤 1：创建数据库模型

在 `app/models/` 目录下创建新的模型文件，例如 `product.py`：

```python
"""Product database model."""

import uuid
from typing import TYPE_CHECKING, List, Optional
from decimal import Decimal

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .user import User


class ProductBase(SQLModel):
    """Shared properties for Product model."""
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    price: Decimal = Field(decimal_places=2)
    is_active: bool = True


class Product(ProductBase, table=True):
    """Product database model."""
    __tablename__ = "product"  # 显式设置表名
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_by_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    created_by: Optional["User"] = Relationship()
```

### 步骤 2：创建 API Schemas

在 `app/schemas/` 目录下创建对应的 schema 文件，例如 `product.py`：

```python
"""Product related schemas for API requests and responses."""

import uuid
from typing import List, Optional
from decimal import Decimal

from sqlmodel import Field, SQLModel


class ProductBase(SQLModel):
    """Shared properties for Product schemas."""
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    price: Decimal = Field(decimal_places=2)
    is_active: bool = True


class ProductCreate(ProductBase):
    """Properties to receive on product creation."""
    pass


class ProductUpdate(SQLModel):
    """Properties to receive on product update."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    price: Optional[Decimal] = Field(default=None, decimal_places=2)
    is_active: Optional[bool] = None


class ProductPublic(ProductBase):
    """Properties to return via API."""
    id: uuid.UUID
    created_by_id: uuid.UUID


class ProductsPublic(SQLModel):
    """Schema for multiple products response."""
    data: List[ProductPublic]
    count: int
```

### 步骤 3：创建服务层

在 `app/services/` 目录下创建业务逻辑服务，例如 `product_service.py`：

```python
"""Product service for business logic operations."""

import uuid
from typing import List

from sqlmodel import Session, func, select

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from .base import BaseService


class ProductService(BaseService[Product, ProductCreate, ProductUpdate]):
    """Product service with business logic."""

    def __init__(self):
        super().__init__(Product)

    def create_with_creator(
        self, session: Session, *, obj_in: ProductCreate, creator_id: uuid.UUID
    ) -> Product:
        """Create a new product with creator."""
        db_obj = Product.model_validate(obj_in, update={"created_by_id": creator_id})
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def get_active_products(
        self, session: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Product]:
        """Get active products with pagination."""
        statement = (
            select(Product)
            .where(Product.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return list(session.exec(statement).all())

    def get_active_count(self, session: Session) -> int:
        """Get count of active products."""
        statement = select(func.count()).select_from(Product).where(Product.is_active == True)
        return session.exec(statement).one()


# Create a singleton instance
product_service = ProductService()
```

### 步骤 4：创建路由

在 `app/routes/` 目录下创建路由文件，例如 `products.py`：

```python
"""Product routes."""

import uuid
from typing import Any

from fastapi import APIRouter

from app.dependencies.auth import CurrentUser
from app.dependencies.database import SessionDep
from app.exceptions.auth import AuthorizationError
from app.exceptions.business import ResourceNotFoundError
from app.schemas.common import Message
from app.schemas.product import ProductCreate, ProductPublic, ProductsPublic, ProductUpdate
from app.services.product_service import product_service

router = APIRouter()


@router.get("/", response_model=ProductsPublic)
async def read_products(
    session: SessionDep, skip: int = 0, limit: int = 100
) -> Any:
    """Retrieve active products."""
    count = product_service.get_active_count(session=session)
    products = product_service.get_active_products(session=session, skip=skip, limit=limit)
    return ProductsPublic(data=products, count=count)


@router.get("/{id}", response_model=ProductPublic)
async def read_product(session: SessionDep, id: uuid.UUID) -> Any:
    """Get product by ID."""
    product = product_service.get(session=session, id=id)
    if not product:
        raise ResourceNotFoundError(message="Product not found")
    return product


@router.post("/", response_model=ProductPublic)
async def create_product(
    *, session: SessionDep, current_user: CurrentUser, product_in: ProductCreate
) -> Any:
    """Create new product."""
    product = product_service.create_with_creator(
        session=session, obj_in=product_in, creator_id=current_user.id
    )
    return product


@router.put("/{id}", response_model=ProductPublic)
async def update_product(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    product_in: ProductUpdate,
) -> Any:
    """Update a product."""
    product = product_service.get(session=session, id=id)
    if not product:
        raise ResourceNotFoundError(message="Product not found")

    # Check if user can update this product (example: only creator or admin)
    if product.created_by_id != current_user.id and not current_user.is_superuser:
        raise AuthorizationError(message="Not enough permissions")

    product = product_service.update(session=session, db_obj=product, obj_in=product_in)
    return product


@router.delete("/{id}", response_model=Message)
async def delete_product(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """Delete a product."""
    product = product_service.get(session=session, id=id)
    if not product:
        raise ResourceNotFoundError(message="Product not found")

    # Check permissions
    if product.created_by_id != current_user.id and not current_user.is_superuser:
        raise AuthorizationError(message="Not enough permissions")

    product_service.delete(session=session, id=id)
    return Message(message="Product deleted successfully")
```

### 步骤 5：注册路由

在 `app/routes/api.py` 中添加新的路由：

```python
# 添加导入
from . import products

# 在 api_router 中包含新路由
api_router.include_router(products.router, prefix="/products", tags=["products"])
```

### 步骤 6：更新模型导入

在 `app/models/__init__.py` 中添加新模型：

```python
from .product import Product

__all__ = ["User", "Item", "Product"]
```

在 `app/schemas/__init__.py` 中添加新 schemas：

```python
from .product import ProductCreate, ProductPublic, ProductsPublic, ProductUpdate

__all__ = [
    # ... 现有的
    # Product schemas
    "ProductCreate",
    "ProductUpdate",
    "ProductPublic",
    "ProductsPublic",
]
```

### 步骤 7：数据库迁移

如果使用 Alembic 迁移：

```bash
# 生成迁移文件
alembic revision --autogenerate -m "Add product table"

# 应用迁移
alembic upgrade head
```

如果使用自动创建表（开发环境）：
- 重启应用，表会自动创建

## 🧪 测试新功能

创建测试文件 `app/tests/api/test_products.py`：

```python
"""Test product endpoints."""

import uuid
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.product import Product


def test_create_product(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test creating a product."""
    data = {
        "name": "Test Product",
        "description": "A test product",
        "price": "99.99"
    }
    response = client.post(
        "/api/v1/products/", headers=superuser_token_headers, json=data
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name"] == data["name"]
    assert "id" in content


def test_read_products(client: TestClient) -> None:
    """Test reading products."""
    response = client.get("/api/v1/products/")
    assert response.status_code == 200
    content = response.json()
    assert "data" in content
    assert "count" in content
```

## 📝 开发最佳实践

### 1. 命名规范
- **文件名**: 使用小写和下划线，如 `product_service.py`
- **类名**: 使用 PascalCase，如 `ProductService`
- **函数名**: 使用小写和下划线，如 `get_active_products`
- **变量名**: 使用小写和下划线，如 `product_count`

### 2. 代码组织
- **单一职责**: 每个文件/类/函数只负责一个功能
- **依赖注入**: 使用 FastAPI 的依赖注入系统
- **错误处理**: 使用自定义异常类，不要直接抛出 HTTPException
- **类型注解**: 为所有函数添加完整的类型注解

### 3. 数据库操作
- **使用服务层**: 不要在路由中直接操作数据库
- **事务管理**: 在服务层处理事务
- **查询优化**: 使用适当的索引和查询优化

### 4. API 设计
- **RESTful**: 遵循 REST 设计原则
- **版本控制**: 使用 URL 前缀进行版本控制
- **文档**: 为所有端点添加详细的文档字符串
- **验证**: 使用 Pydantic 模型进行输入验证

### 5. 安全考虑
- **认证**: 为需要的端点添加认证
- **授权**: 检查用户权限
- **输入验证**: 验证所有用户输入
- **SQL 注入**: 使用 ORM 防止 SQL 注入

## 🔧 常用命令

```bash
# 启动开发服务器
fastapi run app/main.py --reload

# 运行测试
pytest

# 代码格式化
ruff format .

# 代码检查
ruff check .

# 类型检查
mypy .

# 生成数据库迁移
alembic revision --autogenerate -m "描述"

# 应用迁移
alembic upgrade head

# 初始化数据
python app/initial_data.py
```

## 🐛 常见问题

### 1. 导入错误
- 确保所有新模型都在 `__init__.py` 中导入
- 检查循环导入问题

### 2. 数据库表不存在
- 运行数据库迁移
- 或者启用自动创建表（仅开发环境）

### 3. 认证问题
- 检查依赖注入是否正确
- 确保用户已登录并有相应权限

### 4. 类型错误
- 使用正确的类型注解
- 检查 Optional 和 Union 类型的使用

这个指南应该能帮助新手快速理解项目结构并开始开发新功能。记住要遵循现有的代码风格和最佳实践！
```
