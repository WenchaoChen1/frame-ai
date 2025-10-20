from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class QueryResult(BaseModel):
    """SQL 查询结果"""
    columns: List[str]
    rows: List[List[Any]]
    row_count: int


class SQLQueryRequest(BaseModel):
    """SQL 查询请求"""
    question: str
    conversation_id: int


class SQLQueryResponse(BaseModel):
    """SQL 查询响应"""
    needs_database: bool
    sql_query: Optional[str] = None
    query_result: Optional[QueryResult] = None
    explanation: Optional[str] = None
    error: Optional[str] = None


class SQLQueryLogResponse(BaseModel):
    """SQL 查询日志响应"""
    id: int
    conversation_id: int
    user_question: str
    generated_sql: Optional[str]
    query_result: Optional[dict]
    success: bool
    error_message: Optional[str]
    execution_time: float
    created_at: datetime
    
    class Config:
        from_attributes = True

