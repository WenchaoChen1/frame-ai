import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { Layout, message, Spin, Button } from 'antd';
import { MenuUnfoldOutlined } from '@ant-design/icons';
import ConversationList from '../components/Sidebar/ConversationList';
import ChatWindowX from '../components/Chat/ChatWindowX';
import { useConversationStore } from '../store/conversationStore';
import { conversationService } from '../services/conversation';

const { Content } = Layout;

const ChatPage: React.FC = () => {
  const { conversationId } = useParams<{ conversationId: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { setCurrentConversation, setMessages } = useConversationStore();
  const [loading, setLoading] = useState(false);
  const [siderCollapsed, setSiderCollapsed] = useState(false);
  
  // 获取 URL 中的 robot_id 参数
  const robotIdParam = searchParams.get('robot_id');

  useEffect(() => {
    if (conversationId) {
      loadConversation(parseInt(conversationId));
    } else {
      // 清空当前对话和消息（延迟创建模式，不立即创建对话）
      setCurrentConversation(null);
      setMessages([]);
    }
  }, [conversationId]);

  const loadConversation = async (id: number) => {
    setLoading(true);
    try {
      const conv = await conversationService.getConversation(id);
      setCurrentConversation(conv);
      // 设置消息列表
      setMessages(conv.messages || []);
    } catch (error) {
      message.error('加载对话失败');
      navigate('/chat');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout style={{ height: '100%', width: '100%', position: 'relative' }}>
      <Content style={{ 
        background: 'linear-gradient(135deg, #f5f7fa 0%, #e4e9f2 100%)',
        height: '100%',
        overflow: 'hidden',
        position: 'relative',
        marginRight: siderCollapsed ? 0 : 340,
        transition: 'margin-right 0.2s ease'
      }}>
        {loading && (
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'rgba(255, 255, 255, 0.8)',
            zIndex: 10
          }}>
            <Spin size="large" tip="加载对话中..." />
          </div>
        )}
        <ChatWindowX preselectedRobotId={robotIdParam ? parseInt(robotIdParam) : undefined} />
      </Content>

      {/* 展开按钮 - 当对话列表收起时显示 */}
      {siderCollapsed && (
        <Button
          type="text"
          icon={<MenuUnfoldOutlined />}
          onClick={() => setSiderCollapsed(false)}
          style={{
            position: 'fixed',
            top: 20,
            right: 20,
            width: 40,
            height: 40,
            borderRadius: 10,
            background: '#fff',
            boxShadow: '0 2px 12px rgba(0, 0, 0, 0.1)',
            border: '1px solid rgba(0, 0, 0, 0.06)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 100,
            fontSize: 16,
            color: '#667eea',
            transition: 'all 0.2s ease'
          }}
          title="展开对话列表"
        />
      )}

      {/* 右侧对话列表 */}
      <div style={{
        position: 'fixed',
        top: 0,
        right: siderCollapsed ? -340 : 0,
        width: 340,
        height: '100%',
        background: '#fff',
        borderLeft: '1px solid rgba(0, 0, 0, 0.06)',
        boxShadow: '-2px 0 12px rgba(0, 0, 0, 0.04)',
        overflow: 'hidden',
        transition: 'right 0.2s ease',
        zIndex: 50
      }}>
        <ConversationList 
          collapsed={siderCollapsed}
          onToggleCollapse={() => setSiderCollapsed(!siderCollapsed)}
        />
      </div>
    </Layout>
  );
};

export default ChatPage;

