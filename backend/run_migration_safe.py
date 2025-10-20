"""
安全的迁移运行脚本 - 处理已存在的情况
"""
import psycopg2
import os

DB_HOST = "localhost"
DB_PORT = "5432"
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DB_NAME = "chatai"

print(f"🔗 连接数据库: {DB_HOST}:{DB_PORT}/{DB_NAME}")

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME
    )
    conn.autocommit = False
    cursor = conn.cursor()
    
    print("✅ 数据库连接成功")
    
    # 步骤 1: 检查并添加字段
    print("\n📝 步骤 1: 添加新字段...")
    try:
        cursor.execute("""
            ALTER TABLE knowledge_bases 
            ADD COLUMN IF NOT EXISTS vector_store_config_id INTEGER NULL;
        """)
        print("   ✅ vector_store_config_id 字段已添加")
    except Exception as e:
        print(f"   ⚠️  vector_store_config_id 字段: {e}")
    
    # 步骤 2: 创建 embedding_provider 枚举（如果不存在）
    print("\n📝 步骤 2: 创建 embedding_provider 枚举...")
    try:
        cursor.execute("""
            DO $$ BEGIN
                CREATE TYPE embedding_provider_enum AS ENUM ('openai', 'claude', 'ollama');
            EXCEPTION
                WHEN duplicate_object THEN 
                    RAISE NOTICE 'embedding_provider_enum 已存在';
            END $$;
        """)
        print("   ✅ embedding_provider_enum 枚举已创建")
    except Exception as e:
        print(f"   ⚠️  embedding_provider 枚举: {e}")
    
    # 步骤 3: 添加 embedding_provider 字段
    print("\n📝 步骤 3: 添加 embedding_provider 字段...")
    try:
        cursor.execute("""
            ALTER TABLE knowledge_bases 
            ADD COLUMN IF NOT EXISTS embedding_provider embedding_provider_enum DEFAULT 'openai';
        """)
        print("   ✅ embedding_provider 字段已添加")
    except Exception as e:
        print(f"   ⚠️  embedding_provider 字段: {e}")
    
    # 步骤 4: 更新 embedding_model 枚举
    print("\n📝 步骤 4: 更新 embedding_model 枚举...")
    try:
        # 先检查旧枚举是否存在
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM pg_type WHERE typname = 'embedding_model_enum'
            );
        """)
        enum_exists = cursor.fetchone()[0]
        
        if enum_exists:
            print("   - 将现有列转换为 VARCHAR...")
            cursor.execute("""
                ALTER TABLE knowledge_bases 
                ALTER COLUMN embedding_model TYPE VARCHAR(50);
            """)
            
            print("   - 重命名旧枚举...")
            cursor.execute("""
                ALTER TYPE embedding_model_enum RENAME TO embedding_model_enum_old;
            """)
            
        print("   - 创建新枚举...")
        cursor.execute("""
            CREATE TYPE embedding_model_enum AS ENUM (
                'text-embedding-3-small',
                'text-embedding-3-large',
                'text-embedding-ada-002',
                'claude-embed-v1',
                'nomic-embed-text',
                'mxbai-embed-large',
                'all-minilm'
            );
        """)
        
        print("   - 更新现有数据...")
        cursor.execute("""
            UPDATE knowledge_bases 
            SET embedding_model = CASE 
                WHEN embedding_model = 'openai-small' THEN 'text-embedding-3-small'
                WHEN embedding_model = 'openai-large' THEN 'text-embedding-3-large'
                WHEN embedding_model = 'huggingface-bge' THEN 'nomic-embed-text'
                ELSE 'text-embedding-3-small'
            END
            WHERE embedding_model NOT IN (
                'text-embedding-3-small',
                'text-embedding-3-large',
                'text-embedding-ada-002',
                'claude-embed-v1',
                'nomic-embed-text',
                'mxbai-embed-large',
                'all-minilm'
            );
        """)
        
        print("   - 转换列类型...")
        cursor.execute("""
            ALTER TABLE knowledge_bases
            ALTER COLUMN embedding_model TYPE embedding_model_enum 
            USING embedding_model::embedding_model_enum;
        """)
        
        if enum_exists:
            print("   - 删除旧枚举...")
            cursor.execute("""
                DROP TYPE IF EXISTS embedding_model_enum_old CASCADE;
            """)
        
        print("   ✅ embedding_model 枚举已更新")
    except Exception as e:
        print(f"   ⚠️  embedding_model 枚举更新: {e}")
        conn.rollback()
        raise
    
    # 提交事务
    conn.commit()
    print("\n" + "="*60)
    print("✅ 迁移 006 执行成功！")
    print("   - 添加了 vector_store_config_id 字段")
    print("   - 添加了 embedding_provider 字段和枚举")
    print("   - 更新了 embedding_model 枚举类型")
    print("="*60)
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ 迁移失败: {e}")
    if conn:
        conn.rollback()
    raise

