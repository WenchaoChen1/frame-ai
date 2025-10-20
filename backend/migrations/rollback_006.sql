-- 回滚 Migration 006: 删除 embedding_provider 和 vector_store_config_id 字段

-- 1. 删除新添加的字段
ALTER TABLE knowledge_bases 
    DROP COLUMN IF EXISTS embedding_provider,
    DROP COLUMN IF EXISTS vector_store_config_id;

-- 2. 恢复旧的 embedding_model 枚举类型
ALTER TYPE embedding_model_enum RENAME TO embedding_model_enum_new;

CREATE TYPE embedding_model_enum AS ENUM (
    'openai-small',
    'openai-large',
    'huggingface-bge'
);

-- 3. 更新 embedding_model 列使用旧的枚举类型
ALTER TABLE knowledge_bases 
    ALTER COLUMN embedding_model TYPE VARCHAR(50);

UPDATE knowledge_bases 
SET embedding_model = CASE 
    WHEN embedding_model = 'text-embedding-3-small' THEN 'openai-small'
    WHEN embedding_model = 'text-embedding-3-large' THEN 'openai-large'
    WHEN embedding_model = 'text-embedding-ada-002' THEN 'openai-small'
    WHEN embedding_model = 'nomic-embed-text' THEN 'huggingface-bge'
    WHEN embedding_model = 'mxbai-embed-large' THEN 'huggingface-bge'
    WHEN embedding_model = 'all-minilm' THEN 'huggingface-bge'
    ELSE 'openai-small'
END;

ALTER TABLE knowledge_bases
    ALTER COLUMN embedding_model TYPE embedding_model_enum 
    USING embedding_model::embedding_model_enum;

-- 4. 删除新的枚举类型
DROP TYPE IF EXISTS embedding_model_enum_new CASCADE;
DROP TYPE IF EXISTS embedding_provider_enum CASCADE;

