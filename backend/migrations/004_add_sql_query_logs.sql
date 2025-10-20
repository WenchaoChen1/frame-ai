-- Migration: 004_add_sql_query_logs
-- Description: 添加 SQL 查询日志表用于记录 Text-to-SQL 查询历史

CREATE TABLE IF NOT EXISTS sql_query_logs (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL,
    
    -- 查询信息
    user_question TEXT NOT NULL,
    generated_sql TEXT,
    query_result JSON,
    
    -- 执行状态
    success BOOLEAN NOT NULL DEFAULT FALSE,
    error_message TEXT,
    execution_time FLOAT NOT NULL,
    
    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 添加外键约束（如果不存在）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'sql_query_logs_conversation_id_fkey'
    ) THEN
        ALTER TABLE sql_query_logs 
        ADD CONSTRAINT sql_query_logs_conversation_id_fkey 
        FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE;
    END IF;
END $$;

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_sql_query_logs_conversation_id ON sql_query_logs(conversation_id);
CREATE INDEX IF NOT EXISTS idx_sql_query_logs_created_at ON sql_query_logs(created_at DESC);

