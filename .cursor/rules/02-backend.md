# 后端开发规范 (Python/FastAPI)

## 1. 代码风格规范

### 命名规范
- **模块/文件**: 全小写+下划线，如 `user_service.py`
- **类名**: 大驼峰（PascalCase），如 `UserService`
- **函数/方法**: 小写+下划线，如 `get_user_by_id`
- **常量**: 全大写+下划线，如 `MAX_LOGIN_ATTEMPTS`
- **私有变量**: 单下划线前缀，如 `_private_var`

### 导入顺序
```python
# 1. 标准库
import json
from datetime import datetime
from typing import List, Optional

# 2. 第三方库
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

# 3. 本地模块（推荐使用绝对导入）
from app.models.user import User
from app.core.database import get_db
from app.schemas.user import UserResponse
from app.dependencies import get_current_user
```

### 类型注解
**必须使用类型注解**：所有函数参数和返回值都要有类型提示
```python
def get_users(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()
```

### 日志使用
- **使用项目日志系统**：从 `core.logger` 导入
- **日志级别**：info（正常）、warning（警告）、error（错误）、debug（调试）
- **日志格式**：使用表情符号提高可读性
```python
from app.core.logger import get_logger

logger = get_logger(__name__)

logger.info(f"✅ 用户登录成功 - 用户名: {user.username}")
logger.warning(f"⚠️ 登录失败 - 用户不存在: {username}")
logger.error(f"❌ 数据库错误: {str(e)}")
logger.debug(f"🔍 调试信息 - 查询参数: {params}")
```

### 错误处理
使用 HTTPException 抛出规范的 HTTP 错误
```python
from fastapi import HTTPException, status

if not user:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="用户不存在"
    )
```

### API 响应格式

**成功响应**：
```python
# 直接返回 Pydantic 模型
return UserResponse(
    id=user.id,
    username=user.username,
    email=user.email
)

# 或返回列表
return [UserResponse.from_orm(u) for u in users]
```

**错误响应**：
```python
# 400 错误请求
raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="无效的请求参数"
)

# 404 资源不存在
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="用户不存在"
)

# 403 权限不足
raise HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="权限不足"
)

# 500 服务器错误
raise HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="服务器内部错误"
)
```

**一致性原则**：
- 所有错误消息使用中文
- 统一使用 FastAPI 的 HTTPException
- 状态码遵循 RESTful 规范

---

## 2. 项目目录结构

```
backend/
├── app/
│   ├── main.py                 # 应用入口
│   ├── application.py          # 应用启动类
│   ├── dependencies.py         # 依赖注入
│   ├── core/                   # 核心配置
│   │   ├── config.py           # 配置管理
│   │   ├── database.py         # 数据库连接
│   │   ├── logger.py           # 日志配置
│   │   └── security.py         # JWT和密码加密
│   ├── models/                 # SQLAlchemy模型
│   ├── schemas/                # Pydantic模式
│   ├── routers/                # API路由
│   ├── services/               # 业务逻辑服务
│   ├── ai/                     # AI模块
│   │   ├── agent/              # 智能体
│   │   ├── models/             # AI模型服务
│   │   ├── embeddings/         # 嵌入模型
│   │   └── vector_stores/      # 向量存储
│   └── playground/             # 实验功能模块（可删除）
│       └── product_rag/        # 产品RAG示例
├── tests/                      # 测试目录
│   ├── test_models/            # 模型测试
│   ├── test_routers/           # 路由测试
│   ├── test_services/          # 服务测试
│   └── test_ai/                # AI 功能测试
├── docs/                       # 后端文档
│   ├── README.md               # 后端主文档
│   ├── API.md                  # API 文档
│   ├── DEPLOYMENT.md           # 部署文档
│   └── DATABASE.md             # 数据库设计
├── migrations/                 # 数据库迁移
├── requirements.txt            # 生产依赖
└── requirements-dev.txt        # 开发依赖
```

---

## 3. 开发规范

### 模块化设计
- 每个功能独立成模块
- models、schemas、routers 文件名保持一致
- 避免循环依赖

### 数据库命名
- **表名**: 全小写+下划线，如 `users`, `login_audits`
- **列名**: 全小写+下划线，如 `user_id`, `created_at`
- **外键**: 使用 `{table}_id` 格式

### 模块导入规范

**推荐：使用绝对导入 ✅**
```python
# 绝对导入 - 清晰、易维护、IDE 支持好
from app.models.user import User
from app.schemas.user import UserResponse
from app.core.database import get_db
from app.dependencies import get_current_user
```

**不推荐：多层相对导入 ⚠️**
```python
# 避免使用三个或更多点的相对导入（难以理解）
from ...core.database import Base  # ❌ 不推荐
from ...models.user import User    # ❌ 不推荐
```

**可接受：简单相对导入**
```python
# 简单的相对导入（仅限同级或上一级）也可以接受
from .schemas import UserResponse  # ✅ 同级目录
from ..core.database import get_db  # ✅ 上一级目录
```

**导入规则总结**：
- ✅ **优先使用绝对导入** - 更清晰、更易维护
- ✅ **同级目录**可使用单点 `.`
- ⚠️ **上一级目录**使用 `..` 需谨慎
- ❌ **避免** `...` 或更多点的相对导入
- ✅ **新增模块（如 playground）** 必须使用绝对导入

---

## 4. 测试规范

### 测试框架
- pytest + pytest-asyncio
- 文件命名: `test_*.py` 或 `*_test.py`
- 覆盖范围: API端点、数据库操作、业务逻辑、AI 功能

### 测试示例
```python
# tests/test_routers/test_auth.py
import pytest
from fastapi.testclient import TestClient

def test_register_success(client: TestClient):
    """测试成功注册"""
    response = client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

### 测试覆盖率要求
- **API 端点**: 覆盖率 > 80%
- **业务逻辑**: 覆盖率 > 85%
- **工具函数**: 覆盖率 > 90%
- **关键功能**: 必须达到 100% 覆盖

---

## 5. 新增功能指南

### 添加新数据模型
1. 在 `models/` 创建模型文件
2. 在 `schemas/` 创建对应 Schema
3. 在 `routers/` 创建路由
4. 在 `application.py` 注册路由
5. 创建迁移脚本更新数据库

### 添加新实验功能（Playground）
1. 在 `app/playground/` 下创建功能文件夹（如 `product_rag/`）
2. 创建必要文件：
   - `__init__.py`: 模块初始化
   - `models.py`: 数据模型
   - `schemas.py`: 验证模式
   - `router.py`: API 路由
   - `service.py`: 业务逻辑
   - `README.md`: 功能说明
3. **重要**: Playground 模块必须使用绝对导入（`from app.xxx`）
4. 在 `application.py` 中注册路由
5. 创建数据库迁移（如需要）
6. 前端在 `src/playground/` 下创建对应文件夹

