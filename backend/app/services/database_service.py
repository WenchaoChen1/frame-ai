"""
数据库连接服务
支持 PostgreSQL, MySQL, MsSQL, Databricks, Redshift 数据库的连接、测试和结构查询
"""
from typing import List, Dict, Any, Tuple
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from cryptography.fernet import Fernet
import os
import base64
import sqlparse
from ..core.logger import get_logger
from ..core.config import settings
from ..schemas.database_config import TableSchema, TableColumn
from ..schemas.sql_query import QueryResult

logger = get_logger(__name__)

# 加密密钥 - 从配置中读取
def get_cipher_suite():
    """获取加密套件，确保密钥格式正确"""
    key = settings.DB_ENCRYPTION_KEY
    
    # 确保密钥是有效的 Fernet 密钥格式（32字节 base64编码）
    try:
        # 如果密钥已经是有效的 Fernet 密钥，直接使用
        cipher = Fernet(key.encode() if isinstance(key, str) else key)
        return cipher
    except:
        # 如果不是有效的 Fernet 密钥，生成一个新的
        logger.warning("配置的 DB_ENCRYPTION_KEY 无效，生成新密钥")
        new_key = Fernet.generate_key()
        logger.info(f"新的加密密钥（请添加到配置中）: {new_key.decode()}")
        return Fernet(new_key)

cipher_suite = get_cipher_suite()


class DatabaseService:
    """数据库连接服务"""
    
    @staticmethod
    def encrypt_password(password: str) -> str:
        """加密密码"""
        return cipher_suite.encrypt(password.encode()).decode()
    
    @staticmethod
    def decrypt_password(encrypted_password: str) -> str:
        """解密密码"""
        return cipher_suite.decrypt(encrypted_password.encode()).decode()
    
    @staticmethod
    def build_connection_url(
        db_type: str,
        host: str,
        port: int,
        database_name: str,
        username: str,
        password: str
    ) -> str:
        """构建数据库连接URL"""
        if db_type == 'postgresql':
            driver = 'postgresql+psycopg2'
        elif db_type == 'mysql':
            driver = 'mysql+pymysql'
        elif db_type == 'mssql':
            driver = 'mssql+pymssql'
        elif db_type == 'databricks':
            driver = 'databricks+connector'
        elif db_type == 'redshift':
            driver = 'redshift+psycopg2'
        else:
            raise ValueError(f"不支持的数据库类型: {db_type}")
        
        # URL编码密码中的特殊字符
        from urllib.parse import quote_plus
        encoded_password = quote_plus(password)
        encoded_username = quote_plus(username)
        
        return f"{driver}://{encoded_username}:{encoded_password}@{host}:{port}/{database_name}"
    
    @staticmethod
    def test_connection(
        db_type: str,
        host: str,
        port: int,
        database_name: str,
        username: str,
        password: str
    ) -> tuple[bool, str]:
        """
        测试数据库连接
        返回: (成功状态, 消息)
        """
        engine = None
        try:
            logger.info(f"🔌 开始测试数据库连接: {db_type}://{host}:{port}/{database_name}")
            
            connection_url = DatabaseService.build_connection_url(
                db_type, host, port, database_name, username, password
            )
            
            # 创建引擎，设置超时
            engine = create_engine(
                connection_url,
                pool_pre_ping=True,
                pool_recycle=3600,
                connect_args={
                    'connect_timeout': 10
                }
            )
            
            # 测试连接
            with engine.connect() as conn:
                # 执行简单查询验证连接
                if db_type in ['postgresql', 'redshift']:
                    result = conn.execute(text("SELECT version()"))
                elif db_type == 'mysql':
                    result = conn.execute(text("SELECT VERSION()"))
                elif db_type == 'mssql':
                    result = conn.execute(text("SELECT @@VERSION"))
                elif db_type == 'databricks':
                    result = conn.execute(text("SELECT 1"))
                
                version = result.fetchone()[0] if db_type != 'databricks' else 'Databricks'
                logger.info(f"✅ 数据库连接成功: {str(version)[:50]}")
                return True, "数据库连接成功"
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ 数据库连接失败: {error_msg}")
            return False, f"连接失败: {error_msg}"
        
        finally:
            if engine:
                engine.dispose()
    
    @staticmethod
    def get_database_schema(
        db_type: str,
        host: str,
        port: int,
        database_name: str,
        username: str,
        password: str
    ) -> List[TableSchema]:
        """
        获取数据库结构（表和字段信息）
        """
        engine = None
        try:
            logger.info(f"📊 开始获取数据库结构: {db_type}://{host}:{port}/{database_name}")
            
            connection_url = DatabaseService.build_connection_url(
                db_type, host, port, database_name, username, password
            )
            
            engine = create_engine(
                connection_url,
                pool_pre_ping=True,
                connect_args={'connect_timeout': 10}
            )
            
            tables = []
            
            with engine.connect() as conn:
                inspector = inspect(engine)
                table_names = inspector.get_table_names()
                
                logger.info(f"📋 找到 {len(table_names)} 个表")
                
                for table_name in table_names[:100]:  # 限制最多100个表
                    columns = []
                    
                    for column in inspector.get_columns(table_name):
                        columns.append(TableColumn(
                            name=column['name'],
                            type=str(column['type']),
                            nullable=column.get('nullable', True)
                        ))
                    
                    tables.append(TableSchema(
                        name=table_name,
                        columns=columns
                    ))
                
                logger.info(f"✅ 成功获取数据库结构: {len(tables)} 个表")
                return tables
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ 获取数据库结构失败: {error_msg}")
            raise Exception(f"获取数据库结构失败: {error_msg}")
        
        finally:
            if engine:
                engine.dispose()
    
    @staticmethod
    def get_encrypted_config(
        db_type: str,
        host: str,
        port: int,
        database_name: str,
        username: str,
        password: str
    ) -> Dict[str, Any]:
        """
        返回加密后的数据库配置
        """
        return {
            'db_type': db_type,
            'host': host,
            'port': port,
            'database_name': database_name,
            'username': username,
            'password': DatabaseService.encrypt_password(password)
        }
    
    @staticmethod
    def validate_sql_safety(sql: str) -> Tuple[bool, str]:
        """
        验证 SQL 语句的安全性（只允许 SELECT 语句）
        返回: (是否安全, 错误信息)
        """
        try:
            # 解析 SQL
            parsed = sqlparse.parse(sql)
            
            if not parsed:
                return False, "无法解析 SQL 语句"
            
            # 检查每个语句
            for statement in parsed:
                # 获取语句类型
                stmt_type = statement.get_type()
                
                # 只允许 SELECT 语句
                if stmt_type != 'SELECT':
                    return False, f"不允许执行 {stmt_type} 语句，只支持 SELECT 查询"
                
                # 检查是否包含危险关键字
                sql_upper = sql.upper()
                dangerous_keywords = [
                    'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 
                    'CREATE', 'TRUNCATE', 'REPLACE', 'GRANT', 'REVOKE'
                ]
                
                for keyword in dangerous_keywords:
                    if keyword in sql_upper:
                        return False, f"SQL 中包含不允许的关键字: {keyword}"
            
            return True, ""
            
        except Exception as e:
            logger.error(f"❌ SQL 验证失败: {str(e)}")
            return False, f"SQL 验证失败: {str(e)}"
    
    @staticmethod
    def execute_query(
        db_type: str,
        host: str,
        port: int,
        database_name: str,
        username: str,
        password: str,
        sql: str,
        timeout: int = 30
    ) -> QueryResult:
        """
        执行 SQL 查询并返回结果
        参数:
            timeout: 查询超时时间（秒），默认30秒
        返回:
            QueryResult: 包含列名、数据行和行数
        """
        engine = None
        try:
            logger.info(f"🔍 执行 SQL 查询: {sql[:100]}...")
            
            # 验证 SQL 安全性
            is_safe, error_msg = DatabaseService.validate_sql_safety(sql)
            if not is_safe:
                logger.error(f"❌ SQL 安全验证失败: {error_msg}")
                raise ValueError(error_msg)
            
            # 构建连接
            connection_url = DatabaseService.build_connection_url(
                db_type, host, port, database_name, username, password
            )
            
            engine = create_engine(
                connection_url,
                pool_pre_ping=True,
                connect_args={'connect_timeout': timeout}
            )
            
            with engine.connect() as conn:
                # 设置查询超时
                if db_type in ['postgresql', 'redshift']:
                    conn.execute(text(f"SET statement_timeout = {timeout * 1000}"))  # 毫秒
                elif db_type == 'mysql':
                    conn.execute(text(f"SET SESSION MAX_EXECUTION_TIME={timeout * 1000}"))
                
                # 执行查询
                result = conn.execute(text(sql))
                
                # 获取列名
                columns = list(result.keys())
                
                # 获取数据（限制最多1000行）
                rows = []
                for i, row in enumerate(result):
                    if i >= 1000:
                        logger.warning("⚠️ 查询结果超过1000行，已截断")
                        break
                    rows.append(list(row))
                
                row_count = len(rows)
                
                logger.info(f"✅ 查询执行成功: {row_count} 行")
                
                return QueryResult(
                    columns=columns,
                    rows=rows,
                    row_count=row_count
                )
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ SQL 查询执行失败: {error_msg}")
            raise Exception(f"查询执行失败: {error_msg}")
        
        finally:
            if engine:
                engine.dispose()
    
    @staticmethod
    def format_schema_for_prompt(tables_metadata: List[Dict[str, Any]]) -> str:
        """
        将数据库 metadata 格式化为 AI 可理解的文本
        参数:
            tables_metadata: 表元数据列表（来自 DatabaseMetadata.tables_metadata）
        返回:
            格式化的 schema 文本
        """
        schema_text = "数据库表结构:\n\n"
        
        for table in tables_metadata:
            # 只包含选中的表
            if not table.get('selected', True):
                continue
            
            table_name = table.get('name', '')
            table_desc = table.get('description', '')
            
            schema_text += f"表名: {table_name}\n"
            if table_desc:
                schema_text += f"说明: {table_desc}\n"
            
            schema_text += "字段:\n"
            
            for column in table.get('columns', []):
                # 只包含选中的字段
                if not column.get('selected', True):
                    continue
                
                col_name = column.get('name', '')
                col_type = column.get('type', '')
                col_desc = column.get('description', '')
                col_nullable = column.get('nullable', True)
                
                schema_text += f"  - {col_name} ({col_type})"
                if not col_nullable:
                    schema_text += " NOT NULL"
                if col_desc:
                    schema_text += f" - {col_desc}"
                schema_text += "\n"
            
            schema_text += "\n"
        
        return schema_text

