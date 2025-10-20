#!/usr/bin/env python3
"""
运行数据库迁移 004: 添加 SQL 查询日志表
"""
import sys
import os

# 添加父目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings

def run_migration():
    """运行迁移"""
    print("🔄 开始运行迁移 004: 添加 SQL 查询日志表...")
    
    # 创建数据库引擎
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # 读取迁移 SQL 文件
            migration_file = os.path.join(os.path.dirname(__file__), '004_add_sql_query_logs.sql')
            with open(migration_file, 'r', encoding='utf-8') as f:
                sql = f.read()
            
            # 执行迁移
            conn.execute(text(sql))
            conn.commit()
            
            print("✅ 迁移 004 执行成功！")
            return True
            
    except Exception as e:
        print(f"❌ 迁移失败: {str(e)}")
        return False
    
    finally:
        engine.dispose()


def rollback_migration():
    """回滚迁移"""
    print("🔄 开始回滚迁移 004...")
    
    # 创建数据库引擎
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # 读取回滚 SQL 文件
            rollback_file = os.path.join(os.path.dirname(__file__), 'rollback_004.sql')
            with open(rollback_file, 'r', encoding='utf-8') as f:
                sql = f.read()
            
            # 执行回滚
            conn.execute(text(sql))
            conn.commit()
            
            print("✅ 迁移 004 回滚成功！")
            return True
            
    except Exception as e:
        print(f"❌ 回滚失败: {str(e)}")
        return False
    
    finally:
        engine.dispose()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="运行或回滚迁移 004")
    parser.add_argument('--rollback', action='store_true', help='回滚迁移')
    args = parser.parse_args()
    
    if args.rollback:
        success = rollback_migration()
    else:
        success = run_migration()
    
    sys.exit(0 if success else 1)

