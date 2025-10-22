"""
检索服务
支持语义检索、BM25 关键词检索、混合检索
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from rank_bm25 import BM25Okapi
import jieba

from app.models.knowledge_base import KnowledgeBase, KnowledgeBaseChunk, VectorStoreType
from app.core.logger import get_logger
from app.core.config import settings
from app.ai.vector_stores import PGVectorStore, ElasticsearchStore, Document
from app.ai.embeddings import EmbeddingService

logger = get_logger(__name__)


class RetrievalService:
    """检索服务"""
    
    @staticmethod
    async def semantic_search(
        knowledge_base: KnowledgeBase,
        query: str,
        top_k: int = None,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        语义检索（向量相似度搜索）
        
        Args:
            knowledge_base: 知识库对象
            query: 查询文本
            top_k: 返回结果数量
            filter_dict: 过滤条件
            
        Returns:
            文档列表
        """
        top_k = top_k or settings.TOP_K_RETRIEVAL
        
        try:
            # 1. 生成查询向量
            query_embedding = await EmbeddingService.embed_query(
                text=query,
                model=knowledge_base.embedding_model
            )
            
            # 2. 向量搜索
            if knowledge_base.vector_store_type == VectorStoreType.PGVECTOR:
                store = PGVectorStore(knowledge_base_id=knowledge_base.id)
                results = await store.similarity_search(
                    query_embedding=query_embedding,
                    top_k=top_k,
                    filter_dict=filter_dict
                )
                
            elif knowledge_base.vector_store_type == VectorStoreType.ELASTICSEARCH:
                index_name = knowledge_base.es_index_name
                dimension = EmbeddingService.get_embedding_dimension(knowledge_base.embedding_model)
                store = ElasticsearchStore(index_name=index_name, dimension=dimension)
                results = await store.similarity_search(
                    query_embedding=query_embedding,
                    top_k=top_k,
                    filter_dict=filter_dict
                )
            else:
                raise ValueError(f"不支持的向量存储类型: {knowledge_base.vector_store_type}")
            
            logger.info(f"语义检索返回 {len(results)} 个结果")
            return results
            
        except Exception as e:
            logger.error(f"语义检索失败: {e}")
            raise
    
    @staticmethod
    def bm25_search(
        db: Session,
        knowledge_base: KnowledgeBase,
        query: str,
        top_k: int = None
    ) -> List[Document]:
        """
        BM25 关键词检索
        
        Args:
            db: 数据库会话
            knowledge_base: 知识库对象
            query: 查询文本
            top_k: 返回结果数量
            
        Returns:
            文档列表
        """
        top_k = top_k or settings.TOP_K_RETRIEVAL
        
        try:
            # 1. 获取所有文档块
            chunks = db.query(KnowledgeBaseChunk).join(
                KnowledgeBaseChunk.document
            ).filter(
                KnowledgeBaseChunk.document.has(knowledge_base_id=knowledge_base.id)
            ).all()
            
            if not chunks:
                logger.warning(f"知识库 {knowledge_base.id} 没有文档块")
                return []
            
            # 2. 分词
            tokenized_corpus = [list(jieba.cut(chunk.content)) for chunk in chunks]
            tokenized_query = list(jieba.cut(query))
            
            # 3. BM25 检索
            bm25 = BM25Okapi(tokenized_corpus)
            scores = bm25.get_scores(tokenized_query)
            
            # 4. 排序并获取 top_k
            top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
            
            # 5. 构建结果
            results = []
            for idx in top_indices:
                chunk = chunks[idx]
                score = scores[idx]
                
                import json
                metadata = json.loads(chunk.meta_data) if chunk.meta_data else {}
                metadata.update({
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "chunk_index": chunk.chunk_index
                })
                
                doc = Document(
                    id=str(chunk.id),
                    content=chunk.content,
                    metadata=metadata,
                    score=float(score)
                )
                results.append(doc)
            
            logger.info(f"BM25 检索返回 {len(results)} 个结果")
            return results
            
        except Exception as e:
            logger.error(f"BM25 检索失败: {e}")
            raise
    
    @staticmethod
    async def hybrid_search(
        db: Session,
        knowledge_base: KnowledgeBase,
        query: str,
        top_k: int = None,
        semantic_weight: float = 0.7,
        bm25_weight: float = 0.3
    ) -> List[Document]:
        """
        混合检索（语义 + BM25）使用 RRF（Reciprocal Rank Fusion）
        
        Args:
            db: 数据库会话
            knowledge_base: 知识库对象
            query: 查询文本
            top_k: 返回结果数量
            semantic_weight: 语义检索权重
            bm25_weight: BM25 检索权重
            
        Returns:
            文档列表
        """
        top_k = top_k or settings.TOP_K_RETRIEVAL
        
        try:
            # 1. 并行执行两种检索
            semantic_results = await RetrievalService.semantic_search(
                knowledge_base=knowledge_base,
                query=query,
                top_k=top_k * 2  # 获取更多结果用于融合
            )
            
            bm25_results = RetrievalService.bm25_search(
                db=db,
                knowledge_base=knowledge_base,
                query=query,
                top_k=top_k * 2
            )
            
            # 2. RRF 融合（Reciprocal Rank Fusion）
            # RRF 公式: score(d) = sum(1 / (k + rank(d)))
            k = 60  # RRF 常数
            doc_scores = {}
            
            # 语义检索结果
            for rank, doc in enumerate(semantic_results, start=1):
                doc_id = doc.id
                rrf_score = semantic_weight / (k + rank)
                doc_scores[doc_id] = doc_scores.get(doc_id, 0) + rrf_score
            
            # BM25 检索结果
            for rank, doc in enumerate(bm25_results, start=1):
                doc_id = doc.id
                rrf_score = bm25_weight / (k + rank)
                doc_scores[doc_id] = doc_scores.get(doc_id, 0) + rrf_score
            
            # 3. 按分数排序
            sorted_doc_ids = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
            
            # 4. 构建最终结果
            all_docs = {doc.id: doc for doc in semantic_results + bm25_results}
            results = []
            
            for doc_id, score in sorted_doc_ids:
                if doc_id in all_docs:
                    doc = all_docs[doc_id]
                    doc.score = score
                    results.append(doc)
            
            logger.info(f"混合检索返回 {len(results)} 个结果")
            return results
            
        except Exception as e:
            logger.error(f"混合检索失败: {e}")
            # 降级到语义检索
            logger.warning("混合检索失败，降级到语义检索")
            return await RetrievalService.semantic_search(
                knowledge_base=knowledge_base,
                query=query,
                top_k=top_k
            )
    
    @staticmethod
    async def search_multiple_knowledge_bases(
        db: Session,
        knowledge_base_ids: List[int],
        query: str,
        top_k: int = None,
        use_hybrid: bool = True
    ) -> List[Document]:
        """
        在多个知识库中检索
        
        Args:
            db: 数据库会话
            knowledge_base_ids: 知识库 ID 列表
            query: 查询文本
            top_k: 每个知识库返回的结果数量
            use_hybrid: 是否使用混合检索
            
        Returns:
            文档列表
        """
        top_k = top_k or settings.TOP_K_RETRIEVAL
        all_results = []
        
        try:
            for kb_id in knowledge_base_ids:
                kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
                if not kb:
                    logger.warning(f"知识库 {kb_id} 不存在")
                    continue
                
                if use_hybrid:
                    results = await RetrievalService.hybrid_search(
                        db=db,
                        knowledge_base=kb,
                        query=query,
                        top_k=top_k
                    )
                else:
                    results = await RetrievalService.semantic_search(
                        knowledge_base=kb,
                        query=query,
                        top_k=top_k
                    )
                
                # 添加知识库信息到元数据
                for doc in results:
                    doc.metadata["knowledge_base_id"] = kb_id
                    doc.metadata["knowledge_base_name"] = kb.name
                
                all_results.extend(results)
            
            # 按分数排序
            all_results.sort(key=lambda x: x.score or 0, reverse=True)
            
            # 限制总结果数量
            all_results = all_results[:top_k * len(knowledge_base_ids)]
            
            logger.info(f"在 {len(knowledge_base_ids)} 个知识库中检索，返回 {len(all_results)} 个结果")
            return all_results
            
        except Exception as e:
            logger.error(f"多知识库检索失败: {e}")
            raise

