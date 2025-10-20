# 后端目录结构规范

## 项目概述

本项目采用 **FastAPI + SQLAlchemy + PostgreSQL** 架构，是一个AI驱动的智能对话系统后端服务。

### 技术栈
- **Web框架**: FastAPI 0.104+
- **ORM**: SQLAlchemy 2.0+
- **数据库**: PostgreSQL
- **AI框架**: LangChain + LangGraph
- **认证**: JWT (PyJWT)
- **日志**: Python logging
- **迁移**: Alembic

---

## 目录结构树

```
backend/
├── app/                          # 应用主目录
│   ├── __init__.py              # 包初始化
│   ├── main.py                  # 应用入口点
│   ├── application.py           # 应用启动类（负责初始化）
│   ├── dependencies.py          # FastAPI依赖注入
│   │
│   ├── ai/                      # AI模块（智能体、模型服务）
│   │   ├── __init__.py
│   │   ├── agent/               # 智能体实现
│   │   │   ├── __init__.py
│   │   │   └── text_to_sql_agent.py     # Text-to-SQL智能体
│   │   ├── models/              # AI模型服务
│   │   │   ├── __init__.py
│   │   │   ├── ai_provider.py           # AI提供商基类
│   │   │   ├── ai_manager.py            # AI服务管理器
│   │   │   ├── openai_service.py        # OpenAI服务
│   │   │   ├── claude_service.py        # Claude服务
│   │   │   └── ollama_service.py        # Ollama服务
│   │   └── node/                # 智能体节点定义
│   │       ├── __init__.py
│   │       └── text_to_sql_agent_node.py
│   │
│   ├── core/                    # 核心配置模块
│   │   ├── __init__.py
│   │   ├── config.py            # 配置管理（环境变量、设置）
│   │   ├── database.py          # 数据库连接配置
│   │   ├── logger.py            # 日志配置
│   │   └── security.py          # 安全相关（密码哈希、JWT）
│   │
│   ├── models/                  # 数据库模型（SQLAlchemy ORM）
│   │   ├── __init__.py
│   │   ├── user.py              # 用户模型
│   │   ├── conversation.py      # 会话模型
│   │   ├── message.py           # 消息模型
│   │   ├── robot.py             # 机器人模型
│   │   ├── database_config.py   # 数据库配置模型
│   │   ├── login_audit.py       # 登录审计模型
│   │   └── sql_query_log.py     # SQL查询日志模型
│   │
│   ├── schemas/                 # Pydantic模型（请求/响应验证）
│   │   ├── __init__.py
│   │   ├── user.py              # 用户相关Schema
│   │   ├── conversation.py      # 会话相关Schema
│   │   ├── message.py           # 消息相关Schema
│   │   ├── robot.py             # 机器人相关Schema
│   │   ├── database_config.py   # 数据库配置Schema
│   │   ├── login_audit.py       # 登录审计Schema
│   │   └── sql_query.py         # SQL查询Schema
│   │
│   ├── routers/                 # API路由（端点定义）
│   │   ├── __init__.py
│   │   ├── auth.py              # 认证相关路由
│   │   ├── users.py             # 用户管理路由
│   │   ├── conversations.py     # 会话管理路由
│   │   ├── messages.py          # 消息处理路由
│   │   ├── robots.py            # 机器人管理路由
│   │   ├── providers.py         # AI提供商路由
│   │   ├── database_config.py   # 数据库配置路由
│   │   └── login_audit.py       # 登录审计路由
│   │
│   ├── services/                # 业务逻辑服务层
│   │   ├── __init__.py
│   │   └── database_service.py  # 数据库操作服务
│   │
│   ├── swagger/                 # API文档配置
│   │   ├── __init__.py
│   │   └── config.py            # Swagger UI配置
│   │
│   └── middleware/              # 中间件（预留）
│       └── __init__.py
│
├── migrations/                  # 数据库迁移脚本
│   ├── README.md
│   ├── 001_add_robots_table.sql
│   ├── 002_add_database_config_table.sql
│   ├── 003_add_database_metadata_table.sql
│   ├── 004_add_sql_query_logs.sql
│   ├── rollback_001.sql
│   ├── rollback_002.sql
│   └── ...
│
├── config/                      # 外部配置文件（预留）
│
├── venv/                        # Python虚拟环境
│
├── .env                         # 环境变量配置
├── requirements.txt             # Python依赖
├── alembic.ini                  # Alembic配置
├── Dockerfile                   # Docker配置
└── README.md                    # 项目说明

```

---

## 目录详细说明

### 1. `app/` - 应用主目录
应用的核心代码目录，包含所有业务逻辑。

#### 关键文件
- **`main.py`**: 应用入口点，导出FastAPI应用实例
- **`application.py`**: 应用启动类，负责初始化路由、中间件、数据库
- **`dependencies.py`**: FastAPI依赖注入函数（如获取当前用户）

### 2. `app/ai/` - AI模块
所有AI相关功能的集中管理。

#### 子目录结构
- **`agent/`**: 智能体实现
  - 每个智能体一个文件，命名格式：`xxx_agent.py`
  - 示例：`text_to_sql_agent.py`
  - 包含智能体的完整逻辑和状态管理

- **`models/`**: AI模型服务
  - `ai_provider.py`: 所有AI服务的抽象基类
  - `ai_manager.py`: 统一管理所有AI服务的管理器
  - 各AI提供商服务：`openai_service.py`, `claude_service.py`, `ollama_service.py`

- **`node/`**: 智能体节点定义
  - 每个智能体对应一个节点文件，命名格式：`xxx_agent_node.py`
  - 示例：`text_to_sql_agent_node.py`
  - 封装智能体的节点访问接口

#### 添加新智能体的步骤
1. 在 `agent/` 创建 `new_agent.py`
2. 在 `node/` 创建 `new_agent_node.py`
3. 在 `agent/__init__.py` 导出新智能体
4. 在 `node/__init__.py` 导出新节点

### 3. `app/core/` - 核心配置
系统级配置和基础设施。

- **`config.py`**: 使用Pydantic Settings管理配置
  - 从环境变量读取配置
  - 提供类型安全的配置访问
  
- **`database.py`**: SQLAlchemy数据库配置
  - 数据库引擎
  - Session管理
  - Base模型类

- **`logger.py`**: 统一日志配置
  - 格式化输出
  - 日志级别管理
  
- **`security.py`**: 安全相关功能
  - 密码哈希
  - JWT token生成和验证

### 4. `app/models/` - 数据库模型
SQLAlchemy ORM模型定义。

#### 命名规范
- 文件名：小写+下划线，如 `user.py`, `conversation.py`
- 类名：大驼峰，如 `User`, `Conversation`
- 表名：小写+下划线，通过 `__tablename__` 指定

#### 示例结构
```python
# models/user.py
from sqlalchemy import Column, Integer, String
from ..core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
```

### 5. `app/schemas/` - Pydantic模型
请求和响应的数据验证模型。

#### 命名规范
- 文件名与对应的model文件同名
- 类名后缀：
  - `Create`: 创建请求
  - `Update`: 更新请求
  - `Response`: 响应数据
  - `Base`: 基础共享字段

#### 示例
```python
# schemas/user.py
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    
    class Config:
        from_attributes = True
```

### 6. `app/routers/` - API路由
FastAPI路由端点定义。

#### 命名规范
- 文件名：小写+下划线，与资源名对应
- 路由前缀：`/api/{resource}` 
- 标签：用于Swagger分组

#### 示例结构
```python
# routers/users.py
from fastapi import APIRouter, Depends
from ..schemas.user import UserResponse
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/users", tags=["用户"])

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    # 实现逻辑
    pass
```

### 7. `app/services/` - 业务逻辑服务
复杂业务逻辑的封装层。

#### 使用场景
- 数据库操作的封装
- 第三方服务集成
- 复杂计算逻辑
- 可复用的业务功能

#### 命名规范
- 文件名：`xxx_service.py`
- 类名：`XxxService`

### 8. `migrations/` - 数据库迁移
SQL迁移脚本，用于数据库版本管理。

#### 文件命名
- 正向迁移：`001_description.sql`, `002_description.sql`
- 回滚脚本：`rollback_001.sql`, `rollback_002.sql`
- Python脚本：`run_migration_001.py`

---

## 命名规范

### Python文件
- **模块/包**: 全小写+下划线，如 `user_service.py`
- **类**: 大驼峰（PascalCase），如 `UserService`
- **函数/方法**: 小写+下划线，如 `get_user_by_id`
- **常量**: 全大写+下划线，如 `MAX_LOGIN_ATTEMPTS`
- **私有变量**: 单下划线前缀，如 `_private_var`

### 数据库
- **表名**: 全小写+下划线，如 `users`, `login_audits`
- **列名**: 全小写+下划线，如 `user_id`, `created_at`

---

## 导入路径规范

### 相对导入（推荐）
在 `app/` 内部使用相对导入：

```python
# 在 app/routers/users.py 中
from ..models.user import User
from ..schemas.user import UserResponse
from ..core.database import get_db
from ..dependencies import get_current_user
```

### 绝对导入
从项目根目录导入：

```python
from app.models.user import User
from app.schemas.user import UserResponse
```

### 导入顺序
1. 标准库
2. 第三方库
3. 本地模块

```python
# 标准库
import json
from datetime import datetime
from typing import List, Optional

# 第三方库
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

# 本地模块
from ..models.user import User
from ..core.database import get_db
```

---

## 新增功能指南

### 添加新的数据模型
1. 在 `app/models/` 创建模型文件，如 `product.py`
2. 在 `app/schemas/` 创建对应的Schema，如 `product.py`
3. 在 `app/routers/` 创建路由，如 `products.py`
4. 在 `app/application.py` 注册路由
5. 创建迁移脚本更新数据库

### 添加新的AI服务
1. 在 `app/ai/models/` 创建服务文件，如 `gemini_service.py`
2. 继承 `AIProvider` 基类
3. 在 `ai_manager.py` 中注册新服务
4. 更新 `app/ai/models/__init__.py` 导出

### 添加新的业务服务
1. 在 `app/services/` 创建服务文件，如 `email_service.py`
2. 定义服务类和方法
3. 在需要的地方导入使用

---

## 最佳实践

### 1. 单一职责原则
- 每个模块只负责一个功能领域
- Router只处理HTTP请求/响应
- Service处理业务逻辑
- Model只定义数据结构

### 2. 依赖注入
使用FastAPI的 `Depends` 管理依赖：

```python
@router.get("/users/me")
def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return current_user
```

### 3. 错误处理
使用HTTPException抛出规范的HTTP错误：

```python
from fastapi import HTTPException, status

if not user:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="用户不存在"
    )
```

### 4. 日志记录
使用统一的logger：

```python
from ..core.logger import get_logger

logger = get_logger(__name__)

logger.info("用户登录成功")
logger.error(f"错误: {str(e)}")
```

### 5. 类型提示
始终使用类型提示提高代码可读性：

```python
from typing import List, Optional

def get_users(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()
```

---

## 环境配置

### .env 文件示例
```bash
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# JWT配置
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI服务配置
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
OLLAMA_BASE_URL=http://localhost:11434

# CORS配置
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## 测试规范

### 测试文件组织（未来扩展）
```
tests/
├── test_models/
├── test_routers/
├── test_services/
└── test_ai/
```

### 测试命名
- 文件名：`test_xxx.py`
- 测试函数：`test_功能描述`

---

## 常见问题

**Q: 为什么AI代码单独成一个模块？**  
A: AI功能相对独立，单独模块便于管理、扩展和复用。

**Q: 何时使用Service层？**  
A: 当业务逻辑复杂、需要复用或涉及多个模型操作时。

**Q: Router中可以直接操作数据库吗？**  
A: 简单的CRUD可以，复杂逻辑建议封装到Service。

**Q: 如何处理循环导入？**  
A: 使用 `TYPE_CHECKING` 和字符串类型注解，或重新组织模块结构。

---

## 参考资源

- [FastAPI官方文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy文档](https://docs.sqlalchemy.org/)
- [Pydantic文档](https://docs.pydantic.dev/)
- [项目根目录README.md](../README.md)

