"""
PostgreSQL + pgvector 向量存储实现
"""
from typing import List, Dict, Any, Optional
from sqlalchemy import select, delete as sql_delete, func, text
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.core.database import Base, engine
from app.models.knowledge_base import KnowledgeBaseChunk
from app.core.logger import get_logger
from .base import VectorStoreBase, Document

logger = get_logger(__name__)


class PGVectorStore(VectorStoreBase):
    """PostgreSQL + pgvector 向量存储"""
    
    def __init__(self, knowledge_base_id: int):
        """
        初始化
        
        Args:
            knowledge_base_id: 知识库 ID
        """
        self.knowledge_base_id = knowledge_base_id
    
    async def add_documents(
        self,
        documents: List[Document],
        embeddings: List[List[float]]
    ) -> List[str]:
        """
        添加文档和向量到数据库
        
        Args:
            documents: 文档列表
            embeddings: 嵌入向量列表
            
        Returns:
            文档 ID 列表
        """
        if len(documents) != len(embeddings):
            raise ValueError("文档数量和向量数量不匹配")
        
        try:
            from sqlalchemy.orm import Session
            with Session(engine) as session:
                chunk_ids = []
                
                for doc, embedding in zip(documents, embeddings):
                    # 创建文档块
                    chunk = KnowledgeBaseChunk(
                        document_id=doc.metadata.get("document_id"),
                        content=doc.content,
                        chunk_index=doc.metadata.get("chunk_index", 0),
                        embedding=embedding,
                        meta_data=json.dumps(doc.metadata, ensure_ascii=False)
                    )
                    session.add(chunk)
                    session.flush()
                    chunk_ids.append(str(chunk.id))
                
                session.commit()
                logger.info(f"成功添加 {len(chunk_ids)} 个文档块到 pgvector")
                return chunk_ids
                
        except Exception as e:
            logger.error(f"添加文档到 pgvector 失败: {e}")
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
            filter_dict: 过滤条件（如 document_id）
            
        Returns:
            相似文档列表
        """
        try:
            from sqlalchemy.orm import Session
            with Session(engine) as session:
                # 构建查询
                # 使用余弦距离进行相似度搜索（1 - cosine_distance = cosine_similarity）
                query = select(
                    KnowledgeBaseChunk,
                    (1 - KnowledgeBaseChunk.embedding.cosine_distance(query_embedding)).label("score")
                ).join(
                    KnowledgeBaseChunk.document
                ).filter(
                    KnowledgeBaseChunk.document.has(knowledge_base_id=self.knowledge_base_id)
                )
                
                # 应用过滤条件
                if filter_dict:
                    if "document_id" in filter_dict:
                        query = query.filter(KnowledgeBaseChunk.document_id == filter_dict["document_id"])
                
                # 排序和限制
                query = query.order_by(text("score DESC")).limit(top_k)
                
                results = session.execute(query).all()
                
                documents = []
                for chunk, score in results:
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
                    documents.append(doc)
                
                logger.info(f"pgvector 相似度搜索返回 {len(documents)} 个结果")
                return documents
                
        except Exception as e:
            logger.error(f"pgvector 相似度搜索失败: {e}")
            raise
    
    async def delete_documents(self, document_ids: List[str]) -> bool:
        """
        删除文档
        
        Args:
            document_ids: 文档 ID 列表（这里是 chunk_id）
            
        Returns:
            是否成功
        """
        try:
            from sqlalchemy.orm import Session
            with Session(engine) as session:
                chunk_ids = [int(doc_id) for doc_id in document_ids]
                session.execute(
                    sql_delete(KnowledgeBaseChunk).where(
                        KnowledgeBaseChunk.id.in_(chunk_ids)
                    )
                )
                session.commit()
                logger.info(f"成功删除 {len(document_ids)} 个文档块")
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
            from sqlalchemy.orm import Session
            with Session(engine) as session:
                count = session.query(func.count(KnowledgeBaseChunk.id)).join(
                    KnowledgeBaseChunk.document
                ).filter(
                    KnowledgeBaseChunk.document.has(knowledge_base_id=self.knowledge_base_id)
                ).scalar()
                
                return count or 0
                
        except Exception as e:
            logger.error(f"获取文档数量失败: {e}")
            return 0

