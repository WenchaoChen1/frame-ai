from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class DatabaseConfig(Base):
    __tablename__ = "database_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    robot_id = Column(Integer, ForeignKey("robots.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # 数据库配置
    db_type = Column(String, nullable=False)  # 'postgresql', 'mysql', 'redshift'
    host = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    database_name = Column(String, nullable=False)
    username = Column(String, nullable=False)
    password = Column(Text, nullable=False)  # 加密存储
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    robot = relationship("Robot", backref="database_config", uselist=False)


class DatabaseMetadata(Base):
    __tablename__ = "database_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    robot_id = Column(Integer, ForeignKey("robots.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # 表和字段的选择及描述信息 (JSON格式存储)
    # 结构: [{"name": "table1", "description": "表描述", "selected": true, "columns": [{"name": "col1", "description": "字段描述", "selected": true}]}]
    tables_metadata = Column(JSON, nullable=False, default=list)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    robot = relationship("Robot", backref="database_metadata", uselist=False)

