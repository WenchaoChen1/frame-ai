from pydantic import BaseModel, Field, SecretStr
from typing import Optional, Literal
from datetime import datetime


class DatabaseConfigBase(BaseModel):
    db_type: Literal['postgresql', 'mysql', 'mssql', 'databricks', 'redshift'] = Field(..., description="数据库类型")
    host: str = Field(..., min_length=1, description="数据库主机地址")
    port: int = Field(..., ge=1, le=65535, description="数据库端口")
    database_name: str = Field(..., min_length=1, description="数据库名称")
    username: str = Field(..., min_length=1, description="数据库用户名")


class DatabaseConfigCreate(DatabaseConfigBase):
    password: str = Field(..., min_length=1, description="数据库密码")


class DatabaseConfigUpdate(BaseModel):
    db_type: Optional[Literal['postgresql', 'mysql', 'mssql', 'databricks', 'redshift']] = None
    host: Optional[str] = Field(None, min_length=1)
    port: Optional[int] = Field(None, ge=1, le=65535)
    database_name: Optional[str] = Field(None, min_length=1)
    username: Optional[str] = Field(None, min_length=1)
    password: Optional[str] = Field(None, min_length=1)


class DatabaseConfigResponse(DatabaseConfigBase):
    id: int
    robot_id: int
    created_at: datetime
    updated_at: datetime
    # 不返回密码
    
    class Config:
        from_attributes = True


class DatabaseTestRequest(BaseModel):
    db_type: Literal['postgresql', 'mysql', 'mssql', 'databricks', 'redshift']
    host: str
    port: int
    database_name: str
    username: str
    password: str


class DatabaseTestResponse(BaseModel):
    success: bool
    message: str


class TableColumn(BaseModel):
    name: str
    type: str
    nullable: bool = True
    description: Optional[str] = None  # 字段自定义描述


class TableSchema(BaseModel):
    name: str
    columns: list[TableColumn]
    description: Optional[str] = None  # 表自定义描述


class DatabaseSchemaResponse(BaseModel):
    tables: list[TableSchema]


# 表和字段的选择和描述配置
class ColumnMetadata(BaseModel):
    name: str
    description: Optional[str] = None
    selected: bool = True


class TableMetadata(BaseModel):
    name: str
    description: Optional[str] = None
    selected: bool = True
    columns: list[ColumnMetadata]


class DatabaseMetadataCreate(BaseModel):
    tables: list[TableMetadata]


class DatabaseMetadataResponse(BaseModel):
    id: int
    robot_id: int
    tables: list[TableMetadata]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

