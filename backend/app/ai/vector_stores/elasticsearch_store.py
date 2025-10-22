"""
Elasticsearch 向量存储实现
"""
from typing import List, Dict, Any, Optional
from elasticsearch import AsyncElasticsearch
import json

from app.core.config import settings
from app.core.logger import get_logger
from .base import VectorStoreBase, Document

logger = get_logger(__name__)


class ElasticsearchStore(VectorStoreBase):
    """Elasticsearch 向量存储"""
    
    def __init__(self, index_name: str, dimension: int = 1536):
        """
        初始化
        
        Args:
            index_name: 索引名称
            dimension: 向量维度
        """
        self.index_name = index_name
        self.dimension = dimension
        self._client: Optional[AsyncElasticsearch] = None
    
    async def _get_client(self) -> AsyncElasticsearch:
        """获取 ES 客户端"""
        if self._client is None:
            # 优先使用 API Key
            if settings.ELASTICSEARCH_API_KEY:
                self._client = AsyncElasticsearch(
                    settings.ELASTICSEARCH_URL,
                    api_key=settings.ELASTICSEARCH_API_KEY
                )
            # 检查是否有用户名密码认证
            elif hasattr(settings, 'ELASTICSEARCH_USERNAME') and settings.ELASTICSEARCH_USERNAME:
                self._client = AsyncElasticsearch(
                    settings.ELASTICSEARCH_URL,
                    basic_auth=(settings.ELASTICSEARCH_USERNAME, settings.ELASTICSEARCH_PASSWORD)
                )
            else:
                # 尝试无认证连接
                self._client = AsyncElasticsearch(
                    settings.ELASTICSEARCH_URL,
                    verify_certs=False  # 开发环境可以禁用证书验证
                )
        return self._client
    
    async def _ensure_index(self):
        """确保索引存在，如果不存在则创建"""
        client = await self._get_client()
        
        try:
            # 检查索引是否存在
            exists = await client.indices.exists(index=self.index_name)
            
            if not exists:
                logger.info(f"创建 Elasticsearch 索引: {self.index_name}")
                
                # 定义索引 mapping
                mappings = {
                    "properties": {
                        "content": {
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "embedding": {
                            "type": "dense_vector",
                            "dims": self.dimension,
                            "index": True,
                            "similarity": "cosine"
                        },
                        "metadata": {
                            "type": "object",
                            "enabled": True
                        },
                        "document_id": {
                            "type": "integer"
                        },
                        "chunk_index": {
                            "type": "integer"
                        },
                        "created_at": {
                            "type": "date"
                        }
                    }
                }
                
                settings = {
                    "number_of_shards": 1,
                    "number_of_replicas": 0
                }
                
                # Elasticsearch 8.x 使用新的API方式（不使用body参数）
                await client.indices.create(
                    index=self.index_name,
                    mappings=mappings,
                    settings=settings
                )
                logger.info(f"索引 {self.index_name} 创建成功")
        except Exception as e:
            logger.error(f"确保索引存在失败: {e}")
            raise
    
    async def add_documents(
        self,
        documents: List[Document],
        embeddings: List[List[float]]
    ) -> List[str]:
        """
        添加文档和向量到 Elasticsearch
        
        Args:
            documents: 文档列表
            embeddings: 嵌入向量列表
            
        Returns:
            文档 ID 列表
        """
        if len(documents) != len(embeddings):
            raise ValueError("文档数量和向量数量不匹配")
        
        try:
            await self._ensure_index()
            client = await self._get_client()
            
            # 批量索引
            operations = []
            doc_ids = []
            
            for doc, embedding in zip(documents, embeddings):
                doc_id = doc.id or doc.metadata.get("chunk_id")
                
                # 索引操作
                operations.append({"index": {"_index": self.index_name, "_id": doc_id}})
                
                # 文档数据
                doc_data = {
                    "content": doc.content,
                    "embedding": embedding,
                    "metadata": doc.metadata,
                    "document_id": doc.metadata.get("document_id"),
                    "chunk_index": doc.metadata.get("chunk_index", 0)
                }
                operations.append(doc_data)
                doc_ids.append(str(doc_id))
            
            # 执行批量索引
            response = await client.bulk(operations=operations, refresh=True)
            
            if response.get("errors"):
                logger.error(f"批量索引出现错误: {response}")
            
            logger.info(f"成功添加 {len(doc_ids)} 个文档到 Elasticsearch")
            return doc_ids
            
        except Exception as e:
            logger.error(f"添加文档到 Elasticsearch 失败: {e}")
            raise
    
    async def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        向量相似度搜索
        
        Args:
            query_embedding: 查询向量
            top_k: 返回结果数量
            filter_dict: 过滤条件
            
        Returns:
            相似文档列表
        """
        try:
            await self._ensure_index()
            client = await self._get_client()
            
            # 构建KNN查询
            knn = {
                "field": "embedding",
                "query_vector": query_embedding,
                "k": top_k,
                "num_candidates": top_k * 2
            }
            
            # 添加过滤条件
            if filter_dict:
                filters = []
                for key, value in filter_dict.items():
                    filters.append({"term": {key: value}})
                
                if filters:
                    knn["filter"] = filters if len(filters) > 1 else filters[0]
            
            # 执行搜索 - Elasticsearch 8.x API方式
            response = await client.search(
                index=self.index_name,
                knn=knn,
                size=top_k
            )
            
            # 解析结果
            documents = []
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                doc = Document(
                    id=hit["_id"],
                    content=source["content"],
                    metadata=source.get("metadata", {}),
                    score=hit["_score"]
                )
                documents.append(doc)
            
            logger.info(f"Elasticsearch 相似度搜索返回 {len(documents)} 个结果")
            return documents
            
        except Exception as e:
            logger.error(f"Elasticsearch 相似度搜索失败: {e}")
            raise
    
    async def delete_documents(self, document_ids: List[str]) -> bool:
        """
        删除文档
        
        Args:
            document_ids: 文档 ID 列表
            
        Returns:
            是否成功
        """
        try:
            client = await self._get_client()
            
            # 批量删除
            operations = []
            for doc_id in document_ids:
                operations.append({"delete": {"_index": self.index_name, "_id": doc_id}})
            
            response = await client.bulk(operations=operations, refresh=True)
            
            if response.get("errors"):
                logger.error(f"批量删除出现错误: {response}")
                return False
            
            logger.info(f"成功删除 {len(document_ids)} 个文档")
            return True
            
        except Exception as e:
            logger.error(f"删除文档失败: {e}")
            return False
    
    async def get_document_count(self) -> int:
        """
        获取文档数量
        
        Returns:
            文档数量
        """
        try:
            client = await self._get_client()
            
            response = await client.count(index=self.index_name)
            count = response.get("count", 0)
            
            return count
            
        except Exception as e:
            logger.error(f"获取文档数量失败: {e}")
            return 0
    
    async def close(self):
        """关闭客户端连接"""
        if self._client:
            await self._client.close()

