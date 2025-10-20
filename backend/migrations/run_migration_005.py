"""
迁移脚本：添加知识库相关表
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, text
from app.core.config import settings

def run_migration():
    """执行迁移"""
    engine = create_engine(settings.DATABASE_URL)
    
    # 读取 SQL 文件
    sql_file_path = os.path.join(os.path.dirname(__file__), '005_add_knowledge_base_tables.sql')
    
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # 执行 SQL
    with engine.connect() as conn:
        # 分割 SQL 语句并执行
        statements = [s.strip() for s in sql_content.split(';') if s.strip()]
        
        for statement in statements:
            if statement:
                try:
                    print(f"执行: {statement[:100]}...")
                    conn.execute(text(statement))
                    conn.commit()
                    print("✓ 成功")
                except Exception as e:
                    print(f"✗ 失败: {e}")
                    raise
    
    print("\n✅ 迁移完成！知识库相关表已创建。")

if __name__ == "__main__":
    run_migration()

