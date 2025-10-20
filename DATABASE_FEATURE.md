# 机器人数据库关联功能

## 功能概述

为机器人添加了数据库关联功能，支持配置和管理 PostgreSQL、MySQL、Redshift 数据库连接。机器人可以使用这些数据库连接来查询和分析数据。

## 支持的数据库类型

- **PostgreSQL** - 默认端口 5432
- **MySQL** - 默认端口 3306  
- **Redshift** - 默认端口 5439

## 功能特性

### 1. 数据库配置管理
- 为每个机器人配置一个数据库连接
- 安全的密码加密存储
- 支持创建、更新、删除数据库配置

### 2. 连接测试
- 在保存配置前测试数据库连接
- 实时显示连接状态（成功/失败）
- 提供详细的错误信息

### 3. 数据库结构查看
- 查看数据库中的所有表
- 查看每个表的字段信息（名称、类型、是否可为空）
- 树形结构展示，最多显示 100 个表

## 使用方法

### 前端操作

1. **进入机器人管理页面**
   - 点击侧边栏的"机器人管理"

2. **创建或编辑机器人**
   - 点击"新建机器人"或编辑现有机器人
   - 在弹出的表单中填写基本信息

3. **配置数据库连接**
   - 展开"数据库配置（可选）"折叠面板
   - 选择数据库类型（PostgreSQL/MySQL/Redshift）
   - 填写连接信息：
     - 主机地址（如 localhost）
     - 端口（自动填充默认端口）
     - 数据库名称
     - 用户名
     - 密码

4. **测试连接**
   - 点击"测试连接"按钮
   - 等待测试结果
   - 成功后会显示绿色的"连接成功"标签

5. **查看数据库结构**
   - 保存机器人配置后
   - 重新编辑该机器人
   - 点击"查看结构"按钮
   - 在右侧抽屉中查看数据库表结构

### API 端点

#### 创建/更新数据库配置
```http
POST /api/robots/{robot_id}/database
Content-Type: application/json

{
  "db_type": "postgresql",
  "host": "localhost",
  "port": 5432,
  "database_name": "mydb",
  "username": "user",
  "password": "password"
}
```

#### 获取数据库配置
```http
GET /api/robots/{robot_id}/database
```

#### 删除数据库配置
```http
DELETE /api/robots/{robot_id}/database
```

#### 测试数据库连接
```http
POST /api/robots/{robot_id}/database/test
Content-Type: application/json

{
  "db_type": "postgresql",
  "host": "localhost",
  "port": 5432,
  "database_name": "mydb",
  "username": "user",
  "password": "password"
}
```

#### 获取数据库结构
```http
GET /api/robots/{robot_id}/database/schema
```

## 安全性

### 密码加密
- 数据库密码使用 Fernet 对称加密
- 加密密钥从环境变量 `DB_ENCRYPTION_KEY` 读取
- 密码不会在 API 响应中返回

### 权限控制
- 只有机器人创建者和管理员可以配置数据库
- 数据库配置操作需要身份验证

### 连接安全
- 使用参数化查询防止 SQL 注入
- 连接超时设置为 10 秒
- 查询完成后立即关闭连接

## 技术实现

### 后端
- **模型**: `DatabaseConfig` (backend/app/models/database_config.py)
- **Schema**: `DatabaseConfigCreate`, `DatabaseConfigResponse` 等
- **服务**: `DatabaseService` (backend/app/services/database_service.py)
- **路由**: `/api/robots/{robot_id}/database/*`

### 前端
- **组件**: `RobotManagement.tsx`
- **服务**: `robotService` (frontend/src/services/robot.ts)
- **UI**: Collapse 折叠面板、Drawer 抽屉、Tree 树形结构

### 数据库
- **表**: `database_configs`
- **迁移**: `002_add_database_config_table.sql`

## 依赖包

### Python (已添加到 requirements.txt)
- `psycopg2-binary==2.9.9` - PostgreSQL 驱动
- `pymysql==1.1.0` - MySQL 驱动
- `cryptography==41.0.7` - 密码加密
- `sqlalchemy-redshift==0.8.14` - Redshift 支持

## 常见问题

### Q: 密码保存后可以查看吗？
A: 不可以。密码保存后会加密存储，前端不会返回密码字段。编辑时需要重新输入密码或留空保持原密码。

### Q: 可以关联多个数据库吗？
A: 当前版本每个机器人只能关联一个数据库。

### Q: 支持 SSL 连接吗？
A: 当前版本使用基本连接，高级 SSL 配置功能可在后续版本中添加。

### Q: 为什么查看结构最多只显示 100 个表？
A: 为了性能考虑，限制了最多显示 100 个表。大多数应用场景下这个数量是足够的。

## 未来改进

- [ ] 支持多数据库关联
- [ ] 支持 SSL/TLS 连接配置
- [ ] 添加数据库连接池配置
- [ ] 支持更多数据库类型（如 MongoDB、Oracle）
- [ ] 提供数据查询测试功能
- [ ] 添加数据库使用统计

