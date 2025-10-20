#!/usr/bin/env python3
"""
运行数据库迁移 003: 添加数据库元数据表
"""
import psycopg2
import sys
import os

# 从环境变量获取数据库连接信息
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'fangying_ai')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')

def run_migration():
    """执行迁移"""
    try:
        # 连接数据库
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("🚀 开始执行迁移 003...")
        
        # 读取并执行 SQL 文件
        with open('003_add_database_metadata_table.sql', 'r', encoding='utf-8') as f:
            sql = f.read()
            cursor.execute(sql)
        
        print("✅ 迁移 003 执行成功！")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ 迁移失败: {str(e)}", file=sys.stderr)
        return False

if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)

