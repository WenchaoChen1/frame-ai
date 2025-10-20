from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class SQLQueryLog(Base):
    __tablename__ = "sql_query_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    
    # 查询信息
    user_question = Column(Text, nullable=False)
    generated_sql = Column(Text, nullable=True)
    query_result = Column(JSON, nullable=True)  # 存储查询结果（限制大小）
    
    # 执行状态
    success = Column(Boolean, nullable=False, default=False)
    error_message = Column(Text, nullable=True)
    execution_time = Column(Float, nullable=False)  # 执行时间（秒）
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", backref="sql_query_logs")

