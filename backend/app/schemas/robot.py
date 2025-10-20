from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RobotBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    avatar: Optional[str] = None
    default_provider: str = Field(..., min_length=1)
    default_model: str = Field(..., min_length=1)
    system_prompt: Optional[str] = None
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, ge=1)
    is_global: bool = False


class RobotCreate(RobotBase):
    pass


class RobotUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    avatar: Optional[str] = None
    default_provider: Optional[str] = None
    default_model: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1)
    is_global: Optional[bool] = None


class RobotResponse(RobotBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RobotListResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    avatar: Optional[str]
    default_provider: str
    default_model: str
    is_global: bool
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

