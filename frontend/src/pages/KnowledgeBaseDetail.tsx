import React, { useState, useEffect } from 'react';
import {
  Card,
  Button,
  Space,
  Table,
  Modal,
  Form,
  Upload,
  message,
  Tag,
  Popconfirm,
  Descriptions,
  Statistic,
  Row,
  Col,
  Typography,
  Input,
  Layout,
  Menu,
  Slider,
  Radio,
  Select,
  Divider,
  Alert,
  List,
} from 'antd';
import {
  ArrowLeftOutlined,
  UploadOutlined,
  DeleteOutlined,
  ReloadOutlined,
  FileTextOutlined,
  SettingOutlined,
  SearchOutlined,
  SaveOutlined,
} from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import type { ColumnsType } from 'antd/es/table';
import type { UploadFile } from 'antd/es/upload/interface';
import {
  getKnowledgeBase,
  updateKnowledgeBase,
  uploadDocument,
  getDocuments,
  deleteDocument,
  searchKnowledgeBases,
  getDocumentChunks,
  type KnowledgeBase,
  type Document,
  type SearchResult,
  type Chunk,
} from '../services/knowledgeBase';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;
const { Sider, Content } = Layout;
const { Option } = Select;

const KnowledgeBaseDetail: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const [knowledgeBase, setKnowledgeBase] = useState<KnowledgeBase | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [filteredDocuments, setFilteredDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploadModalVisible, setUploadModalVisible] = useState(false);
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [settingsForm] = Form.useForm();
  
  // 左侧导航选中状态
  const [selectedMenu, setSelectedMenu] = useState('documents');
  
  // 文档搜索和筛选
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  
  // 分块查看
  const [chunksModalVisible, setChunksModalVisible] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [chunks, setChunks] = useState<Chunk[]>([]);
  const [chunksLoading, setChunksLoading] = useState(false);
  
  // 召回测试状态
  const [testQuery, setTestQuery] = useState('');
  const [testResults, setTestResults] = useState<SearchResult[]>([]);
  const [testLoading, setTestLoading] = useState(false);
  const [retrievalStrategy, setRetrievalStrategy] = useState<'semantic' | 'fulltext' | 'hybrid'>('hybrid');
  const [topK, setTopK] = useState(3);
  const [scoreThreshold, setScoreThreshold] = useState(0.5);
  const [semanticWeight, setSemanticWeight] = useState(0.7);
  const [enableRerank, setEnableRerank] = useState(false);

  // 加载知识库详情
  const loadKnowledgeBase = async () => {
    if (!id) return;
    
    try {
      setLoading(true);
      const data = await getKnowledgeBase(parseInt(id));
      setKnowledgeBase(data);
      settingsForm.setFieldsValue({
        name: data.name,
        description: data.description,
        chunk_size: data.chunk_size,
        chunk_overlap: data.chunk_overlap,
        is_public: data.is_public,
      });
    } catch (error: any) {
      message.error(error.response?.data?.detail || '加载知识库失败');
    } finally {
      setLoading(false);
    }
  };

  // 加载文档列表
  const loadDocuments = async () => {
    if (!id) return;
    
    try {
      const data = await getDocuments(parseInt(id));
      setDocuments(data);
      setFilteredDocuments(data);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '加载文档失败');
    }
  };

  // 加载文档分块
  const loadDocumentChunks = async (docId: number) => {
    try {
      setChunksLoading(true);
      const data = await getDocumentChunks(docId);
      setChunks(data.chunks);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '加载分块失败');
    } finally {
      setChunksLoading(false);
    }
  };

  // 打开分块查看弹窗
  const openChunksModal = async (doc: Document) => {
    setSelectedDocument(doc);
    setChunksModalVisible(true);
    await loadDocumentChunks(doc.id);
  };

  // 搜索和筛选文档
  useEffect(() => {
    let filtered = documents;
    
    // 按状态筛选
    if (statusFilter !== 'all') {
      filtered = filtered.filter(doc => doc.status === statusFilter);
    }
    
    // 按文件名搜索
    if (searchText) {
      filtered = filtered.filter(doc => 
        doc.filename.toLowerCase().includes(searchText.toLowerCase())
      );
    }
    
    setFilteredDocuments(filtered);
  }, [documents, searchText, statusFilter]);

  useEffect(() => {
    loadKnowledgeBase();
    loadDocuments();
  }, [id]);

  // 更新知识库设置
  const handleUpdateSettings = async (values: any) => {
    if (!id) return;

    try {
      setLoading(true);
      await updateKnowledgeBase(parseInt(id), values);
      message.success('设置已保存');
      await loadKnowledgeBase();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '保存失败');
    } finally {
      setLoading(false);
    }
  };

  // 上传文档
  const handleUpload = async () => {
    if (!id || fileList.length === 0) return;

    const file = fileList[0].originFileObj as File;

    try {
      setLoading(true);
      await uploadDocument(parseInt(id), file);
      message.success('文档上传成功，正在处理...');
      setUploadModalVisible(false);
      setFileList([]);
      await loadDocuments();
      await loadKnowledgeBase();
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
      await loadDocuments();
      await loadKnowledgeBase();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '删除文档失败');
    } finally {
      setLoading(false);
    }
  };

  // 召回测试
  const handleRecallTest = async () => {
    if (!id || !testQuery.trim()) {
      message.warning('请输入测试查询');
      return;
    }

    try {
      setTestLoading(true);
      const response = await searchKnowledgeBases(
        testQuery,
        topK,
        [parseInt(id)]
      );
      setTestResults(response.results);
      message.success(`找到 ${response.total} 个相关结果`);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '召回测试失败');
    } finally {
      setTestLoading(false);
    }
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
      render: (filename: string, record) => (
        <Button
          type="link"
          onClick={() => openChunksModal(record)}
          style={{ padding: 0, height: 'auto' }}
        >
          <FileTextOutlined style={{ marginRight: 4 }} />
          {filename}
        </Button>
      ),
    },
    {
      title: '分段模式',
      key: 'chunk_mode',
      width: 100,
      render: () => <Tag>总是</Tag>,
    },
    {
      title: '字符数',
      dataIndex: 'character_count',
      key: 'character_count',
      width: 100,
      render: (count: number) => {
        if (!count) return '0';
        if (count >= 1000) {
          return (count / 1000).toFixed(1) + 'k';
        }
        return count.toLocaleString();
      },
    },
    {
      title: '召回次数',
      key: 'retrieval_count',
      width: 100,
      render: () => '0',
    },
    {
      title: '上传时间',
      dataIndex: 'uploaded_at',
      key: 'uploaded_at',
      width: 180,
      render: (date: string) => new Date(date).toLocaleString('zh-CN'),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Tag color={getStatusColor(status)} icon={status === 'completed' ? '✓' : undefined}>
          {getStatusText(status)}
        </Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      fixed: 'right' as const,
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            size="small"
            onClick={() => openChunksModal(record)}
          >
            查看分块
          </Button>
          <Popconfirm
            title="确定删除这个文档吗？"
            onConfirm={() => handleDeleteDocument(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" danger size="small">
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // 渲染文档页面
  const renderDocumentsPage = () => (
    <div>
      <Alert
        message="文档"
        description="知识库的所有文件都在这里显示，从而允许你进行Chat操作或引用特定文档进行索引。"
        type="info"
        showIcon
        closable
        style={{ marginBottom: 16 }}
      />
      
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Space>
          <Select
            value={statusFilter}
            onChange={setStatusFilter}
            style={{ width: 120 }}
          >
            <Option value="all">All Status</Option>
            <Option value="completed">已完成</Option>
            <Option value="processing">处理中</Option>
            <Option value="failed">失败</Option>
            <Option value="pending">待处理</Option>
          </Select>
          <Input.Search
            placeholder="搜索文件名..."
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            style={{ width: 300 }}
            allowClear
          />
        </Space>
        <Button type="primary" icon={<UploadOutlined />} onClick={() => setUploadModalVisible(true)}>
          添加文档
        </Button>
      </div>
      
      <Table
        columns={documentColumns}
        dataSource={filteredDocuments}
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 10, showTotal: (total) => `共 ${total} 个文档` }}
        locale={{ emptyText: '暂无文档，点击"添加文档"按钮开始上传' }}
        scroll={{ x: 1200 }}
      />
    </div>
  );

  // 渲染召回测试页面
  const renderRecallTestPage = () => (
    <div>
      <Card title="查询模式" style={{ marginBottom: 16 }}>
        <Alert
          message="高质量"
          description="请用接近真实使用场景中的问答内容类型，用于测试和优化文档的召回效果。这可以帮助你更直观地了解用户问答的效果，从而优化分块策略和索引方式，提高召回率。"
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />
        
        <Radio.Group 
          value={retrievalStrategy} 
          onChange={(e) => setRetrievalStrategy(e.target.value)}
          style={{ marginBottom: 16 }}
        >
          <Space direction="vertical">
            <Radio value="semantic">
              <Space>
                <FileTextOutlined />
                <div>
                  <div><strong>问题检索</strong></div>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    通过生成查询向量对语义匹配的文本块进行检索
                  </Text>
                </div>
              </Space>
            </Radio>
            <Radio value="fulltext">
              <Space>
                <SearchOutlined />
                <div>
                  <div><strong>全文检索</strong></div>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    索引文档的所有词汇，从而允许用户通过任意词汇搜索文档
                  </Text>
                </div>
              </Space>
            </Radio>
            <Radio value="hybrid">
              <Space>
                <FileTextOutlined />
                <div>
                  <div><strong>混合检索 <Tag>推荐</Tag></strong></div>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    同时执行全文检索和向量检索，并应用重排序策略，从两类查询结果中选择匹配用户问题的最佳结果。
                    可以设置 BM25 和语义向量各自比例的权重。
                  </Text>
                </div>
              </Space>
            </Radio>
          </Space>
        </Radio.Group>

        {retrievalStrategy === 'hybrid' && (
          <Card type="inner" title="混合检索设置" style={{ marginTop: 16 }}>
            <Row gutter={16}>
              <Col span={12}>
                <Card size="small" title="权重设置">
                  <div style={{ marginBottom: 16 }}>
                    <Text>语义权重：{semanticWeight.toFixed(1)}</Text>
                    <Slider
                      min={0}
                      max={1}
                      step={0.1}
                      value={semanticWeight}
                      onChange={setSemanticWeight}
                      marks={{
                        0: '0',
                        0.7: '0.7',
                        1: '1.0'
                      }}
                    />
                  </div>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    语义分配比重配置，语义值越高影响越高，反之词本身的匹配比重越高，适合预期文本匹配度高的场景。
                  </Text>
                </Card>
              </Col>
              <Col span={12}>
                <Card size="small" title="Rerank 模型">
                  <Radio.Group value={enableRerank} onChange={(e) => setEnableRerank(e.target.value)}>
                    <Space direction="vertical">
                      <Radio value={false}>
                        <Text>关闭</Text>
                      </Radio>
                      <Radio value={true}>
                        <div>
                          <div><Text>启用 Rerank</Text></div>
                          <Text type="secondary" style={{ fontSize: 12 }}>
                            基于模型对检索结果中的语义排序进行重新排序，提高语义排序的准确度。
                            从而提升中检索效果的准确性。
                          </Text>
                        </div>
                      </Radio>
                    </Space>
                  </Radio.Group>
                </Card>
              </Col>
            </Row>
          </Card>
        )}
      </Card>

      <Card title="检索设置" style={{ marginBottom: 16 }}>
        <Row gutter={24}>
          <Col span={12}>
            <div>
              <div style={{ marginBottom: 8 }}>
                <Text>Top K</Text>
                <Text type="secondary" style={{ marginLeft: 8, fontSize: 12 }}>
                  用于筛选与用户问题相似度最高的文本块
                </Text>
              </div>
              <Slider
                min={1}
                max={10}
                value={topK}
                onChange={setTopK}
                marks={{ 1: '1', 3: '3', 10: '10' }}
              />
              <div style={{ textAlign: 'center', marginTop: 8 }}>
                <Text strong>{topK}</Text>
              </div>
            </div>
          </Col>
          <Col span={12}>
            <div>
              <div style={{ marginBottom: 8 }}>
                <Text>Score 阈值</Text>
                <Text type="secondary" style={{ marginLeft: 8, fontSize: 12 }}>
                  设置文本块筛选的相似度阈值
                </Text>
              </div>
              <Slider
                min={0}
                max={1}
                step={0.1}
                value={scoreThreshold}
                onChange={setScoreThreshold}
                marks={{ 0: '0', 0.5: '0.5', 1: '1.0' }}
              />
              <div style={{ textAlign: 'center', marginTop: 8 }}>
                <Text strong>{scoreThreshold.toFixed(1)}</Text>
              </div>
            </div>
          </Col>
        </Row>
      </Card>

      <Card title="测试查询">
        <TextArea
          rows={4}
          placeholder="输入你的测试查询..."
          value={testQuery}
          onChange={(e) => setTestQuery(e.target.value)}
          style={{ marginBottom: 16 }}
        />
        <Button
          type="primary"
          icon={<SearchOutlined />}
          onClick={handleRecallTest}
          loading={testLoading}
          block
        >
          测试召回
        </Button>
      </Card>

      {testResults.length > 0 && (
        <Card title={`召回结果 (${testResults.length})`} style={{ marginTop: 16 }}>
          <List
            dataSource={testResults}
            renderItem={(item, index) => (
              <List.Item>
                <Card size="small" style={{ width: '100%' }}>
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <Space>
                      <Tag color="blue">#{index + 1}</Tag>
                      <Text strong>相似度: {(item.score * 100).toFixed(2)}%</Text>
                      <Tag>{item.document_name}</Tag>
                      <Text type="secondary">块 #{item.chunk_index}</Text>
                    </Space>
                    <Paragraph
                      ellipsis={{ rows: 3, expandable: true, symbol: '展开' }}
                      style={{ marginBottom: 0 }}
                    >
                      {item.content}
                    </Paragraph>
                  </Space>
                </Card>
              </List.Item>
            )}
          />
        </Card>
      )}
    </div>
  );

  // 渲染设置页面
  const renderSettingsPage = () => {
    const hasDocuments = (knowledgeBase?.document_count || 0) > 0;

    return (
      <Card title="知识库设置">
        {hasDocuments && (
          <Alert
            message="配置已锁定"
            description="由于已上传文档并进行向量化，向量存储类型和嵌入模型配置不可修改，以确保数据一致性。如需更改这些配置，请先删除所有文档。"
            type="warning"
            showIcon
            closable
            style={{ marginBottom: 16 }}
          />
        )}

        <Form
          form={settingsForm}
          layout="vertical"
          onFinish={handleUpdateSettings}
        >
          <Form.Item 
            label="知识库名称" 
            name="name" 
            rules={[{ required: true, message: '请输入知识库名称' }]}
          >
            <Input />
          </Form.Item>
          
          <Form.Item label="描述" name="description">
            <TextArea rows={4} placeholder="输入知识库描述..." />
          </Form.Item>

          <Divider>向量配置</Divider>

          <Form.Item label="向量存储类型">
            <Select 
              value={knowledgeBase?.vector_store_type} 
              disabled={hasDocuments}
            >
              <Option value="pgvector">PostgreSQL + pgvector</Option>
              <Option value="elasticsearch">Elasticsearch</Option>
            </Select>
            {hasDocuments && (
              <Text type="secondary" style={{ fontSize: 12, display: 'block', marginTop: 4 }}>
                已有文档，不可修改
              </Text>
            )}
          </Form.Item>

          {knowledgeBase?.vector_store_type === 'pgvector' ? (
            <div style={{ marginBottom: 16 }}>
              <Text type="secondary">✓ 使用系统库</Text>
            </div>
          ) : knowledgeBase?.vector_store_config_id ? (
            <Form.Item label="外部 ES 配置">
              <Input 
                value={`ES 配置 ID: ${knowledgeBase.vector_store_config_id}`}
                disabled
              />
            </Form.Item>
          ) : null}

          <Form.Item label="嵌入模型厂商">
            <Select 
              value={knowledgeBase?.embedding_provider} 
              disabled={hasDocuments}
            >
              <Option value="openai">OpenAI</Option>
              <Option value="claude">Claude (Anthropic)</Option>
              <Option value="ollama">Ollama (本地模型)</Option>
            </Select>
            {hasDocuments && (
              <Text type="secondary" style={{ fontSize: 12, display: 'block', marginTop: 4 }}>
                已有文档，不可修改
              </Text>
            )}
          </Form.Item>

          <Form.Item label="嵌入模型">
            <Input 
              value={knowledgeBase?.embedding_model} 
              disabled={hasDocuments}
            />
            {hasDocuments && (
              <Text type="secondary" style={{ fontSize: 12, display: 'block', marginTop: 4 }}>
                已有文档，不可修改
              </Text>
            )}
          </Form.Item>

          <Divider>分块配置</Divider>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item 
                label="分块大小" 
                name="chunk_size"
                tooltip="文档分块时每个块的字符数"
              >
                <Input type="number" addonAfter="字符" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item 
                label="分块重叠" 
                name="chunk_overlap"
                tooltip="相邻块之间重叠的字符数，有助于保持上下文连贯性"
              >
                <Input type="number" addonAfter="字符" />
              </Form.Item>
            </Col>
          </Row>

          <Divider>其他信息</Divider>

          <Descriptions bordered column={2} size="small">
            <Descriptions.Item label="文档数量">
              {knowledgeBase?.document_count || 0}
            </Descriptions.Item>
            <Descriptions.Item label="分块数量">
              {knowledgeBase?.total_chunks || 0}
            </Descriptions.Item>
            <Descriptions.Item label="创建时间" span={2}>
              {knowledgeBase?.created_at && new Date(knowledgeBase.created_at).toLocaleString('zh-CN')}
            </Descriptions.Item>
            <Descriptions.Item label="最后更新" span={2}>
              {knowledgeBase?.updated_at && new Date(knowledgeBase.updated_at).toLocaleString('zh-CN')}
            </Descriptions.Item>
          </Descriptions>

          <Divider />

          <Form.Item>
            <Button type="primary" htmlType="submit" icon={<SaveOutlined />} loading={loading}>
              保存设置
            </Button>
          </Form.Item>
        </Form>
      </Card>
    );
  };

  if (!knowledgeBase) {
    return (
      <div style={{ padding: 24, textAlign: 'center' }}>
        <Title level={4}>加载中...</Title>
      </div>
    );
  }

  return (
    <div style={{ height: '100%' }}>
      {/* 顶部导航栏 */}
      <div style={{ 
        padding: '16px 24px', 
        background: '#fff', 
        borderBottom: '1px solid #f0f0f0',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <Space>
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate('/system/knowledge-bases')}
          >
            返回
          </Button>
          <Title level={4} style={{ margin: 0 }}>{knowledgeBase.name}</Title>
        </Space>
        <Button icon={<ReloadOutlined />} onClick={() => {
          loadKnowledgeBase();
          if (selectedMenu === 'documents') loadDocuments();
        }}>
          刷新
        </Button>
      </div>

      {/* 主内容区 - 左侧导航 + 右侧内容 */}
      <Layout style={{ background: '#fff', height: 'calc(100vh - 128px)' }}>
        <Sider width={200} style={{ background: '#fafafa' }}>
          <Menu
            mode="inline"
            selectedKeys={[selectedMenu]}
            onClick={({ key }) => setSelectedMenu(key)}
            style={{ height: '100%', borderRight: 0 }}
          >
            <Menu.Item key="documents" icon={<FileTextOutlined />}>
              文档
            </Menu.Item>
            <Menu.Item key="recall" icon={<SearchOutlined />}>
              召回测试
            </Menu.Item>
            <Menu.Item key="settings" icon={<SettingOutlined />}>
              设置
            </Menu.Item>
          </Menu>
        </Sider>
        <Content style={{ padding: 24, overflow: 'auto' }}>
          {selectedMenu === 'documents' && renderDocumentsPage()}
          {selectedMenu === 'recall' && renderRecallTestPage()}
          {selectedMenu === 'settings' && renderSettingsPage()}
        </Content>
      </Layout>

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
            const isValidType = ['.txt', '.pdf', '.docx', '.json'].some((ext) =>
              file.name.toLowerCase().endsWith(ext)
            );
            if (!isValidType) {
              message.error('只支持 TXT, PDF, DOCX, JSON 格式！');
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
          <Text type="secondary">支持的格式：TXT, PDF, DOCX, JSON (最大 50MB)</Text>
        </div>
      </Modal>

      {/* 分块查看对话框 */}
      <Modal
        title={
          <Space>
            <FileTextOutlined />
            <span>文档分块 - {selectedDocument?.filename}</span>
          </Space>
        }
        open={chunksModalVisible}
        onCancel={() => {
          setChunksModalVisible(false);
          setSelectedDocument(null);
          setChunks([]);
        }}
        width={900}
        footer={[
          <Button key="close" onClick={() => setChunksModalVisible(false)}>
            关闭
          </Button>
        ]}
      >
        {selectedDocument && (
          <>
            <Descriptions bordered size="small" column={3} style={{ marginBottom: 16 }}>
              <Descriptions.Item label="文件类型">
                {selectedDocument.file_type}
              </Descriptions.Item>
              <Descriptions.Item label="文件大小">
                {formatFileSize(selectedDocument.file_size)}
              </Descriptions.Item>
              <Descriptions.Item label="分块数量">
                {selectedDocument.chunk_count}
              </Descriptions.Item>
              <Descriptions.Item label="字符数">
                {selectedDocument.character_count?.toLocaleString() || 0}
              </Descriptions.Item>
              <Descriptions.Item label="状态">
                <Tag color={getStatusColor(selectedDocument.status)}>
                  {getStatusText(selectedDocument.status)}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="上传时间">
                {new Date(selectedDocument.uploaded_at).toLocaleString('zh-CN')}
              </Descriptions.Item>
            </Descriptions>

            <Divider orientation="left">分块列表</Divider>
            
            {chunksLoading ? (
              <div style={{ textAlign: 'center', padding: 40 }}>
                <Text type="secondary">加载中...</Text>
              </div>
            ) : chunks.length === 0 ? (
              <div style={{ textAlign: 'center', padding: 40 }}>
                <Text type="secondary">暂无分块数据</Text>
              </div>
            ) : (
              <List
                dataSource={chunks}
                renderItem={(chunk, index) => (
                  <List.Item>
                    <Card size="small" style={{ width: '100%' }}>
                      <Space direction="vertical" style={{ width: '100%' }}>
                        <Space>
                          <Tag color="blue">块 #{chunk.chunk_index}</Tag>
                          <Text type="secondary">
                            字符数: {chunk.character_count}
                          </Text>
                          <Text type="secondary">
                            创建时间: {new Date(chunk.created_at).toLocaleString('zh-CN')}
                          </Text>
                        </Space>
                        <Paragraph
                          ellipsis={{ rows: 4, expandable: true, symbol: '展开更多' }}
                          style={{ 
                            marginBottom: 0, 
                            whiteSpace: 'pre-wrap',
                            backgroundColor: '#f5f5f5',
                            padding: 12,
                            borderRadius: 4
                          }}
                        >
                          {chunk.content}
                        </Paragraph>
                      </Space>
                    </Card>
                  </List.Item>
                )}
                pagination={{
                  pageSize: 5,
                  size: 'small',
                  showTotal: (total) => `共 ${total} 个分块`
                }}
              />
            )}
          </>
        )}
      </Modal>
    </div>
  );
};

export default KnowledgeBaseDetail;
