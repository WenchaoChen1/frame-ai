-- 回滚脚本：删除机器人表和相关字段
-- 警告：这将删除所有机器人数据！

-- ====================================
-- 1. 删除 conversations 表的 robot_id 列
-- ====================================

-- 删除外键约束
ALTER TABLE conversations DROP CONSTRAINT IF EXISTS fk_conversations_robot;

-- 删除列
ALTER TABLE conversations DROP COLUMN IF EXISTS robot_id;

-- ====================================
-- 2. 删除 robots 表
-- ====================================

DROP TABLE IF EXISTS robots CASCADE;

-- ====================================
-- 验证回滚
-- ====================================

SELECT 'Migration rolled back successfully' AS status;

