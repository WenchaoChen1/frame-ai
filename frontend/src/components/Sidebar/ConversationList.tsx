import React, { useEffect, useState } from 'react';
import { List, Button, message, Popconfirm, Modal, Radio, Avatar, Space, Empty, Spin } from 'antd';
import { PlusOutlined, DeleteOutlined, MessageOutlined, MenuFoldOutlined, RobotOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { conversationService } from '../../services/conversation';
import { robotService, Robot } from '../../services/robot';
import { useConversationStore } from '../../store/conversationStore';

interface ConversationListProps {
  collapsed?: boolean;
  onToggleCollapse?: () => void;
}

const ConversationList: React.FC<ConversationListProps> = ({ collapsed, onToggleCollapse }) => {
  const navigate = useNavigate();
  const { 
    conversations, 
    currentConversation, 
    setConversations, 
    setCurrentConversation 
  } = useConversationStore();

  const [selectRobotModalVisible, setSelectRobotModalVisible] = useState(false);
  const [robots, setRobots] = useState<Robot[]>([]);
  const [selectedRobotId, setSelectedRobotId] = useState<number | null>(null);
  const [loadingRobots, setLoadingRobots] = useState(false);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      const data = await conversationService.getConversations();
      setConversations(data);
    } catch (error) {
      message.error('加载会话列表失败');
    }
  };

  const loadRobots = async () => {
    setLoadingRobots(true);
    try {
      const data = await robotService.getRobots();
      setRobots(data);
      // 默认选择第一个机器人
      if (data.length > 0 && !selectedRobotId) {
        setSelectedRobotId(data[0].id);
      }
    } catch (error) {
      message.error('加载机器人列表失败');
    } finally {
      setLoadingRobots(false);
    }
  };

  const handleOpenCreateModal = async () => {
    // 只在前端创建新页面，不调用后端API
    try {
      const robotsData = await robotService.getRobots();
      
      if (robotsData.length === 0) {
        message.error('请先创建机器人');
        navigate('/system/robots');
        return;
      }

      // 清空当前对话，跳转到新对话页面（不传conversationId）
      setCurrentConversation(null);
      navigate('/chat');
    } catch (error: any) {
      message.error('加载机器人失败');
    }
  };

  const handleCreateWithRobot = async () => {
    try {
      // 机器人必选，如果没选择则使用第一个
      const robotId = selectedRobotId || (robots.length > 0 ? robots[0].id : null);
      
      if (!robotId) {
        message.error('请先创建机器人');
        return;
      }

      const robot = robots.find(r => r.id === robotId);
      const title = `与${robot?.name || '机器人'}的对话`;

      const newConv = await conversationService.createConversation({ 
        title,
        robot_id: robotId
      });
      await loadConversations();
      setCurrentConversation(newConv);
      setSelectRobotModalVisible(false);
      navigate(`/chat/${newConv.id}`);
      message.success('创建新对话成功');
    } catch (error) {
      message.error('创建对话失败');
    }
  };

  const handleSelect = async (id: number) => {
    try {
      const conv = await conversationService.getConversation(id);
      setCurrentConversation(conv);
      navigate(`/chat/${id}`);
    } catch (error) {
      message.error('加载对话失败');
    }
  };

  const handleDelete = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await conversationService.deleteConversation(id);
      await loadConversations();
      if (currentConversation?.id === id) {
        setCurrentConversation(null);
        navigate('/chat');
      }
      message.success('删除成功');
    } catch (error) {
      message.error('删除失败');
    }
  };

  return (
    <div style={{ 
      height: '100%', 
      display: 'flex', 
      flexDirection: 'column',
      background: 'linear-gradient(180deg, #fafafa 0%, #ffffff 100%)'
    }}>
      {/* 头部 */}
      <div style={{ 
        padding: '20px 16px 16px',
        borderBottom: '1px solid rgba(0, 0, 0, 0.06)'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: 12
        }}>
          <h3 style={{
            margin: 0,
            fontSize: 16,
            fontWeight: 600,
            color: '#333',
            display: 'flex',
            alignItems: 'center',
            gap: 8
          }}>
            <MessageOutlined style={{ color: '#667eea' }} />
            对话管理
          </h3>
          <Button
            type="text"
            icon={<MenuFoldOutlined />}
            onClick={onToggleCollapse}
            style={{
              width: 32,
              height: 32,
              borderRadius: 8,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#666',
              fontSize: 14
            }}
            title="收起"
          />
        </div>
        <Button 
          type="primary" 
          icon={<PlusOutlined />} 
          block
          onClick={handleOpenCreateModal}
          style={{
            height: 40,
            borderRadius: 10,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            border: 'none',
            fontWeight: 500,
            boxShadow: '0 2px 8px rgba(102, 126, 234, 0.3)'
          }}
        >
          新建对话
        </Button>
      </div>

      {/* 对话列表 */}
      <div style={{ flex: 1, overflow: 'auto', padding: '8px' }}>
        {conversations.length === 0 ? (
          <div style={{
            padding: '40px 20px',
            textAlign: 'center',
            color: '#999'
          }}>
            <MessageOutlined style={{ fontSize: 48, color: '#ddd', marginBottom: 12 }} />
            <p>暂无对话</p>
          </div>
        ) : (
          conversations.map((item) => (
            <div
              key={item.id}
              onClick={() => handleSelect(item.id)}
              style={{
                padding: '12px 16px',
                marginBottom: 8,
                cursor: 'pointer',
                borderRadius: 10,
                background: currentConversation?.id === item.id 
                  ? 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)'
                  : 'transparent',
                border: currentConversation?.id === item.id 
                  ? '1px solid rgba(102, 126, 234, 0.2)'
                  : '1px solid transparent',
                transition: 'all 0.2s ease',
                display: 'flex',
                alignItems: 'flex-start',
                gap: 12,
                position: 'relative'
              }}
              onMouseEnter={(e) => {
                if (currentConversation?.id !== item.id) {
                  e.currentTarget.style.background = 'rgba(0, 0, 0, 0.02)';
                }
              }}
              onMouseLeave={(e) => {
                if (currentConversation?.id !== item.id) {
                  e.currentTarget.style.background = 'transparent';
                }
              }}
            >
              {/* 图标 */}
              <div style={{
                width: 36,
                height: 36,
                borderRadius: 8,
                background: currentConversation?.id === item.id
                  ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                  : 'rgba(102, 126, 234, 0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
                transition: 'all 0.2s ease'
              }}>
                <MessageOutlined style={{ 
                  color: currentConversation?.id === item.id ? '#fff' : '#667eea',
                  fontSize: 16
                }} />
              </div>

              {/* 内容 */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{
                  fontSize: 14,
                  fontWeight: currentConversation?.id === item.id ? 600 : 500,
                  color: '#333',
                  marginBottom: 4,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap'
                }}>
                  {item.title}
                </div>
                <div style={{
                  fontSize: 12,
                  color: '#999',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap'
                }}>
                  {new Date(item.updated_at).toLocaleString('zh-CN', {
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </div>
              </div>

              {/* 删除按钮 */}
              <Popconfirm
                title="确定删除这个对话吗？"
                onConfirm={(e) => handleDelete(item.id, e as any)}
                okText="确定"
                cancelText="取消"
                placement="left"
              >
                <Button 
                  type="text" 
                  danger 
                  icon={<DeleteOutlined />} 
                  onClick={(e) => e.stopPropagation()}
                  style={{
                    width: 32,
                    height: 32,
                    borderRadius: 8,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    opacity: 0.6,
                    transition: 'all 0.2s ease'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.opacity = '1';
                    e.currentTarget.style.background = 'rgba(255, 77, 79, 0.1)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.opacity = '0.6';
                    e.currentTarget.style.background = 'transparent';
                  }}
                />
              </Popconfirm>
            </div>
          ))
        )}
      </div>

      {/* 选择机器人弹窗 */}
      <Modal
        title="创建新对话"
        open={selectRobotModalVisible}
        onOk={handleCreateWithRobot}
        onCancel={() => setSelectRobotModalVisible(false)}
        okText="创建"
        cancelText="取消"
        width={500}
      >
        <div style={{ marginTop: 20 }}>
          <h4 style={{ marginBottom: 12, color: '#666' }}>
            选择机器人 <span style={{ color: '#ff4d4f' }}>*</span>
          </h4>
          
          {loadingRobots ? (
            <div style={{ textAlign: 'center', padding: '40px 0' }}>
              <Spin tip="加载机器人列表..." />
            </div>
          ) : robots.length === 0 ? (
            <Empty 
              description={
                <div>
                  <p>暂无可用机器人</p>
                  <Button 
                    type="link" 
                    onClick={() => {
                      setSelectRobotModalVisible(false);
                      navigate('/system/robots');
                    }}
                  >
                    去创建机器人
                  </Button>
                </div>
              }
              style={{ padding: '40px 0' }}
            />
          ) : (
            <Radio.Group
              value={selectedRobotId}
              onChange={(e) => setSelectedRobotId(e.target.value)}
              style={{ width: '100%' }}
            >
              <Space direction="vertical" style={{ width: '100%' }} size={12}>
                {/* 机器人列表 */}
                {robots.map(robot => (
                  <Radio key={robot.id} value={robot.id} style={{ width: '100%' }}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 12,
                      padding: '8px 0'
                    }}>
                      <Avatar 
                        size={40}
                        style={{ 
                          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                          fontSize: 20,
                          flexShrink: 0
                        }}
                      >
                        {robot.avatar || '🤖'}
                      </Avatar>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ 
                          fontWeight: 500, 
                          color: '#333',
                          display: 'flex',
                          alignItems: 'center',
                          gap: 6
                        }}>
                          {robot.name}
                          {robot.is_global && (
                            <span style={{
                              fontSize: 11,
                              padding: '2px 6px',
                              borderRadius: 4,
                              background: 'rgba(102, 126, 234, 0.1)',
                              color: '#667eea'
                            }}>
                              全局
                            </span>
                          )}
                        </div>
                        <div style={{ 
                          fontSize: 12, 
                          color: '#999',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap'
                        }}>
                          {robot.description || `${robot.default_provider}/${robot.default_model}`}
                        </div>
                      </div>
                    </div>
                  </Radio>
                ))}
              </Space>
            </Radio.Group>
          )}
        </div>
      </Modal>
    </div>
  );
};

export default ConversationList;

