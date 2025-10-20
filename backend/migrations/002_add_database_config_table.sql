-- 迁移: 添加数据库配置表
-- 版本: 002
-- 描述: 为机器人添加数据库连接配置功能

CREATE TABLE IF NOT EXISTS database_configs (
    id SERIAL PRIMARY KEY,
    robot_id INTEGER NOT NULL UNIQUE REFERENCES robots(id) ON DELETE CASCADE,
    db_type VARCHAR(50) NOT NULL,
    host VARCHAR(255) NOT NULL,
    port INTEGER NOT NULL,
    database_name VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_database_configs_robot_id ON database_configs(robot_id);

-- 添加注释
COMMENT ON TABLE database_configs IS '机器人数据库配置表';
COMMENT ON COLUMN database_configs.robot_id IS '关联的机器人ID';
COMMENT ON COLUMN database_configs.db_type IS '数据库类型: postgresql, mysql, redshift';
COMMENT ON COLUMN database_configs.host IS '数据库主机地址';
COMMENT ON COLUMN database_configs.port IS '数据库端口';
COMMENT ON COLUMN database_configs.database_name IS '数据库名称';
COMMENT ON COLUMN database_configs.username IS '数据库用户名';
COMMENT ON COLUMN database_configs.password IS '加密后的数据库密码';

