"""
商品向量化和召回服务
使用 LangChain Elasticsearch 作为向量存储后端
"""
import json
import time
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from langchain_elasticsearch import ElasticsearchStore
from langchain_core.documents import Document
from elasticsearch import AsyncElasticsearch

from app.core.logger import get_logger
from app.core.config import settings
from app.ai.embeddings import EmbeddingService
from app.ai.models import EmbeddingModel
from .models import Product
from .schemas import (
    ProductCreate,
    SearchResult,
    SearchResponse,
    StatsResponse,
    IndexInfo,
    IndexListResponse
)

logger = get_logger(__name__)

# ES索引名称
PRODUCT_INDEX_NAME = "product_rag_test"
# 使用的embedding模型
EMBEDDING_MODEL = EmbeddingModel.OPENAI_SMALL
# 向量维度
EMBEDDING_DIMENSION = 1536


class ProductRAGService:
    """商品RAG服务 - 使用 LangChain ElasticsearchStore 进行向量存储和搜索"""
    
    def __init__(self, index_name: Optional[str] = None):
        """初始化服务 - 使用 LangChain Elasticsearch 作为向量存储"""
        self.index_name = index_name or PRODUCT_INDEX_NAME
        self.embedding_model = EMBEDDING_MODEL
        self.dimension = EMBEDDING_DIMENSION
        
        # 延迟初始化
        self._vector_store: Optional[ElasticsearchStore] = None
        self._embeddings = None
        self._es_client: Optional[AsyncElasticsearch] = None
    
    @property
    def embeddings(self):
        """延迟获取 Embedding 实例"""
        if self._embeddings is None:
            self._embeddings = EmbeddingService.get_embeddings(self.embedding_model)
        return self._embeddings
    
    @property
    def vector_store(self) -> ElasticsearchStore:
        """延迟初始化 ElasticsearchStore"""
        if self._vector_store is None:
            logger.info(f"初始化 LangChain ElasticsearchStore (索引: {self.index_name})")
            
            # 构建 ES 连接参数
            es_params = {
                "es_url": settings.ELASTICSEARCH_URL,
                "index_name": self.index_name,
                "embedding": self.embeddings,
            }
            
            # 根据配置添加认证方式
            if settings.ELASTICSEARCH_API_KEY:
                es_params["es_api_key"] = settings.ELASTICSEARCH_API_KEY
                logger.info("使用 API Key 认证连接 Elasticsearch")
            elif hasattr(settings, 'ELASTICSEARCH_USERNAME') and settings.ELASTICSEARCH_USERNAME:
                es_params["es_user"] = settings.ELASTICSEARCH_USERNAME
                es_params["es_password"] = settings.ELASTICSEARCH_PASSWORD
                logger.info("使用用户名密码认证连接 Elasticsearch")
            else:
                logger.warning("未配置 Elasticsearch 认证信息，尝试无认证连接")
            
            try:
                self._vector_store = ElasticsearchStore(**es_params)
                logger.info("✅ ElasticsearchStore 初始化成功")
            except Exception as e:
                logger.error(f"❌ ElasticsearchStore 初始化失败: {e}")
                raise RuntimeError(
                    f"无法连接到 Elasticsearch。请检查：\n"
                    f"1. Elasticsearch 是否正在运行 ({settings.ELASTICSEARCH_URL})\n"
                    f"2. API Key 或用户名密码是否正确\n"
                    f"错误详情: {str(e)}"
                )
        
        return self._vector_store
    
    @staticmethod
    def _combine_product_text(product_data: Dict[str, Any]) -> str:
        """
        组合商品文本用于向量化
        
        Args:
            product_data: 商品数据字典
            
        Returns:
            组合后的文本
        """
        # 提取关键字段
        goods_name = product_data.get("goodsName", "")
        goods_alias = product_data.get("goodsAlias", "")
        brand_name = product_data.get("brandName", "")
        specifications = product_data.get("productSpecifications", "")
        search_keyword = product_data.get("searchKeyWord", "")
        
        # 组合文本，过滤空值
        parts = [
            goods_name,
            goods_alias,
            brand_name,
            specifications,
            search_keyword
        ]
        text = " ".join([p for p in parts if p])
        
        return text.strip()
    
    async def process_and_store_products(
        self,
        db: Session,
        products_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        处理并存储商品数据
        
        Args:
            db: 数据库会话
            products_data: 商品数据列表
            
        Returns:
            处理结果统计
        """
        start_time = time.time()
        
        try:
            # 1. 准备商品数据
            documents = []
            
            for product_data in products_data:
                product_id = product_data.get("id", product_data.get("goodsSaleId"))
                
                # 组合文本用于向量化
                text = self._combine_product_text(product_data)
                
                # 创建 LangChain Document 对象
                doc = Document(
                    page_content=text,
                    metadata={
                        "product_id": str(product_id),
                        "sell_spu_id": product_data.get("sellSpuId"),
                        "goods_name": product_data.get("goodsName"),
                        "goods_alias": product_data.get("goodsAlias"),
                        "brand_name": product_data.get("brandName"),
                        "specifications": product_data.get("productSpecifications"),
                        # 保存完整的原始数据以便展示
                        "original_data": json.dumps(product_data, ensure_ascii=False)
                    }
                )
                documents.append(doc)
            
            logger.info(f"准备处理 {len(documents)} 个商品")
            
            # 2. 使用 LangChain ElasticsearchStore 添加文档
            # LangChain 会自动处理向量化和存储
            logger.info("开始向量化并存储到 Elasticsearch...")
            doc_ids = self.vector_store.add_documents(
                documents=documents,
                ids=[doc.metadata["product_id"] for doc in documents]
            )
            logger.info(f"成功存储 {len(doc_ids)} 个文档到 Elasticsearch")
            
            elapsed_time = time.time() - start_time
            
            return {
                "success": True,
                "total": len(documents),
                "processed": len(documents),
                "elapsed_time_seconds": elapsed_time
            }
            
        except Exception as e:
            logger.error(f"处理商品数据失败: {e}")
            db.rollback()
            raise
    
    async def search_products(
        self,
        query: str,
        top_k: int = 1000
    ) -> SearchResponse:
        """
        搜索商品
        
        Args:
            query: 查询词
            top_k: 返回结果数量
            
        Returns:
            搜索响应
        """
        start_time = time.time()
        
        try:
            # 生成查询向量
            logger.info(f"搜索查询: {query}, top_k={top_k}")
            query_vector = self.embeddings.embed_query(query)
            
            # 获取 ES 客户端
            client = await self._get_es_client()
            
            # num_candidates 必须 >= k，设置为 max(k * 2, 100)
            num_candidates = max(top_k * 2, 1000)
            logger.info(f"使用 num_candidates={num_candidates}")
            
            # 构建 kNN 查询 - 使用 LangChain 默认的字段名 "vector"
            knn_query = {
                "field": "vector",
                "query_vector": query_vector,
                "k": top_k,
                "num_candidates": num_candidates
            }
            
            # 执行搜索
            response = await client.search(
                index=self.index_name,
                knn=knn_query,
                size=top_k,
                _source=["text", "metadata"]  # 只返回需要的字段
            )
            
            # 解析结果
            docs_with_scores = []
            for hit in response["hits"]["hits"]:
                source = hit["_source"]
                metadata = source.get("metadata", {})
                
                # 创建 Document 对象
                doc = Document(
                    page_content=source.get("text", ""),
                    metadata=metadata
                )
                score = hit["_score"]
                docs_with_scores.append((doc, score))
            
            # 构建结果
            results = []
            for rank, (doc, score) in enumerate(docs_with_scores, start=1):
                metadata = doc.metadata
                
                # 解析 original_data
                original_data = {}
                if "original_data" in metadata:
                    try:
                        if isinstance(metadata["original_data"], str):
                            original_data = json.loads(metadata["original_data"])
                        else:
                            original_data = metadata["original_data"]
                    except:
                        original_data = {}
                
                result = SearchResult(
                    rank=rank,
                    product_id=metadata.get("product_id", ""),
                    goods_name=metadata.get("goods_name", ""),
                    goods_alias=metadata.get("goods_alias"),
                    brand_name=metadata.get("brand_name"),
                    product_specifications=metadata.get("specifications"),
                    score=float(score),
                    content=doc.page_content,
                    original_data=original_data
                )
                results.append(result)
            
            elapsed_time = (time.time() - start_time) * 1000  # 转换为毫秒
            
            logger.info(f"搜索完成，返回 {len(results)} 个结果，耗时 {elapsed_time:.2f}ms")
            
            return SearchResponse(
                query=query,
                total=len(results),
                results=results,
                search_time_ms=elapsed_time
            )
            
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            raise
    
    async def batch_search_products(
        self,
        queries: List[str],
        top_k: int = 1000
    ) -> List[SearchResponse]:
        """
        批量搜索商品
        
        Args:
            queries: 查询词列表
            top_k: 每个查询返回的结果数量
            
        Returns:
            搜索响应列表
        """
        results = []
        
        for query in queries:
            response = await self.search_products(query=query, top_k=top_k)
            results.append(response)
        
        return results
    
    async def _get_es_client(self) -> AsyncElasticsearch:
        """获取 Elasticsearch 异步客户端"""
        if self._es_client is None:
            # 构建连接参数
            if settings.ELASTICSEARCH_API_KEY:
                self._es_client = AsyncElasticsearch(
                    settings.ELASTICSEARCH_URL,
                    api_key=settings.ELASTICSEARCH_API_KEY
                )
            elif hasattr(settings, 'ELASTICSEARCH_USERNAME') and settings.ELASTICSEARCH_USERNAME:
                self._es_client = AsyncElasticsearch(
                    settings.ELASTICSEARCH_URL,
                    basic_auth=(settings.ELASTICSEARCH_USERNAME, settings.ELASTICSEARCH_PASSWORD)
                )
            else:
                self._es_client = AsyncElasticsearch(
                    settings.ELASTICSEARCH_URL,
                    verify_certs=False
                )
        return self._es_client
    
    async def get_products_from_es(
        self,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        从ES获取商品列表（分页）
        
        Args:
            page: 页码（从1开始）
            page_size: 每页数量
            
        Returns:
            商品列表和分页信息
        """
        try:
            # 计算偏移量
            offset = (page - 1) * page_size
            
            # 获取 ES 客户端
            client = await self._get_es_client()
            
            # 获取总数
            count_response = await client.count(index=self.index_name)
            total = count_response.get('count', 0)
            
            # 获取文档 - Elasticsearch 8.x API方式
            search_response = await client.search(
                index=self.index_name,
                from_=offset,
                size=page_size,
                query={"match_all": {}}
                # 不使用_id排序，使用自然顺序
            )
            
            # 解析结果
            items = []
            hits = search_response.get('hits', {}).get('hits', [])
            for hit in hits:
                source = hit.get('_source', {})
                metadata = source.get('metadata', {})
                
                # 解析 original_data
                original_data = {}
                if "original_data" in metadata:
                    try:
                        if isinstance(metadata["original_data"], str):
                            original_data = json.loads(metadata["original_data"])
                        else:
                            original_data = metadata["original_data"]
                    except:
                        original_data = {}
                
                # 从metadata中提取商品信息
                item = {
                    'id': metadata.get('product_id', hit.get('_id')),
                    'goods_name': metadata.get('goods_name', ''),
                    'goods_alias': metadata.get('goods_alias'),
                    'brand_name': metadata.get('brand_name'),
                    'product_specifications': metadata.get('specifications'),
                    'sell_spu_id': metadata.get('sell_spu_id'),
                    'original_data': original_data,
                    'created_at': '2025-01-01T00:00:00'  # 默认创建时间
                }
                items.append(item)
            
            return {
                'total': total,
                'items': items,
                'page': page,
                'page_size': page_size
            }
            
        except Exception as e:
            logger.error(f"从ES获取商品列表失败: {e}")
            raise
    
    async def get_stats(self, db: Session) -> StatsResponse:
        """
        获取统计信息
        
        Args:
            db: 数据库会话
            
        Returns:
            统计信息
        """
        try:
            # 获取 ES 中的文档总数
            client = await self._get_es_client()
            count_response = await client.count(index=self.index_name)
            total_vectors = count_response.get('count', 0)
            
            return StatsResponse(
                total_products=total_vectors,  # 使用ES中的文档数作为商品总数
                total_vectors=total_vectors,
                index_name=self.index_name,
                embedding_model=self.embedding_model.value
            )
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            raise
    
    async def clear_all_data(self, db: Session) -> Dict[str, Any]:
        """
        清空所有数据（只清空Elasticsearch索引）
        
        Args:
            db: 数据库会话（此参数保留以保持接口兼容，但不使用）
            
        Returns:
            清空结果
        """
        try:
            deleted_count = 0
            
            # 删除ES索引
            client = await self._get_es_client()
            if await client.indices.exists(index=self.index_name):
                # 获取删除前的文档数
                count_response = await client.count(index=self.index_name)
                deleted_count = count_response.get('count', 0)
                
                await client.indices.delete(index=self.index_name)
                logger.info(f"删除了ES索引: {self.index_name}，共 {deleted_count} 个文档")
            else:
                logger.info(f"ES索引 {self.index_name} 不存在，无需删除")
            
            return {
                "success": True,
                "deleted_products": deleted_count,
                "deleted_vectors": True
            }
            
        except Exception as e:
            logger.error(f"清空数据失败: {e}")
            raise
    
    async def get_all_indices(self) -> IndexListResponse:
        """
        获取所有索引列表
        
        Returns:
            索引列表响应
        """
        try:
            client = await self._get_es_client()
            
            # 获取所有索引的统计信息
            # 使用cat API获取索引列表，包含健康状态、文档数、存储大小等信息
            cat_response = await client.cat.indices(
                format='json',
                h='index,docs.count,store.size,health,status,creation.date.string'
            )
            
            # 过滤出产品相关的索引（以product开头或包含向量数据的索引）
            indices = []
            for idx in cat_response:
                index_name = idx.get('index', '')
                
                # 跳过系统索引（以.开头）
                if index_name.startswith('.'):
                    continue
                
                index_info = IndexInfo(
                    name=index_name,
                    docs_count=int(idx.get('docs.count', '0') or 0),
                    store_size=idx.get('store.size', '0b'),
                    health=idx.get('health', 'unknown'),
                    status=idx.get('status', 'unknown'),
                    created_at=idx.get('creation.date.string')
                )
                indices.append(index_info)
            
            # 按文档数量排序（降序）
            indices.sort(key=lambda x: x.docs_count, reverse=True)
            
            return IndexListResponse(
                total=len(indices),
                indices=indices
            )
            
        except Exception as e:
            logger.error(f"获取索引列表失败: {e}")
            raise
    
    async def delete_index(self, index_name: str) -> Dict[str, Any]:
        """
        删除指定索引
        
        Args:
            index_name: 要删除的索引名称
            
        Returns:
            删除结果
        """
        try:
            client = await self._get_es_client()
            
            # 检查索引是否存在
            if not await client.indices.exists(index=index_name):
                raise ValueError(f"索引 {index_name} 不存在")
            
            # 获取删除前的文档数
            count_response = await client.count(index=index_name)
            deleted_count = count_response.get('count', 0)
            
            # 删除索引
            await client.indices.delete(index=index_name)
            logger.info(f"成功删除索引: {index_name}，共 {deleted_count} 个文档")
            
            return {
                "success": True,
                "index_name": index_name,
                "deleted_count": deleted_count
            }
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"删除索引失败: {e}")
            raise

