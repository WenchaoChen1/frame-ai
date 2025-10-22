"""
知识库管理 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import List, Optional
import os

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.knowledge_base import (
    KnowledgeBase, KnowledgeBaseDocument, KnowledgeBaseChunk,
    VectorStoreType, DocumentStatus
)
from app.ai.models import EmbeddingModel
from app.schemas.knowledge_base import (
    KnowledgeBaseCreate, KnowledgeBaseUpdate, KnowledgeBaseResponse,
    KnowledgeBaseListResponse, DocumentResponse, DocumentListResponse,
    BatchImportRequest, BatchImportResponse, SearchRequest, SearchResponse, SearchResult
)
from app.services.knowledge_base_service import KnowledgeBaseService
from app.ai.retrievers import RetrievalService
from app.ai.document_loaders import DocumentLoaderFactory
from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger(__name__)

router = APIRouter(prefix="/api/knowledge-bases", tags=["knowledge-bases"])


@router.post("", response_model=KnowledgeBaseResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_base(
    kb: KnowledgeBaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建知识库"""
    try:
        # 创建知识库
        knowledge_base = KnowledgeBase(
            name=kb.name,
            description=kb.description,
            vector_store_type=kb.vector_store_type,
            embedding_model=kb.embedding_model,
            chunk_size=kb.chunk_size,
            chunk_overlap=kb.chunk_overlap,
            is_public=kb.is_public,
            user_id=current_user.id
        )
        
        # 如果使用 Elasticsearch，生成索引名
        if kb.vector_store_type == VectorStoreType.ELASTICSEARCH:
            import uuid
            knowledge_base.es_index_name = f"{settings.ELASTICSEARCH_INDEX_PREFIX}{uuid.uuid4().hex[:8]}"
        
        db.add(knowledge_base)
        db.commit()
        db.refresh(knowledge_base)
        
        logger.info(f"用户 {current_user.id} 创建知识库: {knowledge_base.name} (ID: {knowledge_base.id})")
        
        return knowledge_base
        
    except Exception as e:
        logger.error(f"创建知识库失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建知识库失败: {str(e)}")


@router.get("", response_model=List[KnowledgeBaseListResponse])
async def list_knowledge_bases(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取知识库列表"""
    try:
        # 获取用户的知识库和公开的知识库
        knowledge_bases = db.query(KnowledgeBase).filter(
            (KnowledgeBase.user_id == current_user.id) | (KnowledgeBase.is_public == True)
        ).offset(skip).limit(limit).all()
        
        return knowledge_bases
        
    except Exception as e:
        logger.error(f"获取知识库列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取知识库列表失败: {str(e)}")


@router.get("/{kb_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(
    kb_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取知识库详情"""
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    
    # 权限检查
    if kb.user_id != current_user.id and not kb.is_public:
        raise HTTPException(status_code=403, detail="无权访问该知识库")
    
    return kb


@router.put("/{kb_id}", response_model=KnowledgeBaseResponse)
async def update_knowledge_base(
    kb_id: int,
    kb_update: KnowledgeBaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新知识库"""
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    
    if kb.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权修改该知识库")
    
    # 配置锁定逻辑：如果已上传文档，不允许修改向量存储和嵌入模型配置
    update_data = kb_update.model_dump(exclude_unset=True)
    
    if kb.document_count > 0:
        locked_fields = ['vector_store_type', 'vector_store_config_id', 'embedding_provider', 'embedding_model']
        attempted_locked_changes = [field for field in locked_fields if field in update_data]
        
        if attempted_locked_changes:
            raise HTTPException(
                status_code=400, 
                detail=f"由于已上传文档并进行向量化，不允许修改以下字段: {', '.join(attempted_locked_changes)}。"
                       "如需更改这些配置，请先删除所有文档。"
            )
    
    # 更新字段
    for field, value in update_data.items():
        setattr(kb, field, value)
    
    db.commit()
    db.refresh(kb)
    
    logger.info(f"用户 {current_user.id} 更新知识库 {kb_id}")
    
    return kb


@router.delete("/{kb_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge_base(
    kb_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除知识库"""
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    
    if kb.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除该知识库")
    
    # 删除知识库（会级联删除文档和块）
    db.delete(kb)
    db.commit()
    
    logger.info(f"用户 {current_user.id} 删除知识库 {kb_id}")
    
    return None


@router.post("/{kb_id}/documents", response_model=DocumentResponse)
async def upload_document(
    kb_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """上传文档到知识库"""
    # 获取知识库
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    
    if kb.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权上传文档到该知识库")
    
    # 检查文件类型
    file_ext = os.path.splitext(file.filename)[1].lower()
    if not DocumentLoaderFactory.supports_file_type(file_ext):
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file_ext}。支持的类型: .txt, .pdf, .docx, .json"
        )
    
    # 读取文件内容
    file_content = await file.read()
    
    # 检查文件大小
    if len(file_content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件大小超过限制 ({settings.MAX_FILE_SIZE / 1024 / 1024:.1f} MB)"
        )
    
    try:
        # 处理文档
        document = await KnowledgeBaseService.process_document(
            db=db,
            knowledge_base=kb,
            file=file,
            file_content=file_content
        )
        
        logger.info(f"用户 {current_user.id} 上传文档到知识库 {kb_id}: {file.filename}")
        
        return document
        
    except Exception as e:
        logger.error(f"上传文档失败: {e}")
        raise HTTPException(status_code=500, detail=f"上传文档失败: {str(e)}")


@router.get("/{kb_id}/documents", response_model=List[DocumentListResponse])
async def list_documents(
    kb_id: int,
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[DocumentStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取知识库的文档列表"""
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    
    if kb.user_id != current_user.id and not kb.is_public:
        raise HTTPException(status_code=403, detail="无权访问该知识库")
    
    # 查询文档
    query = db.query(KnowledgeBaseDocument).filter(
        KnowledgeBaseDocument.knowledge_base_id == kb_id
    )
    
    if status_filter:
        query = query.filter(KnowledgeBaseDocument.status == status_filter)
    
    documents = query.offset(skip).limit(limit).all()
    
    return documents


@router.get("/documents/{doc_id}/chunks")
async def get_document_chunks(
    doc_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取文档的分块列表"""
    # 获取文档
    document = db.query(KnowledgeBaseDocument).filter(
        KnowledgeBaseDocument.id == doc_id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    # 检查权限
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == document.knowledge_base_id).first()
    if kb.user_id != current_user.id and not kb.is_public:
        raise HTTPException(status_code=403, detail="无权访问该文档")
    
    # 获取分块
    chunks = db.query(KnowledgeBaseChunk).filter(
        KnowledgeBaseChunk.document_id == doc_id
    ).order_by(KnowledgeBaseChunk.chunk_index).offset(skip).limit(limit).all()
    
    # 转换为响应格式
    result = []
    for chunk in chunks:
        result.append({
            "id": chunk.id,
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
            "character_count": len(chunk.content),
            "metadata": chunk.meta_data,
            "created_at": chunk.created_at.isoformat() if chunk.created_at else None
        })
    
    return {
        "total": len(chunks),
        "chunks": result
    }


@router.delete("/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除文档"""
    doc = db.query(KnowledgeBaseDocument).filter(KnowledgeBaseDocument.id == doc_id).first()
    
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    kb = doc.knowledge_base
    if kb.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除该文档")
    
    try:
        # 删除文档及其向量数据
        await KnowledgeBaseService.delete_document(db=db, document=doc, knowledge_base=kb)
        
        logger.info(f"用户 {current_user.id} 删除文档 {doc_id}")
        
        return None
        
    except Exception as e:
        logger.error(f"删除文档失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除文档失败: {str(e)}")


@router.post("/{kb_id}/batch-import", response_model=BatchImportResponse)
async def batch_import_documents(
    kb_id: int,
    request: BatchImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """批量导入本地目录中的文档"""
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    
    if kb.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权导入文档到该知识库")
    
    if not os.path.exists(request.directory_path):
        raise HTTPException(status_code=400, detail="目录不存在")
    
    try:
        result = await KnowledgeBaseService.batch_import_documents(
            db=db,
            knowledge_base=kb,
            directory_path=request.directory_path,
            file_extensions=request.file_extensions
        )
        
        logger.info(f"用户 {current_user.id} 批量导入文档到知识库 {kb_id}: {result}")
        
        return result
        
    except Exception as e:
        logger.error(f"批量导入失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量导入失败: {str(e)}")


@router.post("/search", response_model=SearchResponse)
async def search_knowledge_bases(
    request: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """在知识库中搜索"""
    try:
        # 如果未指定知识库，搜索用户所有知识库
        if not request.knowledge_base_ids:
            user_kbs = db.query(KnowledgeBase).filter(
                KnowledgeBase.user_id == current_user.id
            ).all()
            kb_ids = [kb.id for kb in user_kbs]
        else:
            kb_ids = request.knowledge_base_ids
        
        if not kb_ids:
            return SearchResponse(query=request.query, results=[], total=0)
        
        # 执行检索
        docs = await RetrievalService.search_multiple_knowledge_bases(
            db=db,
            knowledge_base_ids=kb_ids,
            query=request.query,
            top_k=request.top_k,
            use_hybrid=True
        )
        
        # 转换为响应格式
        results = []
        for doc in docs:
            result = SearchResult(
                content=doc.content,
                score=doc.score or 0,
                document_id=doc.metadata.get("document_id", 0),
                document_name=doc.metadata.get("filename", "未知"),
                chunk_index=doc.metadata.get("chunk_index", 0),
                metadata=doc.metadata
            )
            results.append(result)
        
        return SearchResponse(
            query=request.query,
            results=results,
            total=len(results)
        )
        
    except Exception as e:
        logger.error(f"搜索失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")

