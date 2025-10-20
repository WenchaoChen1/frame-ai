import React, { useState, useEffect } from 'react';
import { 
  Modal, 
  Form, 
  Input, 
  Select, 
  InputNumber, 
  Switch, 
  message,
  Button
} from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { robotService, RobotCreate } from '../../services/robot';
import { providerService, Provider } from '../../services/provider';
import { useAuthStore } from '../../store/authStore';

const { TextArea } = Input;

// 常用emoji列表
const EMOJI_OPTIONS = [
  '🤖', '🦾', '🧠', '💬', '💡', '⚡', '🔥', '✨', 
  '🎯', '🚀', '🎨', '📚', '🔬', '🎭', '🎪', '🎬',
  '🐱', '🐶', '🦊', '🦁', '🐼', '🐨', '🐯', '🦄'
];

interface CreateRobotModalProps {
  visible: boolean;
  onClose: () => void;
  onRobotCreated?: () => void;
}

const CreateRobotModal: React.FC<CreateRobotModalProps> = ({ 
  visible, 
  onClose,
  onRobotCreated
}) => {
  const { user } = useAuthStore();
  const [form] = Form.useForm();
  const [providers, setProviders] = useState<Provider[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedProviderName, setSelectedProviderName] = useState<string>('');

  useEffect(() => {
    if (visible) {
      loadProviders();
      // 重置表单
      form.resetFields();
      setSelectedProviderName('');
    }
  }, [visible]);

  const loadProviders = async () => {
    try {
      const data = await providerService.getProviders();
      setProviders(data);
    } catch (error) {
      console.error('加载AI提供商失败', error);
      message.error('加载AI提供商失败');
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);

      const robotData: RobotCreate = {
        name: values.name,
        description: values.description,
        avatar: values.avatar,
        default_provider: values.default_provider,
        default_model: values.default_model,
        system_prompt: values.system_prompt,
        temperature: values.temperature,
        max_tokens: values.max_tokens,
        is_global: values.is_global || false,
      };

      await robotService.createRobot(robotData);
      message.success('机器人创建成功');
      
      // 通知父组件刷新列表
      if (onRobotCreated) {
        onRobotCreated();
      }
      
      // 关闭弹框
      onClose();
      form.resetFields();
    } catch (error: any) {
      if (error.errorFields) {
        message.error('请填写完整的信息');
      } else {
        message.error(error.response?.data?.detail || '创建失败');
      }
    } finally {
      setLoading(false);
    }
  };

  // 获取选中提供商的模型列表
  const selectedProvider = providers.find(p => p.name === selectedProviderName);
  const availableModels = selectedProvider?.models || [];
  
  // 处理提供商变化
  const handleProviderChange = (providerName: string) => {
    setSelectedProviderName(providerName);
    form.setFieldsValue({ default_model: undefined });
  };

  return (
    <Modal
      title={
        <div style={{ 
          fontSize: 18, 
          fontWeight: 600,
          display: 'flex',
          alignItems: 'center',
          gap: 8
        }}>
          <PlusOutlined />
          新增机器人
        </div>
      }
      open={visible}
      onCancel={() => {
        onClose();
        form.resetFields();
        setSelectedProviderName('');
      }}
      onOk={handleSubmit}
      confirmLoading={loading}
      width={700}
      okText="创建"
      cancelText="取消"
      okButtonProps={{
        style: {
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          border: 'none'
        }
      }}
    >
      <Form
        form={form}
        layout="vertical"
        autoComplete="off"
        initialValues={{
          temperature: 0.7,
          max_tokens: 2000,
          is_global: false,
        }}
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
            placeholder="选择一个emoji作为头像（可选）"
            showSearch
            allowClear
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
            placeholder="简短描述这个机器人的用途（可选）"
          />
        </Form.Item>

        <Form.Item
          label="系统提示词"
          name="system_prompt"
          tooltip="定义机器人的角色和行为方式"
        >
          <TextArea 
            rows={6} 
            placeholder="例如：你是一个有帮助的AI助手，专注于回答技术问题..."
          />
        </Form.Item>

        <Form.Item
          label="AI提供商"
          name="default_provider"
          rules={[{ required: true, message: '请选择AI提供商' }]}
        >
          <Select
            placeholder="选择AI提供商"
            onChange={handleProviderChange}
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
          <Select 
            placeholder="选择模型"
            disabled={!selectedProviderName}
          >
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
          tooltip="控制输出的随机性，0-2之间，值越大输出越随机"
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
      </Form>
    </Modal>
  );
};

export default CreateRobotModal;

