import React, { useState, useEffect } from 'react';
import { 
  Steps, 
  Card, 
  Form, 
  Input, 
  Button, 
  message, 
  Alert, 
  Spin,
  List,
  Typography,
  Tag,
  Row,
  Col,
  Tree,
  Descriptions,
  Badge,
  Checkbox,
  Modal as AntModal,
  Popconfirm,
  Switch
} from 'antd';
import type { DataNode } from 'antd/es/tree';
import { 
  CheckCircleOutlined,
  LoadingOutlined,
  DatabaseOutlined,
  TableOutlined,
  FieldNumberOutlined,
  SettingOutlined,
  FilterOutlined,
  DisconnectOutlined
} from '@ant-design/icons';
import { 
  robotService, 
  DatabaseConfig as DBConfig,
  DatabaseTestRequest,
  TableSchema,
  TableMetadata,
  ColumnMetadata
} from '../../services/robot';

const { Text, Title } = Typography;

interface DatabaseConfigProps {
  robotId: number;
  existingConfig: DBConfig | null;
  onConfigSaved?: () => void;
}

type DatabaseType = 'postgresql' | 'mysql' | 'mssql' | 'databricks' | 'redshift';

const DATABASE_TYPES: Array<{
  type: DatabaseType;
  label: string;
  icon: string;
  defaultPort: number;
}> = [
  { type: 'postgresql', label: 'PostgreSQL', icon: '🐘', defaultPort: 5432 },
  { type: 'mysql', label: 'MySQL', icon: '🐬', defaultPort: 3306 },
  { type: 'mssql', label: 'MS SQL Server', icon: '🗄️', defaultPort: 1433 },
  { type: 'databricks', label: 'Databricks', icon: '🧱', defaultPort: 443 },
  { type: 'redshift', label: 'AWS Redshift', icon: '📊', defaultPort: 5439 },
];

const DatabaseConfig: React.FC<DatabaseConfigProps> = ({ 
  robotId, 
  existingConfig,
  onConfigSaved 
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [selectedType, setSelectedType] = useState<DatabaseType | null>(null);
  const [form] = Form.useForm();
  const [testing, setTesting] = useState(false);
  const [testSuccess, setTestSuccess] = useState(false);
  const [saving, setSaving] = useState(false);
  const [loadingSchema, setLoadingSchema] = useState(false);
  const [tables, setTables] = useState<TableSchema[]>([]);
  const [selectedTable, setSelectedTable] = useState<TableSchema | null>(null);
  const [expandedKeys, setExpandedKeys] = useState<React.Key[]>([]);
  const [selectedTableNames, setSelectedTableNames] = useState<string[]>([]);
  const [fieldSearchText, setFieldSearchText] = useState('');
  const [tableDescriptions, setTableDescriptions] = useState<Record<string, string>>({});
  const [columnSelections, setColumnSelections] = useState<Record<string, Record<string, boolean>>>({});
  const [columnDescriptions, setColumnDescriptions] = useState<Record<string, Record<string, string>>>({});
  const [showOnlySelected, setShowOnlySelected] = useState(false);

  useEffect(() => {
    if (existingConfig) {
      setSelectedType(existingConfig.db_type);
      setCurrentStep(2); // 跳到步骤2（查看数据库结构）
      form.setFieldsValue({
        host: existingConfig.host,
        port: existingConfig.port,
        database_name: existingConfig.database_name,
        username: existingConfig.username,
      });
      setTestSuccess(true);
      loadDatabaseSchema();
    }
  }, [existingConfig]);

  const loadDatabaseSchema = async () => {
    if (!robotId) return;
    setLoadingSchema(true);
    try {
      const schema = await robotService.getDatabaseSchema(robotId);
      setTables(schema.tables);
      
      // 初始化字段选择状态（默认全部选中）
      const initialColumnSelections: Record<string, Record<string, boolean>> = {};
      schema.tables.forEach(table => {
        initialColumnSelections[table.name] = {};
        table.columns.forEach(col => {
          initialColumnSelections[table.name][col.name] = true;
        });
      });
      
      // 尝试加载已保存的元数据
      let hasMetadata = false;
      try {
        const metadata = await robotService.getDatabaseMetadata(robotId);
        if (metadata && metadata.tables && metadata.tables.length > 0) {
          hasMetadata = true;
          
          // 恢复已保存的表选择状态
          const selectedTables = metadata.tables
            .filter(table => table.selected)
            .map(table => table.name);
          setSelectedTableNames(selectedTables);
          
          // 恢复已保存的选择和描述
          const descriptions: Record<string, string> = {};
          const colSelections: Record<string, Record<string, boolean>> = {};
          const colDescriptions: Record<string, Record<string, string>> = {};
          
          metadata.tables.forEach(table => {
            if (table.description) {
              descriptions[table.name] = table.description;
            }
            colSelections[table.name] = {};
            colDescriptions[table.name] = {};
            
            table.columns.forEach(col => {
              colSelections[table.name][col.name] = col.selected;
              if (col.description) {
                colDescriptions[table.name][col.name] = col.description;
              }
            });
          });
          
          setTableDescriptions(descriptions);
          setColumnSelections(colSelections);
          setColumnDescriptions(colDescriptions);
          
          console.log('已加载保存的元数据配置');
        }
      } catch (error) {
        console.log('未找到已保存的元数据，使用默认配置');
      }
      
      // 如果没有元数据，默认全部选中
      if (!hasMetadata) {
        setSelectedTableNames(schema.tables.map(t => t.name));
        setColumnSelections(initialColumnSelections);
      }
      
      // 默认选中第一个表
      if (schema.tables.length > 0) {
        setSelectedTable(schema.tables[0]);
      }
    } catch (error: any) {
      // 如果是 404 错误，说明配置不存在，静默处理
      if (error.response?.status === 404) {
        console.warn('数据库配置不存在');
        setTables([]);
      } else {
        // 其他错误才显示错误消息
        message.error(error.response?.data?.detail || '加载数据库结构失败');
      }
    } finally {
      setLoadingSchema(false);
    }
  };

  const handleTypeSelect = (type: DatabaseType) => {
    setSelectedType(type);
    const dbType = DATABASE_TYPES.find(db => db.type === type);
    form.setFieldsValue({
      port: dbType?.defaultPort,
    });
    setCurrentStep(1);
  };

  const handleTestConnection = async () => {
    try {
      await form.validateFields();
      const values = form.getFieldsValue();
      
      setTesting(true);
      const testData: DatabaseTestRequest = {
        db_type: selectedType!,
        host: values.host,
        port: values.port,
        database_name: values.database_name,
        username: values.username,
        password: values.password,
      };

      const result = await robotService.testDatabaseConnection(robotId, testData);
      
      if (result.success) {
        message.success('数据库连接测试成功！');
        setTestSuccess(true);
      } else {
        // 提取关键错误信息
        let errorMsg = result.message;
        if (errorMsg.includes('password authentication failed')) {
          errorMsg = '密码认证失败，请检查用户名和密码是否正确';
        } else if (errorMsg.includes('could not connect')) {
          errorMsg = '无法连接到数据库服务器，请检查主机地址和端口';
        } else if (errorMsg.includes('database') && errorMsg.includes('does not exist')) {
          errorMsg = '数据库不存在，请检查数据库名称';
        } else if (errorMsg.includes('timeout')) {
          errorMsg = '连接超时，请检查网络和防火墙设置';
        }
        
        message.error(errorMsg, 5);
        setTestSuccess(false);
      }
    } catch (error: any) {
      if (error.errorFields) {
        message.error('请填写完整的连接信息');
      } else {
        const errorDetail = error.response?.data?.detail || '测试连接失败';
        let friendlyMsg = errorDetail;
        
        if (errorDetail.includes('password authentication failed')) {
          friendlyMsg = '密码认证失败，请检查用户名和密码是否正确';
        } else if (errorDetail.includes('could not connect')) {
          friendlyMsg = '无法连接到数据库服务器，请检查主机地址和端口';
        }
        
        message.error(friendlyMsg, 5);
      }
      setTestSuccess(false);
    } finally {
      setTesting(false);
    }
  };

  const handleSaveConfig = async () => {
    try {
      await form.validateFields();
      const values = form.getFieldsValue();
      
      setSaving(true);
      await robotService.createOrUpdateDatabaseConfig(robotId, {
        db_type: selectedType!,
        host: values.host,
        port: values.port,
        database_name: values.database_name,
        username: values.username,
        password: values.password,
      });

      message.success('数据库配置保存成功！');
      setCurrentStep(2);
      await loadDatabaseSchema();
      if (onConfigSaved) {
        onConfigSaved();
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || '保存配置失败');
    } finally {
      setSaving(false);
    }
  };

  const getTypeColor = (type: string): string => {
    const colors: Record<string, string> = {
      VARCHAR: 'blue',
      INTEGER: 'green',
      BIGINT: 'green',
      TEXT: 'purple',
      TIMESTAMP: 'orange',
      BOOLEAN: 'cyan',
      NUMERIC: 'gold',
    };
    const upperType = type.toUpperCase();
    for (const key in colors) {
      if (upperType.includes(key)) {
        return colors[key];
      }
    }
    return 'default';
  };

  // 构建树形数据
  const buildTreeData = (): DataNode[] => {
    return filteredTables.map((table, index) => {
      const originalIndex = tables.findIndex(t => t.name === table.name);
      const isSelected = selectedTableNames.includes(table.name);
      
      return {
        title: (
          <div 
            style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: 8,
              padding: '4px 0'
            }}
            onClick={(e) => {
              // 阻止事件冒泡，避免触发树节点的选择
              if ((e.target as HTMLElement).tagName === 'INPUT') {
                e.stopPropagation();
              }
            }}
          >
            <Checkbox
              checked={isSelected}
              onChange={(e) => {
                e.stopPropagation();
                handleTableCheckChange(table.name, e.target.checked);
              }}
              onClick={(e) => e.stopPropagation()}
            />
            <TableOutlined style={{ color: isSelected ? '#52c41a' : '#999' }} />
            <span style={{ 
              flex: 1,
              color: isSelected ? '#333' : '#999',
              fontWeight: isSelected ? 500 : 400
            }}>
              {table.name}
            </span>
            <Badge 
              count={table.columns.length} 
              style={{ 
                backgroundColor: isSelected ? '#1890ff' : '#d9d9d9',
                fontSize: 11
              }} 
            />
          </div>
        ),
        key: `table-${originalIndex}`,
        icon: null,
        isLeaf: true,
      };
    });
  };

  const handleTableSelect = (selectedKeys: React.Key[]) => {
    if (selectedKeys.length > 0) {
      const key = selectedKeys[0] as string;
      const index = parseInt(key.replace('table-', ''));
      setSelectedTable(tables[index]);
      setFieldSearchText(''); // 切换表时清空搜索
    }
  };

  const handleTableCheckChange = (tableName: string, checked: boolean) => {
    if (checked) {
      setSelectedTableNames([...selectedTableNames, tableName]);
    } else {
      setSelectedTableNames(selectedTableNames.filter(name => name !== tableName));
    }
  };

  const handleSelectAllTables = (checked: boolean) => {
    if (checked) {
      setSelectedTableNames(tables.map(t => t.name));
    } else {
      setSelectedTableNames([]);
    }
  };

  const handleDisconnect = async () => {
    try {
      setSaving(true);
      await robotService.deleteDatabaseConfig(robotId);
      message.success('数据库连接已断开');
      
      // 重置所有状态
      setCurrentStep(0);
      setSelectedType(null);
      setTables([]);
      setSelectedTable(null);
      setSelectedTableNames([]);
      setTestSuccess(false);
      form.resetFields();
      
      if (onConfigSaved) {
        onConfigSaved();
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || '断开连接失败');
    } finally {
      setSaving(false);
    }
  };

  const handleSaveMetadata = async () => {
    try {
      setSaving(true);
      
      // 构建元数据
      const metadata: TableMetadata[] = tables
        .filter(table => selectedTableNames.includes(table.name))
        .map(table => ({
          name: table.name,
          description: tableDescriptions[table.name] || undefined,
          selected: true,
          columns: table.columns.map(col => ({
            name: col.name,
            description: columnDescriptions[table.name]?.[col.name] || undefined,
            selected: columnSelections[table.name]?.[col.name] ?? true,
          })),
        }));
      
      await robotService.saveDatabaseMetadata(robotId, { tables: metadata });
      message.success('数据库配置已保存');
      
      if (onConfigSaved) {
        onConfigSaved();
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || '保存失败');
    } finally {
      setSaving(false);
    }
  };

  const handleColumnSelectionChange = (tableName: string, columnName: string, selected: boolean) => {
    setColumnSelections(prev => ({
      ...prev,
      [tableName]: {
        ...(prev[tableName] || {}),
        [columnName]: selected,
      },
    }));
  };

  const handleSelectAllColumns = (tableName: string, selected: boolean) => {
    const table = tables.find(t => t.name === tableName);
    if (!table) return;
    
    const newSelections: Record<string, boolean> = {};
    table.columns.forEach(col => {
      newSelections[col.name] = selected;
    });
    
    setColumnSelections(prev => ({
      ...prev,
      [tableName]: newSelections,
    }));
  };

  // 过滤后的表列表（根据筛选条件）
  const filteredTables = showOnlySelected 
    ? tables.filter(table => selectedTableNames.includes(table.name))
    : tables;

  return (
    <div style={{ padding: '16px 0', height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Steps
        current={currentStep}
        size="small"
        style={{ marginBottom: 24, padding: '0 24px' }}
        items={[
          {
            title: '选择数据库类型',
            icon: currentStep > 0 ? <CheckCircleOutlined /> : <DatabaseOutlined />,
          },
          {
            title: '配置连接信息',
            icon: currentStep > 1 ? <CheckCircleOutlined /> : <DatabaseOutlined />,
          },
          {
            title: '查看数据库结构',
            icon: <TableOutlined />,
          },
        ]}
      />

      {/* Step 1: 选择数据库类型 */}
      {currentStep === 0 && (
        <div>
          <Title level={4} style={{ marginBottom: 24 }}>选择数据库类型</Title>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', 
            gap: 16 
          }}>
            {DATABASE_TYPES.map((db) => (
              <Card
                key={db.type}
                hoverable
                onClick={() => handleTypeSelect(db.type)}
                style={{
                  textAlign: 'center',
                  cursor: 'pointer',
                  borderColor: selectedType === db.type ? '#667eea' : undefined,
                  borderWidth: selectedType === db.type ? 2 : 1,
                }}
              >
                <div style={{ fontSize: 48, marginBottom: 8 }}>{db.icon}</div>
                <Title level={5} style={{ margin: 0 }}>{db.label}</Title>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Step 2: 配置连接信息 */}
      {currentStep === 1 && (
        <div>
          <Alert
            message="配置数据库连接"
            description={`配置 ${DATABASE_TYPES.find(db => db.type === selectedType)?.label} 数据库连接信息`}
            type="info"
            showIcon
            style={{ marginBottom: 24 }}
          />

          <Form
            form={form}
            layout="vertical"
            autoComplete="off"
          >
            <Form.Item
              label="主机地址"
              name="host"
              rules={[{ required: true, message: '请输入主机地址' }]}
            >
              <Input placeholder="例如: localhost 或 127.0.0.1" />
            </Form.Item>

            <Form.Item
              label="端口"
              name="port"
              rules={[{ required: true, message: '请输入端口' }]}
            >
              <Input type="number" placeholder="端口号" />
            </Form.Item>

            <Form.Item
              label="数据库名称"
              name="database_name"
              rules={[{ required: true, message: '请输入数据库名称' }]}
            >
              <Input placeholder="数据库名称" />
            </Form.Item>

            <Form.Item
              label="用户名"
              name="username"
              rules={[{ required: true, message: '请输入用户名' }]}
            >
              <Input placeholder="数据库用户名" />
            </Form.Item>

            <Form.Item
              label="密码"
              name="password"
              rules={[{ required: !existingConfig, message: '请输入密码' }]}
            >
              <Input.Password placeholder="数据库密码" />
            </Form.Item>

            <div style={{ display: 'flex', gap: 12 }}>
              <Button onClick={() => setCurrentStep(0)}>
                返回
              </Button>
              <Button 
                type="default" 
                onClick={handleTestConnection}
                loading={testing}
                icon={testing ? <LoadingOutlined /> : undefined}
              >
                测试连接
              </Button>
              <Button 
                type="primary" 
                onClick={handleSaveConfig}
                loading={saving}
                disabled={!testSuccess && !existingConfig}
                style={{
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  border: 'none'
                }}
              >
                保存配置
              </Button>
            </div>
          </Form>
        </div>
      )}

      {/* Step 3: 显示数据库结构 */}
      {currentStep === 2 && (
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          {loadingSchema ? (
            <div style={{ textAlign: 'center', padding: '60px 0' }}>
              <Spin size="large" tip="加载数据库结构..." />
            </div>
          ) : tables.length === 0 ? (
            <Alert
              message="暂无表数据"
              description="数据库中没有找到表，或者没有权限访问"
              type="warning"
              showIcon
            />
          ) : (
            <>
            <Row gutter={24} style={{ flex: 1, minHeight: 600 }}>
              {/* 左侧：数据库连接信息 */}
              <Col span={5}>
                <Card 
                  size="small"
                  style={{ 
                    marginBottom: 16,
                    borderRadius: 12,
                    boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
                  }}
                  styles={{ body: { padding: '16px' } }}
                >
                  <div style={{ textAlign: 'center', marginBottom: 16 }}>
                    <div style={{ 
                      width: 64,
                      height: 64,
                      margin: '0 auto',
                      borderRadius: '50%',
                      background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}>
                      <DatabaseOutlined style={{ fontSize: 32, color: '#667eea' }} />
                    </div>
                  </div>
                  
                  <div style={{ 
                    background: '#f5f7fa',
                    borderRadius: 8,
                    padding: 12,
                    marginBottom: 12
                  }}>
                    <div style={{ 
                      fontSize: 11, 
                      color: '#999',
                      marginBottom: 4 
                    }}>
                      数据库类型
                    </div>
                    <Tag color="blue" style={{ fontSize: 12 }}>
                      {DATABASE_TYPES.find(db => db.type === selectedType)?.label}
                    </Tag>
                  </div>

                  <div style={{ 
                    background: '#f5f7fa',
                    borderRadius: 8,
                    padding: 12,
                    marginBottom: 12
                  }}>
                    <div style={{ 
                      fontSize: 11, 
                      color: '#999',
                      marginBottom: 4 
                    }}>
                      主机
                    </div>
                    <Text style={{ fontSize: 12 }}>
                      {existingConfig?.host || form.getFieldValue('host')}
                    </Text>
                  </div>

                  <div style={{ 
                    background: '#f5f7fa',
                    borderRadius: 8,
                    padding: 12
                  }}>
                    <div style={{ 
                      fontSize: 11, 
                      color: '#999',
                      marginBottom: 4 
                    }}>
                      用户名
                    </div>
                    <Text style={{ fontSize: 12 }}>
                      {existingConfig?.username || form.getFieldValue('username')}
                    </Text>
                  </div>
                </Card>

                <Card 
                  title={
                    <span style={{ fontSize: 13, fontWeight: 600 }}>
                      <CheckCircleOutlined style={{ color: '#52c41a', marginRight: 8 }} />
                      表连接状态
                    </span>
                  }
                  size="small"
                  style={{ 
                    marginBottom: 16,
                    borderRadius: 12,
                    boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
                  }}
                  styles={{ body: { padding: 16 } }}
                >
                  <div style={{ marginBottom: 12 }}>
                    <Badge status="success" />
                    <Text style={{ fontSize: 13, marginLeft: 8 }}>
                      已选择 ({selectedTableNames.length}/{tables.length})
                    </Text>
                  </div>
                  <div>
                    <Badge status="default" />
                    <Text style={{ fontSize: 13, marginLeft: 8 }}>
                      未选择 ({tables.length - selectedTableNames.length})
                    </Text>
                  </div>
                </Card>

                <Button 
                  block
                  icon={<SettingOutlined />}
                  onClick={() => setCurrentStep(1)}
                  style={{ 
                    height: 40,
                    borderRadius: 8,
                    fontWeight: 500,
                    marginBottom: 8
                  }}
                >
                  重新配置
                </Button>

                <Popconfirm
                  title="断开数据库连接"
                  description="确定要断开数据库连接吗？这将删除所有配置信息。"
                  onConfirm={handleDisconnect}
                  okText="确定"
                  cancelText="取消"
                  okButtonProps={{ danger: true }}
                >
                  <Button 
                    block
                    danger
                    icon={<DisconnectOutlined />}
                    loading={saving}
                    style={{ 
                      height: 40,
                      borderRadius: 8,
                      fontWeight: 500
                    }}
                  >
                    断开连接
                  </Button>
                </Popconfirm>
              </Col>

              {/* 中间：表列表树 */}
              <Col span={7}>
                <Card 
                  title={
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <div style={{ fontSize: 14, fontWeight: 600 }}>
                        <TableOutlined style={{ marginRight: 8, color: '#667eea' }} />
                        数据库表 ({filteredTables.length}/{tables.length})
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                        <Checkbox
                          checked={selectedTableNames.length === tables.length}
                          indeterminate={selectedTableNames.length > 0 && selectedTableNames.length < tables.length}
                          onChange={(e) => handleSelectAllTables(e.target.checked)}
                          style={{ fontSize: 12 }}
                        >
                          全选
                        </Checkbox>
                        <div style={{ 
                          width: 1, 
                          height: 16, 
                          background: '#e8e8e8' 
                        }}></div>
                        <Text style={{ fontSize: 12, color: '#666' }}>仅已选</Text>
                        <Switch
                          size="small"
                          checked={showOnlySelected}
                          onChange={setShowOnlySelected}
                        />
                      </div>
                    </div>
                  }
                  size="small"
                  style={{ 
                    borderRadius: 12,
                    boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
                    height: '100%',
                    minHeight: 600
                  }}
                  styles={{ 
                    body: { 
                      padding: 0, 
                      height: 'calc(100% - 46px)',
                      overflow: 'auto' 
                    } 
                  }}
                >
                  <Tree
                    showLine
                    showIcon
                    defaultExpandAll={false}
                    expandedKeys={expandedKeys}
                    onExpand={setExpandedKeys}
                    selectedKeys={selectedTable ? [`table-${tables.indexOf(selectedTable)}`] : []}
                    onSelect={handleTableSelect}
                    treeData={buildTreeData()}
                    style={{ 
                      padding: '16px',
                      fontSize: 13
                    }}
                  />
                </Card>
              </Col>

              {/* 右侧：表详情 */}
              <Col span={12}>
                {selectedTable ? (
                  <Card
                    title={
                      <div style={{ fontSize: 14, fontWeight: 600 }}>
                        <TableOutlined style={{ marginRight: 8, color: '#667eea' }} />
                        {selectedTable.name}
                      </div>
                    }
                    extra={
                      <div style={{
                        background: '#f0f2f5',
                        padding: '4px 12px',
                        borderRadius: 16,
                        fontSize: 12,
                        color: '#666'
                      }}>
                        表字段
                      </div>
                    }
                    size="small"
                    style={{ 
                      borderRadius: 12,
                      boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
                      height: '100%',
                      minHeight: 600
                    }}
                    styles={{ 
                      body: { 
                        padding: 16,
                        height: 'calc(100% - 46px)',
                        overflow: 'hidden',
                        display: 'flex',
                        flexDirection: 'column'
                      } 
                    }}
                  >
                    {/* 搜索框 */}
                    <div style={{ marginBottom: 12 }}>
                      <Input
                        size="small"
                        placeholder="搜索字段名..."
                        prefix={<FilterOutlined style={{ color: '#999', fontSize: 12 }} />}
                        value={fieldSearchText}
                        onChange={(e) => setFieldSearchText(e.target.value)}
                        allowClear
                        style={{
                          borderRadius: 6,
                          border: '1px solid #d9d9d9'
                        }}
                      />
                    </div>

                    {/* 全选字段 */}
                    <div style={{ marginBottom: 12 }}>
                      <Checkbox
                        checked={selectedTable.columns.every(col => 
                          columnSelections[selectedTable.name]?.[col.name] ?? true
                        )}
                        indeterminate={
                          selectedTable.columns.some(col => 
                            columnSelections[selectedTable.name]?.[col.name] ?? true
                          ) && !selectedTable.columns.every(col => 
                            columnSelections[selectedTable.name]?.[col.name] ?? true
                          )
                        }
                        onChange={(e) => handleSelectAllColumns(selectedTable.name, e.target.checked)}
                      >
                        <Text strong style={{ fontSize: 13 }}>全选字段</Text>
                      </Checkbox>
                    </div>

                    {/* 表信息摘要 */}
                    <div style={{ 
                      padding: '12px 16px', 
                      background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%)',
                      border: '1px solid rgba(102, 126, 234, 0.15)',
                      borderRadius: 6,
                      marginBottom: 12,
                      fontSize: 12,
                      color: '#666'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
                        <CheckCircleOutlined style={{ color: '#52c41a', fontSize: 14 }} />
                        <span>
                          {fieldSearchText ? (
                            <>
                              找到 <strong style={{ color: '#667eea' }}>
                                {selectedTable.columns.filter(col => 
                                  col.name.toLowerCase().includes(fieldSearchText.toLowerCase())
                                ).length}
                              </strong> 个匹配字段
                            </>
                          ) : (
                            <>
                              已选择 <strong style={{ color: '#667eea' }}>
                                {selectedTable.columns.filter(col => 
                                  columnSelections[selectedTable.name]?.[col.name] ?? true
                                ).length}
                              </strong> / {selectedTable.columns.length} 个字段
                            </>
                          )}
                        </span>
                      </div>
                      <div style={{ marginTop: 8 }}>
                        <Input.TextArea
                          placeholder="添加表描述..."
                          value={tableDescriptions[selectedTable.name] || ''}
                          onChange={(e) => setTableDescriptions(prev => ({
                            ...prev,
                            [selectedTable.name]: e.target.value
                          }))}
                          autoSize={{ minRows: 2, maxRows: 3 }}
                          style={{ fontSize: 12 }}
                        />
                      </div>
                    </div>

                    {/* 字段列表 */}
                    <div style={{ flex: 1, overflow: 'auto' }}>
                      <List
                        size="small"
                        dataSource={selectedTable.columns.filter(column => 
                          column.name.toLowerCase().includes(fieldSearchText.toLowerCase())
                        )}
                        locale={{
                          emptyText: (
                            <div style={{ padding: '30px 0', textAlign: 'center', color: '#999' }}>
                              <FilterOutlined style={{ fontSize: 36, marginBottom: 12, color: '#e8e8e8' }} />
                              <div style={{ fontSize: 13 }}>没有找到匹配的字段</div>
                            </div>
                          )
                        }}
                        renderItem={(column) => {
                          const isSelected = columnSelections[selectedTable.name]?.[column.name] ?? true;
                          return (
                            <List.Item
                              style={{
                                padding: '12px 14px',
                                borderRadius: 8,
                                marginBottom: 8,
                                background: isSelected ? '#ffffff' : '#fafafa',
                                border: isSelected ? '1px solid #e0e7ff' : '1px solid #e8e8e8',
                                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                                opacity: isSelected ? 1 : 0.5,
                                boxShadow: isSelected ? '0 1px 3px rgba(102, 126, 234, 0.08)' : 'none'
                              }}
                              className="field-item"
                            >
                              <div style={{ width: '100%' }}>
                                <div style={{ 
                                  display: 'flex', 
                                  alignItems: 'center',
                                  gap: 10
                                }}>
                                  <Checkbox
                                    checked={isSelected}
                                    onChange={(e) => handleColumnSelectionChange(
                                      selectedTable.name, 
                                      column.name, 
                                      e.target.checked
                                    )}
                                  />
                                  <div style={{
                                    width: 22,
                                    height: 22,
                                    borderRadius: '6px',
                                    background: isSelected 
                                      ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' 
                                      : '#d0d0d0',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    transition: 'all 0.3s'
                                  }}>
                                    <FieldNumberOutlined 
                                      style={{ 
                                        color: '#fff',
                                        fontSize: 11 
                                      }} 
                                    />
                                  </div>
                                  <Text 
                                    strong 
                                    style={{ 
                                      fontSize: 14,
                                      color: isSelected ? '#1a1a1a' : '#999',
                                      fontWeight: 600,
                                      letterSpacing: '0.2px'
                                    }}
                                  >
                                    {column.name}
                                  </Text>
                                  <Tag 
                                    color={getTypeColor(column.type)}
                                    style={{ 
                                      fontSize: 11,
                                      fontFamily: 'Monaco, Consolas, monospace',
                                      padding: '2px 10px',
                                      fontWeight: 600,
                                      borderRadius: 4,
                                      border: 'none',
                                      textTransform: 'uppercase'
                                    }}
                                  >
                                    {column.type}
                                  </Tag>
                                  {!column.nullable && (
                                    <Tag 
                                      style={{ 
                                        fontSize: 10,
                                        lineHeight: '18px',
                                        padding: '0 8px',
                                        fontWeight: 600,
                                        background: '#fff1f0',
                                        color: '#cf1322',
                                        border: '1px solid #ffccc7',
                                        borderRadius: 4
                                      }}
                                    >
                                      NOT NULL
                                    </Tag>
                                  )}
                                </div>
                                {isSelected && (
                                  <div style={{ 
                                    paddingLeft: 42, 
                                    marginTop: 10,
                                    paddingRight: 4
                                  }}>
                                    <Input
                                      placeholder="添加字段描述（可选）..."
                                      value={columnDescriptions[selectedTable.name]?.[column.name] || ''}
                                      onChange={(e) => setColumnDescriptions(prev => ({
                                        ...prev,
                                        [selectedTable.name]: {
                                          ...(prev[selectedTable.name] || {}),
                                          [column.name]: e.target.value
                                        }
                                      }))}
                                      size="small"
                                      style={{ 
                                        fontSize: 12,
                                        borderRadius: 6,
                                        background: '#fafbfc',
                                        border: '1px solid #e8e8e8'
                                      }}
                                    />
                                  </div>
                                )}
                              </div>
                            </List.Item>
                          );
                        }}
                      />
                    </div>
                  </Card>
                ) : (
                  <Card 
                    size="small"
                    style={{ 
                      height: 600,
                      borderRadius: 12,
                      boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
                    }}
                  >
                    <div style={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      height: '100%',
                      color: '#999'
                    }}>
                      <div style={{ textAlign: 'center' }}>
                        <TableOutlined style={{ fontSize: 64, marginBottom: 16, color: '#e8e8e8' }} />
                        <div style={{ fontSize: 14 }}>请选择一个表查看详情</div>
                      </div>
                    </div>
                  </Card>
                )}
              </Col>
            </Row>

            {/* 底部留白，为浮动按钮留出空间 */}
            <div style={{ height: 60 }}></div>
            </>
          )}
        </div>
      )}


      {/* 浮动保存按钮 */}
      {currentStep === 2 && tables.length > 0 && (
        <div style={{
          position: 'fixed',
          bottom: 0,
          left: 0,
          right: 0,
          padding: '12px 0',
          background: 'linear-gradient(to top, #ffffff 0%, rgba(255,255,255,0.96) 100%)',
          backdropFilter: 'blur(20px)',
          borderTop: '1px solid #e8e8e8',
          boxShadow: '0 -4px 16px rgba(102, 126, 234, 0.08), 0 -1px 4px rgba(0,0,0,0.04)',
          zIndex: 1000,
          textAlign: 'center'
        }}>
          <Button
            type="primary"
            icon={<CheckCircleOutlined />}
            onClick={handleSaveMetadata}
            loading={saving}
            style={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              border: 'none',
              borderRadius: 6,
              height: 36,
              padding: '0 32px',
              fontSize: 14,
              fontWeight: 500,
              boxShadow: '0 2px 8px rgba(102, 126, 234, 0.3)'
            }}
          >
            保存配置
          </Button>
        </div>
      )}

      {/* 添加自定义样式 */}
      <style>{`
        .field-item {
          cursor: pointer;
        }
        .field-item:hover {
          background: #f8faff !important;
          border-color: #667eea !important;
          box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15), 0 2px 4px rgba(0, 0, 0, 0.05) !important;
          transform: translateY(-1px);
        }
        .field-item:active {
          transform: translateY(0);
        }
      `}</style>
    </div>
  );
};

export default DatabaseConfig;

