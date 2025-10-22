# 通用开发规范（前后端共同遵守）

## 1. Git 规范

### 提交信息格式
```
类型: 简短描述

详细描述（可选）

类型：
- feat: 新功能
- fix: Bug修复
- docs: 文档更新
- style: 代码格式调整
- refactor: 代码重构
- test: 测试相关
- chore: 构建/工具链更新
```

### 分支管理
- **主分支**: `master`
- **功能分支**: `feature/功能名称`
- **修复分支**: `fix/问题描述`

---

## 2. 安全规范

### 密码安全
- **使用 bcrypt 加密**
- **加盐哈希**
- **强密码要求**（最小长度、复杂度）

### API 安全
- **JWT 认证**: 所有需要认证的接口使用 Bearer Token
- **Token 过期**: 7天（可配置）
- **CORS 配置**: 生产环境指定具体域名

### 数据安全
- **用户数据隔离**: 使用 user_id 过滤
- **SQL 注入防护**: 使用 ORM
- **敏感数据加密**: 数据库密码等使用 Fernet 加密

### 日志安全
- **不记录密码**: 日志中不包含敏感信息
- **脱敏处理**: 记录部分信息（如邮箱的前后部分）

---

## 3. 性能优化

### 后端优化
- **异步 IO**: FastAPI 的异步特性
- **连接池**: SQLAlchemy 的连接池配置
- **索引优化**: 关键字段添加数据库索引
- **分页查询**: 使用 skip 和 limit

### 前端优化
- **代码分割**: Vite 自动处理
- **懒加载**: 路由级别的代码分割
- **请求缓存**: 合理使用缓存
- **防抖节流**: 搜索、输入等使用防抖

---

## 4. 文档规范
- **中文优先**: 所有文档、注释、错误消息使用中文
- **不主动生成文档**: 除非用户明确要求
- **前后端文档分离**: 各自维护独立的文档目录
- **按需更新**: 只在功能变更时更新文档
- **保持同步**: 代码和文档同步更新

---

## 5. 环境变量管理

### 配置原则
- **配置文件**: `.env`
- **示例文件**: `.env.example`
- **敏感信息**: 永远不要提交到 Git
- **本地优先**: 本地开发使用 `.env.local` 覆盖

### 后端环境变量示例
```bash
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# JWT 认证
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# AI 提供商
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
OLLAMA_BASE_URL=http://localhost:11434

# Elasticsearch
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_API_KEY=your-api-key
ELASTICSEARCH_INDEX_PREFIX=kb_

# 嵌入模型
DEFAULT_EMBEDDING_MODEL=openai
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 前端环境变量示例
```bash
# API 地址
VITE_API_BASE_URL=http://localhost:8000

# 应用配置
VITE_APP_TITLE=AI聊天系统
VITE_APP_VERSION=1.0.0
```

---

## 6. 功能模块组织规范

### 独立功能模块原则
每个独立功能应该在前后端都有对应的文件夹，方便未来删除和迁移。

**组织方式**：
- 前端：`frontend/src/features/功能名/` 或 `frontend/src/playground/功能名/`
- 后端：`backend/app/功能名/` 或 `backend/app/playground/功能名/`

### Playground 文件夹规范
- **用途**: 存放演示、测试、实验性功能
- **特点**: 可以随时删除，不影响核心功能
- **命名规范**: 
  - 后端：小写+下划线（snake_case），如 `product_rag`
  - 前端：小驼峰（camelCase），如 `productRag`
- **结构**: 前后端对应，功能名称一致

**示例**：
```
# 产品 RAG 功能示例
backend/app/playground/product_rag/     # 后端实现（snake_case）
frontend/src/playground/productRag/     # 前端实现（camelCase）
```

**独立功能模块包含**：
- 后端：models、schemas、routers、services
- 前端：components、hooks、services、types

**删除规则**：
1. 确认功能不再需要
2. 同时删除前后端对应文件夹
3. 移除相关路由注册
4. 清理数据库迁移（如有）

---

## 7. 常见问题

**Q: 何时使用 Service 层？**
A: 当业务逻辑复杂、需要复用或涉及多个模型操作时。

**Q: 如何处理循环导入？**
A: 使用 `TYPE_CHECKING` 和字符串类型注解，或重新组织模块结构。

**Q: 什么时候使用 Context vs Zustand？**
A: 简单的主题、语言等用 Context；复杂状态管理用 Zustand。

