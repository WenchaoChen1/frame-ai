from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class LoginAuditCreate(BaseModel):
    user_id: Optional[int] = None
    username: str
    login_status: str  # success, failed
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_info: Optional[str] = None
    location: Optional[str] = None


class LoginAuditResponse(BaseModel):
    id: int
    user_id: Optional[int]
    username: str
    login_time: datetime
    login_status: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    device_info: Optional[str]
    location: Optional[str]
    
    class Config:
        from_attributes = True

