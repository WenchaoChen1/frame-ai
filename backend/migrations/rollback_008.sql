-- Rollback Migration 008: 移除商品表的向量字段

-- 删除向量索引
DROP INDEX IF EXISTS idx_products_embedding_hnsw;
DROP INDEX IF EXISTS idx_products_embedding_ivfflat;

-- 删除向量字段
ALTER TABLE products DROP COLUMN IF EXISTS embedding;

