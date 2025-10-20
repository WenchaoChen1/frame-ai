import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Button, 
  Space, 
  message,
  Popconfirm,
  Tag,
  Row,
  Col,
  Radio,
  Spin,
  Empty,
  Avatar
} from 'antd';
import { 
  DeleteOutlined,
  GlobalOutlined,
  MessageOutlined,
  ReloadOutlined,
  SettingOutlined,
  PlusOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { 
  robotService, 
  Robot
} from '../services/robot';
import { useAuthStore } from '../store/authStore';
import RobotDetailModal from '../components/Robot/RobotDetailModal';
import CreateRobotModal from '../components/Robot/CreateRobotModal';

const RobotManagement: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [robots, setRobots] = useState<Robot[]>([]);
  const [loading, setLoading] = useState(false);
  const [filterType, setFilterType] = useState<'all' | 'global' | 'mine'>('all');
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [selectedRobot, setSelectedRobot] = useState<Robot | null>(null);
  const [createModalVisible, setCreateModalVisible] = useState(false);

  useEffect(() => {
    fetchRobots();
  }, []);

  const fetchRobots = async () => {
    setLoading(true);
    try {
      const data = await robotService.getRobots();
      setRobots(data);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '获取机器人列表失败');
    } finally {
      setLoading(false);
    }
  };


  const handleDelete = async (robotId: number) => {
    try {
      await robotService.deleteRobot(robotId);
      message.success('机器人删除成功');
      fetchRobots();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '删除失败');
    }
  };

  const handleCardClick = (robot: Robot) => {
    // 跳转到聊天页面，并自动选择该机器人
    navigate(`/chat?robot_id=${robot.id}`);
  };

  const handleDeleteClick = (e: React.MouseEvent) => {
    e.stopPropagation();
  };

  const handleOpenDetail = (e: React.MouseEvent, robot: Robot) => {
    e.stopPropagation();
    setSelectedRobot(robot);
    setDetailModalVisible(true);
  };

  const handleCloseDetail = () => {
    setDetailModalVisible(false);
    setSelectedRobot(null);
  };

  const handleRobotUpdated = () => {
    // 重新加载机器人列表
    fetchRobots();
  };

  // 过滤机器人
  const filteredRobots = robots.filter(robot => {
    if (filterType === 'global') return robot.is_global;
    if (filterType === 'mine') return robot.user_id === user?.id;
    return true;
  });

  // 获取提供商显示名称
  const getProviderInfo = (providerName: string) => {
    const configs: Record<string, { label: string; color: string }> = {
      'openai': { label: 'OpenAI', color: '#10a37f' },
      'claude': { label: 'Claude', color: '#6b46c1' },
      'ollama': { label: 'Ollama', color: '#ff6b6b' },
    };
    return configs[providerName] || { label: providerName, color: '#1890ff' };
  };

  return (
    <div style={{ padding: '24px', background: '#f5f7fa', minHeight: 'calc(100vh - 64px)' }}>
      <div style={{ 
        marginBottom: 24, 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: 16
      }}>
        <div>
          <h2 style={{ 
            margin: 0, 
            fontSize: 24, 
            fontWeight: 600,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            机器人管理
          </h2>
          <p style={{ margin: '8px 0 0 0', color: '#999', fontSize: 14 }}>
            管理AI机器人，配置默认模型和参数
          </p>
        </div>
        <Space>
          <Radio.Group value={filterType} onChange={e => setFilterType(e.target.value)}>
            <Radio.Button value="all">全部</Radio.Button>
            <Radio.Button value="global">全局</Radio.Button>
            <Radio.Button value="mine">我的</Radio.Button>
          </Radio.Group>
          <Button 
            icon={<ReloadOutlined />} 
            onClick={fetchRobots}
          >
            刷新
          </Button>
          <Button 
            type="primary"
            icon={<PlusOutlined />} 
            onClick={() => setCreateModalVisible(true)}
            style={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              border: 'none'
            }}
          >
            新增机器人
          </Button>
        </Space>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '100px 0' }}>
          <Spin size="large" tip="加载中..." />
        </div>
      ) : filteredRobots.length === 0 ? (
        <Empty 
          description="暂无机器人，点击新建创建第一个机器人"
          style={{ padding: '100px 0' }}
        />
      ) : (
        <Row gutter={[24, 24]}>
          {filteredRobots.map((robot) => {
            const providerInfo = getProviderInfo(robot.default_provider);
            const isOwner = robot.user_id === user?.id;
            const isAdmin = user?.role === 'admin';
            const canEdit = isOwner || isAdmin;

            return (
              <Col xs={24} sm={12} md={8} lg={6} key={robot.id}>
                <Card
                  hoverable
                  onClick={() => handleCardClick(robot)}
                  style={{
                    borderRadius: 16,
                    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
                    border: '1px solid rgba(0, 0, 0, 0.06)',
                    transition: 'all 0.3s ease',
                    cursor: 'pointer',
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column'
                  }}
                  styles={{ body: { padding: 20, flex: 1, display: 'flex', flexDirection: 'column' } }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
                    <Avatar 
                      size={56} 
                      style={{ 
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        fontSize: 32
                      }}
                    >
                    {robot.avatar || '🤖'}
                  </Avatar>
                    <Space>
                      <Button
                        type="text"
                        size="small"
                        icon={<SettingOutlined />}
                        onClick={(e) => handleOpenDetail(e, robot)}
                        style={{ color: '#667eea' }}
                      />
                      {canEdit && (
                        <Popconfirm
                          title="确定删除此机器人？"
                          onConfirm={() => handleDelete(robot.id)}
                          okText="确定"
                          cancelText="取消"
                        >
                          <Button
                            type="text"
                            size="small"
                            danger
                            icon={<DeleteOutlined />}
                            onClick={handleDeleteClick}
                          />
                        </Popconfirm>
                      )}
                    </Space>
                  </div>

                  <div style={{ flex: 1 }}>
                    <h3 style={{ 
                      margin: '0 0 8px 0', 
                      fontSize: 16, 
                      fontWeight: 600,
                      color: '#333',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 8
                    }}>
                      {robot.name}
                      {robot.is_global && (
                        <Tag color="blue" icon={<GlobalOutlined />}>全局</Tag>
                      )}
                    </h3>
                    <p style={{ 
                      margin: '0 0 16px 0', 
                      color: '#999', 
                      fontSize: 13,
                      lineHeight: 1.6,
                      minHeight: 40,
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden'
                    }}>
                      {robot.description || '暂无描述'}
                    </p>
                  </div>

                  <div style={{ 
                    paddingTop: 16, 
                    borderTop: '1px solid #f0f0f0',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                  }}>
                    <div style={{ fontSize: 12 }}>
                      <Tag 
                        color={providerInfo.color}
                        style={{ 
                          margin: 0,
                          borderRadius: 4,
                          fontSize: 11
                        }}
                      >
                        {robot.default_model}
                      </Tag>
                    </div>
                    <MessageOutlined style={{ color: '#999', fontSize: 16 }} />
                  </div>
                </Card>
              </Col>
            );
          })}
        </Row>
      )}

      {/* 机器人详情弹框 */}
      <RobotDetailModal
        visible={detailModalVisible}
        robot={selectedRobot}
        onClose={handleCloseDetail}
        onRobotUpdated={handleRobotUpdated}
      />

      {/* 创建机器人弹框 */}
      <CreateRobotModal
        visible={createModalVisible}
        onClose={() => setCreateModalVisible(false)}
        onRobotCreated={handleRobotUpdated}
      />
    </div>
  );
};

export default RobotManagement;

