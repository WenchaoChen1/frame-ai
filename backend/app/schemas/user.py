from pydantic import BaseModel
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    email: str  # 改为str以避免email-validator依赖
    password: str
    role: str = "user"  # 默认为普通用户


class UserUpdate(BaseModel):
    username: str | None = None
    email: str | None = None  # 改为str以避免email-validator依赖
    role: str | None = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class ProfileUpdate(BaseModel):
    """个人资料更新"""
    username: str | None = None
    email: str | None = None


class PasswordChange(BaseModel):
    """修改密码（需要旧密码）"""
    old_password: str
    new_password: str
    confirm_password: str


class PasswordReset(BaseModel):
    """重置密码（管理员使用，无需旧密码）"""
    new_password: str
    confirm_password: str

