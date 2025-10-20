from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class Robot(Base):
    __tablename__ = "robots"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    avatar = Column(String, nullable=True)  # emoji or image url
    
    # AI配置
    default_provider = Column(String, nullable=False)  # 'openai', 'claude', 'ollama'
    default_model = Column(String, nullable=False)  # e.g., 'gpt-4', 'claude-3-opus'
    system_prompt = Column(Text, nullable=True)  # 系统提示词
    temperature = Column(Float, nullable=True, default=0.7)  # 温度参数
    max_tokens = Column(Integer, nullable=True)  # 最大token数
    
    # 权限控制
    is_global = Column(Boolean, default=False, nullable=False)  # 是否全局机器人
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 创建者
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="robots")
    conversations = relationship("Conversation", back_populates="robot")
    knowledge_bases = relationship("KnowledgeBase", secondary="robot_knowledge_bases", back_populates="robots")

