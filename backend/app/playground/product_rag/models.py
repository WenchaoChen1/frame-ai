"""
商品数据模型
"""
from sqlalchemy import Column, String, Text, DateTime, BigInteger
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

from app.core.database import Base


class Product(Base):
    """商品表"""
    __tablename__ = "products"
    
    # 使用商品ID作为主键
    id = Column(String(50), primary_key=True, comment="商品ID")
    sell_spu_id = Column(String(50), index=True, comment="销售SPU ID")
    goods_name = Column(Text, comment="商品名称")
    goods_alias = Column(Text, comment="商品别名")
    brand_name = Column(String(200), comment="品牌名称")
    product_specifications = Column(Text, comment="产品规格")
    
    # 存储完整的原始JSON数据
    original_data = Column(JSONB, comment="完整的JSON数据")
    
    # 注意：向量数据存储在 Elasticsearch 中，不存储在 PostgreSQL
    # 如果需要使用 pgvector，需要先在 PostgreSQL 服务器上安装 pgvector 扩展
    # 然后取消注释下面的行：
    # from pgvector.sqlalchemy import Vector
    # embedding = Column(Vector(1536), comment="商品文本的向量表示")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    
    def __repr__(self):
        return f"<Product(id={self.id}, name={self.goods_name[:20] if self.goods_name else 'N/A'}...)>"

