"""
AI模型服务商统一注册中心
集中管理所有AI服务商、对话模型、嵌入模型及其配置
"""
from __future__ import annotations
import enum
from typing import Dict, List, Optional, Union
from dataclasses import dataclass


# ==================== 服务商枚举 ====================

class AIProvider(str, enum.Enum):
    """AI服务商"""
    OPENAI = "OPENAI"
    CLAUDE = "CLAUDE"
    OLLAMA = "OLLAMA"


# ==================== 模型类型 ====================

class ModelType(str, enum.Enum):
    """模型类型"""
    CHAT = "chat"          # 对话模型
    EMBEDDING = "embedding"  # 嵌入模型
    IMAGE = "image"        # 图像模型
    AUDIO = "audio"        # 音频模型


# ==================== 对话模型枚举 ====================

class ChatModel(str, enum.Enum):
    """对话模型"""
    # OpenAI Chat Models
    OPENAI_GPT_4O = "gpt-4o"
    OPENAI_GPT_4O_MINI = "gpt-4o-mini"
    OPENAI_GPT_4_TURBO = "gpt-4-turbo"
    OPENAI_GPT_4 = "gpt-4"
    OPENAI_GPT_35_TURBO = "gpt-3.5-turbo"
    
    # Claude Chat Models
    CLAUDE_3_5_SONNET = "claude-3-5-sonnet-20241022"
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"
    
    # Ollama Chat Models
    OLLAMA_LLAMA3 = "llama3"
    OLLAMA_LLAMA2 = "llama2"
    OLLAMA_MISTRAL = "mistral"
    OLLAMA_QWEN = "qwen"
    OLLAMA_GEMMA = "gemma"


# ==================== 嵌入模型枚举 ====================

class EmbeddingModel(str, enum.Enum):
    """嵌入模型 - 值匹配数据库中的枚举"""
    # 对应数据库中已存在的枚举值
    OPENAI_SMALL = "OPENAI_SMALL"
    OPENAI_LARGE = "OPENAI_LARGE"
    HUGGINGFACE_BGE = "HUGGINGFACE_BGE"


# ==================== 模型元数据 ====================

@dataclass
class ModelMetadata:
    """模型元数据"""
    id: str                          # 模型ID
    name: str                        # 显示名称
    provider: AIProvider             # 服务商
    model_type: ModelType           # 模型类型
    description: str                 # 描述
    context_length: Optional[int] = None    # 上下文长度
    dimensions: Optional[int] = None        # 嵌入维度（仅嵌入模型）
    max_tokens: Optional[int] = None        # 最大输出token（仅对话模型）
    supports_streaming: bool = True         # 是否支持流式输出
    is_available: bool = True               # 是否可用
    price_input: Optional[float] = None     # 输入价格（$/1M tokens）
    price_output: Optional[float] = None    # 输出价格（$/1M tokens）


# ==================== 模型注册表 ====================

# OpenAI 对话模型
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
    ChatModel.OPENAI_GPT_4O_MINI: ModelMetadata(
        id="gpt-4o-mini",
        name="GPT-4O Mini",
        provider=AIProvider.OPENAI,
        model_type=ModelType.CHAT,
        description="轻量级 GPT-4O，速度快成本低",
        context_length=128000,
        max_tokens=4096,
        supports_streaming=True,
        price_input=0.15,
        price_output=0.6,
    ),
    ChatModel.OPENAI_GPT_4_TURBO: ModelMetadata(
        id="gpt-4-turbo",
        name="GPT-4 Turbo",
        provider=AIProvider.OPENAI,
        model_type=ModelType.CHAT,
        description="GPT-4 Turbo 模型",
        context_length=128000,
        max_tokens=4096,
        supports_streaming=True,
        price_input=10.0,
        price_output=30.0,
    ),
    ChatModel.OPENAI_GPT_35_TURBO: ModelMetadata(
        id="gpt-3.5-turbo",
        name="GPT-3.5 Turbo",
        provider=AIProvider.OPENAI,
        model_type=ModelType.CHAT,
        description="经典的 GPT-3.5 模型",
        context_length=16385,
        max_tokens=4096,
        supports_streaming=True,
        price_input=0.5,
        price_output=1.5,
    ),
}

# Claude 对话模型
CLAUDE_CHAT_MODELS = {
    ChatModel.CLAUDE_3_5_SONNET: ModelMetadata(
        id="claude-3-5-sonnet-20241022",
        name="Claude 3.5 Sonnet",
        provider=AIProvider.CLAUDE,
        model_type=ModelType.CHAT,
        description="最新的 Claude 3.5 Sonnet，性能卓越",
        context_length=200000,
        max_tokens=8192,
        supports_streaming=True,
        price_input=3.0,
        price_output=15.0,
    ),
    ChatModel.CLAUDE_3_OPUS: ModelMetadata(
        id="claude-3-opus-20240229",
        name="Claude 3 Opus",
        provider=AIProvider.CLAUDE,
        model_type=ModelType.CHAT,
        description="Claude 3 最强大的模型",
        context_length=200000,
        max_tokens=4096,
        supports_streaming=True,
        price_input=15.0,
        price_output=75.0,
    ),
    ChatModel.CLAUDE_3_SONNET: ModelMetadata(
        id="claude-3-sonnet-20240229",
        name="Claude 3 Sonnet",
        provider=AIProvider.CLAUDE,
        model_type=ModelType.CHAT,
        description="Claude 3 平衡型模型",
        context_length=200000,
        max_tokens=4096,
        supports_streaming=True,
        price_input=3.0,
        price_output=15.0,
    ),
    ChatModel.CLAUDE_3_HAIKU: ModelMetadata(
        id="claude-3-haiku-20240307",
        name="Claude 3 Haiku",
        provider=AIProvider.CLAUDE,
        model_type=ModelType.CHAT,
        description="Claude 3 快速模型",
        context_length=200000,
        max_tokens=4096,
        supports_streaming=True,
        price_input=0.25,
        price_output=1.25,
    ),
}

# Ollama 对话模型
OLLAMA_CHAT_MODELS = {
    ChatModel.OLLAMA_LLAMA3: ModelMetadata(
        id="llama3",
        name="Llama 3",
        provider=AIProvider.OLLAMA,
        model_type=ModelType.CHAT,
        description="Meta 的 Llama 3 模型",
        context_length=8192,
        max_tokens=2048,
        supports_streaming=True,
        price_input=0.0,  # 本地运行免费
        price_output=0.0,
    ),
    ChatModel.OLLAMA_MISTRAL: ModelMetadata(
        id="mistral",
        name="Mistral",
        provider=AIProvider.OLLAMA,
        model_type=ModelType.CHAT,
        description="Mistral AI 模型",
        context_length=8192,
        max_tokens=2048,
        supports_streaming=True,
        price_input=0.0,
        price_output=0.0,
    ),
    ChatModel.OLLAMA_QWEN: ModelMetadata(
        id="qwen",
        name="Qwen (通义千问)",
        provider=AIProvider.OLLAMA,
        model_type=ModelType.CHAT,
        description="阿里巴巴的通义千问模型",
        context_length=8192,
        max_tokens=2048,
        supports_streaming=True,
        price_input=0.0,
        price_output=0.0,
    ),
}

# OpenAI 嵌入模型
OPENAI_EMBEDDING_MODELS = {
    EmbeddingModel.OPENAI_SMALL: ModelMetadata(
        id="OPENAI_SMALL",
        name="OpenAI Small (text-embedding-3-small)",
        provider=AIProvider.OPENAI,
        model_type=ModelType.EMBEDDING,
        description="最新的小型嵌入模型，性能优秀",
        dimensions=1536,
        price_input=0.02,
    ),
    EmbeddingModel.OPENAI_LARGE: ModelMetadata(
        id="OPENAI_LARGE",
        name="OpenAI Large (text-embedding-3-large)",
        provider=AIProvider.OPENAI,
        model_type=ModelType.EMBEDDING,
        description="最新的大型嵌入模型，性能最佳",
        dimensions=3072,
        price_input=0.13,
    ),
}

# HuggingFace 嵌入模型  
HUGGINGFACE_EMBEDDING_MODELS = {
    EmbeddingModel.HUGGINGFACE_BGE: ModelMetadata(
        id="HUGGINGFACE_BGE",
        name="HuggingFace BGE",
        provider=AIProvider.OLLAMA,
        model_type=ModelType.EMBEDDING,
        description="BGE 嵌入模型（开源）",
        dimensions=768,
        price_input=0.0,
    ),
}

# Claude 和 Ollama 暂时没有对应的数据库枚举值
CLAUDE_EMBEDDING_MODELS = {}
OLLAMA_EMBEDDING_MODELS = {}


# ==================== 服务商模型映射 ====================

PROVIDER_CHAT_MODELS: Dict[AIProvider, Dict[ChatModel, ModelMetadata]] = {
    AIProvider.OPENAI: OPENAI_CHAT_MODELS,
    AIProvider.CLAUDE: CLAUDE_CHAT_MODELS,
    AIProvider.OLLAMA: OLLAMA_CHAT_MODELS,
}

PROVIDER_EMBEDDING_MODELS: Dict[AIProvider, Dict[EmbeddingModel, ModelMetadata]] = {
    AIProvider.OPENAI: OPENAI_EMBEDDING_MODELS,
    AIProvider.CLAUDE: CLAUDE_EMBEDDING_MODELS,
    AIProvider.OLLAMA: {**OLLAMA_EMBEDDING_MODELS, **HUGGINGFACE_EMBEDDING_MODELS},
}


# ==================== 工具函数 ====================

def get_chat_model_metadata(model: ChatModel) -> Optional[ModelMetadata]:
    """获取对话模型元数据"""
    for provider_models in PROVIDER_CHAT_MODELS.values():
        if model in provider_models:
            return provider_models[model]
    return None


def get_embedding_model_metadata(model: EmbeddingModel) -> Optional[ModelMetadata]:
    """获取嵌入模型元数据"""
    for provider_models in PROVIDER_EMBEDDING_MODELS.values():
        if model in provider_models:
            return provider_models[model]
    return None


def get_provider_chat_models(provider: AIProvider) -> List[ModelMetadata]:
    """获取指定服务商的所有对话模型"""
    return list(PROVIDER_CHAT_MODELS.get(provider, {}).values())


def get_provider_embedding_models(provider: AIProvider) -> List[ModelMetadata]:
    """获取指定服务商的所有嵌入模型"""
    return list(PROVIDER_EMBEDDING_MODELS.get(provider, {}).values())


def get_all_chat_models() -> List[ModelMetadata]:
    """获取所有对话模型"""
    models = []
    for provider_models in PROVIDER_CHAT_MODELS.values():
        models.extend(provider_models.values())
    return models


def get_all_embedding_models() -> List[ModelMetadata]:
    """获取所有嵌入模型"""
    models = []
    for provider_models in PROVIDER_EMBEDDING_MODELS.values():
        models.extend(provider_models.values())
    return models


def get_model_provider(model: ChatModel | EmbeddingModel) -> Optional[AIProvider]:
    """根据模型获取对应的服务商"""
    # 检查对话模型
    for provider, models in PROVIDER_CHAT_MODELS.items():
        if model in models:
            return provider
    # 检查嵌入模型
    for provider, models in PROVIDER_EMBEDDING_MODELS.items():
        if model in models:
            return provider
    return None


def is_model_available(model: ChatModel | EmbeddingModel) -> bool:
    """检查模型是否可用"""
    metadata = get_chat_model_metadata(model) if isinstance(model, ChatModel) else get_embedding_model_metadata(model)
    return metadata.is_available if metadata else False


# ==================== 向后兼容 ====================

# 为了向后兼容旧代码，保留这些别名
EmbeddingProvider = AIProvider
MODEL_DIMENSIONS = {model: meta.dimensions for model, meta in 
                    {**OPENAI_EMBEDDING_MODELS, **HUGGINGFACE_EMBEDDING_MODELS}.items()}

