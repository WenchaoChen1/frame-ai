# 机器人功能数据库迁移说明

## 概述

本次更新添加了机器人管理功能，需要对数据库进行迁移。

## 数据库变更

### 1. 新增 `robots` 表

```sql
CREATE TABLE robots (
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT,
    avatar VARCHAR,
    default_provider VARCHAR NOT NULL,
    default_model VARCHAR NOT NULL,
    system_prompt TEXT,
    temperature FLOAT DEFAULT 0.7,
    max_tokens INTEGER,
    is_global BOOLEAN NOT NULL DEFAULT 0,
    user_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### 2. 更新 `conversations` 表

添加 `robot_id` 字段：

```sql
ALTER TABLE conversations ADD COLUMN robot_id INTEGER;
ALTER TABLE conversations ADD FOREIGN KEY (robot_id) REFERENCES robots(id);
```

## 迁移方式

### 方式一：使用 Alembic（推荐）

如果您使用 Alembic 进行数据库迁移：

```bash
# 1. 进入 backend 目录
cd backend

# 2. 生成迁移脚本
python -m alembic revision --autogenerate -m "add_robots_table_and_update_conversations"

# 3. 检查生成的迁移脚本（在 alembic/versions/ 目录下）

# 4. 执行迁移
python -m alembic upgrade head
```

### 方式二：自动创建（开发环境）

应用启动时会自动创建/更新表结构（通过 SQLAlchemy 的 `create_all`）：

```bash
# 启动应用即可
python -m uvicorn app.main:app --reload
```

### 方式三：手动执行 SQL

如果您希望手动执行 SQL：

```sql
-- 创建 robots 表
CREATE TABLE IF NOT EXISTS robots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    avatar VARCHAR(100),
    default_provider VARCHAR(50) NOT NULL,
    default_model VARCHAR(100) NOT NULL,
    system_prompt TEXT,
    temperature FLOAT DEFAULT 0.7,
    max_tokens INTEGER,
    is_global BOOLEAN NOT NULL DEFAULT 0,
    user_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 更新 conversations 表
ALTER TABLE conversations ADD COLUMN robot_id INTEGER;

-- 注意：SQLite 不支持直接添加外键约束到已存在的表
-- 如果需要外键约束，需要重建表
```

## 初始数据（可选）

您可以创建一些默认的全局机器人：

```sql
-- 示例：创建一个 GPT-4 助手（假设 admin 用户的 id 为 1）
INSERT INTO robots (name, description, avatar, default_provider, default_model, is_global, user_id)
VALUES ('GPT-4 助手', '强大的通用AI助手，适合各种任务', '🤖', 'openai', 'gpt-4', 1, 1);

-- 示例：创建一个 Python 编程助手
INSERT INTO robots (name, description, avatar, default_provider, default_model, system_prompt, is_global, user_id)
VALUES (
    'Python 编程助手',
    '专业的 Python 编程顾问，帮助解决编程问题',
    '🐍',
    'openai',
    'gpt-4',
    '你是一个专业的 Python 编程专家。你精通 Python 语言的各个方面，包括语法、标准库、第三方库、最佳实践等。你会用清晰、简洁的方式回答问题，并提供可运行的代码示例。',
    1,
    1
);
```

## 验证迁移

迁移完成后，您可以通过以下方式验证：

1. 启动后端服务
2. 访问 API 文档：http://localhost:8000/docs
3. 测试机器人相关的 API 端点：
   - GET /api/robots - 获取机器人列表
   - POST /api/robots - 创建机器人
   - GET /api/robots/{robot_id} - 获取机器人详情

## 注意事项

1. **备份数据**：迁移前请备份您的数据库
2. **外键约束**：SQLite 对外键的支持有限，如果需要完整的外键约束，建议使用 PostgreSQL 或 MySQL
3. **现有对话**：现有的对话不会自动关联机器人，`robot_id` 将为 NULL
4. **权限**：只有管理员可以创建全局机器人

## 回滚

如果需要回滚此次迁移：

```bash
# 使用 Alembic 回滚
python -m alembic downgrade -1

# 或手动删除
DROP TABLE robots;
ALTER TABLE conversations DROP COLUMN robot_id;
```

## 相关文件

- 模型定义：`backend/app/models/robot.py`
- Schema 定义：`backend/app/schemas/robot.py`
- 路由定义：`backend/app/routers/robots.py`
- 前端页面：`frontend/src/pages/RobotManagement.tsx`

