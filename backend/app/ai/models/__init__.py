"""AI模型服务 - 包含各种AI提供商的服务和统一的模型注册中心"""
from .ai_provider import AIProvider as _OldAIProvider  # 保留旧的用于服务
from .ai_manager import AIManager, ai_manager
from .openai_service import OpenAIService
from .claude_service import ClaudeService
from .ollama_service import OllamaService

# 从模型注册中心导入统一的模型定义
from .model_registry import (
    # 枚举类型
    AIProvider,
    ModelType,
    ChatModel,
    EmbeddingModel,
    EmbeddingProvider,  # 向后兼容别名
    
    # 模型注册表
    PROVIDER_CHAT_MODELS,
    PROVIDER_EMBEDDING_MODELS,
    MODEL_DIMENSIONS,
    
    # 元数据类
    ModelMetadata,
    
    # 工具函数
    get_chat_model_metadata,
    get_embedding_model_metadata,
    get_provider_chat_models,
    get_provider_embedding_models,
    get_all_chat_models,
    get_all_embedding_models,
    get_model_provider,
    is_model_available,
)

__all__ = [
    # 服务类
    "AIManager",
    "ai_manager",
    "OpenAIService",
    "ClaudeService",
    "OllamaService",
    
    # 枚举类型
    "AIProvider",
    "ModelType",
    "ChatModel",
    "EmbeddingModel",
    "EmbeddingProvider",  # 向后兼容
    
    # 模型注册表
    "PROVIDER_CHAT_MODELS",
    "PROVIDER_EMBEDDING_MODELS",
    "MODEL_DIMENSIONS",
    
    # 元数据类
    "ModelMetadata",
    
    # 工具函数
    "get_chat_model_metadata",
    "get_embedding_model_metadata",
    "get_provider_chat_models",
    "get_provider_embedding_models",
    "get_all_chat_models",
    "get_all_embedding_models",
    "get_model_provider",
    "is_model_available",
]

