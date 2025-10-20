"""
数据库迁移脚本执行器 - 002
用于执行数据库配置表的迁移
"""
import os
import sys
from pathlib import Path

# 添加父目录到路径，以便导入 app 模块
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine
from app.core.logger import get_logger

logger = get_logger(__name__)


def run_migration():
    """执行数据库迁移 002"""
    
    # 读取迁移 SQL 文件
    migration_file = Path(__file__).parent / "002_add_database_config_table.sql"
    
    if not migration_file.exists():
        logger.error(f"迁移文件不存在: {migration_file}")
        return False
    
    logger.info("开始执行数据库迁移 002...")
    logger.info(f"读取迁移文件: {migration_file}")
    
    try:
        # 读取 SQL 文件内容
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 执行迁移
        with engine.connect() as connection:
            # 开始事务
            trans = connection.begin()
            
            try:
                logger.info("执行迁移 SQL...")
                
                # 执行整个迁移脚本
                connection.execute(text(sql_content))
                
                # 提交事务
                trans.commit()
                logger.info("✅ 数据库迁移 002 成功完成！")
                
                # 验证迁移结果
                logger.info("验证迁移结果...")
                
                # 检查 database_configs 表
                result = connection.execute(text(
                    "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'database_configs')"
                ))
                table_exists = result.scalar()
                
                if table_exists:
                    logger.info("✅ database_configs 表已创建")
                    
                    # 检查外键约束
                    result = connection.execute(text(
                        "SELECT EXISTS (SELECT 1 FROM information_schema.table_constraints "
                        "WHERE table_name = 'database_configs' AND constraint_type = 'FOREIGN KEY')"
                    ))
                    fk_exists = result.scalar()
                    
                    if fk_exists:
                        logger.info("✅ 外键约束已创建")
                    else:
                        logger.warning("⚠️ 外键约束未找到")
                else:
                    logger.warning("⚠️ database_configs 表未找到")
                
                return True
                
            except Exception as e:
                # 回滚事务
                trans.rollback()
                logger.error(f"❌ 迁移执行失败: {str(e)}")
                logger.error("事务已回滚")
                return False
                
    except Exception as e:
        logger.error(f"❌ 读取或执行迁移文件失败: {str(e)}")
        return False


def rollback_migration():
    """回滚数据库迁移 002"""
    
    rollback_file = Path(__file__).parent / "rollback_002.sql"
    
    if not rollback_file.exists():
        logger.error(f"回滚文件不存在: {rollback_file}")
        return False
    
    logger.info("开始执行数据库回滚 002...")
    logger.warning("⚠️ 警告：这将删除所有数据库配置数据！")
    
    try:
        with open(rollback_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        with engine.connect() as connection:
            trans = connection.begin()
            
            try:
                logger.info("执行回滚 SQL...")
                connection.execute(text(sql_content))
                trans.commit()
                logger.info("✅ 数据库回滚 002 成功完成！")
                return True
                
            except Exception as e:
                trans.rollback()
                logger.error(f"❌ 回滚执行失败: {str(e)}")
                return False
                
    except Exception as e:
        logger.error(f"❌ 读取或执行回滚文件失败: {str(e)}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="数据库迁移工具 002")
    parser.add_argument(
        "--rollback",
        action="store_true",
        help="回滚迁移（警告：将删除所有数据库配置数据）"
    )
    
    args = parser.parse_args()
    
    if args.rollback:
        # 确认回滚操作
        print("⚠️ 警告：这将删除 database_configs 表和所有相关数据！")
        confirm = input("确定要继续吗？(yes/no): ")
        if confirm.lower() == 'yes':
            success = rollback_migration()
        else:
            print("回滚操作已取消")
            success = False
    else:
        success = run_migration()
    
    sys.exit(0 if success else 1)

