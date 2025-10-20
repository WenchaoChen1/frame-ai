"""
向量存储基类
定义统一的向量存储接口
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Document:
    """文档数据结构"""
    content: str
    metadata: Dict[str, Any]
    id: Optional[str] = None
    score: Optional[float] = None


class VectorStoreBase(ABC):
    """向量存储抽象基类"""
    
    @abstractmethod
    async def add_documents(
        self,
        documents: List[Document],
        embeddings: List[List[float]]
    ) -> List[str]:
        """
        添加文档和对应的向量
        
        Args:
            documents: 文档列表
            embeddings: 嵌入向量列表
            
        Returns:
            文档 ID 列表
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    async def delete_documents(self, document_ids: List[str]) -> bool:
        """
        删除文档
        
        Args:
            document_ids: 文档 ID 列表
            
        Returns:
            是否成功
        """
        pass
    
    @abstractmethod
    async def get_document_count(self) -> int:
        """
        获取文档数量
        
        Returns:
            文档数量
        """
        pass

