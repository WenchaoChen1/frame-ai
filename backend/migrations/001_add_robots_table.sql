-- 迁移脚本：添加机器人表和更新对话表
-- 执行时间：2025-10-16
-- 描述：添加 robots 表，并为 conversations 表添加 robot_id 字段

-- ====================================
-- 1. 创建 robots 表
-- ====================================

CREATE TABLE IF NOT EXISTS robots (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    avatar VARCHAR(100),
    default_provider VARCHAR(50) NOT NULL,
    default_model VARCHAR(100) NOT NULL,
    system_prompt TEXT,
    temperature FLOAT DEFAULT 0.7,
    max_tokens INTEGER,
    is_global BOOLEAN NOT NULL DEFAULT FALSE,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_robots_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_robots_user_id ON robots(user_id);
CREATE INDEX IF NOT EXISTS idx_robots_is_global ON robots(is_global);

-- ====================================
-- 2. 更新 conversations 表
-- ====================================

-- 添加 robot_id 列（如果不存在）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'conversations' 
        AND column_name = 'robot_id'
    ) THEN
        ALTER TABLE conversations ADD COLUMN robot_id INTEGER;
        ALTER TABLE conversations ADD CONSTRAINT fk_conversations_robot 
            FOREIGN KEY (robot_id) REFERENCES robots(id) ON DELETE SET NULL;
    END IF;
END $$;

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_conversations_robot_id ON conversations(robot_id);

-- ====================================
-- 3. 添加示例数据（可选，注释掉了）
-- ====================================

-- 以下是一些示例机器人，您可以取消注释来创建
-- 注意：需要确保 user_id 存在（通常管理员的 id 是 1）

-- INSERT INTO robots (name, description, avatar, default_provider, default_model, is_global, user_id, system_prompt)
-- VALUES 
-- ('GPT-4 助手', '强大的通用AI助手，适合各种任务', '🤖', 'openai', 'gpt-4', TRUE, 1, '你是一个有帮助的AI助手。'),
-- ('Python 编程助手', '专业的Python编程顾问', '🐍', 'openai', 'gpt-4', TRUE, 1, '你是一个专业的Python编程专家。你精通Python语言的各个方面，包括语法、标准库、第三方库、最佳实践等。'),
-- ('英语翻译助手', '中英互译专家', '🌍', 'openai', 'gpt-3.5-turbo', TRUE, 1, '你是一个专业的翻译助手，精通中文和英文。');

-- ====================================
-- 验证迁移
-- ====================================

-- 验证 robots 表是否创建成功
SELECT 'robots table created' AS status
FROM information_schema.tables 
WHERE table_name = 'robots';

-- 验证 conversations 表的 robot_id 列是否添加成功
SELECT 'robot_id column added to conversations' AS status
FROM information_schema.columns 
WHERE table_name = 'conversations' 
AND column_name = 'robot_id';

