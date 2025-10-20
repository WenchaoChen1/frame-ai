"""
最终迁移脚本 - 添加缺失的字段
"""
import psycopg2

DB_HOST = "localhost"
DB_PORT = "5432"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_NAME = "chatai"

print(f"🔗 连接数据库: {DB_HOST}:{DB_PORT}/{DB_NAME}\n")

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("✅ 数据库连接成功\n")
    
    # 添加缺失的字段
    print("📝 添加 embedding_provider 字段...")
    try:
        cursor.execute("""
            ALTER TABLE knowledge_bases 
            ADD COLUMN IF NOT EXISTS embedding_provider embedding_provider_enum DEFAULT 'OPENAI';
        """)
        print("   ✅ embedding_provider 字段已添加\n")
    except Exception as e:
        print(f"   ⚠️  {e}\n")
    
    print("📝 添加 vector_store_config_id 字段...")
    try:
        cursor.execute("""
            ALTER TABLE knowledge_bases 
            ADD COLUMN IF NOT EXISTS vector_store_config_id INTEGER NULL;
        """)
        print("   ✅ vector_store_config_id 字段已添加\n")
    except Exception as e:
        print(f"   ⚠️  {e}\n")
    
    # 验证字段
    print("📊 验证字段:")
    cursor.execute("""
        SELECT column_name, data_type, udt_name, column_default
        FROM information_schema.columns
        WHERE table_name = 'knowledge_bases'
        AND column_name IN ('embedding_provider', 'vector_store_config_id')
        ORDER BY ordinal_position;
    """)
    
    for row in cursor.fetchall():
        print(f"  ✅ {row[0]}: {row[1]} ({row[2]}) = {row[3]}")
    
    print("\n" + "="*60)
    print("✅ 迁移完成！数据库已更新")
    print("="*60)
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    raise

