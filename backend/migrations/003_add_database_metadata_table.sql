-- 迁移: 添加数据库元数据表
-- 版本: 003
-- 描述: 为机器人添加数据库表和字段的选择及描述配置功能

CREATE TABLE IF NOT EXISTS database_metadata (
    id SERIAL PRIMARY KEY,
    robot_id INTEGER NOT NULL UNIQUE REFERENCES robots(id) ON DELETE CASCADE,
    tables_metadata JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_database_metadata_robot_id ON database_metadata(robot_id);

-- 添加注释
COMMENT ON TABLE database_metadata IS '机器人数据库表和字段元数据配置表';
COMMENT ON COLUMN database_metadata.robot_id IS '关联的机器人ID';
COMMENT ON COLUMN database_metadata.tables_metadata IS '表和字段的选择及描述信息JSON数据';

