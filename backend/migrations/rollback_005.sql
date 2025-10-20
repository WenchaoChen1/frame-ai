-- 回滚知识库相关表

-- 删除触发器
DROP TRIGGER IF EXISTS trigger_update_knowledge_base_updated_at ON knowledge_bases;
DROP FUNCTION IF EXISTS update_knowledge_base_updated_at();

-- 删除索引
DROP INDEX IF EXISTS idx_kb_chunks_embedding;
DROP INDEX IF EXISTS idx_kb_chunks_document_id;
DROP INDEX IF EXISTS idx_kb_documents_status;
DROP INDEX IF EXISTS idx_kb_documents_kb_id;
DROP INDEX IF EXISTS idx_knowledge_bases_created_at;
DROP INDEX IF EXISTS idx_knowledge_bases_user_id;

-- 删除表
DROP TABLE IF EXISTS robot_knowledge_bases;
DROP TABLE IF EXISTS knowledge_base_chunks;
DROP TABLE IF EXISTS knowledge_base_documents;
DROP TABLE IF EXISTS knowledge_bases;

-- 删除枚举类型
DROP TYPE IF EXISTS document_status_enum;
DROP TYPE IF EXISTS embedding_model_enum;
DROP TYPE IF EXISTS vector_store_type_enum;

-- 注意：不删除 pgvector 扩展，因为可能有其他地方在使用
-- DROP EXTENSION IF EXISTS vector;

