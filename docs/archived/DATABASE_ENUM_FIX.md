# 数据库枚举值修复报告

## 🔍 问题诊断

**错误信息**：
```
(psycopg2.errors.UndefinedColumn) column knowledge_bases.vector_store_config_id does not exist
```

**根本原因**：
1. 数据库表缺少新增的字段：`vector_store_config_id` 和 `embedding_provider`
2. 代码中的枚举值（小写）与数据库枚举值（大写）不匹配

## ✅ 修复步骤

### 1. 运行数据库迁移

添加了缺失的字段：
- `embedding_provider` (类型: `embedding_provider_enum`, 默认值: `'OPENAI'`)
- `vector_store_config_id` (类型: `INTEGER`, 可空)

```sql
ALTER TABLE knowledge_bases 
ADD COLUMN IF NOT EXISTS embedding_provider embedding_provider_enum DEFAULT 'OPENAI',
ADD COLUMN IF NOT EXISTS vector_store_config_id INTEGER NULL;
```

### 2. 修复枚举值不匹配

**数据库中的枚举值（大写）**：
```
embedding_provider_enum: OPENAI, CLAUDE, OLLAMA
embedding_model_enum: OPENAI_SMALL, OPENAI_LARGE, HUGGINGFACE_BGE
vector_store_type_enum: PGVECTOR, ELASTICSEARCH
```

**修复文件**：

#### `backend/app/ai/models/model_registry.py`

1. **更新 AIProvider 枚举**：
```python
class AIProvider(str, enum.Enum):
    OPENAI = "OPENAI"  # 从 "openai" 改为 "OPENAI"
    CLAUDE = "CLAUDE"  # 从 "claude" 改为 "CLAUDE"
    OLLAMA = "OLLAMA"  # 从 "ollama" 改为 "OLLAMA"
```

2. **更新 EmbeddingModel 枚举**：
```python
class EmbeddingModel(str, enum.Enum):
    """嵌入模型 - 值匹配数据库中的枚举"""
    OPENAI_SMALL = "OPENAI_SMALL"
    OPENAI_LARGE = "OPENAI_LARGE"
    HUGGINGFACE_BGE = "HUGGINGFACE_BGE"
```

3. **更新模型元数据**：
- 简化了 `OPENAI_EMBEDDING_MODELS` 字典
- 添加了 `HUGGINGFACE_EMBEDDING_MODELS` 字典
- 清空了 `CLAUDE_EMBEDDING_MODELS` 和 `OLLAMA_EMBEDDING_MODELS`（暂无对应数据库枚举）

#### `backend/app/ai/embeddings/embedding_service.py`

1. **更新默认模型**：
```python
# 从 EmbeddingModel.OPENAI_TEXT_EMBEDDING_3_SMALL
# 改为 EmbeddingModel.OPENAI_SMALL
```

2. **添加模型 ID 映射**：
```python
model_id_map = {
    EmbeddingModel.OPENAI_SMALL: "text-embedding-3-small",
    EmbeddingModel.OPENAI_LARGE: "text-embedding-3-large",
    EmbeddingModel.HUGGINGFACE_BGE: "BAAI/bge-large-zh-v1.5",
}
```

将数据库枚举值映射到实际的模型 API ID。

## 📊 修复验证

### 数据库表结构验证
```
✅ knowledge_bases 表字段:
  - embedding_provider: USER-DEFINED (embedding_provider_enum) = 'OPENAI'
  - vector_store_config_id: integer (int4) = NULL
```

### 枚举类型验证
```
✅ embedding_provider_enum: OPENAI, CLAUDE, OLLAMA
✅ embedding_model_enum: OPENAI_SMALL, OPENAI_LARGE, HUGGINGFACE_BGE
✅ vector_store_type_enum: PGVECTOR, ELASTICSEARCH
```

### Linter 检查
```
✅ 无 Linter 错误
```

## 🎯 影响范围

### 修改的文件
1. `backend/app/ai/models/model_registry.py` - 枚举值更新
2. `backend/app/ai/embeddings/embedding_service.py` - 默认值和映射更新

### 数据库更改
1. 添加了 `embedding_provider` 字段
2. 添加了 `vector_store_config_id` 字段

## 🚀 下一步

1. **重启后端服务**（如果正在运行）
2. **刷新前端页面**，测试知识库功能
3. **验证关键功能**：
   - 创建知识库
   - 上传文档
   - 向量化存储
   - 召回测试

## 📝 注意事项

1. **向后兼容性**：
   - 保留了 `EmbeddingProvider = AIProvider` 别名
   - 现有数据库记录会自动使用默认值 `'OPENAI'`

2. **扩展性**：
   - 要添加新的嵌入模型，需要：
     1. 在数据库中添加新的枚举值（使用 ALTER TYPE）
     2. 在 `model_registry.py` 中添加新的枚举项
     3. 在 `embedding_service.py` 的 `model_id_map` 中添加映射

3. **数据迁移**：
   - 所有现有知识库会自动获得 `embedding_provider = 'OPENAI'`
   - `vector_store_config_id` 默认为 `NULL`（使用系统库）

---

**修复完成时间**：2025-10-17 18:30  
**修复状态**：✅ 成功

