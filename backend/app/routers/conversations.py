from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..core.database import get_db
from ..models.user import User
from ..models.conversation import Conversation
from ..models.robot import Robot
from ..schemas.conversation import ConversationCreate, ConversationResponse, ConversationListResponse
from ..dependencies import get_current_user
from ..core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/conversations", tags=["会话"])


@router.post("", response_model=ConversationResponse)
def create_conversation(
    conversation_data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新会话"""
    logger.info(f"📝 用户 {current_user.username} 创建新会话: {conversation_data.title}")
    
    # 如果指定了机器人，验证机器人是否存在且用户有权访问
    if conversation_data.robot_id:
        robot = db.query(Robot).filter(Robot.id == conversation_data.robot_id).first()
        if not robot:
            logger.warning(f"❌ 机器人不存在: robot_id={conversation_data.robot_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="指定的机器人不存在"
            )
        
        # 检查用户是否有权使用该机器人（全局机器人或自己创建的）
        if not robot.is_global and robot.user_id != current_user.id:
            logger.warning(f"❌ 无权使用机器人: robot_id={conversation_data.robot_id}, user={current_user.username}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权使用该机器人"
            )
    
    new_conversation = Conversation(
        user_id=current_user.id,
        title=conversation_data.title,
        robot_id=conversation_data.robot_id
    )
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)
    
    logger.info(f"✅ 会话创建成功: conversation_id={new_conversation.id}")
    return ConversationResponse.model_validate(new_conversation)


@router.get("", response_model=List[ConversationListResponse])
def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的所有会话"""
    logger.info(f"📋 用户 {current_user.username} 获取会话列表")
    
    conversations = db.query(Conversation)\
        .filter(Conversation.user_id == current_user.id)\
        .order_by(Conversation.updated_at.desc())\
        .all()
    
    logger.info(f"✅ 返回 {len(conversations)} 个会话")
    return [ConversationListResponse.model_validate(conv) for conv in conversations]


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取指定会话及其消息"""
    logger.info(f"🔍 用户 {current_user.username} 获取会话详情: conversation_id={conversation_id}")
    
    conversation = db.query(Conversation)\
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )\
        .first()
    
    if not conversation:
        logger.warning(f"❌ 会话不存在: conversation_id={conversation_id}, user={current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    logger.info(f"✅ 会话查询成功: {conversation.title}")
    return ConversationResponse.model_validate(conversation)


@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除会话"""
    logger.info(f"🗑️ 用户 {current_user.username} 删除会话: conversation_id={conversation_id}")
    
    conversation = db.query(Conversation)\
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )\
        .first()
    
    if not conversation:
        logger.warning(f"❌ 会话不存在: conversation_id={conversation_id}, user={current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    db.delete(conversation)
    db.commit()
    
    logger.info(f"✅ 会话删除成功: {conversation.title}")
    return {"message": "会话已删除"}


@router.patch("/{conversation_id}/title")
def update_conversation_title(
    conversation_id: int,
    title: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新会话标题"""
    logger.info(f"✏️ 用户 {current_user.username} 更新会话标题: conversation_id={conversation_id}, new_title={title}")
    
    conversation = db.query(Conversation)\
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )\
        .first()
    
    if not conversation:
        logger.warning(f"❌ 会话不存在: conversation_id={conversation_id}, user={current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    old_title = conversation.title
    conversation.title = title
    db.commit()
    
    logger.info(f"✅ 标题更新成功: {old_title} -> {title}")
    return {"message": "标题已更新", "title": title}

