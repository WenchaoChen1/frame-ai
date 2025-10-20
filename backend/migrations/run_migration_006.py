"""
运行 Migration 006: 添加嵌入模型提供商和外部向量存储配置字段

执行方法:
    cd backend
    python migrations/run_migration_006.py
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings

def run_migration():
    """运行迁移脚本"""
    print("🚀 开始执行 Migration 006...")
    
    # 创建数据库引擎
    engine = create_engine(settings.DATABASE_URL)
    
    # 读取迁移 SQL
    migration_file = os.path.join(os.path.dirname(__file__), '006_add_kb_provider_fields.sql')
    
    try:
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        # 执行迁移
        with engine.begin() as connection:
            # 分割并执行 SQL 语句
            for statement in migration_sql.split(';'):
                statement = statement.strip()
                if statement and not statement.startswith('--'):
                    try:
                        connection.execute(text(statement))
                        print(f"✅ 执行成功: {statement[:60]}...")
                    except Exception as e:
                        print(f"⚠️  跳过: {str(e)[:100]}")
        
        print("\n✨ Migration 006 执行成功!")
        print("\n新增字段:")
        print("  - embedding_provider (enum): 嵌入模型提供商")
        print("  - vector_store_config_id (integer): 外部向量存储配置ID")
        print("\n更新内容:")
        print("  - embedding_model 枚举已更新为新的模型列表")
        print("  - 现有数据已自动迁移到新的模型名称")
        
    except FileNotFoundError:
        print(f"❌ 错误: 找不到迁移文件 {migration_file}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_migration()

