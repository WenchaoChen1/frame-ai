-- 回滚迁移: 删除数据库配置表
-- 版本: 002

-- 删除索引
DROP INDEX IF EXISTS idx_database_configs_robot_id;

-- 删除表
DROP TABLE IF EXISTS database_configs;

