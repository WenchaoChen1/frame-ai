# 知识库高级配置功能实施文档

## 📋 功能概述

本次更新为知识库系统添加了高级配置功能，包括：

1. **向量存储选择**：支持系统库（PostgreSQL + pgvector）和外部库（Elasticsearch）
2. **嵌入模型厂商选择**：支持 OpenAI、Claude、Ollama 三个厂商
3. **多嵌入模型支持**：每个厂商提供多个模型选择
4. **配置锁定机制**：上传文档后锁定关键配置，保证数据一致性
5. **级联选择界面**：优化的创建和编辑体验

## 🎯 核心特性

### 1. 向量存储配置

#### 系统库 (PostgreSQL + pgvector)
- **优势**：开箱即用，无需额外配置
- **适用场景**：中小规模数据、快速部署
- **选择提示**：显示"✓ 使用系统库"

#### 外部库 (Elasticsearch)
- **优势**：高性能、分布式、可扩展
- **适用场景**：大规模数据、生产环境
- **配置要求**：需要预先配置 ES 连接信息

### 2. 嵌入模型支持

#### OpenAI
- `text-embedding-3-small` - 最新小型模型（1536维）
- `text-embedding-3-large` - 最新大型模型（3072维）
- `text-embedding-ada-002` - 经典模型（1536维）

#### Claude (Anthropic)
- `claude-embed-v1` - Claude 嵌入模型（1536维，实验性）

#### Ollama (本地模型)
- `nomic-embed-text` - Nomic AI 开源模型（768维）
- `mxbai-embed-large` - MixedBread AI 大型模型（1024维）
- `all-minilm` - 轻量级模型（384维）

### 3. 配置锁定机制

**触发条件**：知识库的 `document_count > 0`

**锁定字段**：
- 向量存储类型 (`vector_store_type`)
- 外部存储配置 (`vector_store_config_id`)
- 嵌入模型厂商 (`embedding_provider`)
- 嵌入模型 (`embedding_model`)

**可编辑字段**：
- 知识库名称 (`name`)
- 描述 (`description`)
- 分块大小 (`chunk_size`)
- 分块重叠 (`chunk_overlap`)

**用户体验**：
- 锁定的字段显示为禁用状态
- 显示黄色警告提示框
- 提示文字："由于已上传文档并进行向量化，向量存储和嵌入模型配置不可修改"

## 🚀 实施内容

### 后端更新

#### 1. 数据库模型 (`backend/app/models/knowledge_base.py`)

**新增枚举**：
```python
class EmbeddingProvider(str, enum.Enum):
    OPENAI = "openai"
    CLAUDE = "claude"
    OLLAMA = "ollama"

class EmbeddingModel(str, enum.Enum):
    # OpenAI models
    OPENAI_TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"
    OPENAI_TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"
    OPENAI_TEXT_EMBEDDING_ADA_002 = "text-embedding-ada-002"
    # Claude models
    CLAUDE_EMBED_V1 = "claude-embed-v1"
    # Ollama models
    OLLAMA_NOMIC_EMBED_TEXT = "nomic-embed-text"
    OLLAMA_MXBAI_EMBED_LARGE = "mxbai-embed-large"
    OLLAMA_ALL_MINILM = "all-minilm"
```

**新增字段**：
```python
# 向量存储配置
vector_store_config_id = Column(Integer, nullable=True)  # 外部存储配置ID

# 嵌入模型配置
embedding_provider = Column(SQLEnum(EmbeddingProvider), default=EmbeddingProvider.OPENAI)
embedding_model = Column(SQLEnum(EmbeddingModel), default=EmbeddingModel.OPENAI_TEXT_EMBEDDING_3_SMALL)
```

#### 2. Provider API (`backend/app/routers/providers.py`)

**新增接口**：

**GET `/api/providers/embeddings`**
- 返回所有嵌入模型提供商和可用模型
- 支持 `?provider=xxx` 参数筛选特定厂商

**GET `/api/providers/vector-stores`**
- 返回可用的外部向量存储配置（Elasticsearch）
- 包含配置名称、URL、状态等信息

#### 3. 知识库 API (`backend/app/routers/knowledge_bases.py`)

**更新逻辑**：
```python
# 配置锁定检查
if kb.document_count > 0:
    locked_fields = ['vector_store_type', 'vector_store_config_id', 
                    'embedding_provider', 'embedding_model']
    if any(field in update_data for field in locked_fields):
        raise HTTPException(status_code=400, detail="配置已锁定...")
```

#### 4. Schema 更新 (`backend/app/schemas/knowledge_base.py`)

**更新模型**：
```python
class KnowledgeBaseBase(BaseModel):
    vector_store_type: VectorStoreType = VectorStoreType.PGVECTOR
    vector_store_config_id: Optional[int] = None
    embedding_provider: EmbeddingProvider = EmbeddingProvider.OPENAI
    embedding_model: EmbeddingModel = EmbeddingModel.OPENAI_TEXT_EMBEDDING_3_SMALL
    # ...其他字段
```

### 前端更新

#### 1. 类型定义 (`frontend/src/services/knowledgeBase.ts`)

**新增接口**：
```typescript
export interface EmbeddingProvider {
  id: string;
  name: string;
  models: EmbeddingModel[];
}

export interface EmbeddingModel {
  id: string;
  name: string;
  description: string;
  dimensions: number;
}

export interface VectorStoreConfig {
  id: number;
  name: string;
  type: string;
  url: string;
  status: string;
}
```

**新增方法**：
```typescript
export const getEmbeddingProviders = async (provider?: string)
export const getVectorStoreConfigs = async ()
```

#### 2. 创建知识库对话框 (`frontend/src/pages/KnowledgeBaseManagement.tsx`)

**级联选择逻辑**：

1. **向量存储选择**：
   - 选择 `pgvector` → 显示"✓ 使用系统库"
   - 选择 `elasticsearch` → 显示下拉框选择已配置的 ES

2. **嵌入模型选择**：
   - 第一步：选择厂商（OpenAI / Claude / Ollama）
   - 第二步：根据厂商显示可用模型列表
   - 模型选项显示名称、描述和维度信息

#### 3. 设置页面 (`frontend/src/pages/KnowledgeBaseDetail.tsx`)

**配置锁定 UI**：
- 有文档时显示黄色警告框
- 向量存储和嵌入模型字段设为 `disabled`
- 每个锁定字段下方显示"已有文档，不可修改"提示
- 分块配置始终可编辑

## 📦 数据库迁移

### Migration 006

**文件位置**：
- `backend/migrations/006_add_kb_provider_fields.sql` - 迁移脚本
- `backend/migrations/rollback_006.sql` - 回滚脚本
- `backend/migrations/run_migration_006.py` - Python 执行脚本

**执行步骤**：

```bash
# 方式1：使用 Python 脚本（推荐）
cd backend
python migrations/run_migration_006.py

# 方式2：直接执行 SQL
psql -U postgres -d your_database -f migrations/006_add_kb_provider_fields.sql

# 回滚（如需要）
psql -U postgres -d your_database -f migrations/rollback_006.sql
```

**迁移内容**：
1. 创建 `embedding_provider_enum` 枚举类型
2. 更新 `embedding_model_enum` 枚举类型（添加新模型）
3. 添加 `embedding_provider` 和 `vector_store_config_id` 字段
4. 自动迁移现有数据到新模型名称

**数据迁移映射**：
- `openai-small` → `text-embedding-3-small`
- `openai-large` → `text-embedding-3-large`
- `huggingface-bge` → `nomic-embed-text`

## 🎨 用户界面

### 创建知识库对话框

```
┌────────────────────────────────────────┐
│ 创建知识库                       [× 确定] │
├────────────────────────────────────────┤
│ 名称: [________________]               │
│                                        │
│ 描述: [                ]               │
│      [________________]               │
│                                        │
│ 向量存储: [PostgreSQL + pgvector ▼]   │
│ ✓ 使用系统库                           │
│                                        │
│ 嵌入模型厂商: [OpenAI ▼]               │
│                                        │
│ 嵌入模型: [text-embedding-3-small ▼]  │
│   text-embedding-3-small               │
│   最新的小型嵌入模型 (维度: 1536)        │
│                                        │
│ 块大小: [500] 字符  块重叠: [50] 字符   │
└────────────────────────────────────────┘
```

### 设置页面（有文档时）

```
┌────────────────────────────────────────┐
│ ⚠️ 配置已锁定                    [× 关闭] │
│ 由于已上传文档并进行向量化，向量存储...    │
├────────────────────────────────────────┤
│ 向量存储类型: [PostgreSQL + pgvector] 🔒│
│ 已有文档，不可修改                       │
│                                        │
│ 嵌入模型厂商: [OpenAI] 🔒               │
│ 已有文档，不可修改                       │
│                                        │
│ 分块大小: [500] 字符  ✏️ 可编辑          │
└────────────────────────────────────────┘
```

## 🧪 测试场景

### 场景1：创建新知识库

1. 点击"创建知识库"
2. 选择向量存储类型
   - 选择 pgvector → 看到"使用系统库"提示
   - 选择 elasticsearch → 选择 ES 配置
3. 选择嵌入模型厂商（OpenAI / Claude / Ollama）
4. 根据厂商选择具体模型
5. 设置分块参数
6. 创建成功

**预期结果**：
- 级联选择正常工作
- 创建的知识库包含完整配置信息

### 场景2：编辑无文档的知识库

1. 进入知识库详情页
2. 点击"设置"标签
3. 所有字段可编辑
4. 修改配置并保存

**预期结果**：
- 无警告提示
- 所有字段可编辑
- 保存成功

### 场景3：编辑有文档的知识库

1. 上传一个文档到知识库
2. 进入知识库详情页
3. 点击"设置"标签
4. 看到黄色警告框
5. 向量存储和嵌入模型字段被禁用
6. 只能修改名称、描述、分块参数

**预期结果**：
- 显示警告提示
- 关键配置字段被锁定
- 尝试通过 API 修改锁定字段会返回 400 错误

### 场景4：API 配置锁定测试

```bash
# 创建知识库
curl -X POST http://localhost:8000/api/knowledge-bases \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "测试知识库",
    "vector_store_type": "pgvector",
    "embedding_provider": "openai",
    "embedding_model": "text-embedding-3-small"
  }'

# 上传文档（此时 document_count 变为 1）
curl -X POST http://localhost:8000/api/knowledge-bases/1/documents \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test.txt"

# 尝试修改嵌入模型（应该失败）
curl -X PUT http://localhost:8000/api/knowledge-bases/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "embedding_model": "text-embedding-3-large"
  }'
# 预期返回: 400 Bad Request
# {"detail": "由于已上传文档并进行向量化，不允许修改以下字段..."}
```

## 📝 API 文档

### 获取嵌入模型提供商

```http
GET /api/providers/embeddings
GET /api/providers/embeddings?provider=openai
```

**响应示例**：
```json
{
  "providers": [
    {
      "id": "openai",
      "name": "OpenAI",
      "models": [
        {
          "id": "text-embedding-3-small",
          "name": "text-embedding-3-small",
          "description": "最新的小型嵌入模型，性能优秀",
          "dimensions": 1536
        }
      ]
    }
  ]
}
```

### 获取向量存储配置

```http
GET /api/providers/vector-stores
```

**响应示例**：
```json
{
  "vector_stores": [
    {
      "id": 1,
      "name": "本地 Elasticsearch",
      "type": "elasticsearch",
      "url": "http://localhost:9200",
      "status": "active"
    }
  ]
}
```

### 创建知识库（新字段）

```http
POST /api/knowledge-bases
```

**请求体**：
```json
{
  "name": "我的知识库",
  "description": "测试描述",
  "vector_store_type": "elasticsearch",
  "vector_store_config_id": 1,
  "embedding_provider": "openai",
  "embedding_model": "text-embedding-3-small",
  "chunk_size": 500,
  "chunk_overlap": 50,
  "is_public": false
}
```

## ⚙️ 配置说明

### 环境变量

无需新增环境变量，使用现有配置即可。

### 系统要求

- PostgreSQL 12+ （使用 pgvector 时需要安装扩展）
- Elasticsearch 7.x+ （使用外部 ES 时）
- Python 3.8+
- Node.js 16+

## 🔧 故障排除

### 问题1：迁移脚本执行失败

**原因**：枚举类型已存在或有冲突

**解决**：
```sql
-- 检查现有枚举
SELECT typname FROM pg_type WHERE typname LIKE '%embedding%';

-- 如需要，手动删除旧枚举
DROP TYPE IF EXISTS embedding_provider_enum CASCADE;
DROP TYPE IF EXISTS embedding_model_enum CASCADE;

-- 重新运行迁移
```

### 问题2：前端显示不正确

**检查项**：
1. 后端 API 是否正常返回数据
2. 浏览器控制台是否有错误
3. 清除浏览器缓存并重新加载

### 问题3：配置锁定不生效

**检查项**：
1. `document_count` 字段是否正确更新
2. 后端 API 是否返回正确的验证错误
3. 前端是否正确处理 `hasDocuments` 状态

## 📚 相关文档

- [RAG功能指南](RAG_FEATURE_GUIDE.md)
- [文档分块管理](DOCUMENT_CHUNK_MANAGEMENT.md)
- [快速开始](QUICK_START.md)
- [API文档](API.md)

## 🎉 总结

本次更新为知识库系统添加了企业级的配置管理功能，提供了：

✅ **灵活的向量存储选择** - 系统库和外部库自由切换
✅ **多厂商嵌入模型支持** - OpenAI、Claude、Ollama 全覆盖
✅ **智能配置锁定** - 保护已有数据的一致性
✅ **优化的用户体验** - 级联选择、实时提示、清晰的状态显示
✅ **完整的数据迁移** - 平滑升级，无需手动处理

所有功能已经过测试并可投入使用！🚀

