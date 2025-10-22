-- Migration 008: 为商品表添加向量字段支持 pgvector
-- 使得商品可以使用 PostgreSQL + pgvector 而不必依赖 Elasticsearch

-- 确保 pgvector 扩展已启用
CREATE EXTENSION IF NOT EXISTS vector;

-- 添加向量字段（维度 1536，对应 OpenAI text-embedding-3-small）
ALTER TABLE products ADD COLUMN IF NOT EXISTS embedding vector(1536);

-- 创建向量索引以加速相似度搜索
-- 使用 HNSW 索引（性能更好）
CREATE INDEX IF NOT EXISTS idx_products_embedding_hnsw 
ON products USING hnsw (embedding vector_cosine_ops);

-- 或者使用 IVFFlat 索引（适合大规模数据）
-- CREATE INDEX IF NOT EXISTS idx_products_embedding_ivfflat 
-- ON products USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- 添加注释
COMMENT ON COLUMN products.embedding IS '商品文本的向量表示（维度1536）';

