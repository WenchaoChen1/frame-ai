"""
商品RAG Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ProductCreate(BaseModel):
    """创建商品请求"""
    id: str
    sell_spu_id: Optional[str] = None
    goods_name: str
    goods_alias: Optional[str] = None
    brand_name: Optional[str] = None
    product_specifications: Optional[str] = None
    original_data: Dict[str, Any]


class ProductResponse(BaseModel):
    """商品响应"""
    id: str
    sell_spu_id: Optional[str] = None
    goods_name: str
    goods_alias: Optional[str] = None
    brand_name: Optional[str] = None
    product_specifications: Optional[str] = None
    original_data: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """商品列表响应"""
    total: int
    items: List[ProductResponse]
    page: int
    page_size: int


class SearchRequest(BaseModel):
    """搜索请求"""
    query: str = Field(..., description="搜索查询词")
    top_k: int = Field(default=1000, ge=1, le=1000, description="返回结果数量")


class SearchResult(BaseModel):
    """单个搜索结果"""
    rank: int = Field(..., description="排名")
    product_id: str = Field(..., description="商品ID")
    goods_name: str = Field(..., description="商品名称")
    goods_alias: Optional[str] = Field(None, description="商品别名")
    brand_name: Optional[str] = Field(None, description="品牌名称")
    product_specifications: Optional[str] = Field(None, description="产品规格")
    score: float = Field(..., description="相似度分数")
    content: str = Field(..., description="匹配的文本内容")
    original_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="原始商品数据")


class SearchResponse(BaseModel):
    """搜索响应"""
    query: str
    total: int
    results: List[SearchResult]
    search_time_ms: float = Field(..., description="搜索耗时（毫秒）")


class BatchSearchRequest(BaseModel):
    """批量搜索请求"""
    queries: List[str] = Field(..., min_items=1, description="查询词列表")
    top_k: int = Field(default=1000, ge=1, le=1000, description="每个查询返回的结果数量")


class BatchSearchResponse(BaseModel):
    """批量搜索响应"""
    results: List[SearchResponse]
    total_time_ms: float = Field(..., description="总耗时（毫秒）")


class StatsResponse(BaseModel):
    """统计信息响应"""
    total_products: int = Field(..., description="总商品数")
    total_vectors: int = Field(..., description="ES中的向量总数")
    index_name: str = Field(..., description="ES索引名称")
    embedding_model: str = Field(..., description="使用的嵌入模型")


class IndexInfo(BaseModel):
    """索引信息"""
    name: str = Field(..., description="索引名称")
    docs_count: int = Field(..., description="文档数量")
    store_size: str = Field(..., description="存储大小")
    health: str = Field(..., description="健康状态")
    status: str = Field(..., description="状态")
    created_at: Optional[str] = Field(None, description="创建时间")


class IndexListResponse(BaseModel):
    """索引列表响应"""
    total: int
    indices: List[IndexInfo]


class DeleteIndexRequest(BaseModel):
    """删除索引请求"""
    index_name: str = Field(..., description="要删除的索引名称")
