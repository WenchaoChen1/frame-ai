-- Migration 007: 添加商品RAG测试表
-- 用于存储商品数据和向量化测试

-- 创建商品表
CREATE TABLE IF NOT EXISTS products (
    id VARCHAR(50) PRIMARY KEY,
    sell_spu_id VARCHAR(50),
    goods_name TEXT NOT NULL,
    goods_alias TEXT,
    brand_name VARCHAR(200),
    product_specifications TEXT,
    original_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_products_sell_spu_id ON products(sell_spu_id);
CREATE INDEX IF NOT EXISTS idx_products_brand_name ON products(brand_name);
CREATE INDEX IF NOT EXISTS idx_products_created_at ON products(created_at);

-- 添加注释
COMMENT ON TABLE products IS '商品RAG测试表';
COMMENT ON COLUMN products.id IS '商品ID';
COMMENT ON COLUMN products.sell_spu_id IS '销售SPU ID';
COMMENT ON COLUMN products.goods_name IS '商品名称';
COMMENT ON COLUMN products.goods_alias IS '商品别名';
COMMENT ON COLUMN products.brand_name IS '品牌名称';
COMMENT ON COLUMN products.product_specifications IS '产品规格';
COMMENT ON COLUMN products.original_data IS '完整的JSON数据';
COMMENT ON COLUMN products.created_at IS '创建时间';

