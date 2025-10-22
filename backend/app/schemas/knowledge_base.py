from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from app.models.knowledge_base import VectorStoreType, DocumentStatus
from app.ai.models import EmbeddingModel, EmbeddingProvider


# ============= 知识库 Schemas =============

class KnowledgeBaseBase(BaseModel):
    """知识库基础模型"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    vector_store_type: VectorStoreType = VectorStoreType.PGVECTOR
    vector_store_config_id: Optional[int] = None  # 外部向量存储配置ID（NULL表示使用系统库）
    embedding_provider: EmbeddingProvider = EmbeddingProvider.OPENAI
    embedding_model: EmbeddingModel = EmbeddingModel.OPENAI_SMALL
    chunk_size: int = Field(default=500, ge=100, le=2000)
    chunk_overlap: int = Field(default=50, ge=0, le=500)
    is_public: bool = False


class KnowledgeBaseCreate(KnowledgeBaseBase):
    """创建知识库"""
    pass


class KnowledgeBaseUpdate(BaseModel):
    """更新知识库"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    vector_store_type: Optional[VectorStoreType] = None
    vector_store_config_id: Optional[int] = None
    embedding_provider: Optional[EmbeddingProvider] = None
    embedding_model: Optional[EmbeddingModel] = None
    chunk_size: Optional[int] = Field(None, ge=100, le=2000)
    chunk_overlap: Optional[int] = Field(None, ge=0, le=500)
    is_public: Optional[bool] = None


class KnowledgeBaseResponse(KnowledgeBaseBase):
    """知识库响应模型"""
    id: int
    user_id: int
    es_index_name: Optional[str]
    document_count: int
    total_chunks: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class KnowledgeBaseListResponse(BaseModel):
    """知识库列表响应"""
    id: int
    name: str
    description: Optional[str]
    vector_store_type: VectorStoreType
    vector_store_config_id: Optional[int]
    embedding_provider: EmbeddingProvider
    embedding_model: EmbeddingModel
    document_count: int
    total_chunks: int
    is_public: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= 文档 Schemas =============

class DocumentUpload(BaseModel):
    """文档上传（表单数据不需要 schema，这里用于元数据）"""
    pass


class DocumentResponse(BaseModel):
    """文档响应模型"""
    id: int
    knowledge_base_id: int
    filename: str
    file_type: str
    file_size: int
    status: DocumentStatus
    error_message: Optional[str]
    chunk_count: int
    character_count: int
    uploaded_at: datetime
    processed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """文档列表响应"""
    id: int
    filename: str
    file_type: str
    file_size: int
    status: DocumentStatus
    chunk_count: int
    character_count: int
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


# ============= 文档块 Schemas =============

class ChunkResponse(BaseModel):
    """文档块响应"""
    id: int
    document_id: int
    content: str
    chunk_index: int
    metadata: Optional[str] = Field(None, alias='meta_data')
    created_at: datetime
    
    @property
    def character_count(self) -> int:
        """计算字符数"""
        return len(self.content) if self.content else 0
    
    class Config:
        from_attributes = True
        populate_by_name = True  # 允许使用 alias


# ============= 机器人关联知识库 Schemas =============

class RobotKnowledgeBaseAssociate(BaseModel):
    """关联知识库到机器人"""
    knowledge_base_ids: List[int] = Field(..., min_items=1)


class RobotKnowledgeBaseResponse(BaseModel):
    """机器人关联的知识库"""
    robot_id: int
    knowledge_bases: List[KnowledgeBaseListResponse]


# ============= 批量导入 Schemas =============

class BatchImportRequest(BaseModel):
    """批量导入请求"""
    directory_path: str = Field(..., description="本地目录路径")
    file_extensions: List[str] = Field(default=[".txt", ".pdf", ".docx"], description="要导入的文件扩展名")


class BatchImportResponse(BaseModel):
    """批量导入响应"""
    success_count: int
    failed_count: int
    total_count: int
    failed_files: List[str] = []


# ============= 检索相关 Schemas =============

class SearchRequest(BaseModel):
    """知识库搜索请求"""
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    knowledge_base_ids: Optional[List[int]] = None


class SearchResult(BaseModel):
    """搜索结果项"""
    content: str
    score: float
    document_id: int
    document_name: str
    chunk_index: int
    metadata: Optional[dict] = None


class SearchResponse(BaseModel):
    """搜索响应"""
    query: str
    results: List[SearchResult]
    total: int

