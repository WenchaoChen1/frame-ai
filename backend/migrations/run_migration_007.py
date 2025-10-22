"""
Migration 007: 添加商品RAG测试表
"""
import sys
import os

# 添加父目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings

def run_migration():
    """执行迁移"""
    print("开始执行 Migration 007: 添加商品RAG测试表")
    
    # 创建数据库引擎
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        # 读取 SQL 文件
        sql_file = os.path.join(os.path.dirname(__file__), '007_add_products_table.sql')
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        # 执行 SQL
        with engine.begin() as conn:
            # 分割并执行每个语句
            statements = [s.strip() for s in sql.split(';') if s.strip() and not s.strip().startswith('--')]
            for statement in statements:
                if statement:
                    print(f"执行: {statement[:100]}...")
                    conn.execute(text(statement))
        
        print("✅ Migration 007 执行成功！")
        print("\n创建的表:")
        print("- products (商品表)")
        
    except Exception as e:
        print(f"❌ Migration 007 执行失败: {e}")
        raise
    finally:
        engine.dispose()

if __name__ == '__main__':
    run_migration()

