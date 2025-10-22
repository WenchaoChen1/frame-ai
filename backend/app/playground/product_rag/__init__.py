"""
商品RAG召回测试模块
独立的功能模块，用于测试商品数据的向量化和RAG召回效果
"""
from .models import Product
from .schemas import (
    ProductCreate,
    ProductResponse,
    ProductListResponse,
    SearchRequest,
    SearchResult,
    SearchResponse,
    BatchSearchRequest,
    BatchSearchResponse,
    StatsResponse
)

__all__ = [
    "Product",
    "ProductCreate",
    "ProductResponse",
    "ProductListResponse",
    "SearchRequest",
    "SearchResult",
    "SearchResponse",
    "BatchSearchRequest",
    "BatchSearchResponse",
    "StatsResponse"
]

