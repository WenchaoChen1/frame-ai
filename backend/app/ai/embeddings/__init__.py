"""
嵌入服务模块
提供统一的嵌入模型访问接口
"""
from .embedding_service import EmbeddingService, embed_documents, embed_query

__all__ = [
    "EmbeddingService",
    "embed_documents",
    "embed_query",
]

