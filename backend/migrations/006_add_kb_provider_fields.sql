-- 为知识库表添加嵌入模型提供商和外部向量存储配置字段
-- Migration 006: Add embedding_provider and vector_store_config_id fields

-- 1. 添加 embedding_provider 枚举类型
DO $$ BEGIN
    CREATE TYPE embedding_provider_enum AS ENUM ('openai', 'claude', 'ollama');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 2. 更新 embedding_model 枚举类型（添加新模型）
ALTER TYPE embedding_model_enum RENAME TO embedding_model_enum_old;

CREATE TYPE embedding_model_enum AS ENUM (
    -- OpenAI models
    'text-embedding-3-small',
    'text-embedding-3-large',
    'text-embedding-ada-002',
    -- Claude models
    'claude-embed-v1',
    -- Ollama models
    'nomic-embed-text',
    'mxbai-embed-large',
    'all-minilm'
);

-- 3. 添加新字段到 knowledge_bases 表
ALTER TABLE knowledge_bases 
    ADD COLUMN IF NOT EXISTS embedding_provider embedding_provider_enum DEFAULT 'openai',
    ADD COLUMN IF NOT EXISTS vector_store_config_id INTEGER NULL;

-- 4. 更新 embedding_model 列使用新的枚举类型
-- 先将现有数据映射到新值
ALTER TABLE knowledge_bases 
    ALTER COLUMN embedding_model TYPE VARCHAR(50);

UPDATE knowledge_bases 
SET embedding_model = CASE 
    WHEN embedding_model = 'openai-small' THEN 'text-embedding-3-small'
    WHEN embedding_model = 'openai-large' THEN 'text-embedding-3-large'
    WHEN embedding_model = 'huggingface-bge' THEN 'nomic-embed-text'
    ELSE 'text-embedding-3-small'
END;

-- 转换为新的枚举类型
ALTER TABLE knowledge_bases
    ALTER COLUMN embedding_model TYPE embedding_model_enum 
    USING embedding_model::embedding_model_enum;

-- 5. 删除旧的枚举类型
DROP TYPE IF EXISTS embedding_model_enum_old CASCADE;

-- 6. 添加注释
COMMENT ON COLUMN knowledge_bases.embedding_provider IS '嵌入模型提供商（openai/claude/ollama）';
COMMENT ON COLUMN knowledge_bases.vector_store_config_id IS '外部向量存储配置ID（NULL表示使用系统库）';
COMMENT ON TYPE embedding_provider_enum IS '嵌入模型提供商枚举';

