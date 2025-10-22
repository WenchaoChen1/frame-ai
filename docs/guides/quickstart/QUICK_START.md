# RAG 智能体快速启动指南

## 问题解决

如果遇到 `ImportError: cannot import name 'VECTOR'` 错误，说明需要安装 pgvector 包。

## 安装步骤

### 1. 安装 Python 依赖

```bash
cd backend

# 激活虚拟环境
.\venv\Scripts\activate

# 安装所有依赖（包括 pgvector）
pip install -r requirements.txt
```

或者单独安装 pgvector：

```bash
pip install pgvector
```

### 2. 数据库准备

#### 选项 A：使用 PostgreSQL + pgvector（推荐）

1. **启动 PostgreSQL 数据库**（如果还没有）

2. **启用 pgvector 扩展**：
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

3. **运行迁移脚本**：
   ```bash
   python migrations/run_migration_005.py
   ```

#### 选项 B：仅使用 Elasticsearch

如果只想使用 Elasticsearch 作为向量存储，pgvector 包仍然需要安装（用于类型定义），但不需要 PostgreSQL 的 vector 扩展。

### 3. 配置环境变量

在 `backend/.env` 文件中添加：

```env
# 基础配置
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/chatai
OPENAI_API_KEY=your_api_key_here

# 向量存储配置
ELASTICSEARCH_URL=http://localhost:9200
PGVECTOR_ENABLED=true

# 嵌入模型配置
DEFAULT_EMBEDDING_MODEL=openai
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

### 4. 启动服务

```bash
# 在 backend 目录下
python -m app.main
```

或使用 uvicorn：

```bash
uvicorn app.main:app --reload
```

## 验证安装

访问 http://localhost:8000/docs 查看 API 文档，应该能看到新增的知识库相关接口：

- `/api/knowledge-bases` - 知识库管理
- `/api/robots/{id}/knowledge-bases` - 机器人关联知识库

## 快速测试

### 1. 创建知识库

```bash
curl -X POST "http://localhost:8000/api/knowledge-bases" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试知识库",
    "description": "用于测试的知识库",
    "vector_store_type": "pgvector",
    "embedding_model": "openai-small"
  }'
```

### 2. 上传文档

```bash
curl -X POST "http://localhost:8000/api/knowledge-bases/1/documents" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test.txt"
```

### 3. 关联到机器人

```bash
curl -X POST "http://localhost:8000/api/robots/1/knowledge-bases" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "knowledge_base_ids": [1]
  }'
```

### 4. 开始 RAG 对话

机器人现在会自动使用关联的知识库来回答问题！

## 故障排除

### 问题 1：pgvector 导入错误

**错误信息**：`ImportError: cannot import name 'VECTOR'`

**解决方案**：
```bash
pip install pgvector
```

### 问题 2：PostgreSQL vector 扩展未安装

**错误信息**：SQL 执行失败，提示 vector 类型不存在

**解决方案**：
1. 连接到数据库：`psql -U postgres -d chatai`
2. 运行：`CREATE EXTENSION vector;`

### 问题 3：依赖包版本冲突

**解决方案**：
```bash
# 重新创建虚拟环境
rm -rf venv
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 问题 4：Elasticsearch 连接失败

如果不使用 Elasticsearch，可以：
1. 在创建知识库时选择 `vector_store_type: "pgvector"`
2. 或启动 Elasticsearch：
   ```bash
   docker run -d --name elasticsearch \
     -e "discovery.type=single-node" \
     -e "xpack.security.enabled=false" \
     -p 9200:9200 elasticsearch:8.11.0
   ```

## 最小化配置（仅使用 pgvector）

如果只想最快速度体验，最小配置如下：

1. **安装依赖**：
   ```bash
   pip install pgvector
   ```

2. **确保 PostgreSQL 有 vector 扩展**

3. **运行迁移**：
   ```bash
   python migrations/run_migration_005.py
   ```

4. **启动应用**：
   ```bash
   python -m app.main
   ```

5. **创建知识库时选择 pgvector**

就这样！现在你可以上传文档并开始使用 RAG 功能了。

## 更多信息

查看详细文档：
- `backend/RAG_FEATURE_GUIDE.md` - 完整功能指南
- `RAG_IMPLEMENTATION_SUMMARY.md` - 实现总结

