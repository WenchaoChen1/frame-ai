"""
嵌入模型服务
支持多种嵌入模型：OpenAI、HuggingFace、Claude、Ollama
"""
from typing import List
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from ...core.config import settings
from ...core.logger import get_logger
from ..models import EmbeddingModel, get_embedding_model_metadata, AIProvider

logger = get_logger(__name__)


class EmbeddingService:
    """嵌入模型服务"""
    
    _embeddings_cache = {}
    
    @classmethod
    def get_embeddings(cls, model: EmbeddingModel):
        """
        获取嵌入模型实例（使用缓存）
        
        Args:
            model: 嵌入模型类型
            
        Returns:
            嵌入模型实例
        """
        if model in cls._embeddings_cache:
            return cls._embeddings_cache[model]
        
        embeddings = cls._create_embeddings(model)
        cls._embeddings_cache[model] = embeddings
        return embeddings
    
    @classmethod
    def _create_embeddings(cls, model: EmbeddingModel):
        """
        创建嵌入模型实例（使用模型注册中心元数据）
        
        Args:
            model: 嵌入模型类型
            
        Returns:
            嵌入模型实例
        """
        # 从注册中心获取模型元数据
        metadata = get_embedding_model_metadata(model)
        if not metadata:
            raise ValueError(f"未知的嵌入模型: {model}")
        
        if not metadata.is_available:
            raise ValueError(f"嵌入模型 {model.value} 暂不可用")
        
        logger.info(f"创建嵌入模型: {metadata.name} (Provider: {metadata.provider.value})")
        
        # 映射数据库枚举值到实际的模型 ID
        model_id_map = {
            EmbeddingModel.OPENAI_SMALL: "text-embedding-3-small",
            EmbeddingModel.OPENAI_LARGE: "text-embedding-3-large",
            EmbeddingModel.HUGGINGFACE_BGE: "BAAI/bge-large-zh-v1.5",
        }
        
        # 根据服务商创建对应的嵌入实例
        if metadata.provider == AIProvider.OPENAI:
            openai_model_id = model_id_map.get(model, "text-embedding-3-small")
            return OpenAIEmbeddings(
                model=openai_model_id,
                api_key=settings.OPENAI_API_KEY
            )
        
        elif metadata.provider == AIProvider.OLLAMA:
            # HuggingFace 模型实现
            hf_model_name = model_id_map.get(model, "BAAI/bge-large-zh-v1.5")
            return HuggingFaceEmbeddings(
                model_name=hf_model_name,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        
        elif metadata.provider == AIProvider.CLAUDE:
            # Claude 暂不支持嵌入，使用 OpenAI 替代
            logger.warning(f"Claude 嵌入模型暂不支持，使用 OpenAI text-embedding-3-small 替代")
            return OpenAIEmbeddings(
                model="text-embedding-3-small",
                api_key=settings.OPENAI_API_KEY
            )
        
        else:
            raise ValueError(f"不支持的服务商: {metadata.provider}")
    
    @classmethod
    def get_embedding_dimension(cls, model: EmbeddingModel) -> int:
        """
        获取嵌入维度（从模型注册中心读取）
        
        Args:
            model: 嵌入模型类型
            
        Returns:
            维度大小
        """
        metadata = get_embedding_model_metadata(model)
        return metadata.dimensions if metadata else 1536
    
    @classmethod
    async def embed_documents(cls, texts: List[str], model: EmbeddingModel) -> List[List[float]]:
        """
        批量生成文档嵌入
        
        Args:
            texts: 文本列表
            model: 嵌入模型类型
            
        Returns:
            嵌入向量列表
        """
        if not texts:
            return []
        
        try:
            embeddings = cls.get_embeddings(model)
            logger.info(f"生成 {len(texts)} 个文档的嵌入向量")
            vectors = await embeddings.aembed_documents(texts)
            return vectors
        except Exception as e:
            logger.error(f"生成文档嵌入失败: {e}")
            raise
    
    @classmethod
    async def embed_query(cls, text: str, model: EmbeddingModel) -> List[float]:
        """
        生成查询嵌入
        
        Args:
            text: 查询文本
            model: 嵌入模型类型
            
        Returns:
            嵌入向量
        """
        try:
            embeddings = cls.get_embeddings(model)
            logger.info(f"生成查询嵌入向量: {text[:50]}...")
            vector = await embeddings.aembed_query(text)
            return vector
        except Exception as e:
            logger.error(f"生成查询嵌入失败: {e}")
            raise


# 便捷函数
async def embed_documents(
    texts: List[str], 
    model: EmbeddingModel = EmbeddingModel.OPENAI_SMALL
) -> List[List[float]]:
    """生成文档嵌入向量"""
    return await EmbeddingService.embed_documents(texts, model)


async def embed_query(
    text: str, 
    model: EmbeddingModel = EmbeddingModel.OPENAI_SMALL
) -> List[float]:
    """生成查询嵌入向量"""
    return await EmbeddingService.embed_query(text, model)

