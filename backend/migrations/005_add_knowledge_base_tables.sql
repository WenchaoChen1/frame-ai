-- 启用 pgvector 扩展（用于向量相似度搜索）
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建枚举类型
CREATE TYPE vector_store_type_enum AS ENUM ('elasticsearch', 'pgvector');
CREATE TYPE embedding_model_enum AS ENUM ('openai-small', 'openai-large', 'huggingface-bge');
CREATE TYPE document_status_enum AS ENUM ('pending', 'processing', 'completed', 'failed');

-- 知识库表
CREATE TABLE IF NOT EXISTS knowledge_bases (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    
    -- 向量存储配置
    vector_store_type vector_store_type_enum NOT NULL DEFAULT 'pgvector',
    embedding_model embedding_model_enum NOT NULL DEFAULT 'openai-small',
    es_index_name VARCHAR(100),
    
    -- 文档分块配置
    chunk_size INTEGER DEFAULT 500,
    chunk_overlap INTEGER DEFAULT 50,
    
    -- 权限控制
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- 统计信息
    document_count INTEGER DEFAULT 0,
    total_chunks INTEGER DEFAULT 0,
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 知识库文档表
CREATE TABLE IF NOT EXISTS knowledge_base_documents (
    id SERIAL PRIMARY KEY,
    knowledge_base_id INTEGER NOT NULL REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    
    -- 文件信息
    filename VARCHAR(500) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size INTEGER NOT NULL,
    file_path VARCHAR(1000),
    
    -- 处理状态
    status document_status_enum NOT NULL DEFAULT 'pending',
    error_message TEXT,
    
    -- 统计信息
    chunk_count INTEGER DEFAULT 0,
    character_count INTEGER DEFAULT 0,
    
    -- 时间戳
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP
);

-- 文档块表（用于 pgvector）
CREATE TABLE IF NOT EXISTS knowledge_base_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES knowledge_base_documents(id) ON DELETE CASCADE,
    
    -- 块内容
    content TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    
    -- 向量（1536维，适用于 OpenAI text-embedding-3-small）
    embedding vector(1536),
    
    -- 元数据（使用 meta_data 而不是 metadata，因为 metadata 是 SQLAlchemy 保留字）
    meta_data TEXT,
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 机器人与知识库多对多关联表
CREATE TABLE IF NOT EXISTS robot_knowledge_bases (
    robot_id INTEGER NOT NULL REFERENCES robots(id) ON DELETE CASCADE,
    knowledge_base_id INTEGER NOT NULL REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (robot_id, knowledge_base_id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_knowledge_bases_user_id ON knowledge_bases(user_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_bases_created_at ON knowledge_bases(created_at);
CREATE INDEX IF NOT EXISTS idx_kb_documents_kb_id ON knowledge_base_documents(knowledge_base_id);
CREATE INDEX IF NOT EXISTS idx_kb_documents_status ON knowledge_base_documents(status);
CREATE INDEX IF NOT EXISTS idx_kb_chunks_document_id ON knowledge_base_chunks(document_id);

-- 创建向量相似度搜索索引（使用 HNSW 算法，性能更好）
CREATE INDEX IF NOT EXISTS idx_kb_chunks_embedding ON knowledge_base_chunks 
USING hnsw (embedding vector_cosine_ops);

-- 创建更新时间戳的触发器函数
CREATE OR REPLACE FUNCTION update_knowledge_base_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 为 knowledge_bases 表创建触发器
CREATE TRIGGER trigger_update_knowledge_base_updated_at
    BEFORE UPDATE ON knowledge_bases
    FOR EACH ROW
    EXECUTE FUNCTION update_knowledge_base_updated_at();

-- 添加注释
COMMENT ON TABLE knowledge_bases IS '知识库表';
COMMENT ON TABLE knowledge_base_documents IS '知识库文档表';
COMMENT ON TABLE knowledge_base_chunks IS '文档块表（用于 pgvector 向量搜索）';
COMMENT ON TABLE robot_knowledge_bases IS '机器人与知识库关联表';
COMMENT ON COLUMN knowledge_base_chunks.embedding IS '文本向量（1536维）';
COMMENT ON COLUMN knowledge_base_chunks.meta_data IS '元数据（JSON 字符串）';

