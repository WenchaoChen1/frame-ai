from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime
import time
from ..core.database import get_db
from ..models.user import User
from ..models.conversation import Conversation
from ..models.message import Message
from ..models.database_config import DatabaseConfig, DatabaseMetadata
from ..models.sql_query_log import SQLQueryLog
from ..schemas.message import MessageCreate, MessageResponse
from ..dependencies import get_current_user
from ..ai.models.ai_manager import ai_manager
from ..ai.agent.text_to_sql_agent import text_to_sql_agent
from ..ai.agent.rag_agent import create_rag_agent
from ..services.database_service import DatabaseService
from ..core.logger import get_logger
import json
import asyncio

logger = get_logger(__name__)
router = APIRouter(prefix="/api/conversations/{conversation_id}/messages", tags=["消息"])

# 存储活跃的流式任务，用于取消
active_streams: Dict[str, bool] = {}


@router.get("", response_model=List[MessageResponse])
def get_messages(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取会话的所有消息"""
    logger.info(f"💬 用户 {current_user.username} 获取消息列表: conversation_id={conversation_id}")
    
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
    
    logger.info(f"✅ 返回 {len(conversation.messages)} 条消息")
    return [MessageResponse.model_validate(msg) for msg in conversation.messages]


@router.post("/stream")
async def send_message_stream(
    conversation_id: int,
    message_data: MessageCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """发送消息并流式返回AI响应（支持停止）"""
    logger.info(f"🚀 用户 {current_user.username} 发送流式消息: conversation_id={conversation_id}, provider={message_data.provider}, model={message_data.model}")
    
    # 验证会话
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
    
    # 保存用户消息
    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=message_data.content,
        provider=message_data.provider,
        model=message_data.model
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)
    logger.info(f"✅ 用户消息已保存: message_id={user_message.id}")
    
    # 更新会话时间
    conversation.updated_at = datetime.utcnow()
    db.commit()
    
    # 获取历史消息
    messages = db.query(Message)\
        .filter(Message.conversation_id == conversation_id)\
        .order_by(Message.created_at)\
        .all()
    
    # 构建消息历史（用于AI上下文）
    message_history = []
    for msg in messages:
        message_history.append({
            "role": msg.role,
            "content": msg.content
        })
    
    # 生成唯一的stream_id
    stream_id = f"{current_user.id}_{conversation_id}_{user_message.id}"
    active_streams[stream_id] = True
    logger.info(f"📡 开始流式生成响应: stream_id={stream_id}")
    
    # 检查机器人是否配置了数据库
    has_database = False
    db_config = None
    db_metadata = None
    
    if conversation.robot_id:
        db_config_obj = db.query(DatabaseConfig).filter(
            DatabaseConfig.robot_id == conversation.robot_id
        ).first()
        
        if db_config_obj:
            db_metadata_obj = db.query(DatabaseMetadata).filter(
                DatabaseMetadata.robot_id == conversation.robot_id
            ).first()
            
            if db_metadata_obj:
                has_database = True
                # 解密密码
                decrypted_password = DatabaseService.decrypt_password(db_config_obj.password)
                db_config = {
                    "db_type": db_config_obj.db_type,
                    "host": db_config_obj.host,
                    "port": db_config_obj.port,
                    "database_name": db_config_obj.database_name,
                    "username": db_config_obj.username,
                    "password": decrypted_password
                }
                db_metadata = db_metadata_obj.tables_metadata
                logger.info(f"✅ 机器人已配置数据库，启用 Text-to-SQL 功能")
    
    # 流式生成响应
    async def generate():
        try:
            assistant_content = ""
            assistant_message = None
            sql_query_log = None
            sql_query = None
            query_result_data = None
            
            # 发送用户消息确认
            yield f"data: {json.dumps({'type': 'user_message', 'data': MessageResponse.model_validate(user_message).model_dump(mode='json')}, ensure_ascii=False)}\n\n"
            
            # 如果配置了数据库，先尝试 Text-to-SQL
            if has_database and db_config and db_metadata:
                try:
                    start_time = time.time()
                    
                    # 格式化数据库 schema
                    schema_text = DatabaseService.format_schema_for_prompt(db_metadata)
                    
                    # 运行 Text-to-SQL Agent
                    needs_database = False
                    async for event in text_to_sql_agent.run_stream(
                        user_question=message_data.content,
                        database_schema=schema_text,
                        db_config=db_config,
                        provider=message_data.provider,
                        model=message_data.model
                    ):
                        # 检查是否被停止
                        if not active_streams.get(stream_id, False):
                            logger.warning(f"⏹️ Text-to-SQL 被停止")
                            break
                        
                        event_type = event.get("type")
                        event_data = event.get("data")
                        
                        if event_type == "no_database_needed":
                            # 不需要数据库查询，继续普通对话
                            logger.info("ℹ️ 不需要数据库查询，使用普通对话模式")
                            break
                        elif event_type == "sql_generated":
                            needs_database = True
                            sql_query = event_data.get("sql")
                            yield f"data: {json.dumps({'type': 'sql_generated', 'data': event_data}, ensure_ascii=False)}\n\n"
                        elif event_type == "query_executing":
                            yield f"data: {json.dumps({'type': 'query_executing', 'data': {}}, ensure_ascii=False)}\n\n"
                        elif event_type == "query_result":
                            query_result_data = event_data
                            yield f"data: {json.dumps({'type': 'query_result', 'data': event_data}, ensure_ascii=False)}\n\n"
                        elif event_type == "status":
                            yield f"data: {json.dumps({'type': 'status', 'data': event_data}, ensure_ascii=False)}\n\n"
                        elif event_type == "complete":
                            # Text-to-SQL 完成
                            execution_time = time.time() - start_time
                            
                            # 保存 SQL 查询日志
                            sql_query_log = SQLQueryLog(
                                conversation_id=conversation_id,
                                user_question=message_data.content,
                                generated_sql=event_data.get("sql"),
                                query_result=event_data.get("result"),
                                success=True,
                                error_message=None,
                                execution_time=execution_time
                            )
                            db.add(sql_query_log)
                            db.commit()
                            
                            # 使用解释作为助手内容
                            assistant_content = event_data.get("explanation", "")
                            
                            # 保存消息（包含 SQL 和查询结果）
                            assistant_message = Message(
                                conversation_id=conversation_id,
                                role="assistant",
                                content=assistant_content,
                                provider=message_data.provider,
                                model=message_data.model
                            )
                            db.add(assistant_message)
                            db.commit()
                            db.refresh(assistant_message)
                            
                            # 流式返回解释
                            for char in assistant_content:
                                if not active_streams.get(stream_id, False):
                                    break
                                yield f"data: {json.dumps({'type': 'content', 'data': char}, ensure_ascii=False)}\n\n"
                                await asyncio.sleep(0.01)
                            
                            # 发送完成信号（包含 SQL 和结果）
                            response_data = MessageResponse.model_validate(assistant_message).model_dump(mode='json')
                            response_data['sql_query'] = event_data.get("sql")
                            response_data['query_result'] = event_data.get("result")
                            
                            yield f"data: {json.dumps({'type': 'done', 'data': response_data}, ensure_ascii=False)}\n\n"
                            
                            logger.info(f"✅ Text-to-SQL 完成: execution_time={execution_time:.2f}s")
                            return
                        elif event_type == "error":
                            # SQL 查询失败，记录日志但继续普通对话
                            logger.warning(f"⚠️ Text-to-SQL 失败: {event_data.get('error')}")
                            
                            execution_time = time.time() - start_time
                            sql_query_log = SQLQueryLog(
                                conversation_id=conversation_id,
                                user_question=message_data.content,
                                generated_sql=sql_query,
                                query_result=None,
                                success=False,
                                error_message=event_data.get('error'),
                                execution_time=execution_time
                            )
                            db.add(sql_query_log)
                            db.commit()
                            
                            # 继续普通对话
                            break
                    
                    # 如果 Text-to-SQL 处理了请求，直接返回
                    if needs_database and assistant_content:
                        return
                        
                except Exception as e:
                    logger.error(f"❌ Text-to-SQL 处理异常: {str(e)}")
                    # 继续普通对话流程
            
            # 检查机器人是否关联了知识库，如果是，使用 RAG
            has_knowledge_bases = False
            knowledge_base_ids = []
            
            if conversation.robot_id:
                robot = conversation.robot
                if robot and robot.knowledge_bases:
                    knowledge_base_ids = [kb.id for kb in robot.knowledge_bases]
                    if knowledge_base_ids:
                        has_knowledge_bases = True
                        logger.info(f"✅ 机器人关联了 {len(knowledge_base_ids)} 个知识库，启用 RAG 功能")
            
            # 如果有知识库，使用 RAG Agent
            if has_knowledge_bases and knowledge_base_ids:
                try:
                    start_time = time.time()
                    
                    # 创建 RAG Agent
                    rag_agent = create_rag_agent(db)
                    
                    # 运行 RAG Agent
                    rag_used = False
                    async for event in rag_agent.run_stream(
                        user_question=message_data.content,
                        knowledge_base_ids=knowledge_base_ids,
                        provider=message_data.provider,
                        model=message_data.model,
                        temperature=conversation.robot.temperature or 0.7
                    ):
                        # 检查是否被停止
                        if not active_streams.get(stream_id, False):
                            logger.warning(f"⏹️ RAG 被停止")
                            break
                        
                        event_type = event.get("type")
                        event_data = event.get("data")
                        
                        if event_type == "status":
                            yield f"data: {json.dumps({'type': 'rag_status', 'data': event_data}, ensure_ascii=False)}\n\n"
                        elif event_type == "rewritten_queries":
                            yield f"data: {json.dumps({'type': 'rag_rewritten_queries', 'data': event_data}, ensure_ascii=False)}\n\n"
                        elif event_type == "retrieved":
                            yield f"data: {json.dumps({'type': 'rag_retrieved', 'data': event_data}, ensure_ascii=False)}\n\n"
                        elif event_type == "complete":
                            rag_used = True
                            execution_time = time.time() - start_time
                            
                            # 获取答案和来源
                            answer = event_data.get("answer", "")
                            sources = event_data.get("sources", [])
                            
                            # 保存消息
                            assistant_message = Message(
                                conversation_id=conversation_id,
                                role="assistant",
                                content=answer,
                                provider=message_data.provider,
                                model=message_data.model
                            )
                            db.add(assistant_message)
                            db.commit()
                            db.refresh(assistant_message)
                            
                            # 流式返回答案
                            for char in answer:
                                if not active_streams.get(stream_id, False):
                                    break
                                yield f"data: {json.dumps({'type': 'content', 'data': char}, ensure_ascii=False)}\n\n"
                                await asyncio.sleep(0.01)
                            
                            # 发送完成信号（包含来源）
                            response_data = MessageResponse.model_validate(assistant_message).model_dump(mode='json')
                            response_data['rag_sources'] = sources
                            
                            yield f"data: {json.dumps({'type': 'done', 'data': response_data}, ensure_ascii=False)}\n\n"
                            
                            logger.info(f"✅ RAG 完成: execution_time={execution_time:.2f}s")
                            return
                        elif event_type == "error":
                            logger.warning(f"⚠️ RAG 失败: {event_data.get('error')}")
                            # 继续普通对话
                            break
                    
                    # 如果 RAG 处理了请求，直接返回
                    if rag_used:
                        return
                        
                except Exception as e:
                    logger.error(f"❌ RAG 处理异常: {str(e)}")
                    # 继续普通对话流程
            
            # 普通对话流程（未配置数据库或 Text-to-SQL 不适用）
            # 流式获取AI响应
            async for chunk in ai_manager.chat_stream(
                provider=message_data.provider,
                messages=message_history,
                model=message_data.model
            ):
                # 检查是否被停止
                if not active_streams.get(stream_id, False):
                    logger.warning(f"⏹️ 流式响应被停止: stream_id={stream_id}, 已生成字符数={len(assistant_content)}")
                    # 如果已有部分内容，保存到数据库
                    if assistant_content:
                        assistant_message = Message(
                            conversation_id=conversation_id,
                            role="assistant",
                            content=assistant_content + " [已停止]",
                            provider=message_data.provider,
                            model=message_data.model
                        )
                        db.add(assistant_message)
                        db.commit()
                        db.refresh(assistant_message)
                        
                        yield f"data: {json.dumps({'type': 'stopped', 'data': MessageResponse.model_validate(assistant_message).model_dump(mode='json')}, ensure_ascii=False)}\n\n"
                    break
                
                assistant_content += chunk
                yield f"data: {json.dumps({'type': 'content', 'data': chunk}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0)  # 让出控制权，允许检查停止信号
            
            # 如果正常完成（未被停止），保存完整内容
            if active_streams.get(stream_id, False) and assistant_content:
                assistant_message = Message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=assistant_content,
                    provider=message_data.provider,
                    model=message_data.model
                )
                db.add(assistant_message)
                db.commit()
                db.refresh(assistant_message)
                
                logger.info(f"✅ 流式响应完成: stream_id={stream_id}, 生成字符数={len(assistant_content)}")
                # 发送完成信号
                yield f"data: {json.dumps({'type': 'done', 'data': MessageResponse.model_validate(assistant_message).model_dump(mode='json')}, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            error_message = str(e)
            logger.error(f"❌ 流式响应错误: stream_id={stream_id}, error={error_message}")
            yield f"data: {json.dumps({'type': 'error', 'data': error_message}, ensure_ascii=False)}\n\n"
        finally:
            # 清理stream_id
            active_streams.pop(stream_id, None)
            logger.info(f"🧹 清理stream_id: {stream_id}")
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/stop/{message_id}")
async def stop_message_stream(
    conversation_id: int,
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """停止正在进行的流式响应"""
    # 验证会话
    conversation = db.query(Conversation)\
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )\
        .first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    # 构建stream_id并设置停止标志
    stream_id = f"{current_user.id}_{conversation_id}_{message_id}"
    if stream_id in active_streams:
        active_streams[stream_id] = False
        return {"message": "停止信号已发送"}
    else:
        return {"message": "未找到活跃的流"}

