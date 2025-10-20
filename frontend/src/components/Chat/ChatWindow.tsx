import React from 'react';
import { Empty } from 'antd';
import { useConversationStore } from '../../store/conversationStore';
import MessageList from './MessageList';
import MessageInput from './MessageInput';

const ChatWindow: React.FC = () => {
  const currentConversation = useConversationStore((state) => state.currentConversation);

  if (!currentConversation) {
    return (
      <div style={{ 
        height: '100%', 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center' 
      }}>
        <Empty description="请选择或创建一个对话" />
      </div>
    );
  }

  return (
    <div style={{ 
      height: '100%', 
      display: 'flex', 
      flexDirection: 'column',
      background: '#fff'
    }}>
      <MessageList />
      <MessageInput />
    </div>
  );
};

export default ChatWindow;

