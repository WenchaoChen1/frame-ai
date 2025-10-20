import React, { useState, useEffect } from 'react';
import { 
  Modal, 
  Tabs, 
  Descriptions, 
  Tag, 
  List, 
  Avatar, 
  Spin, 
  Empty,
  message,
  Button,
  Space,
  Form,
  Input,
  Select,
  InputNumber,
  Switch,
  Card
} from 'antd';
import { 
  SettingOutlined,
  MessageOutlined,
  DatabaseOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  GlobalOutlined,
  PlusOutlined,
  EditOutlined,
  SaveOutlined,
  CloseOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { 
  robotService, 
  Robot, 
  Conversation,
  DatabaseConfig as DBConfig
} from '../../services/robot';
import { providerService, Provider } from '../../services/provider';
import { useAuthStore } from '../../store/authStore';
import DatabaseConfig from './DatabaseConfig';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import 'dayjs/locale/zh-cn';

dayjs.extend(relativeTime);
dayjs.locale('zh-cn');

const { TextArea } = Input;

// 常用emoji列表
const EMOJI_OPTIONS = [
  '🤖', '🦾', '🧠', '💬', '💡', '⚡', '🔥', '✨', 
  '🎯', '🚀', '🎨', '📚', '🔬', '🎭', '🎪', '🎬',
  '🐱', '🐶', '🦊', '🦁', '🐼', '🐨', '🐯', '🦄'
];

interface RobotDetailModalProps {
  visible: boolean;
  robot: Robot | null;
  onClose: () => void;
  onRobotUpdated?: () => void;
}

const RobotDetailModal: React.FC<RobotDetailModalProps> = ({ 
  visible, 
  robot, 
  onClose,
  onRobotUpdated
}) => {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [loading, setLoading] = useState(false);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [dbConfig, setDbConfig] = useState<DBConfig | null>(null);
  const [activeTab, setActiveTab] = useState('config');
  const [isEditing, setIsEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [providers, setProviders] = useState<Provider[]>([]);
  const [form] = Form.useForm();

  useEffect(() => {
    if (visible && robot) {
      loadData();
      loadProviders();
      // 重置表单数据
      form.setFieldsValue({
        name: robot.name,
        description: robot.description,
        avatar: robot.avatar,
        default_provider: robot.default_provider,
        default_model: robot.default_model,
        system_prompt: robot.system_prompt,
        temperature: robot.temperature,
        max_tokens: robot.max_tokens,
        is_global: robot.is_global,
      });
    }
  }, [visible, robot]);

  const loadData = async () => {
    if (!robot) return;
    
    setLoading(true);
    try {
      // 并行加载对话列表和数据库配置
      const [conversationsData, dbConfigData] = await Promise.all([
        robotService.getRobotConversations(robot.id),
        robotService.getDatabaseConfig(robot.id).catch(() => null),
      ]);
      
      setConversations(conversationsData);
      setDbConfig(dbConfigData);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '加载数据失败');
    } finally {
      setLoading(false);
    }
  };

  const loadProviders = async () => {
    try {
      const data = await providerService.getProviders();
      setProviders(data);
    } catch (error) {
      console.error('加载AI提供商失败', error);
    }
  };

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    // 重置表单
    if (robot) {
      form.setFieldsValue({
        name: robot.name,
        description: robot.description,
        avatar: robot.avatar,
        default_provider: robot.default_provider,
        default_model: robot.default_model,
        system_prompt: robot.system_prompt,
        temperature: robot.temperature,
        max_tokens: robot.max_tokens,
        is_global: robot.is_global,
      });
    }
  };

  const handleSave = async () => {
    if (!robot) return;
    
    try {
      const values = await form.validateFields();
      setSaving(true);
      
      await robotService.updateRobot(robot.id, values);
      message.success('机器人信息更新成功');
      setIsEditing(false);
      
      // 重新加载数据
      await loadData();
      
      // 通知父组件刷新机器人列表
      if (onRobotUpdated) {
        onRobotUpdated();
      }
    } catch (error: any) {
      if (error.errorFields) {
        message.error('请填写完整的信息');
      } else {
        message.error(error.response?.data?.detail || '更新失败');
      }
    } finally {
      setSaving(false);
    }
  };

  const handleConversationClick = (convId: number) => {
    navigate(`/chat/${convId}`);
    onClose();
  };

  const handleCreateConversation = () => {
    if (robot) {
      navigate(`/chat?robot_id=${robot.id}`);
      onClose();
    }
  };

  const handleConfigSaved = () => {
    // 重新加载数据库配置
    if (robot) {
      robotService.getDatabaseConfig(robot.id)
        .then(setDbConfig)
        .catch(() => setDbConfig(null));
    }
  };

  if (!robot) return null;

  // 检查是否有编辑权限
  const canEdit = robot && (robot.user_id === user?.id || user?.role === 'admin');

  // 获取选中提供商的模型列表
  const selectedProvider = providers.find(p => p.name === form.getFieldValue('default_provider'));
  const availableModels = selectedProvider?.models || [];

  const tabItems = [
    {
      key: 'config',
      label: (
        <span>
          <SettingOutlined />
          机器人详情
        </span>
      ),
      children: (
        <div style={{ padding: '16px 0' }}>
          {/* 编辑按钮 */}
          {canEdit && !isEditing && (
            <div style={{ marginBottom: 16, textAlign: 'right' }}>
              <Button 
                type="primary" 
                icon={<EditOutlined />}
                onClick={handleEdit}
                style={{
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  border: 'none'
                }}
              >
                编辑信息
              </Button>
            </div>
          )}

          {/* 编辑模式 */}
          {isEditing ? (
            <Card 
              style={{ 
                background: '#fafafa',
                border: '1px solid #e8e8e8'
              }}
            >
              <Form
                form={form}
                layout="vertical"
                autoComplete="off"
              >
                <Form.Item
                  label="机器人名称"
                  name="name"
                  rules={[{ required: true, message: '请输入机器人名称' }]}
                >
                  <Input placeholder="为你的机器人起个名字" />
                </Form.Item>

                <Form.Item
                  label="头像"
                  name="avatar"
                >
                  <Select
                    placeholder="选择一个emoji作为头像"
                    showSearch
                    style={{ width: '100%' }}
                  >
                    {EMOJI_OPTIONS.map(emoji => (
                      <Select.Option key={emoji} value={emoji}>
                        <span style={{ fontSize: 20, marginRight: 8 }}>{emoji}</span>
                        {emoji}
                      </Select.Option>
                    ))}
                  </Select>
                </Form.Item>

                <Form.Item
                  label="描述"
                  name="description"
                >
                  <TextArea 
                    rows={3} 
                    placeholder="简短描述这个机器人的用途"
                  />
                </Form.Item>

                <Form.Item
                  label="系统提示词"
                  name="system_prompt"
                  tooltip="定义机器人的角色和行为方式"
                >
                  <TextArea 
                    rows={6} 
                    placeholder="你是一个有帮助的AI助手..."
                  />
                </Form.Item>

                <Form.Item
                  label="AI提供商"
                  name="default_provider"
                  rules={[{ required: true, message: '请选择AI提供商' }]}
                >
                  <Select
                    placeholder="选择AI提供商"
                    onChange={() => form.setFieldsValue({ default_model: undefined })}
                  >
                    {providers.map(provider => (
                      <Select.Option key={provider.name} value={provider.name}>
                        {provider.name}
                      </Select.Option>
                    ))}
                  </Select>
                </Form.Item>

                <Form.Item
                  label="默认模型"
                  name="default_model"
                  rules={[{ required: true, message: '请选择默认模型' }]}
                >
                  <Select placeholder="选择模型">
                    {availableModels.map(model => (
                      <Select.Option key={model} value={model}>
                        {model}
                      </Select.Option>
                    ))}
                  </Select>
                </Form.Item>

                <Form.Item
                  label="温度 (Temperature)"
                  name="temperature"
                  tooltip="控制输出的随机性，0-2之间"
                >
                  <InputNumber 
                    min={0} 
                    max={2} 
                    step={0.1} 
                    style={{ width: '100%' }}
                    placeholder="0.7"
                  />
                </Form.Item>

                <Form.Item
                  label="最大Token数"
                  name="max_tokens"
                  tooltip="限制响应的最大长度"
                >
                  <InputNumber 
                    min={1} 
                    max={32000} 
                    style={{ width: '100%' }}
                    placeholder="2000"
                  />
                </Form.Item>

                {user?.role === 'admin' && (
                  <Form.Item
                    label="全局机器人"
                    name="is_global"
                    valuePropName="checked"
                    tooltip="全局机器人对所有用户可见"
                  >
                    <Switch />
                  </Form.Item>
                )}

                <div style={{ textAlign: 'right', marginTop: 24 }}>
                  <Space>
                    <Button 
                      icon={<CloseOutlined />}
                      onClick={handleCancelEdit}
                    >
                      取消
                    </Button>
                    <Button 
                      type="primary" 
                      icon={<SaveOutlined />}
                      onClick={handleSave}
                      loading={saving}
                      style={{
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        border: 'none'
                      }}
                    >
                      保存修改
                    </Button>
                  </Space>
                </div>
              </Form>
            </Card>
          ) : (
            /* 查看模式 */
            <div>
              <Card 
                style={{ 
                  marginBottom: 16,
                  background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%)',
                  border: '1px solid rgba(102, 126, 234, 0.2)'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                  <Avatar 
                    size={80} 
                    style={{ 
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      fontSize: 48
                    }}
                  >
                    {robot.avatar || '🤖'}
                  </Avatar>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 24, fontWeight: 600, marginBottom: 8 }}>
                      {robot.name}
                    </div>
                    <div style={{ color: '#666', fontSize: 14 }}>
                      {robot.description || '暂无描述'}
                    </div>
                  </div>
                </div>
              </Card>

              <Descriptions
                bordered
                column={{ xs: 1, sm: 1, md: 2 }}
                labelStyle={{ fontWeight: 600, background: '#fafafa', width: '140px' }}
                contentStyle={{ background: '#fff' }}
              >
                <Descriptions.Item label="系统提示词" span={2}>
                  <div style={{ 
                    maxHeight: 200, 
                    overflow: 'auto',
                    whiteSpace: 'pre-wrap',
                    background: '#f5f5f5',
                    padding: 12,
                    borderRadius: 8,
                    fontSize: 13,
                    lineHeight: 1.6
                  }}>
                    {robot.system_prompt || '-'}
                  </div>
                </Descriptions.Item>
                <Descriptions.Item label="AI提供商">
                  <Tag color="blue" style={{ fontSize: 13 }}>{robot.default_provider}</Tag>
                </Descriptions.Item>
                <Descriptions.Item label="默认模型">
                  <Tag color="purple" style={{ fontSize: 13 }}>{robot.default_model}</Tag>
                </Descriptions.Item>
                <Descriptions.Item label="温度">
                  <Tag color="orange">
                    {robot.temperature !== null && robot.temperature !== undefined ? robot.temperature : '-'}
                  </Tag>
                </Descriptions.Item>
                <Descriptions.Item label="最大Token数">
                  <Tag color="cyan">{robot.max_tokens || '-'}</Tag>
                </Descriptions.Item>
                <Descriptions.Item label="全局机器人" span={2}>
                  {robot.is_global ? (
                    <Tag color="green" icon={<CheckCircleOutlined />}>是</Tag>
                  ) : (
                    <Tag>否</Tag>
                  )}
                </Descriptions.Item>
                <Descriptions.Item label="创建时间">
                  {dayjs(robot.created_at).format('YYYY-MM-DD HH:mm:ss')}
                </Descriptions.Item>
                <Descriptions.Item label="更新时间">
                  {dayjs(robot.updated_at).format('YYYY-MM-DD HH:mm:ss')}
                </Descriptions.Item>
              </Descriptions>
            </div>
          )}
        </div>
      ),
    },
    {
      key: 'conversations',
      label: (
        <span>
          <MessageOutlined />
          历史对话
          <Tag color="blue" style={{ marginLeft: 8 }}>{conversations.length}</Tag>
        </span>
      ),
      children: (
        <div style={{ padding: '16px 0' }}>
          <div style={{ marginBottom: 16, textAlign: 'right' }}>
            <Button 
              type="primary" 
              icon={<PlusOutlined />}
              onClick={handleCreateConversation}
              style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                border: 'none'
              }}
            >
              新建对话
            </Button>
          </div>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '60px 0' }}>
              <Spin size="large" tip="加载中..." />
            </div>
          ) : conversations.length === 0 ? (
            <Empty 
              description="暂无对话，点击新建对话开始聊天"
              style={{ padding: '60px 0' }}
            />
          ) : (
            <List
              dataSource={conversations}
              renderItem={(conv) => (
                <List.Item
                  key={conv.id}
                  onClick={() => handleConversationClick(conv.id)}
                  style={{
                    cursor: 'pointer',
                    padding: '16px 20px',
                    borderRadius: 12,
                    transition: 'all 0.2s ease',
                    marginBottom: 8,
                    border: '1px solid transparent',
                    background: '#fafafa'
                  }}
                  className="conversation-item"
                >
                  <List.Item.Meta
                    avatar={
                      <Avatar 
                        size={48}
                        style={{ 
                          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                          fontSize: 24
                        }}
                      >
                        {robot.avatar || '🤖'}
                      </Avatar>
                    }
                    title={
                      <div style={{ fontSize: 16, fontWeight: 500, color: '#333' }}>
                        {conv.title}
                      </div>
                    }
                    description={
                      <Space style={{ color: '#999', fontSize: 13 }}>
                        <ClockCircleOutlined />
                        <span>更新于 {dayjs(conv.updated_at).fromNow()}</span>
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          )}
        </div>
      ),
    },
    {
      key: 'database',
      label: (
        <span>
          <DatabaseOutlined />
          数据库连接
          {dbConfig && <CheckCircleOutlined style={{ marginLeft: 8, color: '#52c41a' }} />}
        </span>
      ),
      children: (
        <DatabaseConfig
          robotId={robot.id}
          existingConfig={dbConfig}
          onConfigSaved={handleConfigSaved}
        />
      ),
    },
  ];

  return (
    <>
      <Modal
        title={
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <Avatar 
              size={48} 
              style={{ 
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                fontSize: 24
              }}
            >
              {robot.avatar || '🤖'}
            </Avatar>
            <div>
              <div style={{ fontSize: 18, fontWeight: 600 }}>
                {robot.name}
                {robot.is_global && (
                  <Tag color="blue" icon={<GlobalOutlined />} style={{ marginLeft: 8 }}>
                    全局
                  </Tag>
                )}
              </div>
              <div style={{ fontSize: 13, color: '#999', fontWeight: 'normal' }}>
                {robot.description || '暂无描述'}
              </div>
            </div>
          </div>
        }
        open={visible}
        onCancel={onClose}
        footer={null}
        width="100vw"
        style={{ top: 0, margin: 0, padding: 0, maxWidth: '100vw' }}
        styles={{ 
          body: { 
            height: 'calc(100vh - 110px)', 
            maxHeight: 'calc(100vh - 110px)', 
            overflow: 'auto', 
            padding: '24px 32px' 
          } 
        }}
        centered={false}
      >
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={tabItems}
          size="large"
        />
      </Modal>

      <style>{`
        .conversation-item:hover {
          background: #f5f7fa !important;
          border-color: #667eea !important;
        }
      `}</style>
    </>
  );
};

export default RobotDetailModal;

