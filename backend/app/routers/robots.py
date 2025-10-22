from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.user import User
from app.models.robot import Robot
from app.models.conversation import Conversation
from app.models.knowledge_base import KnowledgeBase
from app.schemas.robot import RobotCreate, RobotUpdate, RobotResponse, RobotListResponse
from app.schemas.conversation import ConversationListResponse
from app.schemas.knowledge_base import RobotKnowledgeBaseAssociate, RobotKnowledgeBaseResponse, KnowledgeBaseListResponse
from app.dependencies import get_current_user
from app.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/robots", tags=["机器人管理"])


def check_robot_permission(robot: Robot, current_user: User, allow_global: bool = True):
    """检查用户是否有权限操作机器人"""
    # 管理员可以操作所有机器人
    if current_user.role == "admin":
        return True
    
    # 创建者可以操作自己的机器人
    if robot.user_id == current_user.id:
        return True
    
    # 全局机器人可以被所有人查看
    if allow_global and robot.is_global:
        return True
    
    return False


@router.get("", response_model=List[RobotListResponse])
def get_robots(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取机器人列表（全局机器人 + 当前用户创建的私有机器人）"""
    logger.info(f"🤖 用户 {current_user.username} 获取机器人列表")
    
    # 获取全局机器人 + 当前用户创建的机器人
    robots = db.query(Robot).filter(
        (Robot.is_global == True) | (Robot.user_id == current_user.id)
    ).order_by(Robot.created_at.desc()).all()
    
    logger.info(f"✅ 返回 {len(robots)} 个机器人")
    return [RobotListResponse.model_validate(robot) for robot in robots]


@router.get("/{robot_id}", response_model=RobotResponse)
def get_robot(
    robot_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取机器人详情"""
    logger.info(f"🔍 用户 {current_user.username} 获取机器人详情: robot_id={robot_id}")
    
    robot = db.query(Robot).filter(Robot.id == robot_id).first()
    
    if not robot:
        logger.warning(f"❌ 机器人不存在: robot_id={robot_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="机器人不存在"
        )
    
    # 检查权限
    if not check_robot_permission(robot, current_user, allow_global=True):
        logger.warning(f"❌ 无权访问机器人: robot_id={robot_id}, user={current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该机器人"
        )
    
    logger.info(f"✅ 机器人查询成功: {robot.name}")
    return RobotResponse.model_validate(robot)


@router.post("", response_model=RobotResponse, status_code=status.HTTP_201_CREATED)
def create_robot(
    robot_data: RobotCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新机器人"""
    logger.info(f"📝 用户 {current_user.username} 创建新机器人: {robot_data.name}")
    
    # 只有管理员可以创建全局机器人
    if robot_data.is_global and current_user.role != "admin":
        logger.warning(f"❌ 非管理员尝试创建全局机器人: user={current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以创建全局机器人"
        )
    
    new_robot = Robot(
        name=robot_data.name,
        description=robot_data.description,
        avatar=robot_data.avatar,
        default_provider=robot_data.default_provider,
        default_model=robot_data.default_model,
        system_prompt=robot_data.system_prompt,
        temperature=robot_data.temperature,
        max_tokens=robot_data.max_tokens,
        is_global=robot_data.is_global,
        user_id=current_user.id
    )
    
    db.add(new_robot)
    db.commit()
    db.refresh(new_robot)
    
    logger.info(f"✅ 机器人创建成功: robot_id={new_robot.id}")
    return RobotResponse.model_validate(new_robot)


@router.put("/{robot_id}", response_model=RobotResponse)
def update_robot(
    robot_id: int,
    robot_data: RobotUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新机器人"""
    logger.info(f"🔄 用户 {current_user.username} 更新机器人: robot_id={robot_id}")
    
    robot = db.query(Robot).filter(Robot.id == robot_id).first()
    
    if not robot:
        logger.warning(f"❌ 机器人不存在: robot_id={robot_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="机器人不存在"
        )
    
    # 检查权限（只允许创建者和管理员修改）
    if not check_robot_permission(robot, current_user, allow_global=False):
        logger.warning(f"❌ 无权修改机器人: robot_id={robot_id}, user={current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改该机器人"
        )
    
    # 只有管理员可以修改is_global
    if robot_data.is_global is not None and robot_data.is_global != robot.is_global:
        if current_user.role != "admin":
            logger.warning(f"❌ 非管理员尝试修改全局属性: user={current_user.username}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有管理员可以修改全局属性"
            )
    
    # 更新字段
    update_data = robot_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(robot, field, value)
    
    db.commit()
    db.refresh(robot)
    
    logger.info(f"✅ 机器人更新成功: robot_id={robot_id}")
    return RobotResponse.model_validate(robot)


@router.delete("/{robot_id}")
def delete_robot(
    robot_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除机器人"""
    logger.info(f"🗑️ 用户 {current_user.username} 删除机器人: robot_id={robot_id}")
    
    robot = db.query(Robot).filter(Robot.id == robot_id).first()
    
    if not robot:
        logger.warning(f"❌ 机器人不存在: robot_id={robot_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="机器人不存在"
        )
    
    # 检查权限（只允许创建者和管理员删除）
    if not check_robot_permission(robot, current_user, allow_global=False):
        logger.warning(f"❌ 无权删除机器人: robot_id={robot_id}, user={current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除该机器人"
        )
    
    db.delete(robot)
    db.commit()
    
    logger.info(f"✅ 机器人删除成功: robot_id={robot_id}")
    return {"message": "机器人删除成功"}


@router.get("/{robot_id}/conversations", response_model=List[ConversationListResponse])
def get_robot_conversations(
    robot_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取机器人的对话历史"""
    logger.info(f"📋 用户 {current_user.username} 获取机器人对话列表: robot_id={robot_id}")
    
    robot = db.query(Robot).filter(Robot.id == robot_id).first()
    
    if not robot:
        logger.warning(f"❌ 机器人不存在: robot_id={robot_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="机器人不存在"
        )
    
    # 检查权限
    if not check_robot_permission(robot, current_user, allow_global=True):
        logger.warning(f"❌ 无权访问机器人: robot_id={robot_id}, user={current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该机器人"
        )
    
    # 只返回当前用户的对话
    conversations = db.query(Conversation).filter(
        Conversation.robot_id == robot_id,
        Conversation.user_id == current_user.id
    ).order_by(Conversation.updated_at.desc()).all()
    
    logger.info(f"✅ 返回 {len(conversations)} 个对话")
    return [ConversationListResponse.model_validate(conv) for conv in conversations]


@router.post("/{robot_id}/knowledge-bases", response_model=RobotKnowledgeBaseResponse)
def associate_knowledge_bases(
    robot_id: int,
    request: RobotKnowledgeBaseAssociate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """关联知识库到机器人"""
    logger.info(f"🔗 用户 {current_user.username} 关联知识库到机器人: robot_id={robot_id}")
    
    robot = db.query(Robot).filter(Robot.id == robot_id).first()
    
    if not robot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="机器人不存在"
        )
    
    # 检查权限
    if not check_robot_permission(robot, current_user, allow_global=False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改该机器人"
        )
    
    # 验证知识库是否存在且用户有权限访问
    knowledge_bases = []
    for kb_id in request.knowledge_base_ids:
        kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
        if not kb:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"知识库 {kb_id} 不存在"
            )
        if kb.user_id != current_user.id and not kb.is_public:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"无权访问知识库 {kb_id}"
            )
        knowledge_bases.append(kb)
    
    # 清除现有关联并添加新关联
    robot.knowledge_bases.clear()
    robot.knowledge_bases.extend(knowledge_bases)
    
    db.commit()
    db.refresh(robot)
    
    logger.info(f"✅ 成功关联 {len(knowledge_bases)} 个知识库到机器人 {robot_id}")
    
    return RobotKnowledgeBaseResponse(
        robot_id=robot.id,
        knowledge_bases=[KnowledgeBaseListResponse.model_validate(kb) for kb in robot.knowledge_bases]
    )


@router.delete("/{robot_id}/knowledge-bases/{kb_id}")
def disassociate_knowledge_base(
    robot_id: int,
    kb_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """取消机器人与知识库的关联"""
    logger.info(f"🔓 用户 {current_user.username} 取消关联: robot_id={robot_id}, kb_id={kb_id}")
    
    robot = db.query(Robot).filter(Robot.id == robot_id).first()
    
    if not robot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="机器人不存在"
        )
    
    # 检查权限
    if not check_robot_permission(robot, current_user, allow_global=False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改该机器人"
        )
    
    # 查找并移除关联
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    if kb and kb in robot.knowledge_bases:
        robot.knowledge_bases.remove(kb)
        db.commit()
        logger.info(f"✅ 成功取消关联: robot_id={robot_id}, kb_id={kb_id}")
    
    return {"message": "关联已取消"}


@router.get("/{robot_id}/knowledge-bases", response_model=RobotKnowledgeBaseResponse)
def get_robot_knowledge_bases(
    robot_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取机器人关联的知识库列表"""
    logger.info(f"📚 用户 {current_user.username} 获取机器人关联的知识库: robot_id={robot_id}")
    
    robot = db.query(Robot).filter(Robot.id == robot_id).first()
    
    if not robot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="机器人不存在"
        )
    
    # 检查权限
    if not check_robot_permission(robot, current_user, allow_global=True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该机器人"
        )
    
    logger.info(f"✅ 返回 {len(robot.knowledge_bases)} 个关联的知识库")
    
    return RobotKnowledgeBaseResponse(
        robot_id=robot.id,
        knowledge_bases=[KnowledgeBaseListResponse.model_validate(kb) for kb in robot.knowledge_bases]
    )

