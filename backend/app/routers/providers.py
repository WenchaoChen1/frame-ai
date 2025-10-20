from fastapi import APIRouter, Query
from typing import Optional
from ..ai.models.ai_manager import ai_manager
from ..ai.models import (
    AIProvider,
    EmbeddingModel,
    ChatModel,
    get_provider_chat_models,
    get_provider_embedding_models,
    get_all_embedding_models,
)

router = APIRouter(prefix="/api/providers", tags=["AI提供商"])


@router.get("")
def get_providers():
    """获取所有可用的AI提供商和对话模型"""
    providers = ai_manager.get_available_providers()
    
    # 按优先级排序：openai > claude > ollama
    priority_order = ["openai", "claude", "ollama"]
    sorted_providers = []
    
    # 先添加优先级列表中的提供商
    for priority_name in priority_order:
        if priority_name in providers:
            sorted_providers.append({
                "name": priority_name,
                "models": providers[priority_name]
            })
    
    # 添加其他提供商
    for name, models in providers.items():
        if name not in priority_order:
            sorted_providers.append({
                "name": name,
                "models": models
            })
    
    return {
        "providers": sorted_providers
    }


@router.get("/embeddings")
def get_embedding_providers(provider: Optional[str] = Query(None, description="筛选特定提供商")):
    """获取嵌入模型提供商和可用模型（从统一模型注册中心读取）"""
    
    # 服务商名称映射
    provider_names = {
        AIProvider.OPENAI: "OpenAI",
        AIProvider.CLAUDE: "Claude (Anthropic)",
        AIProvider.OLLAMA: "Ollama (本地模型)",
    }
    
    # 如果指定了 provider，只返回该提供商
    if provider:
        try:
            provider_enum = AIProvider(provider)
            models_metadata = get_provider_embedding_models(provider_enum)
            
            return {
                "provider": {
                    "id": provider_enum.value,
                    "name": provider_names.get(provider_enum, provider_enum.value),
                    "models": [
                        {
                            "id": meta.id,
                            "name": meta.name,
                            "description": meta.description,
                            "dimensions": meta.dimensions,
                            "is_available": meta.is_available,
                        }
                        for meta in models_metadata
                    ]
                }
            }
        except ValueError:
            return {"error": f"未知的服务商: {provider}"}
    
    # 返回所有提供商
    all_providers = []
    for provider_enum in AIProvider:
        models_metadata = get_provider_embedding_models(provider_enum)
        all_providers.append({
            "id": provider_enum.value,
            "name": provider_names.get(provider_enum, provider_enum.value),
            "models": [
                {
                    "id": meta.id,
                    "name": meta.name,
                    "description": meta.description,
                    "dimensions": meta.dimensions,
                    "is_available": meta.is_available,
                }
                for meta in models_metadata
            ]
        })
    
    return {
        "providers": all_providers
    }


@router.get("/vector-stores")
def get_vector_store_configs():
    """获取可用的外部向量存储配置（如 Elasticsearch）"""
    
    # 这里可以从数据库或配置文件读取已配置的 ES 连接
    # 暂时返回示例配置
    vector_stores = [
        {
            "id": 1,
            "name": "本地 Elasticsearch",
            "type": "elasticsearch",
            "url": "http://localhost:9200",
            "status": "active"
        },
        {
            "id": 2,
            "name": "云端 Elasticsearch",
            "type": "elasticsearch",
            "url": "https://elastic.example.com",
            "status": "active"
        }
    ]
    
    return {
        "vector_stores": vector_stores
    }

