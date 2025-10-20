import React, { useState, useEffect, useRef } from 'react';
import { Bubble } from '@ant-design/x';
import { Select, Space, message as antMessage, Button, Tag, Avatar } from 'antd';
import { StopOutlined, RobotOutlined, UserOutlined, ThunderboltOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useConversationStore } from '../../store/conversationStore';
import { messageService, Message } from '../../services/message';
import { providerService, Provider } from '../../services/provider';
import { robotService, Robot } from '../../services/robot';

interface ChatWindowXProps {
  preselectedRobotId?: number;
}

const ChatWindowX: React.FC<ChatWindowXProps> = ({ preselectedRobotId }) => {
  const { currentConversation, messages, setMessages, addMessage, setCurrentConversation } = useConversationStore();
  
  const [content, setContent] = useState('');
  const [providers, setProviders] = useState<Provider[]>([]);
  const [selectedProvider, setSelectedProvider] = useState('openai');
  const [selectedModel, setSelectedModel] = useState('gpt-3.5-turbo');
  const [isLoading, setIsLoading] = useState(false);
  const [currentStreamMessageId, setCurrentStreamMessageId] = useState<number | null>(null);
  const [streamingContent, setStreamingContent] = useState('');
  const [currentRobot, setCurrentRobot] = useState<Robot | null>(null);
  const [availableRobots, setAvailableRobots] = useState<Robot[]>([]);
  const [selectedRobotForInput, setSelectedRobotForInput] = useState<number | undefined>(undefined);
  const abortControllerRef = useRef<AbortController | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadProviders();
    loadAvailableRobots();
  }, []);

  useEffect(() => {
    if (currentConversation) {
      setMessages(currentConversation.messages || []);
      loadRobotIfNeeded();
    } else {
      // 新建对话时，根据 preselectedRobotId 选择机器人
      setCurrentRobot(null);
      if (availableRobots.length > 0) {
        let robotToSelect = availableRobots[0];
        
        // 如果有预选的机器人 ID，则选择该机器人
        if (preselectedRobotId) {
          const preselectedRobot = availableRobots.find(r => r.id === preselectedRobotId);
          if (preselectedRobot) {
            robotToSelect = preselectedRobot;
          }
        }
        
        setSelectedRobotForInput(robotToSelect.id);
        setSelectedProvider(robotToSelect.default_provider);
        setSelectedModel(robotToSelect.default_model);
      }
    }
  }, [currentConversation, availableRobots, preselectedRobotId]);

  // 加载可用的机器人列表
  const loadAvailableRobots = async () => {
    try {
      const robots = await robotService.getRobots();
      setAvailableRobots(robots);
      // 默认选择第一个机器人（机器人为必选）
      if (robots.length > 0) {
        if (!selectedRobotForInput || !robots.find(r => r.id === selectedRobotForInput)) {
          setSelectedRobotForInput(robots[0].id);
          // 使用第一个机器人的默认配置
          setSelectedProvider(robots[0].default_provider);
          setSelectedModel(robots[0].default_model);
        }
      }
    } catch (error) {
      console.error('加载机器人列表失败:', error);
    }
  };

  // 加载机器人信息并设置默认配置
  const loadRobotIfNeeded = async () => {
    if (currentConversation?.robot_id) {
      try {
        const robot = await robotService.getRobot(currentConversation.robot_id);
        setCurrentRobot(robot);
        // 使用机器人的默认配置
        setSelectedProvider(robot.default_provider);
        setSelectedModel(robot.default_model);
        setSelectedRobotForInput(robot.id);
      } catch (error) {
        console.error('加载机器人信息失败:', error);
        setCurrentRobot(null);
      }
    } else {
      setCurrentRobot(null);
    }
  };

  // 当选择机器人时，更新provider和model
  const handleRobotChange = (robotId: number) => {
    setSelectedRobotForInput(robotId);
    const robot = availableRobots.find(r => r.id === robotId);
    if (robot) {
      setSelectedProvider(robot.default_provider);
      setSelectedModel(robot.default_model);
    }
  };

  // 滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

  const loadProviders = async () => {
    try {
      const data = await providerService.getProviders();
      setProviders(data);
      if (data.length > 0) {
        // 优先选择 OpenAI，如果不可用则选择第一个
        const openaiProvider = data.find(p => p.name === 'openai');
        if (openaiProvider && openaiProvider.models.length > 0) {
          setSelectedProvider('openai');
          // 优先选择 gpt-4o，如果不可用则选择第一个模型
          const preferredModel = openaiProvider.models.find(m => m === 'gpt-4o') || 
                                  openaiProvider.models.find(m => m === 'gpt-3.5-turbo') ||
                                  openaiProvider.models[0];
          setSelectedModel(preferredModel);
        } else {
          setSelectedProvider(data[0].name);
          setSelectedModel(data[0].models[0]);
        }
      }
    } catch (error) {
      antMessage.error('加载AI提供商失败');
    }
  };


  const handleStop = async () => {
    // 取消客户端的流式请求
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }

    // 如果有正在进行的消息，通知服务器停止
    if (currentConversation && currentStreamMessageId) {
      try {
        await fetch(
        `/api/conversations/${currentConversation.id}/messages/stop/${currentStreamMessageId}`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );
      } catch (error) {
        console.error('停止失败:', error);
      }
    }
      
        antMessage.success('已停止生成');
        setIsLoading(false);
        setCurrentStreamMessageId(null);
    setStreamingContent('');
  };

  const handleSend = async (messageContent: string) => {
    if (!messageContent.trim() || isLoading) {
      return;
    }

    // 如果没有当前对话，先创建对话
    let conversationToUse = currentConversation;
    if (!conversationToUse) {
      try {
        // 使用选中的机器人创建对话
        if (!selectedRobotForInput) {
          antMessage.error('请选择一个机器人');
          return;
        }

        const robot = availableRobots.find(r => r.id === selectedRobotForInput);
        const title = `与${robot?.name || '机器人'}的对话`;

        const { conversationService: convService } = await import('../../services/conversation');
        const newConv = await convService.createConversation({
          title,
          robot_id: selectedRobotForInput
        });

        setCurrentConversation(newConv);
        conversationToUse = newConv;
        
        // 更新URL
        window.history.replaceState(null, '', `/chat/${newConv.id}`);
      } catch (error) {
        antMessage.error('创建对话失败');
        return;
      }
    }

    if (!conversationToUse) {
      antMessage.error('对话创建失败');
      return;
    }

    setIsLoading(true);
    setStreamingContent('');
    
    // 创建新的AbortController
    abortControllerRef.current = new AbortController();

    try {
      let assistantContent = '';
      let hasStartedAssistant = false;
      let currentSqlQuery = '';
      let currentQueryResult: any = null;
      
      await messageService.sendMessageStream(
        conversationToUse.id,
        {
          content: messageContent,
          provider: selectedProvider,
          model: selectedModel,
        },
        (event) => {
          if (event.type === 'user_message') {
            const userMsg = event.data as Message;
            setCurrentStreamMessageId(userMsg.id);
            addMessage(userMsg);
          } else if (event.type === 'sql_generated') {
            // SQL 已生成
            currentSqlQuery = event.data.sql;
            if (!hasStartedAssistant) {
              hasStartedAssistant = true;
              const tempMessage: Message = {
                id: Date.now(),
                conversation_id: conversationToUse.id,
                role: 'assistant',
                content: '正在执行查询...',
                provider: selectedProvider,
                model: selectedModel,
                created_at: new Date().toISOString(),
                sql_query: currentSqlQuery,
              };
              addMessage(tempMessage);
            }
          } else if (event.type === 'query_executing') {
            // 正在执行查询
            setMessages((prevMessages) => {
              const newMessages = [...prevMessages];
              if (newMessages.length > 0) {
                const lastMessage = newMessages[newMessages.length - 1];
                if (lastMessage.role === 'assistant') {
                  lastMessage.content = '正在执行查询...';
                }
              }
              return newMessages;
            });
          } else if (event.type === 'query_result') {
            // 查询结果返回
            currentQueryResult = event.data;
            setMessages((prevMessages) => {
              const newMessages = [...prevMessages];
              if (newMessages.length > 0) {
                const lastMessage = newMessages[newMessages.length - 1];
                if (lastMessage.role === 'assistant') {
                  lastMessage.query_result = currentQueryResult;
                  lastMessage.content = '正在分析结果...';
                }
              }
              return newMessages;
            });
          } else if (event.type === 'status') {
            // 状态更新
            setMessages((prevMessages) => {
              const newMessages = [...prevMessages];
              if (newMessages.length > 0) {
                const lastMessage = newMessages[newMessages.length - 1];
                if (lastMessage.role === 'assistant') {
                  lastMessage.content = event.data;
                }
              }
              return newMessages;
            });
          } else if (event.type === 'content') {
            if (!hasStartedAssistant) {
              // 第一次收到内容，创建助手消息占位符
              hasStartedAssistant = true;
              const tempMessage: Message = {
                id: Date.now(),
                conversation_id: conversationToUse.id,
                role: 'assistant',
                content: event.data,
                provider: selectedProvider,
                model: selectedModel,
                created_at: new Date().toISOString(),
              };
              addMessage(tempMessage);
              assistantContent = event.data;
              setStreamingContent(event.data);
            } else {
              assistantContent += event.data;
              setStreamingContent(assistantContent);
              // 更新最后一条消息
              setMessages((prevMessages) => {
                const newMessages = [...prevMessages];
                if (newMessages.length > 0) {
                  const lastMessage = newMessages[newMessages.length - 1];
                  if (lastMessage.role === 'assistant') {
                    lastMessage.content = assistantContent;
                  }
                }
                return newMessages;
              });
            }
          } else if (event.type === 'done') {
            // 流结束，更新为最终消息
            const finalMessage = event.data as Message;
            setMessages((prevMessages) => {
              const newMessages = [...prevMessages];
              if (newMessages.length > 0) {
                const lastMessage = newMessages[newMessages.length - 1];
                if (lastMessage.role === 'assistant') {
                  lastMessage.id = finalMessage.id;
                  lastMessage.content = finalMessage.content;
                  lastMessage.provider = finalMessage.provider;
                  lastMessage.model = finalMessage.model;
                  lastMessage.sql_query = finalMessage.sql_query;
                  lastMessage.query_result = finalMessage.query_result;
                }
              }
              return newMessages;
            });
            setCurrentStreamMessageId(null);
            setStreamingContent('');
          }
          
          if (event.type === 'error') {
            antMessage.error(`发送失败: ${event.data}`);
            setCurrentStreamMessageId(null);
            setStreamingContent('');
          }
        }
      );
    } catch (error: any) {
      if (error.name === 'AbortError') {
        console.log('请求已取消');
      } else {
      antMessage.error('发送消息失败');
      }
      setCurrentStreamMessageId(null);
      setStreamingContent('');
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  };

  // 移除空状态检查，即使没有对话也显示输入框

  // 获取提供商显示名称和图标
  const getProviderInfo = (providerName: string) => {
    const configs: Record<string, { label: string; color: string; icon: string }> = {
      'openai': { label: 'OpenAI', color: '#10a37f', icon: '🤖' },
      'claude': { label: 'Claude', color: '#6b46c1', icon: '🧠' },
      'ollama': { label: 'Ollama', color: '#ff6b6b', icon: '🦙' },
    };
    return configs[providerName] || { label: providerName, color: '#1890ff', icon: '🤖' };
  };

  return (
    <div style={{ 
      height: '100%',
      width: '100%',
      display: 'flex', 
      flexDirection: 'column', 
      background: 'transparent',
      overflow: 'hidden'
    }}>
      {/* 机器人信息栏 - 显示当前对话的机器人或选中的机器人 */}
      {(() => {
        const displayRobot = currentRobot || availableRobots.find(r => r.id === selectedRobotForInput);
        return displayRobot && (
          <div style={{
            padding: '12px 24px',
            background: 'rgba(255, 255, 255, 0.95)',
            borderBottom: '1px solid rgba(0, 0, 0, 0.06)',
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.04)'
          }}>
            <Avatar 
              size={32}
              style={{ 
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                fontSize: 18
              }}
            >
              {displayRobot.avatar || '🤖'}
            </Avatar>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 14, fontWeight: 600, color: '#333' }}>
                {displayRobot.name}
              </div>
              <div style={{ fontSize: 12, color: '#999' }}>
                {displayRobot.default_provider} / {displayRobot.default_model}
              </div>
            </div>
            {displayRobot.is_global && (
              <Tag color="blue" style={{ margin: 0 }}>全局</Tag>
            )}
            {!currentConversation && (
              <Tag color="orange" style={{ margin: 0 }}>新对话</Tag>
            )}
          </div>
        );
      })()}

      {/* 聊天区域 */}
      <div style={{ 
        flex: 1, 
        overflow: 'auto',
        background: 'transparent',
        display: 'flex',
        justifyContent: 'center',
        padding: '24px 0'
      }}>
        <div style={{
          width: '100%',
          maxWidth: 1000,
          padding: '0 24px'
        }}>
          {messages.length === 0 ? (
            <div style={{
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#999',
              textAlign: 'center',
              minHeight: 400
            }}>
              <div style={{
                fontSize: 64,
                marginBottom: 16,
                opacity: 0.6
              }}>💬</div>
              <h3 style={{ marginBottom: 8, color: '#666', fontSize: 20 }}>
                {availableRobots.find(r => r.id === selectedRobotForInput)?.name || '开始智能对话'}
              </h3>
              <p style={{ fontSize: 14 }}>
                {!currentConversation && selectedRobotForInput 
                  ? '在下方输入您的问题，开始与AI对话' 
                  : '选择AI模型，输入您的问题开始对话'
                }
              </p>
            </div>
          ) : (
            messages.map((msg, index) => {
            const isStreaming = isLoading && index === messages.length - 1 && msg.role === 'assistant';
            const displayContent = isStreaming && streamingContent ? streamingContent : msg.content;
            const isUserMessage = msg.role === 'user';

            return (
              <div
                key={msg.id}
                style={{
                  display: 'flex',
                  justifyContent: isUserMessage ? 'flex-end' : 'flex-start',
                  marginBottom: 20,
                  animation: 'fadeIn 0.3s ease-in',
                  width: '100%'
                }}
              >
                <div style={{
                  display: 'flex',
                  maxWidth: '80%',
                  flexDirection: isUserMessage ? 'row-reverse' : 'row',
                  gap: 12,
                  alignItems: 'flex-start'
                }}>
                  <Avatar
                    size={40}
                    icon={isUserMessage ? <UserOutlined /> : <RobotOutlined />}
                    style={{
                      background: isUserMessage
                        ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                        : 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
                      flexShrink: 0
                    }}
                  />
                  <Bubble
                    style={{
                      background: isUserMessage
                        ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                        : '#fff',
                      borderRadius: 16,
                      boxShadow: isUserMessage
                        ? '0 4px 16px rgba(102, 126, 234, 0.3)'
                        : '0 4px 16px rgba(0, 0, 0, 0.08)',
                      border: 'none',
                      padding: '14px 18px',
                      color: isUserMessage ? '#fff' : 'inherit'
                    }}
                    content={
                      <div>
                        <div className="markdown-body" style={{ 
                          color: isUserMessage ? '#fff' : 'inherit'
                        }}>
                          <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {displayContent}
                          </ReactMarkdown>
                          {isStreaming && (
                            <span style={{ 
                              display: 'inline-block',
                              width: 8,
                              height: 16,
                              marginLeft: 4,
                              background: 'currentColor',
                              animation: 'blink 1s infinite'
                            }}>▋</span>
                          )}
                        </div>
                        {msg.model && (
                          <div style={{
                            marginTop: 8,
                            paddingTop: 8,
                            borderTop: isUserMessage 
                              ? '1px solid rgba(255, 255, 255, 0.2)'
                              : '1px solid #f0f0f0',
                            display: 'flex',
                            alignItems: 'center',
                            gap: 6,
                            fontSize: 11,
                            color: isUserMessage ? 'rgba(255, 255, 255, 0.8)' : '#999'
                          }}>
                            <ThunderboltOutlined />
                            <span>{msg.provider}</span>
                            <span>/</span>
                            <span>{msg.model}</span>
                          </div>
                        )}
                      </div>
                    }
                  />
                </div>
              </div>
            );
            })
          )}
          <div ref={messagesEndRef} />
          <style>{`
            @keyframes blink {
              0%, 50% { opacity: 1; }
              51%, 100% { opacity: 0; }
            }
            @keyframes fadeIn {
              from {
                opacity: 0;
                transform: translateY(10px);
              }
              to {
                opacity: 1;
                transform: translateY(0);
              }
            }
          `}</style>
        </div>
      </div>

      {/* 输入区域 */}
      <div style={{
        padding: '20px 0',
        background: 'transparent',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        flexDirection: 'column',
        gap: 8
      }}>
        {/* 输入框区域 */}
        <div style={{
          maxWidth: 1000,
          width: 'calc(100% - 48px)',
          margin: '0 24px',
          background: '#fff',
          borderRadius: 16,
          boxShadow: '0 2px 16px rgba(0, 0, 0, 0.08)',
          border: '1px solid rgba(0, 0, 0, 0.06)',
          overflow: 'hidden'
        }}>
          {/* 输入框主体 */}
          <div style={{
            display: 'flex',
            alignItems: 'flex-end',
            padding: '16px 16px 12px 16px',
            minHeight: 80
          }}>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  if (content.trim() && !isLoading) {
                    handleSend(content);
                    setContent('');
                  }
                }
              }}
              placeholder="问我任何问题..."
              disabled={isLoading}
              rows={1}
              style={{
                flex: 1,
                border: 'none',
                background: 'transparent',
                outline: 'none',
                fontSize: 15,
                color: '#333',
                resize: 'none',
                fontFamily: 'inherit',
                lineHeight: '24px',
                maxHeight: '200px',
                overflow: 'auto'
              }}
            />
            
            {/* 发送按钮 */}
            {isLoading ? (
              <Button 
                type="text" 
                danger
                icon={<StopOutlined />} 
                onClick={handleStop}
                style={{
                  borderRadius: 10,
                  height: 36,
                  width: 36,
                  padding: 0,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 16,
                  marginLeft: 8,
                  flexShrink: 0
                }}
              />
            ) : (
              <Button
                type="primary"
                onClick={() => {
                  if (content.trim()) {
                    handleSend(content);
                    setContent('');
                  }
                }}
                disabled={!content.trim()}
                style={{
                  borderRadius: 10,
                  height: 36,
                  width: 36,
                  padding: 0,
                  background: content.trim() 
                    ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' 
                    : '#f0f0f0',
                  border: 'none',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: 18,
                  color: content.trim() ? '#fff' : '#999',
                  cursor: content.trim() ? 'pointer' : 'not-allowed',
                  boxShadow: content.trim() ? '0 2px 8px rgba(102, 126, 234, 0.3)' : 'none',
                  marginLeft: 8,
                  flexShrink: 0
                }}
              >
                ↑
              </Button>
            )}
          </div>

          {/* 底部工具栏 */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '8px 16px',
            borderTop: '1px solid rgba(0, 0, 0, 0.06)',
            background: 'rgba(0, 0, 0, 0.01)'
          }}>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              {/* 机器人选择器 - 标签样式（必选） */}
              {availableRobots.length > 0 ? (
                <Select
                  value={selectedRobotForInput}
                  onChange={handleRobotChange}
                  style={{ minWidth: 120 }}
                  disabled={isLoading}
                  size="small"
                  bordered={false}
                  suffixIcon={<span style={{ fontSize: 10, color: '#999' }}>▼</span>}
                  dropdownStyle={{ minWidth: 200 }}
                >
                  {availableRobots.map((robot) => (
                    <Select.Option key={robot.id} value={robot.id}>
                      <Space size={6}>
                        <span style={{ fontSize: 12 }}>{robot.avatar || '🤖'}</span>
                        <span style={{ fontSize: 12, color: '#666' }}>{robot.name}</span>
                      </Space>
                    </Select.Option>
                  ))}
                </Select>
              ) : (
                <span style={{ fontSize: 12, color: '#999', padding: '4px 8px' }}>
                  暂无机器人
                </span>
              )}

              {/* 模型选择 - 标签样式 */}
              <Select
                value={`${selectedProvider}/${selectedModel}`}
                onChange={(value) => {
                  const [provider, model] = value.split('/');
                  setSelectedProvider(provider);
                  setSelectedModel(model);
                }}
                style={{ minWidth: 100 }}
                disabled={isLoading}
                size="small"
                bordered={false}
                suffixIcon={<span style={{ fontSize: 10, color: '#999' }}>▼</span>}
              >
                {providers.map((p) => {
                  const info = getProviderInfo(p.name);
                  return p.models.map((m) => (
                    <Select.Option key={`${p.name}/${m}`} value={`${p.name}/${m}`}>
                      <Space size={4}>
                        <span style={{ fontSize: 11 }}>{info.icon}</span>
                        <span style={{ fontSize: 11, color: '#666' }}>{m}</span>
                      </Space>
                    </Select.Option>
                  ));
                })}
              </Select>
            </div>

            <div style={{ fontSize: 11, color: '#999' }}>
              Enter发送 • Shift+Enter换行
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};

export default ChatWindowX;
