# RAG 智能体功能指南

## 功能概述

本系统实现了完整的 RAG（Retrieval-Augmented Generation）智能体功能，支持：

- ✅ 多向量存储（Elasticsearch、PostgreSQL+pgvector）
- ✅ 多嵌入模型（OpenAI、HuggingFace）
- ✅ 多格式文档（TXT、PDF、DOCX）
- ✅ 高级检索（语义检索、BM25、混合检索）
- ✅ 查询重写和结果重排序
- ✅ 机器人与知识库关联

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

在 `backend/.env` 文件中添加：

```bash
# 向量存储配置
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_API_KEY=
PGVECTOR_ENABLED=true

# 嵌入模型配置
DEFAULT_EMBEDDING_MODEL=openai
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
HUGGINGFACE_EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5

# 文档处理配置
MAX_FILE_SIZE=52428800  # 50MB
CHUNK_SIZE=500
CHUNK_OVERLAP=50

# RAG 配置
TOP_K_RETRIEVAL=10
TOP_K_RERANK=5
ENABLE_QUERY_REWRITE=true
ENABLE_RERANKING=true
```

### 3. 运行数据库迁移

```bash
cd backend
python migrations/run_migration_005.py
```

这将创建以下表：
- `knowledge_bases` - 知识库表
- `knowledge_base_documents` - 文档表
- `knowledge_base_chunks` - 文档块表
- `robot_knowledge_bases` - 机器人与知识库关联表

### 4. 启动 PostgreSQL + pgvector

如果使用 pgvector：

```bash
# 使用 Docker
docker run -d \
  --name pgvector \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  pgvector/pgvector:pg16
```

### 5. 启动 Elasticsearch（可选）

如果使用 Elasticsearch：

```bash
# 使用 Docker
docker run -d \
  --name elasticsearch \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  -p 9200:9200 \
  elasticsearch:8.11.0
```

## API 使用指南

### 知识库管理

#### 创建知识库

```http
POST /api/knowledge-bases
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "技术文档库",
  "description": "存储技术文档和API说明",
  "vector_store_type": "pgvector",  // 或 "elasticsearch"
  "embedding_model": "openai-small",  // 或 "openai-large", "huggingface-bge"
  "chunk_size": 500,
  "chunk_overlap": 50,
  "is_public": false
}
```

#### 上传文档

```http
POST /api/knowledge-bases/{kb_id}/documents
Content-Type: multipart/form-data
Authorization: Bearer <token>

file: <文件>
```

支持的文件格式：
- `.txt` - 纯文本文件
- `.pdf` - PDF文档
- `.docx` - Word文档

#### 批量导入文档

```http
POST /api/knowledge-bases/{kb_id}/batch-import
Content-Type: application/json
Authorization: Bearer <token>

{
  "directory_path": "/path/to/documents",
  "file_extensions": [".txt", ".pdf", ".docx"]
}
```

#### 搜索知识库

```http
POST /api/knowledge-bases/search
Content-Type: application/json
Authorization: Bearer <token>

{
  "query": "如何使用 RAG？",
  "top_k": 5,
  "knowledge_base_ids": [1, 2]  // 可选，不指定则搜索所有知识库
}
```

### 机器人关联知识库

#### 关联知识库

```http
POST /api/robots/{robot_id}/knowledge-bases
Content-Type: application/json
Authorization: Bearer <token>

{
  "knowledge_base_ids": [1, 2, 3]
}
```

#### 获取机器人的知识库

```http
GET /api/robots/{robot_id}/knowledge-bases
Authorization: Bearer <token>
```

#### 取消关联

```http
DELETE /api/robots/{robot_id}/knowledge-bases/{kb_id}
Authorization: Bearer <token>
```

### 使用 RAG 进行对话

一旦机器人关联了知识库，在对话时会自动使用 RAG：

```http
POST /api/conversations/{conversation_id}/messages/stream
Content-Type: application/json
Authorization: Bearer <token>

{
  "content": "请介绍一下 RAG 技术",
  "provider": "openai",
  "model": "gpt-4"
}
```

系统会自动：
1. 检测到机器人关联了知识库
2. 从知识库中检索相关文档
3. 基于检索到的文档生成回答
4. 返回答案和引用来源

## 流式事件类型

RAG 对话流式返回以下事件：

```javascript
// RAG 状态更新
{
  "type": "rag_status",
  "data": "正在分析问题..."
}

// 查询重写结果
{
  "type": "rag_rewritten_queries",
  "data": {
    "queries": ["查询1", "查询2", "查询3"]
  }
}

// 检索结果
{
  "type": "rag_retrieved",
  "data": {
    "count": 5
  }
}

// 内容流式输出
{
  "type": "content",
  "data": "文"  // 单个字符
}

// 完成（包含来源）
{
  "type": "done",
  "data": {
    "id": 123,
    "content": "完整答案...",
    "rag_sources": [
      {
        "index": 1,
        "content": "文档摘要...",
        "document_id": 10,
        "filename": "文档名.pdf",
        "chunk_index": 0,
        "score": 0.95
      }
    ]
  }
}
```

## 架构说明

### 组件层次

```
API 层 (knowledge_bases.py, robots.py, messages.py)
    ↓
RAG Agent (rag_agent.py)
    ↓
检索服务 (retrieval_service.py)
    ↓
向量存储 (pgvector_store.py, elasticsearch_store.py)
    ↓
嵌入服务 (embedding_service.py)
```

### 文档处理流程

```
1. 文档上传
   ↓
2. 文档解析 (document_processors/)
   ↓
3. 文本分块 (chunking_service.py)
   ↓
4. 生成嵌入 (embedding_service.py)
   ↓
5. 存储向量 (vector_store/)
```

### RAG 检索流程

```
1. 查询重写 (可选)
   ↓
2. 生成查询向量
   ↓
3. 混合检索 (语义 + BM25)
   ↓
4. 结果重排序 (可选)
   ↓
5. 生成回答
   ↓
6. 返回答案和来源
```

## 性能优化建议

### 1. 向量索引

pgvector 使用 HNSW 索引：
```sql
CREATE INDEX idx_kb_chunks_embedding ON knowledge_base_chunks 
USING hnsw (embedding vector_cosine_ops);
```

### 2. 分块策略

- 技术文档：chunk_size=500, overlap=50
- 长篇文章：chunk_size=1000, overlap=100
- 代码文件：chunk_size=300, overlap=30

### 3. 嵌入模型选择

- **OpenAI Small** (text-embedding-3-small): 快速、成本低
- **OpenAI Large** (text-embedding-3-large): 高精度
- **HuggingFace BGE**: 离线使用、隐私保护

### 4. 检索策略

- 简单查询：语义检索
- 复杂查询：混合检索 + 重排序
- 精确匹配：BM25

## 故障排除

### 问题：无法创建向量索引

**原因**：pgvector 扩展未安装

**解决**：
```sql
CREATE EXTENSION vector;
```

### 问题：Elasticsearch 连接失败

**检查**：
1. Elasticsearch 是否运行：`curl http://localhost:9200`
2. 配置是否正确：检查 `ELASTICSEARCH_URL`

### 问题：文档处理失败

**常见原因**：
1. 文件格式不支持
2. 文件损坏
3. 依赖包未安装（pypdf, python-docx）

**解决**：
```bash
pip install pypdf python-docx pdfplumber
```

### 问题：嵌入生成慢

**优化方案**：
1. 使用本地模型（HuggingFace）
2. 批量处理文档
3. 减小 chunk_size

## 扩展开发

### 添加新的文档处理器

```python
# backend/app/services/document_processors/custom_processor.py
from .base import DocumentProcessor

class CustomProcessor(DocumentProcessor):
    def extract_text(self, file: BinaryIO) -> str:
        # 实现文本提取逻辑
        pass
    
    def supports_file_type(self, file_type: str) -> bool:
        return file_type.lower() in ['.custom']
```

### 添加新的向量存储

```python
# backend/app/services/vector_store/custom_store.py
from .base import VectorStoreBase

class CustomStore(VectorStoreBase):
    async def add_documents(self, documents, embeddings):
        # 实现文档添加逻辑
        pass
    
    async def similarity_search(self, query_embedding, top_k, filter_dict):
        # 实现相似度搜索逻辑
        pass
```

## 最佳实践

1. **知识库组织**：按主题创建独立的知识库
2. **文档准备**：清理文档格式，移除无用内容
3. **定期更新**：保持知识库内容最新
4. **权限管理**：合理设置 is_public 标志
5. **监控性能**：关注检索延迟和准确率

## 参考资料

- [LangChain 文档](https://python.langchain.com/)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [pgvector 文档](https://github.com/pgvector/pgvector)
- [Elasticsearch 文档](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)

