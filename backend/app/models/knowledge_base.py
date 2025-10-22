from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Table, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base
from app.ai.models import EmbeddingProvider, EmbeddingModel

# 尝试导入 pgvector 的 Vector 类型
try:
    from pgvector.sqlalchemy import Vector
    HAS_PGVECTOR = True
except ImportError:
    # 如果 pgvector 未安装，使用 Text 类型作为后备
    HAS_PGVECTOR = False
    Vector = None


class VectorStoreType(str, enum.Enum):
    """向量存储类型"""
    ELASTICSEARCH = "elasticsearch"
    PGVECTOR = "pgvector"


class DocumentStatus(str, enum.Enum):
    """文档处理状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# 机器人与知识库多对多关联表
robot_knowledge_bases = Table(
    'robot_knowledge_bases',
    Base.metadata,
    Column('robot_id', Integer, ForeignKey('robots.id', ondelete='CASCADE'), primary_key=True),
    Column('knowledge_base_id', Integer, ForeignKey('knowledge_bases.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow)
)


class KnowledgeBase(Base):
    """知识库表"""
    __tablename__ = "knowledge_bases"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # 向量存储配置
    vector_store_type = Column(
        SQLEnum(VectorStoreType, name='vector_store_type_enum'),
        nullable=False,
        default=VectorStoreType.PGVECTOR
    )
    vector_store_config_id = Column(Integer, nullable=True)  # 外部向量存储配置ID（NULL表示使用系统库）
    
    # 嵌入模型配置
    embedding_provider = Column(
        SQLEnum(EmbeddingProvider, name='embedding_provider_enum'),
        nullable=False,
        default=EmbeddingProvider.OPENAI
    )
    embedding_model = Column(
        SQLEnum(EmbeddingModel, name='embedding_model_enum'),
        nullable=False,
        default=EmbeddingModel.OPENAI_SMALL
    )
    
    # Elasticsearch 索引名（仅当使用 ES 时）
    es_index_name = Column(String(100), nullable=True)
    
    # 文档分块配置
    chunk_size = Column(Integer, default=500)
    chunk_overlap = Column(Integer, default=50)
    
    # 权限控制
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)
    
    # 统计信息
    document_count = Column(Integer, default=0)
    total_chunks = Column(Integer, default=0)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="knowledge_bases")
    documents = relationship("KnowledgeBaseDocument", back_populates="knowledge_base", cascade="all, delete-orphan")
    robots = relationship("Robot", secondary=robot_knowledge_bases, back_populates="knowledge_bases")


class KnowledgeBaseDocument(Base):
    """知识库文档表"""
    __tablename__ = "knowledge_base_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=False)
    
    # 文件信息
    filename = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)  # txt, pdf, docx
    file_size = Column(Integer, nullable=False)  # bytes
    file_path = Column(String(1000), nullable=True)  # 本地存储路径（可选）
    
    # 处理状态
    status = Column(
        SQLEnum(DocumentStatus, name='document_status_enum'),
        nullable=False,
        default=DocumentStatus.PENDING
    )
    error_message = Column(Text, nullable=True)
    
    # 统计信息
    chunk_count = Column(Integer, default=0)
    character_count = Column(Integer, default=0)
    
    # 时间戳
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    knowledge_base = relationship("KnowledgeBase", back_populates="documents")
    chunks = relationship("KnowledgeBaseChunk", back_populates="document", cascade="all, delete-orphan")


class KnowledgeBaseChunk(Base):
    """文档块表（用于 pgvector）"""
    __tablename__ = "knowledge_base_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("knowledge_base_documents.id", ondelete="CASCADE"), nullable=False)
    
    # 块内容
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)  # 块在文档中的顺序
    
    # 向量（仅 pgvector 使用）
    # 如果 pgvector 可用，使用 Vector 类型，否则使用 Text（仅用于表创建，实际不会存储）
    embedding = Column(Vector(1536) if HAS_PGVECTOR and Vector is not None else Text, nullable=True)
    
    # 元数据（使用 meta_data 而不是 metadata，因为 metadata 是保留字）
    meta_data = Column(Text, nullable=True)  # JSON 字符串
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("KnowledgeBaseDocument", back_populates="chunks")

