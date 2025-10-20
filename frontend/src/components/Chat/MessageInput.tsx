import React, { useState, useEffect } from 'react';
import { Input, Button, Select, Space, message as antMessage } from 'antd';
import { SendOutlined } from '@ant-design/icons';
import { useConversationStore } from '../../store/conversationStore';
import { messageService, Message } from '../../services/message';
import { providerService, Provider } from '../../services/provider';

const { TextArea } = Input;

const MessageInput: React.FC = () => {
  const { currentConversation, addMessage, updateLastMessage, isLoading, setLoading } = 
    useConversationStore();
  
  const [content, setContent] = useState('');
  const [providers, setProviders] = useState<Provider[]>([]);
  const [selectedProvider, setSelectedProvider] = useState('openai');
  const [selectedModel, setSelectedModel] = useState('gpt-3.5-turbo');

  useEffect(() => {
    loadProviders();
  }, []);

  const loadProviders = async () => {
    try {
      const data = await providerService.getProviders();
      setProviders(data);
      if (data.length > 0) {
        setSelectedProvider(data[0].name);
        setSelectedModel(data[0].models[0]);
      }
    } catch (error) {
      antMessage.error('加载AI提供商失败');
    }
  };

  const handleProviderChange = (value: string) => {
    setSelectedProvider(value);
    const provider = providers.find((p) => p.name === value);
    if (provider && provider.models.length > 0) {
      setSelectedModel(provider.models[0]);
    }
  };

  const handleSend = async () => {
    if (!content.trim() || !currentConversation) {
      return;
    }

    const messageContent = content.trim();
    setContent('');
    setLoading(true);

    try {
      let assistantContent = '';
      
      await messageService.sendMessageStream(
        currentConversation.id,
        {
          content: messageContent,
          provider: selectedProvider,
          model: selectedModel,
        },
        (event) => {
          if (event.type === 'user_message') {
            addMessage(event.data as Message);
          } else if (event.type === 'content') {
            if (assistantContent === '') {
              // 第一次收到内容，创建助手消息占位符
              const tempMessage: Message = {
                id: Date.now(),
                conversation_id: currentConversation.id,
                role: 'assistant',
                content: event.data,
                provider: selectedProvider,
                model: selectedModel,
                created_at: new Date().toISOString(),
              };
              addMessage(tempMessage);
              assistantContent = event.data;
            } else {
              assistantContent += event.data;
              updateLastMessage(assistantContent);
            }
          } else if (event.type === 'done') {
            // 流结束，更新为最终消息
            const finalMessage = event.data as Message;
            updateLastMessage(finalMessage.content);
          } else if (event.type === 'error') {
            antMessage.error(`发送失败: ${event.data}`);
          }
        }
      );
    } catch (error) {
      antMessage.error('发送消息失败');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const currentModels = providers.find((p) => p.name === selectedProvider)?.models || [];

  return (
    <div style={{ 
      padding: 16, 
      borderTop: '1px solid #f0f0f0',
      background: '#fff'
    }}>
      <Space.Compact style={{ width: '100%', marginBottom: 12 }}>
        <Select
          value={selectedProvider}
          onChange={handleProviderChange}
          style={{ width: 150 }}
          options={providers.map((p) => ({ label: p.name, value: p.name }))}
        />
        <Select
          value={selectedModel}
          onChange={setSelectedModel}
          style={{ flex: 1 }}
          options={currentModels.map((m) => ({ label: m, value: m }))}
        />
      </Space.Compact>
      <Space.Compact style={{ width: '100%' }}>
        <TextArea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="输入消息... (Shift+Enter换行，Enter发送)"
          autoSize={{ minRows: 1, maxRows: 4 }}
          disabled={isLoading}
          style={{ flex: 1 }}
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={handleSend}
          loading={isLoading}
          disabled={!content.trim()}
        >
          发送
        </Button>
      </Space.Compact>
    </div>
  );
};

export default MessageInput;

