"""
商品RAG API路由
"""
import json
import time
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.logger import get_logger
from app.dependencies import get_current_user
from .models import Product
from .schemas import (
    ProductResponse,
    ProductListResponse,
    SearchRequest,
    SearchResponse,
    BatchSearchRequest,
    BatchSearchResponse,
    StatsResponse,
    IndexListResponse,
    DeleteIndexRequest
)
from .service import ProductRAGService

logger = get_logger(__name__)

router = APIRouter(
    prefix="/api/product-rag",
    tags=["商品RAG测试"]
)

# 创建默认服务实例
rag_service = ProductRAGService()


@router.post("/upload")
async def upload_products(
    file: UploadFile = File(...),
    index_name: str = Query(None, description="索引名称，不指定则使用默认索引"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    上传JSON文件并向量化存储
    
    - 支持单个商品对象或商品数组
    - 自动提取商品信息并生成向量
    - 存储到数据库和Elasticsearch
    """
    try:
        # 读取文件内容
        content = await file.read()
        
        # 解析JSON
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"JSON解析失败: {str(e)}")
        
        # 转换为列表
        if isinstance(data, dict):
            # 检查是否是分页格式（包含 list 字段）
            if "list" in data:
                products_data = data["list"]
                logger.info(f"检测到分页格式，提取 list 字段，共 {len(products_data)} 个商品")
            else:
                # 单个商品对象
                products_data = [data]
        elif isinstance(data, list):
            products_data = data
        else:
            raise HTTPException(status_code=400, detail="不支持的JSON格式")
        
        if not products_data:
            raise HTTPException(status_code=400, detail="没有找到商品数据")
        
        logger.info(f"开始处理 {len(products_data)} 个商品")
        
        # 使用指定的索引或默认索引
        service = ProductRAGService(index_name=index_name) if index_name else rag_service
        
        # 处理并存储
        result = await service.process_and_store_products(
            db=db,
            products_data=products_data
        )
        
        return {
            "message": "商品数据上传成功",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传商品数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.get("/products", response_model=ProductListResponse)
async def get_products(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    index_name: str = Query(None, description="索引名称，不指定则使用默认索引"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取商品列表（分页）- 从Elasticsearch查询
    """
    try:
        # 使用指定的索引或默认索引
        service = ProductRAGService(index_name=index_name) if index_name else rag_service
        
        # 从ES查询商品
        result = await service.get_products_from_es(
            page=page,
            page_size=page_size
        )
        
        return ProductListResponse(
            total=result['total'],
            items=result['items'],
            page=result['page'],
            page_size=result['page_size']
        )
        
    except Exception as e:
        logger.error(f"获取商品列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.post("/search", response_model=SearchResponse)
async def search_products(
    request: SearchRequest,
    index_name: str = Query(None, description="索引名称，不指定则使用默认索引"),
    current_user = Depends(get_current_user)
):
    """
    单次召回测试
    
    - 输入查询词
    - 返回相似商品列表，包含排名和相似度分数
    """
    try:
        # 使用指定的索引或默认索引
        service = ProductRAGService(index_name=index_name) if index_name else rag_service
        
        response = await service.search_products(
            query=request.query,
            top_k=request.top_k
        )
        
        return response
        
    except Exception as e:
        logger.error(f"搜索失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.post("/batch-search", response_model=BatchSearchResponse)
async def batch_search_products(
    request: BatchSearchRequest,
    index_name: str = Query(None, description="索引名称，不指定则使用默认索引"),
    current_user = Depends(get_current_user)
):
    """
    批量召回测试
    
    - 输入多个查询词
    - 返回每个查询词的召回结果
    """
    try:
        start_time = time.time()
        
        # 使用指定的索引或默认索引
        service = ProductRAGService(index_name=index_name) if index_name else rag_service
        
        # 批量搜索
        results = await service.batch_search_products(
            queries=request.queries,
            top_k=request.top_k
        )
        
        total_time = (time.time() - start_time) * 1000  # 转换为毫秒
        
        return BatchSearchResponse(
            results=results,
            total_time_ms=total_time
        )
        
    except Exception as e:
        logger.error(f"批量搜索失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量搜索失败: {str(e)}")


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    index_name: str = Query(None, description="索引名称，不指定则使用默认索引"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取统计信息
    
    - 总商品数
    - ES中的向量总数
    - 索引名称
    - 使用的嵌入模型
    """
    try:
        # 使用指定的索引或默认索引
        service = ProductRAGService(index_name=index_name) if index_name else rag_service
        
        stats = await service.get_stats(db=db)
        return stats
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@router.delete("/clear")
async def clear_all_data(
    index_name: str = Query(None, description="索引名称，不指定则使用默认索引"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    清空所有数据
    
    - 删除数据库中的所有商品
    - 删除Elasticsearch索引
    """
    try:
        # 使用指定的索引或默认索引
        service = ProductRAGService(index_name=index_name) if index_name else rag_service
        
        result = await service.clear_all_data(db=db)
        
        return {
            "message": "数据已清空",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"清空数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"清空数据失败: {str(e)}")


@router.get("/indices", response_model=IndexListResponse)
async def get_all_indices(
    current_user = Depends(get_current_user)
):
    """
    获取所有ES索引列表
    
    - 返回所有索引信息，包含文档数、存储大小、健康状态等
    """
    try:
        result = await rag_service.get_all_indices()
        return result
        
    except Exception as e:
        logger.error(f"获取索引列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取索引列表失败: {str(e)}")


@router.delete("/indices/{index_name}")
async def delete_index(
    index_name: str,
    current_user = Depends(get_current_user)
):
    """
    删除指定索引
    
    - 删除指定名称的Elasticsearch索引及其所有数据
    """
    try:
        result = await rag_service.delete_index(index_name=index_name)
        
        return {
            "message": f"索引 {index_name} 已删除",
            "result": result
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"删除索引失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除索引失败: {str(e)}")

