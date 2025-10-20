import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  Button,
  Space,
  Table,
  Modal,
  Form,
  Input,
  Select,
  Upload,
  message,
  Tag,
  Popconfirm,
  Row,
  Col,
  Statistic,
  InputNumber,
  Typography,
  Divider,
  Badge,
} from 'antd';
import {
  PlusOutlined,
  UploadOutlined,
  DeleteOutlined,
  ReloadOutlined,
  FileTextOutlined,
  DatabaseOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import type { UploadFile } from 'antd/es/upload/interface';
import {
  getKnowledgeBases,
  createKnowledgeBase,
  deleteKnowledgeBase,
  uploadDocument,
  getDocuments,
  deleteDocument,
  getEmbeddingProviders,
  getVectorStoreConfigs,
  type KnowledgeBase,
  type KnowledgeBaseCreate,
  type Document,
  type EmbeddingProvider,
  type EmbeddingModel,
  type VectorStoreConfig,
} from '../services/knowledgeBase';

const { Title, Text } = Typography;
const { TextArea } = Input;

const KnowledgeBaseManagement: React.FC = () => {
  const navigate = useNavigate();
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedKB, setSelectedKB] = useState<KnowledgeBase | null>(null);
  const [loading, setLoading] = useState(false);

  // 对话框状态
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [uploadModalVisible, setUploadModalVisible] = useState(false);
  const [documentsModalVisible, setDocumentsModalVisible] = useState(false);

  // 表单
  const [createForm] = Form.useForm();
  const [fileList, setFileList] = useState<UploadFile[]>([]);

  // 嵌入模型和向量存储配置
  const [embeddingProviders, setEmbeddingProviders] = useState<EmbeddingProvider[]>([]);
  const [vectorStoreConfigs, setVectorStoreConfigs] = useState<VectorStoreConfig[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<string>('openai');
  const [selectedVectorType, setSelectedVectorType] = useState<string>('pgvector');

  // 加载知识库列表
  const loadKnowledgeBases = async () => {
    try {
      setLoading(true);
      const data = await getKnowledgeBases();
      console.log('✅ 知识库数据:', data);
      setKnowledgeBases(data);
      if (data.length === 0) {
        message.info('暂无知识库，请点击"创建知识库"按钮开始创建');
      }
    } catch (error: any) {
      console.error('❌ 加载知识库失败:', error);
      message.error(error.response?.data?.detail || '加载知识库失败');
    } finally {
      setLoading(false);
    }
  };

  // 加载嵌入模型提供商
  const loadEmbeddingProviders = async () => {
    try {
      const data = await getEmbeddingProviders();
      setEmbeddingProviders(data.providers);
    } catch (error: any) {
      console.error('加载嵌入模型提供商失败:', error);
    }
  };

  // 加载向量存储配置
  const loadVectorStoreConfigs = async () => {
    try {
      const data = await getVectorStoreConfigs();
      setVectorStoreConfigs(data.vector_stores);
    } catch (error: any) {
      console.error('加载向量存储配置失败:', error);
    }
  };

  // 加载文档列表
  const loadDocuments = async (kbId: number) => {
    try {
      const data = await getDocuments(kbId);
      setDocuments(data);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '加载文档失败');
    }
  };

  useEffect(() => {
    loadKnowledgeBases();
    loadEmbeddingProviders();
    loadVectorStoreConfigs();
  }, []);

  // 创建知识库
  const handleCreate = async (values: KnowledgeBaseCreate) => {
    try {
      setLoading(true);
      await createKnowledgeBase(values);
      message.success('知识库创建成功');
      setCreateModalVisible(false);
      createForm.resetFields();
      await loadKnowledgeBases();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '创建知识库失败');
    } finally {
      setLoading(false);
    }
  };

  // 删除知识库
  const handleDelete = async (id: number) => {
    try {
      setLoading(true);
      await deleteKnowledgeBase(id);
      message.success('知识库删除成功');
      await loadKnowledgeBases();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '删除知识库失败');
    } finally {
      setLoading(false);
    }
  };

  // 上传文档
  const handleUpload = async () => {
    if (!selectedKB || fileList.length === 0) {
      return;
    }

    const file = fileList[0].originFileObj as File;

    try {
      setLoading(true);
      await uploadDocument(selectedKB.id, file);
      message.success('文档上传成功，正在处理...');
      setUploadModalVisible(false);
      setFileList([]);
      await loadDocuments(selectedKB.id);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '上传文档失败');
    } finally {
      setLoading(false);
    }
  };

  // 删除文档
  const handleDeleteDocument = async (docId: number) => {
    try {
      setLoading(true);
      await deleteDocument(docId);
      message.success('文档删除成功');
      if (selectedKB) {
        await loadDocuments(selectedKB.id);
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || '删除文档失败');
    } finally {
      setLoading(false);
    }
  };

  // 打开文档管理对话框
  const openDocumentsModal = async (kb: KnowledgeBase) => {
    setSelectedKB(kb);
    await loadDocuments(kb.id);
    setDocumentsModalVisible(true);
  };

  // 获取状态颜色
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'processing':
        return 'processing';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  // 获取状态文本
  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return '已完成';
      case 'processing':
        return '处理中';
      case 'failed':
        return '失败';
      default:
        return '待处理';
    }
  };

  // 格式化文件大小
  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  // 文档表格列
  const documentColumns: ColumnsType<Document> = [
    {
      title: '文件名',
      dataIndex: 'filename',
      key: 'filename',
      ellipsis: true,
    },
    {
      title: '类型',
      dataIndex: 'file_type',
      key: 'file_type',
      width: 80,
    },
    {
      title: '大小',
      dataIndex: 'file_size',
      key: 'file_size',
      width: 100,
      render: (size: number) => formatFileSize(size),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>{getStatusText(status)}</Tag>
      ),
    },
    {
      title: '块数',
      dataIndex: 'chunk_count',
      key: 'chunk_count',
      width: 80,
    },
    {
      title: '上传时间',
      dataIndex: 'uploaded_at',
      key: 'uploaded_at',
      width: 180,
      render: (date: string) => new Date(date).toLocaleString('zh-CN'),
    },
    {
      title: '操作',
      key: 'action',
      width: 80,
      render: (_, record) => (
        <Popconfirm
          title="确定删除这个文档吗？"
          onConfirm={() => handleDeleteDocument(record.id)}
          okText="确定"
          cancelText="取消"
        >
          <Button type="link" danger icon={<DeleteOutlined />} size="small">
            删除
          </Button>
        </Popconfirm>
      ),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Title level={2}>知识库管理</Title>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={loadKnowledgeBases} loading={loading}>
            刷新
          </Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setCreateModalVisible(true)}>
            创建知识库
          </Button>
        </Space>
      </div>

      {knowledgeBases.length === 0 && !loading ? (
        <Card style={{ textAlign: 'center', padding: '40px 20px' }}>
          <div style={{ fontSize: 48, color: '#bfbfbf', marginBottom: 16 }}>
            <DatabaseOutlined />
          </div>
          <Title level={4} style={{ color: '#8c8c8c' }}>暂无知识库</Title>
          <Text type="secondary">点击右上角"创建知识库"按钮开始创建</Text>
        </Card>
      ) : (
        <Row gutter={[16, 16]}>
          {knowledgeBases.map((kb) => (
            <Col xs={24} sm={12} lg={8} key={kb.id}>
              <Card
              hoverable
              onClick={() => navigate(`/system/knowledge-bases/${kb.id}`)}
              title={
                <Space>
                  <DatabaseOutlined />
                  {kb.name}
                </Space>
              }
              extra={
                <Popconfirm
                  title="确定删除这个知识库吗？所有文档和数据将被永久删除。"
                  onConfirm={(e) => {
                    e?.stopPropagation();
                    handleDelete(kb.id);
                  }}
                  okText="确定"
                  cancelText="取消"
                >
                  <Button 
                    type="text" 
                    danger 
                    icon={<DeleteOutlined />} 
                    size="small"
                    onClick={(e) => e.stopPropagation()}
                  />
                </Popconfirm>
              }
              actions={[
                <Button
                  key="view"
                  type="link"
                  icon={<FileTextOutlined />}
                  onClick={(e) => {
                    e.stopPropagation();
                    openDocumentsModal(kb);
                  }}
                >
                  查看文档
                </Button>,
                <Button
                  key="upload"
                  type="link"
                  icon={<UploadOutlined />}
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedKB(kb);
                    setUploadModalVisible(true);
                  }}
                >
                  上传文档
                </Button>,
              ]}
            >
              <Text type="secondary">{kb.description || '无描述'}</Text>
              <Divider style={{ margin: '12px 0' }} />
              <Space direction="vertical" style={{ width: '100%' }}>
                <Space wrap>
                  <Tag color="blue">{kb.vector_store_type}</Tag>
                  <Tag color="purple">{kb.embedding_model}</Tag>
                  {kb.is_public && <Tag color="green">公开</Tag>}
                </Space>
                <Row gutter={16}>
                  <Col span={12}>
                    <Statistic title="文档数" value={kb.document_count} prefix={<FileTextOutlined />} />
                  </Col>
                  <Col span={12}>
                    <Statistic title="块数" value={kb.total_chunks} />
                  </Col>
                </Row>
              </Space>
            </Card>
          </Col>
        ))}
      </Row>
      )}

      {/* 创建知识库对话框 */}
      <Modal
        title="创建知识库"
        open={createModalVisible}
        onCancel={() => {
          setCreateModalVisible(false);
          createForm.resetFields();
          setSelectedProvider('openai');
          setSelectedVectorType('pgvector');
        }}
        onOk={() => createForm.submit()}
        confirmLoading={loading}
        width={600}
      >
        <Form
          form={createForm}
          layout="vertical"
          onFinish={handleCreate}
          initialValues={{
            vector_store_type: 'pgvector',
            embedding_provider: 'openai',
            embedding_model: 'text-embedding-3-small',
            chunk_size: 500,
            chunk_overlap: 50,
            is_public: false,
          }}
        >
          <Form.Item
            label="名称"
            name="name"
            rules={[{ required: true, message: '请输入知识库名称' }]}
          >
            <Input placeholder="请输入知识库名称" />
          </Form.Item>

          <Form.Item label="描述" name="description">
            <TextArea rows={3} placeholder="请输入描述（可选）" />
          </Form.Item>

          <Form.Item label="向量存储" name="vector_store_type">
            <Select onChange={(value) => {
              setSelectedVectorType(value);
              if (value === 'pgvector') {
                createForm.setFieldValue('vector_store_config_id', null);
              }
            }}>
              <Select.Option value="pgvector">PostgreSQL + pgvector</Select.Option>
              <Select.Option value="elasticsearch">Elasticsearch</Select.Option>
            </Select>
          </Form.Item>

          {selectedVectorType === 'pgvector' ? (
            <div style={{ marginBottom: 16 }}>
              <Text type="secondary">✓ 使用系统库</Text>
            </div>
          ) : (
            <Form.Item 
              label="选择外部 ES 配置" 
              name="vector_store_config_id"
              rules={[{ required: true, message: '请选择外部 ES 配置' }]}
            >
              <Select placeholder="选择已配置的 ES 连接">
                {vectorStoreConfigs.map(config => (
                  <Select.Option key={config.id} value={config.id}>
                    {config.name} ({config.url})
                  </Select.Option>
                ))}
              </Select>
            </Form.Item>
          )}

          <Form.Item label="嵌入模型厂商" name="embedding_provider">
            <Select onChange={(value) => {
              setSelectedProvider(value);
              // 清空模型选择
              createForm.setFieldValue('embedding_model', undefined);
            }}>
              {embeddingProviders.map(provider => (
                <Select.Option key={provider.id} value={provider.id}>
                  {provider.name}
                </Select.Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item 
            label="嵌入模型" 
            name="embedding_model"
            rules={[{ required: true, message: '请选择嵌入模型' }]}
          >
            <Select placeholder="选择嵌入模型">
              {embeddingProviders
                .find(p => p.id === selectedProvider)
                ?.models.map(model => (
                  <Select.Option key={model.id} value={model.id}>
                    <div>
                      <div>{model.name}</div>
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        {model.description} (维度: {model.dimensions})
                      </Text>
                    </div>
                  </Select.Option>
                ))}
            </Select>
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item label="块大小" name="chunk_size">
                <InputNumber min={100} max={2000} addonAfter="字符" style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item label="块重叠" name="chunk_overlap">
                <InputNumber min={0} max={500} addonAfter="字符" style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>

      {/* 上传文档对话框 */}
      <Modal
        title="上传文档"
        open={uploadModalVisible}
        onCancel={() => {
          setUploadModalVisible(false);
          setFileList([]);
        }}
        onOk={handleUpload}
        confirmLoading={loading}
        okButtonProps={{ disabled: fileList.length === 0 }}
      >
        <Upload
          beforeUpload={(file) => {
            const isValidType = ['.txt', '.pdf', '.docx'].some((ext) =>
              file.name.toLowerCase().endsWith(ext)
            );
            if (!isValidType) {
              message.error('只支持 TXT, PDF, DOCX 格式！');
              return false;
            }
            const isLt50M = file.size / 1024 / 1024 < 50;
            if (!isLt50M) {
              message.error('文件大小不能超过 50MB！');
              return false;
            }
            setFileList([file as any]);
            return false;
          }}
          fileList={fileList}
          onRemove={() => setFileList([])}
          maxCount={1}
        >
          <Button icon={<UploadOutlined />}>选择文件</Button>
        </Upload>
        <div style={{ marginTop: 16 }}>
          <Text type="secondary">支持的格式：TXT, PDF, DOCX (最大 50MB)</Text>
        </div>
      </Modal>

      {/* 文档列表对话框 */}
      <Modal
        title={`文档列表 - ${selectedKB?.name}`}
        open={documentsModalVisible}
        onCancel={() => setDocumentsModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDocumentsModalVisible(false)}>
            关闭
          </Button>,
        ]}
        width={1000}
      >
        <Table
          columns={documentColumns}
          dataSource={documents}
          rowKey="id"
          pagination={{ pageSize: 10 }}
          locale={{ emptyText: '暂无文档' }}
        />
      </Modal>
    </div>
  );
};

export default KnowledgeBaseManagement;
