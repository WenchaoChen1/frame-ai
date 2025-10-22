#!/usr/bin/env python
"""
运行迁移 008: 为商品表添加向量字段
"""
import sys
import os

# 添加父目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings

def run_migration():
    """执行迁移"""
    engine = create_engine(settings.DATABASE_URL)
    
    # 读取 SQL 文件
    sql_file = os.path.join(os.path.dirname(__file__), "008_add_product_embedding.sql")
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    # 执行迁移
    with engine.begin() as conn:
        # 分割 SQL 语句（按分号分隔）
        statements = [s.strip() for s in sql.split(';') if s.strip()]
        
        for statement in statements:
            if statement and not statement.startswith('--'):
                print(f"执行: {statement[:100]}...")
                conn.execute(text(statement))
        
        print("✅ Migration 008 执行成功！")

if __name__ == "__main__":
    try:
        run_migration()
    except Exception as e:
        print(f"❌ Migration 008 执行失败: {e}")
        sys.exit(1)

