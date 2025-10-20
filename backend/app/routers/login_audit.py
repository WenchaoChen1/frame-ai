from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..core.database import get_db
from ..models.user import User
from ..models.login_audit import LoginAudit
from ..schemas.login_audit import LoginAuditResponse
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/login-audits", tags=["登录审计"])


def check_admin(current_user: User) -> User:
    """检查当前用户是否为管理员"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user


@router.get("", response_model=List[LoginAuditResponse])
def get_all_login_audits(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取所有登录审计记录（仅管理员）"""
    check_admin(current_user)
    
    audits = db.query(LoginAudit).order_by(
        LoginAudit.login_time.desc()
    ).offset(skip).limit(limit).all()
    
    return [LoginAuditResponse.model_validate(audit) for audit in audits]


@router.get("/me", response_model=List[LoginAuditResponse])
def get_my_login_audits(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的登录审计记录"""
    audits = db.query(LoginAudit).filter(
        LoginAudit.user_id == current_user.id
    ).order_by(
        LoginAudit.login_time.desc()
    ).offset(skip).limit(limit).all()
    
    return [LoginAuditResponse.model_validate(audit) for audit in audits]


@router.get("/user/{user_id}", response_model=List[LoginAuditResponse])
def get_user_login_audits(
    user_id: int,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取指定用户的登录审计记录（管理员可查看所有，普通用户只能查看自己的）"""
    # 只能查看自己的记录或管理员可以查看所有
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看该用户的登录记录"
        )
    
    audits = db.query(LoginAudit).filter(
        LoginAudit.user_id == user_id
    ).order_by(
        LoginAudit.login_time.desc()
    ).offset(skip).limit(limit).all()
    
    return [LoginAuditResponse.model_validate(audit) for audit in audits]

