# 数据库迁移脚本

## 使用方法

### 方式一：使用 psql 命令行（推荐）

```bash
# 确保你在 backend 目录下
cd backend

# 执行迁移（替换为你的数据库连接信息）
psql -h localhost -U your_username -d your_database -f migrations/001_add_robots_table.sql

# 如果需要回滚
psql -h localhost -U your_username -d your_database -f migrations/rollback_001.sql
```

### 方式二：使用 Python 脚本

```bash
cd backend
python migrations/run_migration.py
```

### 方式三：在 PostgreSQL 客户端中执行

1. 打开你的 PostgreSQL 客户端（如 pgAdmin, DBeaver 等）
2. 连接到数据库
3. 打开 `migrations/001_add_robots_table.sql` 文件
4. 执行整个脚本

## 迁移内容

### 001_add_robots_table.sql

- 创建 `robots` 表
- 为 `conversations` 表添加 `robot_id` 字段
- 创建必要的索引和外键约束

## 注意事项

1. **备份数据库**：在执行迁移前，请务必备份数据库
2. **检查权限**：确保数据库用户有创建表和修改表结构的权限
3. **验证结果**：迁移后检查表结构是否正确
4. **现有数据**：现有的对话数据不会受影响，`robot_id` 将为 NULL

## 验证迁移是否成功

执行以下 SQL 查询：

```sql
-- 检查 robots 表
SELECT * FROM information_schema.tables WHERE table_name = 'robots';

-- 检查 robot_id 列
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'conversations' AND column_name = 'robot_id';

-- 查看 robots 表结构
\d robots

-- 查看 conversations 表结构
\d conversations
```

