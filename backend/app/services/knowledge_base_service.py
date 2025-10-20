"""
知识库服务
负责知识库的创建、文档上传、向量化等核心业务逻辑
"""
from typing import BinaryIO, List, Optional
from sqlalchemy.orm import Session
from fastapi import UploadFile
import os
from datetime import datetime
from ..models.knowledge_base import (
    KnowledgeBase, KnowledgeBaseDocument, KnowledgeBaseChunk,
    VectorStoreType, DocumentStatus
)
from ..ai.models import EmbeddingModel
from ..core.logger import get_logger
from ..core.config import settings
from ..ai.document_loaders import DocumentLoaderFactory
from ..ai.text_splitters import ChunkingService
from ..ai.embeddings import EmbeddingService
from ..ai.vector_stores import PGVectorStore, ElasticsearchStore, Document

logger = get_logger(__name__)


class KnowledgeBaseService:
    """知识库服务"""
    
    @staticmethod
    async def process_document(
        db: Session,
        knowledge_base: KnowledgeBase,
        file: UploadFile,
        file_content: bytes
    ) -> KnowledgeBaseDocument:
        """
        处理上传的文档（解析、分块、向量化、存储）
        
        Args:
            db: 数据库会话
            knowledge_base: 知识库对象
            file: 上传的文件
            file_content: 文件内容（字节）
            
        Returns:
            文档对象
        """
        document = None
        
        try:
            # 1. 创建文档记录
            file_type = os.path.splitext(file.filename)[1].lower()
            document = KnowledgeBaseDocument(
                knowledge_base_id=knowledge_base.id,
                filename=file.filename,
                file_type=file_type,
                file_size=len(file_content),
                status=DocumentStatus.PROCESSING
            )
            db.add(document)
            db.commit()
            db.refresh(document)
            
            logger.info(f"开始处理文档: {file.filename} (ID: {document.id})")
            
            # 2. 解析文档内容
            loader = DocumentLoaderFactory.get_loader(file_type)
            
            from io import BytesIO
            file_io = BytesIO(file_content)
            text = loader.extract_text(file_io)
            
            if not text or not text.strip():
                raise ValueError("文档内容为空")
            
            logger.info(f"成功提取文本，长度: {len(text)} 字符")
            
            # 3. 文本分块
            chunks = ChunkingService.chunk_text(
                text=text,
                chunk_size=knowledge_base.chunk_size,
                chunk_overlap=knowledge_base.chunk_overlap,
                metadata={
                    "document_id": document.id,
                    "filename": file.filename,
                    "file_type": file_type
                }
            )
            
            if not chunks:
                raise ValueError("文档分块失败，未生成任何块")
            
            logger.info(f"文档分块完成，共 {len(chunks)} 个块")
            
            # 4. 生成嵌入向量
            chunk_texts = [chunk["content"] for chunk in chunks]
            embeddings = await EmbeddingService.embed_documents(
                texts=chunk_texts,
                model=knowledge_base.embedding_model
            )
            
            logger.info(f"成功生成 {len(embeddings)} 个嵌入向量")
            
            # 5. 存储到向量数据库
            if knowledge_base.vector_store_type == VectorStoreType.PGVECTOR:
                # 使用 pgvector
                store = PGVectorStore(knowledge_base_id=knowledge_base.id)
                documents_to_store = [
                    Document(
                        content=chunk["content"],
                        metadata=chunk["metadata"]
                    )
                    for chunk in chunks
                ]
                await store.add_documents(documents_to_store, embeddings)
                
            elif knowledge_base.vector_store_type == VectorStoreType.ELASTICSEARCH:
                # 使用 Elasticsearch
                index_name = knowledge_base.es_index_name or f"{settings.ELASTICSEARCH_INDEX_PREFIX}{knowledge_base.id}"
                dimension = EmbeddingService.get_embedding_dimension(knowledge_base.embedding_model)
                store = ElasticsearchStore(index_name=index_name, dimension=dimension)
                
                # 为 ES 创建带 ID 的文档
                documents_to_store = []
                for i, chunk in enumerate(chunks):
                    doc = Document(
                        id=f"{document.id}_{i}",
                        content=chunk["content"],
                        metadata=chunk["metadata"]
                    )
                    documents_to_store.append(doc)
                
                await store.add_documents(documents_to_store, embeddings)
                
                # 更新索引名（如果是第一次）
                if not knowledge_base.es_index_name:
                    knowledge_base.es_index_name = index_name
            
            # 6. 更新文档状态和统计信息
            document.status = DocumentStatus.COMPLETED
            document.chunk_count = len(chunks)
            document.character_count = len(text)
            document.processed_at = datetime.utcnow()
            
            # 更新知识库统计
            knowledge_base.document_count += 1
            knowledge_base.total_chunks += len(chunks)
            
            db.commit()
            db.refresh(document)
            
            logger.info(f"文档处理完成: {file.filename}")
            return document
            
        except Exception as e:
            logger.error(f"处理文档失败: {e}")
            
            # 更新文档状态为失败
            if document:
                document.status = DocumentStatus.FAILED
                document.error_message = str(e)
                db.commit()
            
            raise
    
    @staticmethod
    async def delete_document(
        db: Session,
        document: KnowledgeBaseDocument,
        knowledge_base: KnowledgeBase
    ) -> bool:
        """
        删除文档及其向量数据
        
        Args:
            db: 数据库会话
            document: 文档对象
            knowledge_base: 知识库对象
            
        Returns:
            是否成功
        """
        try:
            # 1. 从向量数据库删除
            if knowledge_base.vector_store_type == VectorStoreType.PGVECTOR:
                # pgvector 的数据会通过级联删除自动删除
                pass
                
            elif knowledge_base.vector_store_type == VectorStoreType.ELASTICSEARCH:
                # 从 ES 删除
                index_name = knowledge_base.es_index_name
                if index_name:
                    store = ElasticsearchStore(index_name=index_name)
                    # 删除该文档的所有块
                    doc_ids = [f"{document.id}_{i}" for i in range(document.chunk_count)]
                    await store.delete_documents(doc_ids)
            
            # 2. 更新知识库统计
            knowledge_base.document_count = max(0, knowledge_base.document_count - 1)
            knowledge_base.total_chunks = max(0, knowledge_base.total_chunks - document.chunk_count)
            
            # 3. 删除数据库记录（会级联删除 chunks）
            db.delete(document)
            db.commit()
            
            logger.info(f"成功删除文档: {document.filename}")
            return True
            
        except Exception as e:
            logger.error(f"删除文档失败: {e}")
            return False
    
    @staticmethod
    async def batch_import_documents(
        db: Session,
        knowledge_base: KnowledgeBase,
        directory_path: str,
        file_extensions: List[str] = None
    ) -> dict:
        """
        批量导入本地目录中的文档
        
        Args:
            db: 数据库会话
            knowledge_base: 知识库对象
            directory_path: 目录路径
            file_extensions: 要导入的文件扩展名列表
            
        Returns:
            导入结果统计
        """
        if file_extensions is None:
            file_extensions = ['.txt', '.pdf', '.docx']
        
        success_count = 0
        failed_count = 0
        failed_files = []
        
        try:
            # 遍历目录
            for root, dirs, files in os.walk(directory_path):
                for filename in files:
                    file_ext = os.path.splitext(filename)[1].lower()
                    
                    if file_ext not in file_extensions:
                        continue
                    
                    file_path = os.path.join(root, filename)
                    
                    try:
                        # 读取文件
                        with open(file_path, 'rb') as f:
                            file_content = f.read()
                        
                        # 创建 UploadFile 对象
                        from fastapi import UploadFile
                        from io import BytesIO
                        
                        upload_file = UploadFile(
                            filename=filename,
                            file=BytesIO(file_content)
                        )
                        
                        # 处理文档
                        await KnowledgeBaseService.process_document(
                            db=db,
                            knowledge_base=knowledge_base,
                            file=upload_file,
                            file_content=file_content
                        )
                        
                        success_count += 1
                        logger.info(f"成功导入: {file_path}")
                        
                    except Exception as e:
                        failed_count += 1
                        failed_files.append(filename)
                        logger.error(f"导入失败 {file_path}: {e}")
            
            return {
                "success_count": success_count,
                "failed_count": failed_count,
                "total_count": success_count + failed_count,
                "failed_files": failed_files
            }
            
        except Exception as e:
            logger.error(f"批量导入失败: {e}")
            raise

