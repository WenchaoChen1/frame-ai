-- Rollback 007: 删除商品RAG测试表

-- 删除索引
DROP INDEX IF EXISTS idx_products_created_at;
DROP INDEX IF EXISTS idx_products_brand_name;
DROP INDEX IF EXISTS idx_products_sell_spu_id;

-- 删除表
DROP TABLE IF EXISTS products;

