"""
Text-to-SQL AI Agent
使用 LangChain 和 LangGraph 实现的智能 SQL 生成和执行代理
"""
from typing import TypedDict, Annotated, Optional, AsyncGenerator
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
import json
import time

from app.core.logger import get_logger
from app.core.config import settings
from app.services.database_service import DatabaseService
from app.schemas.sql_query import QueryResult

logger = get_logger(__name__)


# 定义 State
class TextToSQLState(TypedDict):
    """Text-to-SQL Agent 状态"""
    user_question: str
    database_schema: str
    needs_database: Optional[bool]
    sql_query: Optional[str]
    query_result: Optional[QueryResult]
    explanation: Optional[str]
    error: Optional[str]
    retry_count: int
    
    # 数据库连接信息
    db_type: str
    host: str
    port: int
    database_name: str
    username: str
    password: str
    
    # AI 配置
    provider: str
    model: str


class TextToSQLAgent:
    """Text-to-SQL 智能代理"""
    
    def __init__(self):
        self.max_retries = 3
    
    def _get_llm(self, provider: str, model: str):
        """获取 LLM 实例"""
        if provider == "openai":
            return ChatOpenAI(
                model=model,
                api_key=settings.OPENAI_API_KEY,
                temperature=0
            )
        elif provider == "claude":
            return ChatAnthropic(
                model=model,
                api_key=settings.ANTHROPIC_API_KEY,
                temperature=0
            )
        else:
            # 默认使用 OpenAI
            return ChatOpenAI(
                model="gpt-3.5-turbo",
                api_key=settings.OPENAI_API_KEY,
                temperature=0
            )
    
    def classify_question(self, state: TextToSQLState) -> TextToSQLState:
        """判断用户问题是否需要数据库查询"""
        try:
            logger.info("🤔 正在判断是否需要查询数据库...")
            
            llm = self._get_llm(state["provider"], state["model"])
            
            system_prompt = """你是一个智能分类助手。你的任务是判断用户的问题是否需要查询数据库。

以下情况需要查询数据库：
- 询问具体数据、统计信息、数量等
- 需要从表中检索信息
- 询问某些条件下的记录

以下情况不需要查询数据库：
- 一般性问候、闲聊
- 询问数据库结构本身（不是数据）
- 询问如何使用系统
- 不涉及数据的问题

请只回答 YES 或 NO。
YES 表示需要查询数据库，NO 表示不需要。"""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"用户问题: {state['user_question']}\n\n这个问题需要查询数据库吗？")
            ]
            
            response = llm.invoke(messages)
            answer = response.content.strip().upper()
            
            needs_database = "YES" in answer
            
            logger.info(f"✅ 分类结果: {'需要' if needs_database else '不需要'}查询数据库")
            
            state["needs_database"] = needs_database
            return state
            
        except Exception as e:
            logger.error(f"❌ 分类问题失败: {str(e)}")
            state["error"] = f"分类问题失败: {str(e)}"
            state["needs_database"] = False
            return state
    
    def generate_sql(self, state: TextToSQLState) -> TextToSQLState:
        """根据用户问题和数据库 schema 生成 SQL"""
        try:
            logger.info("📝 正在生成 SQL 查询...")
            
            llm = self._get_llm(state["provider"], state["model"])
            
            system_prompt = f"""你是一个专业的 SQL 查询专家。根据用户的问题和数据库结构，生成准确的 SQL 查询语句。

{state['database_schema']}

要求：
1. 只生成 SELECT 查询语句
2. SQL 必须符合标准 SQL 语法
3. 使用正确的表名和字段名
4. 如果需要连接多个表，使用正确的 JOIN
5. 添加适当的 WHERE 条件和排序
6. 只返回 SQL 语句，不要有任何其他解释

请生成 SQL 查询："""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=state['user_question'])
            ]
            
            response = llm.invoke(messages)
            sql_query = response.content.strip()
            
            # 清理 SQL（移除可能的 markdown 代码块标记）
            if sql_query.startswith("```"):
                lines = sql_query.split("\n")
                sql_query = "\n".join(lines[1:-1]) if len(lines) > 2 else sql_query
            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
            
            logger.info(f"✅ 生成的 SQL: {sql_query}")
            
            state["sql_query"] = sql_query
            return state
            
        except Exception as e:
            logger.error(f"❌ 生成 SQL 失败: {str(e)}")
            state["error"] = f"生成 SQL 失败: {str(e)}"
            return state
    
    def execute_sql(self, state: TextToSQLState) -> TextToSQLState:
        """执行 SQL 查询"""
        try:
            logger.info("⚡ 正在执行 SQL 查询...")
            
            result = DatabaseService.execute_query(
                db_type=state["db_type"],
                host=state["host"],
                port=state["port"],
                database_name=state["database_name"],
                username=state["username"],
                password=state["password"],
                sql=state["sql_query"],
                timeout=30
            )
            
            logger.info(f"✅ SQL 执行成功: {result.row_count} 行")
            
            state["query_result"] = result
            state["error"] = None
            return state
            
        except Exception as e:
            logger.error(f"❌ SQL 执行失败: {str(e)}")
            state["error"] = f"SQL 执行失败: {str(e)}"
            return state
    
    def handle_error(self, state: TextToSQLState) -> TextToSQLState:
        """处理错误并决定是否重试"""
        state["retry_count"] += 1
        logger.warning(f"⚠️ 处理错误，重试次数: {state['retry_count']}/{self.max_retries}")
        
        if state["retry_count"] >= self.max_retries:
            logger.error(f"❌ 达到最大重试次数，放弃")
            state["explanation"] = f"抱歉，生成 SQL 查询时遇到了问题: {state['error']}"
        
        return state
    
    def explain_result(self, state: TextToSQLState) -> TextToSQLState:
        """将查询结果转换为自然语言解释"""
        try:
            logger.info("💬 正在生成结果解释...")
            
            llm = self._get_llm(state["provider"], state["model"])
            
            result = state["query_result"]
            
            # 构建结果摘要
            result_summary = f"""
用户问题: {state['user_question']}

执行的 SQL:
{state['sql_query']}

查询结果 ({result.row_count} 行):
列名: {', '.join(result.columns)}

前几行数据:
"""
            # 只显示前5行
            for i, row in enumerate(result.rows[:5]):
                result_summary += f"{i+1}. {row}\n"
            
            if result.row_count > 5:
                result_summary += f"... 还有 {result.row_count - 5} 行\n"
            
            system_prompt = """你是一个友好的数据分析助手。请根据 SQL 查询结果，用自然、友好的语言向用户解释结果。

要求：
1. 直接回答用户的问题
2. 用清晰、易懂的语言
3. 突出重要的发现或数据
4. 如果结果为空，友好地告知用户
5. 不要重复 SQL 语句本身"""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=result_summary)
            ]
            
            response = llm.invoke(messages)
            explanation = response.content.strip()
            
            logger.info(f"✅ 结果解释生成完成")
            
            state["explanation"] = explanation
            return state
            
        except Exception as e:
            logger.error(f"❌ 生成解释失败: {str(e)}")
            state["explanation"] = "查询已执行完成，请查看结果表格。"
            return state
    
    def should_retry(self, state: TextToSQLState) -> str:
        """决定是否应该重试"""
        if state.get("error") and state["retry_count"] < self.max_retries:
            return "retry"
        return "end"
    
    def should_query_database(self, state: TextToSQLState) -> str:
        """决定是否需要查询数据库"""
        if state.get("needs_database"):
            return "query"
        return "skip"
    
    def should_execute(self, state: TextToSQLState) -> str:
        """决定是否执行 SQL"""
        if state.get("sql_query") and not state.get("error"):
            return "execute"
        return "error"
    
    def create_graph(self) -> StateGraph:
        """创建 LangGraph 工作流"""
        workflow = StateGraph(TextToSQLState)
        
        # 添加节点
        workflow.add_node("classify", self.classify_question)
        workflow.add_node("generate_sql", self.generate_sql)
        workflow.add_node("execute_sql", self.execute_sql)
        workflow.add_node("handle_error", self.handle_error)
        workflow.add_node("explain_result", self.explain_result)
        
        # 设置入口点
        workflow.set_entry_point("classify")
        
        # 添加条件边
        workflow.add_conditional_edges(
            "classify",
            self.should_query_database,
            {
                "query": "generate_sql",
                "skip": END
            }
        )
        
        workflow.add_conditional_edges(
            "generate_sql",
            self.should_execute,
            {
                "execute": "execute_sql",
                "error": "handle_error"
            }
        )
        
        workflow.add_conditional_edges(
            "execute_sql",
            lambda state: "explain" if not state.get("error") else "error",
            {
                "explain": "explain_result",
                "error": "handle_error"
            }
        )
        
        workflow.add_conditional_edges(
            "handle_error",
            self.should_retry,
            {
                "retry": "generate_sql",
                "end": END
            }
        )
        
        workflow.add_edge("explain_result", END)
        
        return workflow.compile()
    
    async def run_stream(
        self,
        user_question: str,
        database_schema: str,
        db_config: dict,
        provider: str,
        model: str
    ) -> AsyncGenerator[dict, None]:
        """
        流式运行 Text-to-SQL Agent
        
        Args:
            user_question: 用户问题
            database_schema: 数据库结构描述
            db_config: 数据库连接配置
            provider: AI 提供商
            model: AI 模型
        
        Yields:
            流式事件 (type, data)
        """
        start_time = time.time()
        
        # 初始化状态
        initial_state: TextToSQLState = {
            "user_question": user_question,
            "database_schema": database_schema,
            "needs_database": None,
            "sql_query": None,
            "query_result": None,
            "explanation": None,
            "error": None,
            "retry_count": 0,
            "db_type": db_config["db_type"],
            "host": db_config["host"],
            "port": db_config["port"],
            "database_name": db_config["database_name"],
            "username": db_config["username"],
            "password": db_config["password"],
            "provider": provider,
            "model": model
        }
        
        try:
            # 创建图
            graph = self.create_graph()
            
            # 执行分类
            yield {"type": "status", "data": "正在分析问题..."}
            state = self.classify_question(initial_state)
            
            # 如果不需要数据库查询
            if not state.get("needs_database"):
                yield {
                    "type": "no_database_needed",
                    "data": {"message": "这个问题不需要查询数据库"}
                }
                return
            
            # 生成 SQL
            yield {"type": "status", "data": "正在生成 SQL..."}
            state = self.generate_sql(state)
            
            if state.get("error"):
                yield {"type": "error", "data": {"error": state["error"]}}
                return
            
            # 发送生成的 SQL
            yield {
                "type": "sql_generated",
                "data": {"sql": state["sql_query"]}
            }
            
            # 执行 SQL
            yield {"type": "query_executing", "data": {}}
            state = self.execute_sql(state)
            
            if state.get("error"):
                # 尝试重试
                for retry in range(self.max_retries):
                    logger.info(f"🔄 重试 {retry + 1}/{self.max_retries}")
                    yield {"type": "status", "data": f"查询失败，正在重试 ({retry + 1}/{self.max_retries})..."}
                    
                    state = self.generate_sql(state)
                    if state.get("error"):
                        continue
                    
                    yield {
                        "type": "sql_generated",
                        "data": {"sql": state["sql_query"]}
                    }
                    
                    state = self.execute_sql(state)
                    if not state.get("error"):
                        break
                
                # 如果仍然失败
                if state.get("error"):
                    yield {"type": "error", "data": {"error": state["error"]}}
                    return
            
            # 发送查询结果
            result = state["query_result"]
            yield {
                "type": "query_result",
                "data": {
                    "columns": result.columns,
                    "rows": result.rows,
                    "row_count": result.row_count
                }
            }
            
            # 生成解释
            yield {"type": "status", "data": "正在分析结果..."}
            state = self.explain_result(state)
            
            execution_time = time.time() - start_time
            
            # 返回最终结果
            yield {
                "type": "complete",
                "data": {
                    "sql": state["sql_query"],
                    "result": {
                        "columns": result.columns,
                        "rows": result.rows,
                        "row_count": result.row_count
                    },
                    "explanation": state["explanation"],
                    "execution_time": execution_time
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Agent 执行失败: {str(e)}")
            yield {"type": "error", "data": {"error": str(e)}}


# 全局 Agent 实例
text_to_sql_agent = TextToSQLAgent()

