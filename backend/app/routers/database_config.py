from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from ..core.database import get_db
from ..models.user import User
from ..models.robot import Robot
from ..models.database_config import DatabaseConfig, DatabaseMetadata
from ..schemas.database_config import (
    DatabaseConfigCreate,
    DatabaseConfigUpdate,
    DatabaseConfigResponse,
    DatabaseTestRequest,
    DatabaseTestResponse,
    DatabaseSchemaResponse,
    DatabaseMetadataCreate,
    DatabaseMetadataResponse
)
from ..dependencies import get_current_user
from ..services.database_service import DatabaseService
from ..core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/robots", tags=["数据库配置"])


def check_robot_permission(robot: Robot, current_user: User):
    """检查用户是否有权限配置机器人数据库"""
    if current_user.role == "admin":
        return True
    if robot.user_id == current_user.id:
        return True
    return False


@router.post("/{robot_id}/database", response_model=DatabaseConfigResponse, status_code=status.HTTP_201_CREATED)
def create_or_update_database_config(
    robot_id: int,
    config_data: DatabaseConfigCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建或更新机器人的数据库配置"""
    logger.info(f"💾 用户 {current_user.username} 配置机器人数据库: robot_id={robot_id}")
    
    # 检查机器人是否存在
    robot = db.query(Robot).filter(Robot.id == robot_id).first()
    if not robot:
        logger.warning(f"❌ 机器人不存在: robot_id={robot_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="机器人不存在"
        )
    
    # 检查权限
    if not check_robot_permission(robot, current_user):
        logger.warning(f"❌ 无权配置机器人数据库: robot_id={robot_id}, user={current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权配置该机器人的数据库"
        )
    
    # 加密密码
    encrypted_password = DatabaseService.encrypt_password(config_data.password)
    
    # 检查是否已存在配置
    existing_config = db.query(DatabaseConfig).filter(
        DatabaseConfig.robot_id == robot_id
    ).first()
    
    if existing_config:
        # 更新现有配置
        logger.info(f"🔄 更新现有数据库配置: config_id={existing_config.id}")
        existing_config.db_type = config_data.db_type
        existing_config.host = config_data.host
        existing_config.port = config_data.port
        existing_config.database_name = config_data.database_name
        existing_config.username = config_data.username
        existing_config.password = encrypted_password
        
        db.commit()
        db.refresh(existing_config)
        
        logger.info(f"✅ 数据库配置更新成功")
        return DatabaseConfigResponse.model_validate(existing_config)
    else:
        # 创建新配置
        new_config = DatabaseConfig(
            robot_id=robot_id,
            db_type=config_data.db_type,
            host=config_data.host,
            port=config_data.port,
            database_name=config_data.database_name,
            username=config_data.username,
            password=encrypted_password
        )
        
        db.add(new_config)
        db.commit()
        db.refresh(new_config)
        
        logger.info(f"✅ 数据库配置创建成功: config_id={new_config.id}")
        return DatabaseConfigResponse.model_validate(new_config)


@router.get("/{robot_id}/database", response_model=Optional[DatabaseConfigResponse])
def get_database_config(
    robot_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取机器人的数据库配置"""
    logger.info(f"🔍 用户 {current_user.username} 获取数据库配置: robot_id={robot_id}")
    
    # 检查机器人是否存在
    robot = db.query(Robot).filter(Robot.id == robot_id).first()
    if not robot:
        logger.warning(f"❌ 机器人不存在: robot_id={robot_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="机器人不存在"
        )
    
    # 检查权限
    if not check_robot_permission(robot, current_user):
        logger.warning(f"❌ 无权访问机器人数据库配置: robot_id={robot_id}, user={current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该机器人的数据库配置"
        )
    
    # 获取配置
    config = db.query(DatabaseConfig).filter(
        DatabaseConfig.robot_id == robot_id
    ).first()
    
    if not config:
        logger.info(f"ℹ️ 机器人暂无数据库配置")
        return None
    
    logger.info(f"✅ 成功获取数据库配置")
    return DatabaseConfigResponse.model_validate(config)


@router.delete("/{robot_id}/database")
def delete_database_config(
    robot_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除机器人的数据库配置"""
    logger.info(f"🗑️ 用户 {current_user.username} 删除数据库配置: robot_id={robot_id}")
    
    # 检查机器人是否存在
    robot = db.query(Robot).filter(Robot.id == robot_id).first()
    if not robot:
        logger.warning(f"❌ 机器人不存在: robot_id={robot_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="机器人不存在"
        )
    
    # 检查权限
    if not check_robot_permission(robot, current_user):
        logger.warning(f"❌ 无权删除机器人数据库配置: robot_id={robot_id}, user={current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除该机器人的数据库配置"
        )
    
    # 删除配置
    config = db.query(DatabaseConfig).filter(
        DatabaseConfig.robot_id == robot_id
    ).first()
    
    if not config:
        logger.warning(f"❌ 数据库配置不存在")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="数据库配置不存在"
        )
    
    db.delete(config)
    db.commit()
    
    logger.info(f"✅ 数据库配置删除成功")
    return {"message": "数据库配置删除成功"}


@router.post("/{robot_id}/database/test", response_model=DatabaseTestResponse)
def test_database_connection(
    robot_id: int,
    test_data: DatabaseTestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """测试数据库连接"""
    logger.info(f"🔌 用户 {current_user.username} 测试数据库连接: robot_id={robot_id}")
    
    # 检查机器人是否存在
    robot = db.query(Robot).filter(Robot.id == robot_id).first()
    if not robot:
        logger.warning(f"❌ 机器人不存在: robot_id={robot_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="机器人不存在"
        )
    
    # 检查权限
    if not check_robot_permission(robot, current_user):
        logger.warning(f"❌ 无权测试机器人数据库: robot_id={robot_id}, user={current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权测试该机器人的数据库"
        )
    
    # 测试连接
    success, message = DatabaseService.test_connection(
        db_type=test_data.db_type,
        host=test_data.host,
        port=test_data.port,
        database_name=test_data.database_name,
        username=test_data.username,
        password=test_data.password
    )
    
    return DatabaseTestResponse(success=success, message=message)


@router.get("/{robot_id}/database/schema", response_model=DatabaseSchemaResponse)
def get_database_schema(
    robot_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取数据库结构"""
    logger.info(f"📊 用户 {current_user.username} 获取数据库结构: robot_id={robot_id}")
    
    # 检查机器人是否存在
    robot = db.query(Robot).filter(Robot.id == robot_id).first()
    if not robot:
        logger.warning(f"❌ 机器人不存在: robot_id={robot_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="机器人不存在"
        )
    
    # 检查权限
    if not check_robot_permission(robot, current_user):
        logger.warning(f"❌ 无权访问机器人数据库: robot_id={robot_id}, user={current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该机器人的数据库"
        )
    
    # 获取数据库配置
    config = db.query(DatabaseConfig).filter(
        DatabaseConfig.robot_id == robot_id
    ).first()
    
    if not config:
        logger.warning(f"❌ 数据库配置不存在")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="请先配置数据库连接"
        )
    
    # 解密密码
    password = DatabaseService.decrypt_password(config.password)
    
    try:
        # 获取数据库结构
        tables = DatabaseService.get_database_schema(
            db_type=config.db_type,
            host=config.host,
            port=config.port,
            database_name=config.database_name,
            username=config.username,
            password=password
        )
        
        logger.info(f"✅ 成功获取数据库结构: {len(tables)} 个表")
        return DatabaseSchemaResponse(tables=tables)
        
    except Exception as e:
        logger.error(f"❌ 获取数据库结构失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{robot_id}/database/metadata", response_model=DatabaseMetadataResponse, status_code=status.HTTP_201_CREATED)
def save_database_metadata(
    robot_id: int,
    metadata_data: DatabaseMetadataCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """保存数据库表和字段的选择及描述信息"""
    logger.info(f"💾 用户 {current_user.username} 保存数据库元数据: robot_id={robot_id}")
    
    # 检查机器人是否存在
    robot = db.query(Robot).filter(Robot.id == robot_id).first()
    if not robot:
        logger.warning(f"❌ 机器人不存在: robot_id={robot_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="机器人不存在"
        )
    
    # 检查权限
    if not check_robot_permission(robot, current_user):
        logger.warning(f"❌ 无权保存机器人数据库元数据: robot_id={robot_id}, user={current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权配置该机器人的数据库"
        )
    
    # 转换为JSON格式
    tables_json = [table.model_dump() for table in metadata_data.tables]
    
    # 检查是否已存在元数据
    existing_metadata = db.query(DatabaseMetadata).filter(
        DatabaseMetadata.robot_id == robot_id
    ).first()
    
    if existing_metadata:
        # 更新现有元数据
        logger.info(f"🔄 更新现有数据库元数据: metadata_id={existing_metadata.id}")
        existing_metadata.tables_metadata = tables_json
        
        db.commit()
        db.refresh(existing_metadata)
        
        logger.info(f"✅ 数据库元数据更新成功")
        return DatabaseMetadataResponse(
            id=existing_metadata.id,
            robot_id=existing_metadata.robot_id,
            tables=metadata_data.tables,
            created_at=existing_metadata.created_at,
            updated_at=existing_metadata.updated_at
        )
    else:
        # 创建新元数据
        new_metadata = DatabaseMetadata(
            robot_id=robot_id,
            tables_metadata=tables_json
        )
        
        db.add(new_metadata)
        db.commit()
        db.refresh(new_metadata)
        
        logger.info(f"✅ 数据库元数据创建成功: metadata_id={new_metadata.id}")
        return DatabaseMetadataResponse(
            id=new_metadata.id,
            robot_id=new_metadata.robot_id,
            tables=metadata_data.tables,
            created_at=new_metadata.created_at,
            updated_at=new_metadata.updated_at
        )


@router.get("/{robot_id}/database/metadata", response_model=Optional[DatabaseMetadataResponse])
def get_database_metadata(
    robot_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取数据库表和字段的选择及描述信息"""
    logger.info(f"🔍 用户 {current_user.username} 获取数据库元数据: robot_id={robot_id}")
    
    # 检查机器人是否存在
    robot = db.query(Robot).filter(Robot.id == robot_id).first()
    if not robot:
        logger.warning(f"❌ 机器人不存在: robot_id={robot_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="机器人不存在"
        )
    
    # 检查权限
    if not check_robot_permission(robot, current_user):
        logger.warning(f"❌ 无权访问机器人数据库元数据: robot_id={robot_id}, user={current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问该机器人的数据库配置"
        )
    
    # 获取元数据
    metadata = db.query(DatabaseMetadata).filter(
        DatabaseMetadata.robot_id == robot_id
    ).first()
    
    if not metadata:
        logger.info(f"ℹ️ 机器人暂无数据库元数据")
        return None
    
    logger.info(f"✅ 成功获取数据库元数据")
    
    # 从 JSON 中解析表元数据
    from ..schemas.database_config import TableMetadata, ColumnMetadata
    tables = []
    for table_json in metadata.tables_metadata:
        columns = [ColumnMetadata(**col) for col in table_json.get('columns', [])]
        tables.append(TableMetadata(
            name=table_json['name'],
            description=table_json.get('description'),
            selected=table_json.get('selected', True),
            columns=columns
        ))
    
    return DatabaseMetadataResponse(
        id=metadata.id,
        robot_id=metadata.robot_id,
        tables=tables,
        created_at=metadata.created_at,
        updated_at=metadata.updated_at
    )

