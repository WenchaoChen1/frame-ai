from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/chatai"
    
    # JWT
    SECRET_KEY: str = "2b4e8aa4f1d6e1030132a78e539f35438edcc59029d19bd9878d45e2979c3f64"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    
    # Database Encryption (用于加密数据库配置中的密码)
    # 生产环境中应该使用环境变量设置
    DB_ENCRYPTION_KEY: str = "LVRGJFUzg1GSWbC6EvSeB2b2AK72FsOikEkQFFq4Dx0="
    
    # AI Providers
    # 如果不使用某个提供商，可以留空
    OPENAI_API_KEY: str = ""  # 配置你的 OpenAI API Key
    ANTHROPIC_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    # CORS
    # 开发环境使用 "*" 允许所有源访问（包括IP地址）
    # 生产环境应该指定具体的域名
    CORS_ORIGINS: str = "*"
    
    # Vector Store
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    ELASTICSEARCH_API_KEY: str = ""
    ELASTICSEARCH_INDEX_PREFIX: str = "kb_"
    PGVECTOR_ENABLED: bool = True
    
    # Embeddings
    DEFAULT_EMBEDDING_MODEL: str = "openai"  # openai, huggingface
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    HUGGINGFACE_EMBEDDING_MODEL: str = "BAAI/bge-small-zh-v1.5"
    
    # Document Processing
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    
    # RAG
    TOP_K_RETRIEVAL: int = 10
    TOP_K_RERANK: int = 5
    ENABLE_QUERY_REWRITE: bool = True
    ENABLE_RERANKING: bool = True
    
    @property
    def cors_origins_list(self) -> List[str]:
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

