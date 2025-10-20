# 嵌入模型定义重构说明

## 📋 重构概述

将嵌入模型的定义从 `models/knowledge_base.py` 移动到 `ai/models/embedding_models.py`，使代码结构更加清晰和模块化。

## 🔄 主要变更

### 1. 新增文件

**`backend/app/ai/models/embedding_models.py`**
- 集中定义所有嵌入模型相关的枚举和工具函数
- 包含内容：
  - `EmbeddingProvider` - 嵌入模型提供商枚举
  - `EmbeddingModel` - 嵌入模型枚举
  - `PROVIDER_MODELS` - 提供商与模型的映射关系
  - `MODEL_DIMENSIONS` - 模型维度映射
  - `get_model_provider()` - 根据模型获取提供商
  - `get_model_dimension()` - 获取模型维度

### 2. 更新的文件

#### `backend/app/ai/models/__init__.py`
- 导出嵌入模型相关的定义
- 使其他模块可以通过 `from ..ai.models import EmbeddingModel` 导入

#### `backend/app/models/knowledge_base.py`
- 从 `..ai.models` 导入 `EmbeddingProvider` 和 `EmbeddingModel`
- 删除本地的枚举定义
- 保持 `VectorStoreType` 和 `DocumentStatus` 在本地定义

#### `backend/app/services/embedding_service.py`
- 从 `..ai.models` 导入 `EmbeddingModel`
- 更新 `_create_embeddings()` 方法支持所有新模型
- 更新 `get_embedding_dimension()` 使用 `MODEL_DIMENSIONS`
- 修复便捷函数默认参数：
  - `EmbeddingModel.OPENAI_SMALL` → `EmbeddingModel.OPENAI_TEXT_EMBEDDING_3_SMALL`

#### `backend/app/routers/providers.py`
- 从 `..ai.models` 导入枚举

#### `backend/app/schemas/knowledge_base.py`
- 从 `..ai.models` 导入枚举

## 📊 模型枚举对比

### 旧枚举值
```python
EmbeddingModel.OPENAI_SMALL = "openai-small"
EmbeddingModel.OPENAI_LARGE = "openai-large"
EmbeddingModel.HUGGINGFACE_BGE = "huggingface-bge"
```

### 新枚举值
```python
# OpenAI models
EmbeddingModel.OPENAI_TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"
EmbeddingModel.OPENAI_TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"
EmbeddingModel.OPENAI_TEXT_EMBEDDING_ADA_002 = "text-embedding-ada-002"

# Claude models
EmbeddingModel.CLAUDE_EMBED_V1 = "claude-embed-v1"

# Ollama models
EmbeddingModel.OLLAMA_NOMIC_EMBED_TEXT = "nomic-embed-text"
EmbeddingModel.OLLAMA_MXBAI_EMBED_LARGE = "mxbai-embed-large"
EmbeddingModel.OLLAMA_ALL_MINILM = "all-minilm"
```

## 🎯 代码结构优化

### 之前的结构
```
backend/app/
├── models/
│   └── knowledge_base.py  (包含嵌入模型枚举)
└── services/
    └── embedding_service.py  (使用嵌入模型)
```

### 现在的结构
```
backend/app/
├── ai/
│   └── models/
│       ├── embedding_models.py  ✨ 新增：集中管理嵌入模型定义
│       └── __init__.py  (导出嵌入模型)
├── models/
│   └── knowledge_base.py  (导入并使用嵌入模型)
└── services/
    └── embedding_service.py  (导入并使用嵌入模型)
```

## 🔧 使用方式

### 导入嵌入模型
```python
# 推荐方式
from ..ai.models import EmbeddingModel, EmbeddingProvider

# 也可以
from ..ai.models.embedding_models import EmbeddingModel, EmbeddingProvider
```

### 使用便捷函数
```python
from ..services.embedding_service import embed_documents, embed_query

# 使用默认模型（text-embedding-3-small）
vectors = await embed_documents(["文本1", "文本2"])

# 指定模型
vectors = await embed_documents(
    ["文本1", "文本2"], 
    model=EmbeddingModel.OPENAI_TEXT_EMBEDDING_3_LARGE
)
```

### 获取模型信息
```python
from ..ai.models import get_model_dimension, get_model_provider

# 获取模型维度
dim = get_model_dimension(EmbeddingModel.OPENAI_TEXT_EMBEDDING_3_SMALL)  # 1536

# 获取模型提供商
provider = get_model_provider(EmbeddingModel.OPENAI_TEXT_EMBEDDING_3_SMALL)  # "openai"
```

## ✅ 优势

1. **模块化**：AI 相关的定义集中在 `ai/` 目录下
2. **可维护性**：添加新模型只需修改 `embedding_models.py`
3. **可扩展性**：提供了工具函数方便查询模型信息
4. **避免循环导入**：清晰的依赖关系
5. **语义清晰**：模型名称直接对应实际的 API 模型名

## 🔍 迁移检查清单

- [x] 创建 `ai/models/embedding_models.py`
- [x] 更新 `ai/models/__init__.py` 导出
- [x] 更新 `models/knowledge_base.py` 导入
- [x] 更新 `services/embedding_service.py` 
  - [x] 导入路径
  - [x] `_create_embeddings()` 方法
  - [x] `get_embedding_dimension()` 方法
  - [x] 便捷函数默认参数
- [x] 更新 `routers/providers.py` 导入
- [x] 更新 `schemas/knowledge_base.py` 导入
- [x] 所有 Linter 检查通过

## 🎉 兼容性说明

**数据库迁移**：
- 数据库中存储的是模型的字符串值（如 "text-embedding-3-small"）
- 现有数据库需要运行 Migration 006 来更新
- 旧的枚举值会自动映射到新值

**API 兼容性**：
- API 请求和响应中使用模型的字符串值
- 前端无需修改（已在之前更新）
- Provider API 返回新的模型列表

## 📚 相关文档

- [知识库高级配置](KNOWLEDGE_BASE_ADVANCED_CONFIG.md)
- [快速开始指南](QUICKSTART_ADVANCED_KB.md)
- [RAG功能指南](RAG_FEATURE_GUIDE.md)

---

重构完成！代码结构更清晰，维护更方便！✨

