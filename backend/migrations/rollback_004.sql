-- Rollback Migration: 004_add_sql_query_logs
-- Description: 删除 SQL 查询日志表

DROP INDEX IF EXISTS idx_sql_query_logs_created_at;
DROP INDEX IF EXISTS idx_sql_query_logs_conversation_id;
DROP TABLE IF EXISTS sql_query_logs;

