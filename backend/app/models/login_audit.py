from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class LoginAudit(Base):
    __tablename__ = "login_audits"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    username = Column(String, nullable=False)
    login_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    login_status = Column(String, nullable=False)  # success, failed
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    device_info = Column(String, nullable=True)
    location = Column(String, nullable=True)
    
    # Relationship
    user = relationship("User", backref="login_audits")

