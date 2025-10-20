"""
简单的迁移运行脚本
"""
import psycopg2
import os

# 直接从环境变量或默认值读取数据库配置
DB_HOST = os.getenv("POSTGRES_SERVER", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_NAME = os.getenv("POSTGRES_DB", "chatai")

print(f"🔗 连接数据库: {DB_HOST}:{DB_PORT}/{DB_NAME}")

try:
    # 连接数据库
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("✅ 数据库连接成功")
    
    # 读取并执行 SQL
    with open("migrations/006_add_kb_provider_fields.sql", "r", encoding="utf-8") as f:
        sql = f.read()
    
    print("📝 执行迁移 SQL...")
    cursor.execute(sql)
    
    print("✅ 迁移 006 执行成功！")
    print("   - 添加了 embedding_provider 字段")
    print("   - 添加了 vector_store_config_id 字段")
    print("   - 更新了 embedding_model 枚举类型")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ 迁移失败: {e}")
    raise

