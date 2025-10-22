"""
商品 RAG 的 PGVector 存储实现
"""
from typing import List, Dict, Any
from sqlalchemy import select, func, text
from sqlalchemy.orm import Session

from app.core.database import engine
from app.core.logger import get_logger
from app.ai.vector_stores.base import Document
from .models import Product

logger = get_logger(__name__)


class ProductPGVectorStore:
    """商品数据的 PostgreSQL + pgvector 向量存储"""
    
    def __init__(self, dimension: int = 1536):
        """
        初始化
        
        Args:
            dimension: 向量维度
        """
        self.dimension = dimension
    
    async def add_documents(
        self,
        documents: List[Document],
        embeddings: List[List[float]]
    ) -> List[str]:
        """
        添加商品文档和向量
        
        Args:
            documents: 文档列表（每个文档的 id 应该是商品ID）
            embeddings: 嵌入向量列表
            
        Returns:
            商品 ID 列表
        """
        if len(documents) != len(embeddings):
            raise ValueError("文档数量和向量数量不匹配")
        
        try:
            with Session(engine) as session:
                product_ids = []
                
                for doc, embedding in zip(documents, embeddings):
                    product_id = doc.id
                    
                    # 查找是否已存在
                    product = session.query(Product).filter(Product.id == product_id).first()
                    
                    if product:
                        # 更新向量
                        product.embedding = embedding
                        logger.debug(f"更新商品 {product_id} 的向量")
                    else:
                        # 创建新商品（这种情况不应该发生，因为商品应该先被创建）
                        logger.warning(f"商品 {product_id} 不存在，无法添加向量")
                        continue
                    
                    product_ids.append(product_id)
                
                session.commit()
                logger.info(f"成功添加/更新 {len(product_ids)} 个商品向量到 pgvector")
                return product_ids
                
        except Exception as e:
            logger.error(f"添加商品向量到 pgvector 失败: {e}")
            raise
    
    async def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int = 10
    ) -> List[Document]:
        """
        向量相似度搜索
        
        Args:
            query_embedding: 查询向量
            top_k: 返回结果数量
            
        Returns:
            相似文档列表
        """
        try:
            with Session(engine) as session:
                # 使用余弦距离进行相似度搜索
                # score = 1 - cosine_distance
                query = select(
                    Product,
                    (1 - Product.embedding.cosine_distance(query_embedding)).label("score")
                ).where(
                    Product.embedding.isnot(None)
                ).order_by(
                    text("score DESC")
                ).limit(top_k)
                
                results = session.execute(query).all()
                
                documents = []
                for product, score in results:
                    # 组合文本
                    parts = [
                        product.goods_name,
                        product.goods_alias,
                        product.brand_name,
                        product.product_specifications
                    ]
                    content = " ".join([p for p in parts if p])
                    
                    doc = Document(
                        id=product.id,
                        content=content,
                        metadata={
                            "product_id": product.id,
                            "goods_name": product.goods_name,
                            "goods_alias": product.goods_alias,
                            "brand_name": product.brand_name,
                            "specifications": product.product_specifications
                        },
                        score=float(score)
                    )
                    documents.append(doc)
                
                logger.info(f"pgvector 相似度搜索返回 {len(documents)} 个商品")
                return documents
                
        except Exception as e:
            logger.error(f"pgvector 相似度搜索失败: {e}")
            raise
    
    async def get_document_count(self) -> int:
        """
        获取有向量的商品数量
        
        Returns:
            商品数量
        """
        try:
            with Session(engine) as session:
                count = session.query(func.count(Product.id)).filter(
                    Product.embedding.isnot(None)
                ).scalar()
                
                return count or 0
                
        except Exception as e:
            logger.error(f"获取商品数量失败: {e}")
            return 0
    
    async def clear_all_vectors(self) -> bool:
        """
        清空所有商品的向量（但保留商品数据）
        
        Returns:
            是否成功
        """
        try:
            with Session(engine) as session:
                session.query(Product).update({"embedding": None})
                session.commit()
                logger.info("成功清空所有商品向量")
                return True
                
        except Exception as e:
            logger.error(f"清空商品向量失败: {e}")
            return False

