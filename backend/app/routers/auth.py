from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User
from app.models.login_audit import LoginAudit
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.dependencies import get_current_user
from app.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", response_model=Token)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    logger.info(f"📝 用户注册请求 - 用户名: {user_data.username}, 邮箱: {user_data.email}")
    
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == user_data.username).first():
        logger.warning(f"⚠️ 注册失败 - 用户名已存在: {user_data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    if db.query(User).filter(User.email == user_data.email).first():
        logger.warning(f"⚠️ 注册失败 - 邮箱已被注册: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    
    logger.debug(f"🔍 开始创建新用户: {user_data.username}")
    
    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"✅ 用户注册成功 - 用户名: {new_user.username}, ID: {new_user.id}")
    
    # 生成访问令牌
    access_token = create_access_token(data={"sub": str(new_user.id)})
    logger.debug(f"🎫 生成访问令牌成功 - 用户ID: {new_user.id}")
    
    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(new_user)
    )


@router.post("/login", response_model=Token)
def login(user_data: UserLogin, request: Request, db: Session = Depends(get_db)):
    """用户登录"""
    logger.info(f"🔐 用户登录请求 - 用户名: {user_data.username}")
    logger.debug(f"🔍 调试信息 - 开始查询用户: {user_data.username}")
    
    # 获取请求信息
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent", "")
    
    # 查找用户
    user = db.query(User).filter(User.username == user_data.username).first()
    
    if not user:
        logger.warning(f"⚠️ 登录失败 - 用户不存在: {user_data.username}")
        
        # 记录失败的登录审计
        audit = LoginAudit(
            user_id=None,
            username=user_data.username,
            login_status="failed",
            ip_address=ip_address,
            user_agent=user_agent,
            device_info=_parse_device_info(user_agent),
            login_time=datetime.utcnow()
        )
        db.add(audit)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(user_data.password, user.hashed_password):
        logger.warning(f"⚠️ 登录失败 - 密码错误: {user_data.username}")
        
        # 记录失败的登录审计
        audit = LoginAudit(
            user_id=user.id,
            username=user_data.username,
            login_status="failed",
            ip_address=ip_address,
            user_agent=user_agent,
            device_info=_parse_device_info(user_agent),
            login_time=datetime.utcnow()
        )
        db.add(audit)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"✅ 用户登录成功 - 用户名: {user.username}, ID: {user.id}")
    
    # 记录成功的登录审计
    audit = LoginAudit(
        user_id=user.id,
        username=user.username,
        login_status="success",
        ip_address=ip_address,
        user_agent=user_agent,
        device_info=_parse_device_info(user_agent),
        login_time=datetime.utcnow()
    )
    db.add(audit)
    db.commit()
    
    # 生成访问令牌
    access_token = create_access_token(data={"sub": str(user.id)})
    logger.debug(f"🎫 生成访问令牌成功 - 用户ID: {user.id}")
    
    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return UserResponse.model_validate(current_user)


def _parse_device_info(user_agent: str) -> str:
    """解析设备信息"""
    if not user_agent:
        return "Unknown"
    
    user_agent_lower = user_agent.lower()
    
    # 判断操作系统
    if "windows" in user_agent_lower:
        os = "Windows"
    elif "mac" in user_agent_lower or "darwin" in user_agent_lower:
        os = "macOS"
    elif "linux" in user_agent_lower:
        os = "Linux"
    elif "android" in user_agent_lower:
        os = "Android"
    elif "iphone" in user_agent_lower or "ipad" in user_agent_lower:
        os = "iOS"
    else:
        os = "Unknown"
    
    # 判断浏览器
    if "chrome" in user_agent_lower and "edg" not in user_agent_lower:
        browser = "Chrome"
    elif "firefox" in user_agent_lower:
        browser = "Firefox"
    elif "safari" in user_agent_lower and "chrome" not in user_agent_lower:
        browser = "Safari"
    elif "edg" in user_agent_lower:
        browser = "Edge"
    elif "opera" in user_agent_lower or "opr" in user_agent_lower:
        browser = "Opera"
    else:
        browser = "Unknown"
    
    return f"{os} - {browser}"

