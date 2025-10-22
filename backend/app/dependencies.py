from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.core.logger import get_logger

logger = get_logger(__name__)
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前登录用户"""
    logger.info("🔐 开始验证用户身份")
    
    # 获取token
    token = credentials.credentials
    logger.info("📨 获取到认证Token")
    
    # 解码token
    payload = decode_access_token(token)
    
    if payload is None:
        logger.error("❌ Token解码失败")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 从payload中获取user_id
    user_id_str = payload.get("sub")
    
    if user_id_str is None:
        logger.error("❌ Token中缺少用户ID")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user_id: int = int(user_id_str)
    except (ValueError, TypeError):
        logger.error(f"❌ Token中的用户ID格式无效: {user_id_str}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 查询数据库
    logger.info(f"🔍 查询用户: user_id={user_id}")
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        logger.error(f"❌ 用户不存在: user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"✅ 用户验证成功: username={user.username}, role={user.role}")
    return user

