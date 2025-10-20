"""
检查数据库当前状态
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
    cursor = conn.cursor()
    
    # 检查枚举类型
    print("📊 现有的枚举类型:")
    cursor.execute("""
        SELECT typname, enumlabel 
        FROM pg_type t 
        JOIN pg_enum e ON t.oid = e.enumtypid
        WHERE typname LIKE '%embedding%' OR typname LIKE '%vector%'
        ORDER BY typname, enumlabel;
    """)
    
    current_enum = None
    for row in cursor.fetchall():
        if row[0] != current_enum:
            print(f"\n  {row[0]}:")
            current_enum = row[0]
        print(f"    - {row[1]}")
    
    # 检查 knowledge_bases 表结构
    print("\n\n📊 knowledge_bases 表字段:")
    cursor.execute("""
        SELECT column_name, data_type, udt_name
        FROM information_schema.columns
        WHERE table_name = 'knowledge_bases'
        ORDER BY ordinal_position;
    """)
    
    for row in cursor.fetchall():
        print(f"  - {row[0]}: {row[1]} ({row[2]})")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ 错误: {e}")

