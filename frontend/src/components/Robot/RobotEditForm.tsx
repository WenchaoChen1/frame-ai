import React, { useState } from 'react';
import {
  Form,
  Input,
  Select,
  InputNumber,
  Radio,
  Row,
  Col,
  Collapse,
  Space,
  Button,
  Tag,
  Drawer,
  Tree,
  Empty,
  message
} from 'antd';
import {
  DatabaseOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  EyeOutlined
} from '@ant-design/icons';
import { Provider } from '../../services/provider';
import { 
  DatabaseConfig, 
  DatabaseSchemaResponse,
  robotService 
} from '../../services/robot';
import { useAuthStore } from '../../store/authStore';

const { TextArea } = Input;

// 常用emoji列表
const EMOJI_OPTIONS = [
  '🤖', '🦾', '🧠', '💬', '💡', '⚡', '🔥', '✨', 
  '🎯', '🚀', '🎨', '📚', '🔬', '🎭', '🎪', '🎬',
  '🐱', '🐶', '🦊', '🦁', '🐼', '🐨', '🐯', '🦄'
];

interface RobotEditFormProps {
  form: any;
  providers: Provider[];
  robotId?: number;
  dbConfig: DatabaseConfig | null;
  setDbConfig?: (config: DatabaseConfig | null) => void;
  showGlobalOption?: boolean;
}

const RobotEditForm: React.FC<RobotEditFormProps> = ({
  form,
  providers,
  robotId,
  dbConfig,
  setDbConfig: _setDbConfig,
  showGlobalOption = true
}) => {
  const { user } = useAuthStore();
  const [testingConnection, setTestingConnection] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'success' | 'error' | null>(null);
  const [schemaDrawerVisible, setSchemaDrawerVisible] = useState(false);
  const [databaseSchema, setDatabaseSchema] = useState<DatabaseSchemaResponse | null>(null);
  const [loadingSchema, setLoadingSchema] = useState(false);
  const [expandedDbPanel, setExpandedDbPanel] = useState<string[]>([]);

  // 测试数据库连接
  const handleTestConnection = async () => {
    try {
      const values = await form.validateFields(['db_type', 'db_host', 'db_port', 'db_name', 'db_username', 'db_password']);
      
      if (!values.db_type || !values.db_host || !values.db_port || !values.db_name || !values.db_username) {
        message.warning('请先填写完整的数据库连接信息');
        return;
      }

      if (!values.db_password && !dbConfig) {
        message.warning('请输入数据库密码');
        return;
      }

      setTestingConnection(true);
      setConnectionStatus(null);

      const testData = {
        db_type: values.db_type,
        host: values.db_host,
        port: values.db_port,
        database_name: values.db_name,
        username: values.db_username,
        password: values.db_password || ''
      };

      const result = await robotService.testDatabaseConnection(robotId || 0, testData);

      if (result.success) {
        message.success(result.message);
        setConnectionStatus('success');
      } else {
        message.error(result.message);
        setConnectionStatus('error');
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || '测试连接失败');
      setConnectionStatus('error');
    } finally {
      setTestingConnection(false);
    }
  };

  // 查看数据库结构
  const handleViewSchema = async () => {
    if (!robotId || !dbConfig) {
      message.warning('请先保存数据库配置');
      return;
    }

    setLoadingSchema(true);
    try {
      const schema = await robotService.getDatabaseSchema(robotId);
      setDatabaseSchema(schema);
      setSchemaDrawerVisible(true);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '获取数据库结构失败');
    } finally {
      setLoadingSchema(false);
    }
  };

  return (
    <>
      <Form.Item
        label="机器人名称"
        name="name"
        rules={[{ required: true, message: '请输入机器人名称' }]}
      >
        <Input placeholder="请输入机器人名称" size="large" />
      </Form.Item>

      <Form.Item
        label="头像"
        name="avatar"
      >
        <Select
          placeholder="选择一个emoji作为头像"
          style={{ width: '100%' }}
          size="large"
        >
          {EMOJI_OPTIONS.map(emoji => (
            <Select.Option key={emoji} value={emoji}>
              <span style={{ fontSize: 20 }}>{emoji}</span>
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
          placeholder="请输入机器人描述"
          size="large"
        />
      </Form.Item>

      <Form.Item
        label="系统提示词"
        name="system_prompt"
        tooltip="定义机器人的角色和行为特征"
      >
        <TextArea 
          rows={5} 
          placeholder="例如：你是一个专业的Python编程助手..."
          size="large"
        />
      </Form.Item>

      <Row gutter={24}>
        <Col span={12}>
          <Form.Item
            label="默认提供商"
            name="default_provider"
            rules={[{ required: true, message: '请选择默认提供商' }]}
          >
            <Select
              placeholder="选择AI提供商"
              size="large"
              onChange={(value) => {
                const provider = providers.find(p => p.name === value);
                if (provider && provider.models.length > 0) {
                  form.setFieldsValue({ default_model: provider.models[0] });
                }
              }}
            >
              {providers.map(p => (
                <Select.Option key={p.name} value={p.name}>
                  {p.name}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item
            label="默认模型"
            name="default_model"
            rules={[{ required: true, message: '请选择默认模型' }]}
          >
            <Select placeholder="选择模型" size="large">
              {providers
                .find(p => p.name === form.getFieldValue('default_provider'))
                ?.models.map(m => (
                  <Select.Option key={m} value={m}>
                    {m}
                  </Select.Option>
                )) || []}
            </Select>
          </Form.Item>
        </Col>
      </Row>

      <Row gutter={24}>
        <Col span={12}>
          <Form.Item
            label="温度"
            name="temperature"
            tooltip="控制生成文本的随机性，0-2之间"
          >
            <InputNumber 
              min={0} 
              max={2} 
              step={0.1}
              style={{ width: '100%' }}
              placeholder="0.7"
              size="large"
            />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item
            label="最大Token数"
            name="max_tokens"
            tooltip="限制生成文本的长度"
          >
            <InputNumber 
              min={1}
              style={{ width: '100%' }}
              placeholder="留空使用默认值"
              size="large"
            />
          </Form.Item>
        </Col>
      </Row>

      {showGlobalOption && user?.role === 'admin' && (
        <Form.Item
          label="是否全局"
          name="is_global"
          valuePropName="checked"
          tooltip="全局机器人对所有用户可见"
        >
          <Radio.Group>
            <Radio value={true}>全局机器人</Radio>
            <Radio value={false}>私有机器人</Radio>
          </Radio.Group>
        </Form.Item>
      )}

      {/* 数据库配置折叠面板 */}
      <Collapse 
        ghost 
        activeKey={expandedDbPanel}
        onChange={(keys) => setExpandedDbPanel(keys as string[])}
        style={{ marginTop: 16 }}
        items={[
          {
            key: 'database',
            label: (
              <Space>
                <DatabaseOutlined />
                <span>数据库配置（可选）</span>
                {dbConfig && <Tag color="green">已配置</Tag>}
              </Space>
            ),
            children: (
              <>
                <Form.Item
                  label="数据库类型"
                  name="db_type"
                >
                  <Select 
                    placeholder="选择数据库类型"
                    size="large"
                    onChange={() => {
                      const dbType = form.getFieldValue('db_type');
                      if (dbType === 'postgresql') {
                        form.setFieldsValue({ db_port: 5432 });
                      } else if (dbType === 'mysql') {
                        form.setFieldsValue({ db_port: 3306 });
                      } else if (dbType === 'redshift') {
                        form.setFieldsValue({ db_port: 5439 });
                      }
                    }}
                  >
                    <Select.Option value="postgresql">PostgreSQL</Select.Option>
                    <Select.Option value="mysql">MySQL</Select.Option>
                    <Select.Option value="redshift">Redshift</Select.Option>
                  </Select>
                </Form.Item>

                <Row gutter={24}>
                  <Col span={16}>
                    <Form.Item
                      label="主机地址"
                      name="db_host"
                    >
                      <Input placeholder="例如: localhost 或 192.168.1.100" size="large" />
                    </Form.Item>
                  </Col>
                  <Col span={8}>
                    <Form.Item
                      label="端口"
                      name="db_port"
                    >
                      <InputNumber 
                        min={1} 
                        max={65535} 
                        style={{ width: '100%' }}
                        placeholder="5432"
                        size="large"
                      />
                    </Form.Item>
                  </Col>
                </Row>

                <Form.Item
                  label="数据库名称"
                  name="db_name"
                >
                  <Input placeholder="数据库名称" size="large" />
                </Form.Item>

                <Row gutter={24}>
                  <Col span={12}>
                    <Form.Item
                      label="用户名"
                      name="db_username"
                    >
                      <Input placeholder="数据库用户名" size="large" />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item
                      label="密码"
                      name="db_password"
                    >
                      <Input.Password 
                        placeholder={dbConfig ? "留空则不修改密码" : "数据库密码"}
                        size="large"
                      />
                    </Form.Item>
                  </Col>
                </Row>

                <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
                  {connectionStatus === 'success' && (
                    <Tag color="success" icon={<CheckCircleOutlined />}>连接成功</Tag>
                  )}
                  {connectionStatus === 'error' && (
                    <Tag color="error" icon={<CloseCircleOutlined />}>连接失败</Tag>
                  )}
                  <Button 
                    icon={<DatabaseOutlined />}
                    onClick={handleTestConnection}
                    loading={testingConnection}
                  >
                    测试连接
                  </Button>
                  {robotId && dbConfig && (
                    <Button 
                      icon={<EyeOutlined />}
                      onClick={handleViewSchema}
                      loading={loadingSchema}
                      type="primary"
                      ghost
                    >
                      查看结构
                    </Button>
                  )}
                </Space>
              </>
            )
          }
        ]}
      />

      {/* 数据库结构查看抽屉 */}
      <Drawer
        title="数据库结构"
        placement="right"
        width={600}
        open={schemaDrawerVisible}
        onClose={() => setSchemaDrawerVisible(false)}
      >
        {databaseSchema && databaseSchema.tables.length > 0 ? (
          <div>
            <p style={{ marginBottom: 16, color: '#666' }}>
              共 {databaseSchema.tables.length} 个表
            </p>
            <Tree
              showLine
              defaultExpandAll
              treeData={databaseSchema.tables.map(table => ({
                title: (
                  <Space>
                    <DatabaseOutlined />
                    <strong>{table.name}</strong>
                    <Tag>{table.columns.length} 个字段</Tag>
                  </Space>
                ),
                key: table.name,
                children: table.columns.map(column => ({
                  title: (
                    <Space>
                      <span>{column.name}</span>
                      <Tag color="blue">{column.type}</Tag>
                      {!column.nullable && <Tag color="red">NOT NULL</Tag>}
                    </Space>
                  ),
                  key: `${table.name}.${column.name}`,
                  isLeaf: true
                }))
              }))}
            />
          </div>
        ) : (
          <Empty description="暂无数据" />
        )}
      </Drawer>
    </>
  );
};

export default RobotEditForm;

