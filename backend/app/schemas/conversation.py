from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from .message import MessageResponse


class ConversationCreate(BaseModel):
    title: Optional[str] = "新对话"
    robot_id: Optional[int] = None


class ConversationResponse(BaseModel):
    id: int
    user_id: int
    robot_id: Optional[int] = None
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []
    
    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    id: int
    user_id: int
    robot_id: Optional[int] = None
    title: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

