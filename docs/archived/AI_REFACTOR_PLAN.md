# 🔧 AI 模块重构计划

## 📋 重构目标

将所有与 AI、LangChain、LangGraph 相关的底层服务统一移到 `backend/app/ai/` 目录下，实现清晰的分层架构。

---

## 📁 新的目录结构

```
backend/app/
├── ai/                              # 🎯 AI 底层服务（LangChain/LangGraph相关）
│   ├── models/                      # ✅ 模型定义和服务商管理
│   │   ├── model_registry.py       # 统一模型注册中心
│   │   ├── ai_manager.py           # AI 管理器
│   │   ├── openai_service.py       # OpenAI 服务
│   │   ├── claude_service.py       # Claude 服务
│   │   ├── ollama_service.py       # Ollama 服务
│   │   └── __init__.py
│   │
│   ├── embeddings/                  # ✅ 嵌入服务
│   │   ├── embedding_service.py    # 嵌入模型服务（使用 LangChain）
│   │   └── __init__.py
│   │
│   ├── vector_stores/               # ✅ 向量存储
│   │   ├── base.py                 # 向量存储基类
│   │   ├── pgvector_store.py       # PGVector 实现
│   │   ├── elasticsearch_store.py  # Elasticsearch 实现
│   │   └── __init__.py
│   │
│   ├── retrievers/                  # 🔄 检索服务
│   │   ├── retrieval_service.py    # 检索服务（语义/BM25/混合）
│   │   └── __init__.py
│   │
│   ├── document_loaders/            # 🔄 文档加载器
│   │   ├── base.py                 # 文档处理器基类
│   │   ├── txt_loader.py           # TXT 加载器
│   │   ├── pdf_loader.py           # PDF 加载器
│   │   ├── docx_loader.py          # DOCX 加载器
│   │   └── __init__.py
│   │
│   ├── text_splitters/              # 🔄 文本分割器
│   │   ├── chunking_service.py     # 分块服务（使用 LangChain）
│   │   └── __init__.py
│   │
│   └── agent/                       # ✅ RAG Agent
│       ├── rag_agent.py            # RAG Agent（使用 LangGraph）
│       └── __init__.py
│
├── services/                        # 📦 业务逻辑层
│   └── knowledge_base_service.py   # 知识库业务服务（调用 ai 模块）
│
├── routers/                         # 🌐 API 路由层
├── models/                          # 💾 数据库模型
├── schemas/                         # 📝 Pydantic Schemas
└── core/                            # ⚙️ 核心配置
```

---

## 🔄 迁移状态

### ✅ 已完成

| 模块 | 源位置 | 目标位置 | 状态 |
|------|--------|----------|------|
| **模型注册中心** | `ai/models/model_registry.py` | ✅ 已创建 | ✅ 完成 |
| **嵌入服务** | `services/embedding_service.py` | `ai/embeddings/embedding_service.py` | ✅ 完成 |
| **向量存储** | `services/vector_store/*` | `ai/vector_stores/*` | ✅ 完成 |

### 🔄 进行中

| 模块 | 源位置 | 目标位置 | 状态 |
|------|--------|----------|------|
| **检索服务** | `services/retrieval_service.py` | `ai/retrievers/retrieval_service.py` | 🔄 迁移中 |
| **文档加载器** | `services/document_processors/*` | `ai/document_loaders/*` | ⏳ 待处理 |
| **文本分割器** | `services/chunking_service.py` | `ai/text_splitters/chunking_service.py` | ⏳ 待处理 |

### ⏳ 待处理

- 更新所有引用这些服务的文件
- 删除旧的 `services/` 下的文件
- 更新文档

---

## 📝 导入路径变更

### 嵌入服务
```python
# ❌ 旧导入
from app.services.embedding_service import EmbeddingService

# ✅ 新导入
from app.ai.embeddings import EmbeddingService
```

### 向量存储
```python
# ❌ 旧导入
from app.services.vector_store import PGVectorStore, ElasticsearchStore, Document

# ✅ 新导入
from app.ai.vector_stores import PGVectorStore, ElasticsearchStore, Document
```

### 检索服务
```python
# ❌ 旧导入
from app.services.retrieval_service import RetrievalService

# ✅ 新导入
from app.ai.retrievers import RetrievalService
```

### 文档加载器
```python
# ❌ 旧导入
from app.services.document_processors import TxtProcessor, PdfProcessor

# ✅ 新导入
from app.ai.document_loaders import TxtLoader, PdfLoader
```

### 文本分割器
```python
# ❌ 旧导入
from app.services.chunking_service import ChunkingService

# ✅ 新导入
from app.ai.text_splitters import ChunkingService
```

---

## 🎯 重构原则

### 1. 分层清晰
- **AI 层** (`app/ai/`): LangChain/LangGraph 相关的底层 AI 服务
- **业务层** (`app/services/`): 业务逻辑，调用 AI 层
- **API 层** (`app/routers/`): HTTP 接口，调用业务层

### 2. 依赖方向
```
routers/ → services/ → ai/ → models/
         ↓            ↓      ↓
      schemas/     core/  models/
```

### 3. 命名规范
- **AI 层**: 使用 LangChain 术语 (Loader, Splitter, Retriever, Store)
- **业务层**: 使用业务术语 (Service, Manager)
- **保持一致性**: 所有 AI 模块都在 `ai/` 下

---

## ✅ 验证清单

迁移完成后需要验证：

- [ ] 所有文件移动到正确位置
- [ ] 所有 `__init__.py` 创建并导出
- [ ] 所有导入路径已更新
- [ ] `knowledge_base_service.py` 更新所有引用
- [ ] `rag_agent.py` 更新所有引用
- [ ] `routers/knowledge_bases.py` 更新引用
- [ ] Linter 检查通过
- [ ] 应用能正常启动
- [ ] API 能正常调用

---

## 🚀 下一步

1. 完成剩余模块迁移
2. 更新所有引用文件
3. 删除旧文件
4. 运行测试验证
5. 更新文档

---

**目标**: 清晰、模块化、易维护的 AI 服务架构！

