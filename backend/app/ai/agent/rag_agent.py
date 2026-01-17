"""
RAG (Retrieval-Augmented Generation) Agent
使用 LangGraph 构建的 RAG 工作流
"""
from typing import TypedDict, List, Optional, AsyncGenerator
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from sqlalchemy.orm import Session
import time

from app.core.logger import get_logger
from app.core.config import settings
from app.models.knowledge_base import KnowledgeBase
from app.ai.retrievers import RetrievalService
from app.ai.vector_stores import Document

logger = get_logger(__name__)


# 定义 State
class RAGState(TypedDict):
    """RAG Agent 状态"""
    user_question: str
    rewritten_queries: Optional[List[str]]
    retrieved_docs: Optional[List[Document]]
    reranked_docs: Optional[List[Document]]
    generated_answer: Optional[str]
    sources: Optional[List[dict]]
    error: Optional[str]
    
    # 配置
    knowledge_base_ids: List[int]
    provider: str
    model: str
    temperature: float
    
    # 控制标志
    enable_query_rewrite: bool
    enable_reranking: bool


class RAGAgent:
    """RAG 智能代理"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _get_llm(self, provider: str, model: str, temperature: float = 0.7):
        """获取 LLM 实例"""
        if provider == "openai":
            return ChatOpenAI(
                model=model,
                api_key=settings.OPENAI_API_KEY,
                temperature=temperature
            )
        elif provider == "claude":
            return ChatAnthropic(
                model=model,
                api_key=settings.ANTHROPIC_API_KEY,
                temperature=temperature
            )
        else:
            return ChatOpenAI(
                model="gpt-3.5-turbo",
                api_key=settings.OPENAI_API_KEY,
                temperature=temperature
            )
    
    async def rewrite_query(self, state: RAGState) -> RAGState:
        """
        查询重写节点
        将用户查询改写为更适合检索的多个查询
        """
        try:
            if not state["enable_query_rewrite"]:
                logger.info("查询重写已禁用，跳过")
                state["rewritten_queries"] = [state["user_question"]]
                return state
            
            logger.info("🔄 正在重写查询...")
            
            llm = self._get_llm(state["provider"], state["model"], temperature=0.3)
            
            system_prompt = """你是一个查询重写专家。你的任务是将用户的问题改写为 2-3 个不同角度的搜索查询，以提高检索效果。

要求：
1. 保持原问题的核心意图
2. 从不同角度表达同一个问题
3. 使用同义词和相关术语
4. 每个查询应该简洁明了
5. 用换行符分隔每个查询

示例：
原问题：如何提高 Python 代码性能？
重写：
1. Python 性能优化方法
2. 提升 Python 程序运行速度的技巧
3. Python 代码优化最佳实践"""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"请重写以下问题：\n{state['user_question']}")
            ]
            
            response = llm.invoke(messages)
            rewritten_text = response.content.strip()
            
            # 解析重写的查询
            queries = []
            for line in rewritten_text.split('\n'):
                line = line.strip()
                # 移除序号
                if line and len(line) > 2:
                    # 移除开头的数字和标点
                    import re
                    clean_line = re.sub(r'^\d+[\.\)、]\s*', '', line)
                    if clean_line:
                        queries.append(clean_line)
            
            # 确保至少包含原问题
            if not queries:
                queries = [state["user_question"]]
            elif state["user_question"] not in queries:
                queries.insert(0, state["user_question"])
            
            state["rewritten_queries"] = queries[:3]  # 最多3个查询
            logger.info(f"✅ 查询重写完成，生成 {len(state['rewritten_queries'])} 个查询")
            
            return state
            
        except Exception as e:
            logger.error(f"❌ 查询重写失败: {e}")
            state["rewritten_queries"] = [state["user_question"]]
            return state
    
    async def retrieve_documents(self, state: RAGState) -> RAGState:
        """
        检索节点
        从知识库中检索相关文档
        """
        try:
            logger.info("🔍 正在检索相关文档...")
            
            queries = state["rewritten_queries"] or [state["user_question"]]
            all_docs = []
            
            # 对每个查询进行检索
            for query in queries:
                docs = await RetrievalService.search_multiple_knowledge_bases(
                    db=self.db,
                    knowledge_base_ids=state["knowledge_base_ids"],
                    query=query,
                    top_k=settings.TOP_K_RETRIEVAL,
                    use_hybrid=True
                )
                all_docs.extend(docs)
            
            # 去重（基于 content）
            seen_contents = set()
            unique_docs = []
            for doc in all_docs:
                if doc.content not in seen_contents:
                    seen_contents.add(doc.content)
                    unique_docs.append(doc)
            
            # 按分数排序并限制数量
            unique_docs.sort(key=lambda x: x.score or 0, reverse=True)
            unique_docs = unique_docs[:settings.TOP_K_RETRIEVAL * 2]
            
            state["retrieved_docs"] = unique_docs
            logger.info(f"✅ 检索完成，找到 {len(unique_docs)} 个相关文档")
            
            return state
            
        except Exception as e:
            logger.error(f"❌ 检索失败: {e}")
            state["error"] = f"检索失败: {str(e)}"
            state["retrieved_docs"] = []
            return state
    
    async def rerank_documents(self, state: RAGState) -> RAGState:
        """
        重排序节点
        使用 LLM 对检索结果进行重排序
        """
        try:
            if not state["enable_reranking"] or not state["retrieved_docs"]:
                logger.info("重排序已禁用或无文档，跳过")
                state["reranked_docs"] = state["retrieved_docs"][:settings.TOP_K_RERANK]
                return state
            
            logger.info("📊 正在重排序文档...")
            
            # 简化版本：基于 LLM 的相关性评分
            llm = self._get_llm(state["provider"], state["model"], temperature=0)
            
            scored_docs = []
            for doc in state["retrieved_docs"][:settings.TOP_K_RETRIEVAL]:
                try:
                    system_prompt = """你是一个相关性评分专家。请评估文档与问题的相关性，给出 0-10 的分数。
只返回数字分数，不要有任何解释。"""
                    
                    messages = [
                        SystemMessage(content=system_prompt),
                        HumanMessage(content=f"问题: {state['user_question']}\n\n文档: {doc.content[:500]}\n\n相关性分数:")
                    ]
                    
                    response = llm.invoke(messages)
                    score_text = response.content.strip()
                    
                    # 提取数字
                    import re
                    match = re.search(r'\d+', score_text)
                    if match:
                        score = int(match.group())
                        scored_docs.append((doc, score))
                    else:
                        scored_docs.append((doc, 5))  # 默认分数
                        
                except Exception as e:
                    logger.warning(f"文档评分失败: {e}")
                    scored_docs.append((doc, 5))
            
            # 按分数排序
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            state["reranked_docs"] = [doc for doc, score in scored_docs[:settings.TOP_K_RERANK]]
            
            logger.info(f"✅ 重排序完成，保留前 {len(state['reranked_docs'])} 个文档")
            
            return state
            
        except Exception as e:
            logger.error(f"❌ 重排序失败: {e}")
            state["reranked_docs"] = state["retrieved_docs"][:settings.TOP_K_RERANK]
            return state
    
    async def generate_answer(self, state: RAGState) -> RAGState:
        """
        生成答案节点
        基于检索到的文档生成回答
        """
        try:
            logger.info("💡 正在生成答案...")
            
            docs = state["reranked_docs"] or state["retrieved_docs"] or []
            
            if not docs:
                state["generated_answer"] = "抱歉，我在知识库中没有找到相关信息来回答您的问题。"
                state["sources"] = []
                return state
            
            # 构建上下文
            context_parts = []
            sources = []
            
            for i, doc in enumerate(docs[:5], start=1):
                context_parts.append(f"[文档{i}]\n{doc.content}\n")
                sources.append({
                    "index": i,
                    "content": doc.content[:200] + "..." if len(doc.content) > 200 else doc.content,
                    "document_id": doc.metadata.get("document_id"),
                    "filename": doc.metadata.get("filename", "未知"),
                    "chunk_index": doc.metadata.get("chunk_index", 0),
                    "score": doc.score
                })
            
            context = "\n".join(context_parts)
            
            # 生成答案
            llm = self._get_llm(state["provider"], state["model"], state["temperature"])
            
            system_prompt = f"""你是一个专业的知识助手。请根据提供的文档内容回答用户的问题。

要求：
1. 基于文档内容准确回答
2. 如果文档中没有明确答案，诚实说明
3. 引用相关文档时使用 [文档X] 标记
4. 语言清晰、友好、专业
5. 不要编造文档中没有的信息

参考文档：
{context}"""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=state["user_question"])
            ]
            
            response = llm.invoke(messages)
            answer = response.content.strip()
            
            state["generated_answer"] = answer
            state["sources"] = sources
            
            logger.info("✅ 答案生成完成")
            
            return state
            
        except Exception as e:
            logger.error(f"❌ 生成答案失败: {e}")
            state["error"] = f"生成答案失败: {str(e)}"
            state["generated_answer"] = "抱歉，生成答案时遇到了问题。"
            return state
    
    def create_graph(self) -> StateGraph:
        """创建 LangGraph 工作流"""
        workflow = StateGraph(RAGState)
        
        # 添加节点
        workflow.add_node("rewrite_query", self.rewrite_query)
        workflow.add_node("retrieve", self.retrieve_documents)
        workflow.add_node("rerank", self.rerank_documents)
        workflow.add_node("generate", self.generate_answer)
        
        # 设置入口点
        workflow.set_entry_point("rewrite_query")
        
        # 添加边
        workflow.add_edge("rewrite_query", "retrieve")
        workflow.add_edge("retrieve", "rerank")
        workflow.add_edge("rerank", "generate")
        workflow.add_edge("generate", END)
        
        return workflow.compile()
    
    async def run_stream(
        self,
        user_question: str,
        knowledge_base_ids: List[int],
        provider: str,
        model: str,
        temperature: float = 0.7,
        enable_query_rewrite: bool = None,
        enable_reranking: bool = None
    ) -> AsyncGenerator[dict, None]:
        """
        流式运行 RAG Agent
        
        Args:
            user_question: 用户问题
            knowledge_base_ids: 知识库 ID 列表
            provider: AI 提供商
            model: AI 模型
            temperature: 温度参数
            enable_query_rewrite: 是否启用查询重写
            enable_reranking: 是否启用重排序
            
        Yields:
            流式事件
        """
        start_time = time.time()
        
        if enable_query_rewrite is None:
            enable_query_rewrite = settings.ENABLE_QUERY_REWRITE
        if enable_reranking is None:
            enable_reranking = settings.ENABLE_RERANKING
        
        # 初始化状态
        initial_state: RAGState = {
            "user_question": user_question,
            "rewritten_queries": None,
            "retrieved_docs": None,
            "reranked_docs": None,
            "generated_answer": None,
            "sources": None,
            "error": None,
            "knowledge_base_ids": knowledge_base_ids,
            "provider": provider,
            "model": model,
            "temperature": temperature,
            "enable_query_rewrite": enable_query_rewrite,
            "enable_reranking": enable_reranking
        }
        
        try:
            # 查询重写
            yield {"type": "status", "data": "正在分析问题..."}
            state = await self.rewrite_query(initial_state)
            
            if state.get("rewritten_queries"):
                yield {
                    "type": "rewritten_queries",
                    "data": {"queries": state["rewritten_queries"]}
                }
            
            # 检索文档
            yield {"type": "status", "data": "正在检索相关文档..."}
            state = await self.retrieve_documents(state)
            
            if state.get("error"):
                yield {"type": "error", "data": {"error": state["error"]}}
                return
            
            yield {
                "type": "retrieved",
                "data": {"count": len(state.get("retrieved_docs", []))}
            }
            
            # 重排序
            if state["enable_reranking"]:
                yield {"type": "status", "data": "正在优化结果..."}
                state = await self.rerank_documents(state)
            else:
                state["reranked_docs"] = state["retrieved_docs"][:settings.TOP_K_RERANK]
            
            # 生成答案
            yield {"type": "status", "data": "正在生成回答..."}
            state = await self.generate_answer(state)
            
            if state.get("error"):
                yield {"type": "error", "data": {"error": state["error"]}}
                return
            
            execution_time = time.time() - start_time
            
            # 返回最终结果
            yield {
                "type": "complete",
                "data": {
                    "answer": state["generated_answer"],
                    "sources": state["sources"],
                    "execution_time": execution_time
                }
            }
            
        except Exception as e:
            logger.error(f"❌ RAG Agent 执行失败: {str(e)}")
            yield {"type": "error", "data": {"error": str(e)}}


# 创建全局 RAG Agent 实例的工厂函数
def create_rag_agent(db: Session) -> RAGAgent:
    """创建 RAG Agent 实例"""
    return RAGAgent(db)

