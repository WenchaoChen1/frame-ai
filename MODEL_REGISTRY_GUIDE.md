# 🎯 AI 模型服务商统一注册中心

## 📋 概述

`model_registry.py` 是一个集中管理所有 AI 服务商、对话模型、嵌入模型及其元数据的统一注册中心。

### 🎨 设计理念

- **统一管理**：所有模型定义和元数据集中在一个文件中
- **类型安全**：使用 Python 枚举确保模型引用的类型安全
- **可扩展**：轻松添加新的服务商或模型
- **元数据丰富**：包含价格、上下文长度、维度等详细信息
- **向后兼容**：保持对现有代码的兼容性

---

## 📁 文件结构

```
backend/app/ai/models/
├── model_registry.py      # 🆕 统一的模型注册中心
├── __init__.py            # 导出所有模型定义
├── ai_manager.py          # AI 管理器
├── openai_service.py      # OpenAI 服务
├── claude_service.py      # Claude 服务
└── ollama_service.py      # Ollama 服务
```

---

## 🔧 核心组件

### 1️⃣ 枚举类型

#### `AIProvider` - AI 服务商
```python
class AIProvider(str, enum.Enum):
    OPENAI = "openai"
    CLAUDE = "claude"
    OLLAMA = "ollama"
```

#### `ModelType` - 模型类型
```python
class ModelType(str, enum.Enum):
    CHAT = "chat"          # 对话模型
    EMBEDDING = "embedding"  # 嵌入模型
    IMAGE = "image"        # 图像模型
    AUDIO = "audio"        # 音频模型
```

#### `ChatModel` - 对话模型
```python
class ChatModel(str, enum.Enum):
    # OpenAI
    OPENAI_GPT_4O = "gpt-4o"
    OPENAI_GPT_4O_MINI = "gpt-4o-mini"
    
    # Claude
    CLAUDE_3_5_SONNET = "claude-3-5-sonnet-20241022"
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    
    # Ollama
    OLLAMA_LLAMA3 = "llama3"
    OLLAMA_MISTRAL = "mistral"
    # ... 更多模型
```

#### `EmbeddingModel` - 嵌入模型
```python
class EmbeddingModel(str, enum.Enum):
    # OpenAI
    OPENAI_TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"
    OPENAI_TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"
    
    # Claude
    CLAUDE_EMBED_V1 = "claude-embed-v1"
    
    # Ollama
    OLLAMA_NOMIC_EMBED_TEXT = "nomic-embed-text"
    # ... 更多模型
```

---

### 2️⃣ 元数据类

#### `ModelMetadata` - 模型元数据
```python
@dataclass
class ModelMetadata:
    id: str                          # 模型ID
    name: str                        # 显示名称
    provider: AIProvider             # 服务商
    model_type: ModelType           # 模型类型
    description: str                 # 描述
    context_length: Optional[int]    # 上下文长度
    dimensions: Optional[int]        # 嵌入维度（仅嵌入模型）
    max_tokens: Optional[int]        # 最大输出token（仅对话模型）
    supports_streaming: bool         # 是否支持流式输出
    is_available: bool               # 是否可用
    price_input: Optional[float]     # 输入价格（$/1M tokens）
    price_output: Optional[float]    # 输出价格（$/1M tokens）
```

---

### 3️⃣ 模型注册表

#### 对话模型注册表
```python
PROVIDER_CHAT_MODELS: Dict[AIProvider, Dict[ChatModel, ModelMetadata]]
```

**示例**：
```python
# OpenAI GPT-4O
OPENAI_CHAT_MODELS = {
    ChatModel.OPENAI_GPT_4O: ModelMetadata(
        id="gpt-4o",
        name="GPT-4O",
        provider=AIProvider.OPENAI,
        model_type=ModelType.CHAT,
        description="最新的 GPT-4O 模型，性能强大",
        context_length=128000,
        max_tokens=4096,
        supports_streaming=True,
        price_input=5.0,
        price_output=15.0,
    ),
}
```

#### 嵌入模型注册表
```python
PROVIDER_EMBEDDING_MODELS: Dict[AIProvider, Dict[EmbeddingModel, ModelMetadata]]
```

---

### 4️⃣ 工具函数

| 函数 | 说明 | 示例 |
|------|------|------|
| `get_chat_model_metadata()` | 获取对话模型元数据 | `get_chat_model_metadata(ChatModel.OPENAI_GPT_4O)` |
| `get_embedding_model_metadata()` | 获取嵌入模型元数据 | `get_embedding_model_metadata(EmbeddingModel.OPENAI_TEXT_EMBEDDING_3_SMALL)` |
| `get_provider_chat_models()` | 获取服务商的所有对话模型 | `get_provider_chat_models(AIProvider.OPENAI)` |
| `get_provider_embedding_models()` | 获取服务商的所有嵌入模型 | `get_provider_embedding_models(AIProvider.OPENAI)` |
| `get_all_chat_models()` | 获取所有对话模型 | `get_all_chat_models()` |
| `get_all_embedding_models()` | 获取所有嵌入模型 | `get_all_embedding_models()` |
| `get_model_provider()` | 根据模型获取服务商 | `get_model_provider(ChatModel.OPENAI_GPT_4O)` |
| `is_model_available()` | 检查模型是否可用 | `is_model_available(ChatModel.OPENAI_GPT_4O)` |

---

## 💡 使用示例

### 示例 1：获取嵌入模型元数据
```python
from app.ai.models import EmbeddingModel, get_embedding_model_metadata

model = EmbeddingModel.OPENAI_TEXT_EMBEDDING_3_SMALL
metadata = get_embedding_model_metadata(model)

print(f"模型名称: {metadata.name}")
print(f"维度: {metadata.dimensions}")
print(f"服务商: {metadata.provider.value}")
print(f"价格: ${metadata.price_input}/1M tokens")
```

**输出**：
```
模型名称: Text Embedding 3 Small
维度: 1536
服务商: openai
价格: $0.02/1M tokens
```

---

### 示例 2：列出所有 OpenAI 对话模型
```python
from app.ai.models import AIProvider, get_provider_chat_models

models = get_provider_chat_models(AIProvider.OPENAI)

for metadata in models:
    print(f"- {metadata.name} ({metadata.id})")
    print(f"  上下文: {metadata.context_length} tokens")
    print(f"  价格: ${metadata.price_input} (输入) / ${metadata.price_output} (输出)")
```

**输出**：
```
- GPT-4O (gpt-4o)
  上下文: 128000 tokens
  价格: $5.0 (输入) / $15.0 (输出)
- GPT-4O Mini (gpt-4o-mini)
  上下文: 128000 tokens
  价格: $0.15 (输入) / $0.6 (输出)
...
```

---

### 示例 3：在 API 路由中使用
```python
from fastapi import APIRouter
from app.ai.models import AIProvider, get_provider_embedding_models

router = APIRouter()

@router.get("/api/embeddings/{provider}")
def get_embeddings(provider: str):
    """获取指定服务商的嵌入模型列表"""
    provider_enum = AIProvider(provider)
    models = get_provider_embedding_models(provider_enum)
    
    return {
        "provider": provider,
        "models": [
            {
                "id": m.id,
                "name": m.name,
                "dimensions": m.dimensions,
                "description": m.description,
                "is_available": m.is_available,
            }
            for m in models
        ]
    }
```

---

### 示例 4：在嵌入服务中使用
```python
from app.ai.models import EmbeddingModel, get_embedding_model_metadata

class EmbeddingService:
    @classmethod
    def get_embeddings(cls, model: EmbeddingModel):
        metadata = get_embedding_model_metadata(model)
        
        if not metadata.is_available:
            raise ValueError(f"模型 {model.value} 暂不可用")
        
        # 根据服务商创建对应的嵌入实例
        if metadata.provider == AIProvider.OPENAI:
            return OpenAIEmbeddings(model=model.value)
        elif metadata.provider == AIProvider.OLLAMA:
            return HuggingFaceEmbeddings(model_name=model.value)
        # ...
```

---

## 🚀 添加新模型

### 1️⃣ 添加对话模型

#### 步骤 1：在 `ChatModel` 枚举中添加
```python
class ChatModel(str, enum.Enum):
    # ... 现有模型 ...
    OPENAI_GPT_5 = "gpt-5"  # 🆕 新模型
```

#### 步骤 2：在注册表中添加元数据
```python
OPENAI_CHAT_MODELS = {
    # ... 现有模型 ...
    ChatModel.OPENAI_GPT_5: ModelMetadata(
        id="gpt-5",
        name="GPT-5",
        provider=AIProvider.OPENAI,
        model_type=ModelType.CHAT,
        description="下一代 GPT 模型",
        context_length=256000,
        max_tokens=8192,
        supports_streaming=True,
        price_input=10.0,
        price_output=30.0,
    ),
}
```

---

### 2️⃣ 添加嵌入模型

#### 步骤 1：在 `EmbeddingModel` 枚举中添加
```python
class EmbeddingModel(str, enum.Enum):
    # ... 现有模型 ...
    OPENAI_TEXT_EMBEDDING_4 = "text-embedding-4"  # 🆕 新模型
```

#### 步骤 2：在注册表中添加元数据
```python
OPENAI_EMBEDDING_MODELS = {
    # ... 现有模型 ...
    EmbeddingModel.OPENAI_TEXT_EMBEDDING_4: ModelMetadata(
        id="text-embedding-4",
        name="Text Embedding 4",
        provider=AIProvider.OPENAI,
        model_type=ModelType.EMBEDDING,
        description="最新的嵌入模型",
        dimensions=2048,
        price_input=0.01,
    ),
}
```

---

### 3️⃣ 添加新服务商

#### 步骤 1：在 `AIProvider` 枚举中添加
```python
class AIProvider(str, enum.Enum):
    OPENAI = "openai"
    CLAUDE = "claude"
    OLLAMA = "ollama"
    GEMINI = "gemini"  # 🆕 新服务商
```

#### 步骤 2：创建模型字典
```python
# Gemini 对话模型
GEMINI_CHAT_MODELS = {
    ChatModel.GEMINI_PRO: ModelMetadata(
        id="gemini-pro",
        name="Gemini Pro",
        provider=AIProvider.GEMINI,
        model_type=ModelType.CHAT,
        description="Google 的 Gemini Pro 模型",
        context_length=32000,
        max_tokens=2048,
        supports_streaming=True,
        price_input=0.5,
        price_output=1.5,
    ),
}
```

#### 步骤 3：注册到服务商映射表
```python
PROVIDER_CHAT_MODELS: Dict[AIProvider, Dict[ChatModel, ModelMetadata]] = {
    AIProvider.OPENAI: OPENAI_CHAT_MODELS,
    AIProvider.CLAUDE: CLAUDE_CHAT_MODELS,
    AIProvider.OLLAMA: OLLAMA_CHAT_MODELS,
    AIProvider.GEMINI: GEMINI_CHAT_MODELS,  # 🆕 添加
}
```

---

## 🔄 迁移指南

### 从旧代码迁移

#### 之前（分散定义）
```python
# 在 knowledge_base.py 中
class EmbeddingModel(str, enum.Enum):
    OPENAI_SMALL = "text-embedding-3-small"
    OPENAI_LARGE = "text-embedding-3-large"

# 在 embedding_service.py 中
MODEL_DIMENSIONS = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
}
```

#### 现在（统一注册中心）
```python
# 从统一注册中心导入
from app.ai.models import (
    EmbeddingModel,
    get_embedding_model_metadata,
    MODEL_DIMENSIONS,
)

# 使用枚举
model = EmbeddingModel.OPENAI_TEXT_EMBEDDING_3_SMALL

# 获取元数据
metadata = get_embedding_model_metadata(model)
print(metadata.dimensions)  # 1536

# 或者使用旧的 MODEL_DIMENSIONS（向后兼容）
print(MODEL_DIMENSIONS[model])  # 1536
```

---

## ✅ 优势总结

| 优势 | 说明 |
|------|------|
| 🎯 **集中管理** | 所有模型定义在一个文件中，易于维护和更新 |
| 🔒 **类型安全** | 使用枚举避免字符串拼写错误 |
| 📊 **元数据丰富** | 包含价格、上下文、维度等详细信息 |
| 🔍 **易于查询** | 提供丰富的工具函数快速查找模型信息 |
| 🚀 **可扩展** | 添加新模型或服务商只需三步 |
| 🔄 **向后兼容** | 保留旧的接口，现有代码无需修改 |
| 🧪 **易于测试** | 集中的定义便于单元测试和集成测试 |

---

## 📚 相关文件

- `backend/app/ai/models/model_registry.py` - 模型注册中心主文件
- `backend/app/ai/models/__init__.py` - 模块导出
- `backend/app/routers/providers.py` - API 路由使用示例
- `backend/app/services/embedding_service.py` - 嵌入服务使用示例
- `backend/app/models/knowledge_base.py` - 数据库模型使用示例

---

## 🎉 总结

统一的模型注册中心为整个项目提供了一个**单一的真实来源（Single Source of Truth）**，使得模型管理变得简单、清晰、可维护。所有新功能和模型扩展都应该从这个注册中心开始！🚀

