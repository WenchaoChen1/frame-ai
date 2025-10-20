from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class MessageCreate(BaseModel):
    content: str
    provider: str = "openai"  # 'openai', 'claude', 'ollama'
    model: str = "gpt-3.5-turbo"


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    provider: Optional[str]
    model: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

