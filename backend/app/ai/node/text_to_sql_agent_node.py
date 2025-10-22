"""
Text-to-SQL Agent 节点定义
包含 Text-to-SQL Agent 工作流中的所有节点
"""
from typing import Callable

from app.ai.agent.text_to_sql_agent import TextToSQLState, TextToSQLAgent


class TextToSQLAgentNode:
    """Text-to-SQL Agent 节点集合"""
    
    def __init__(self, agent: TextToSQLAgent):
        """
        初始化节点集合
        
        Args:
            agent: TextToSQLAgent 实例
        """
        self.agent = agent
    
    def get_classify_node(self) -> Callable[[TextToSQLState], TextToSQLState]:
        """
        获取分类节点
        判断用户问题是否需要数据库查询
        """
        return self.agent.classify_question
    
    def get_generate_sql_node(self) -> Callable[[TextToSQLState], TextToSQLState]:
        """
        获取SQL生成节点
        根据用户问题和数据库schema生成SQL
        """
        return self.agent.generate_sql
    
    def get_execute_sql_node(self) -> Callable[[TextToSQLState], TextToSQLState]:
        """
        获取SQL执行节点
        执行生成的SQL查询
        """
        return self.agent.execute_sql
    
    def get_handle_error_node(self) -> Callable[[TextToSQLState], TextToSQLState]:
        """
        获取错误处理节点
        处理执行过程中的错误并决定是否重试
        """
        return self.agent.handle_error
    
    def get_explain_result_node(self) -> Callable[[TextToSQLState], TextToSQLState]:
        """
        获取结果解释节点
        将查询结果转换为自然语言解释
        """
        return self.agent.explain_result
    
    def get_should_retry_edge(self) -> Callable[[TextToSQLState], str]:
        """
        获取重试判断边
        决定是否应该重试
        """
        return self.agent.should_retry
    
    def get_should_query_database_edge(self) -> Callable[[TextToSQLState], str]:
        """
        获取数据库查询判断边
        决定是否需要查询数据库
        """
        return self.agent.should_query_database
    
    def get_should_execute_edge(self) -> Callable[[TextToSQLState], str]:
        """
        获取执行判断边
        决定是否执行SQL
        """
        return self.agent.should_execute
    
    @classmethod
    def create_from_agent(cls, agent: TextToSQLAgent) -> 'TextToSQLAgentNode':
        """
        从Agent实例创建节点集合
        
        Args:
            agent: TextToSQLAgent 实例
            
        Returns:
            TextToSQLAgentNode 实例
        """
        return cls(agent)

