/**
 * 索引管理组件 - 显示和管理所有ES索引
 */
import React, { useState, useEffect } from 'react';
import { Table, Card, Button, Popconfirm, message, Tag, Space, Tooltip, Input, Upload, Modal } from 'antd';
import { DeleteOutlined, ReloadOutlined, DatabaseOutlined, InboxOutlined, PlusOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import type { UploadProps, UploadFile } from 'antd';
import { getAllIndices, deleteIndex, uploadProductFile } from '../services/productRagApi';
import { IndexInfo } from '../types';

const { Dragger } = Upload;

interface IndexManagementProps {
  onIndexSelected?: (indexName: string) => void;
  onUploadSuccess?: () => void;
}

const IndexManagement: React.FC<IndexManagementProps> = ({ onIndexSelected, onUploadSuccess }) => {
  const [indices, setIndices] = useState<IndexInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [deletingIndex, setDeletingIndex] = useState<string | null>(null);
  const [indexName, setIndexName] = useState('');
  const [uploading, setUploading] = useState(false);
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [isModalVisible, setIsModalVisible] = useState(false);

  const fetchIndices = async () => {
    setLoading(true);
    try {
      const response = await getAllIndices();
      setIndices(response.indices);
      message.success(`已加载 ${response.total} 个知识库`);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '获取知识库列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIndices();
  }, []);

  const handleDeleteIndex = async (indexName: string) => {
    setDeletingIndex(indexName);
    try {
      await deleteIndex(indexName);
      message.success(`知识库 ${indexName} 已删除`);
      await fetchIndices(); // 刷新列表
    } catch (error: any) {
      message.error(error.response?.data?.detail || '删除知识库失败');
    } finally {
      setDeletingIndex(null);
    }
  };

  const handleSave = async () => {
    // 验证索引名称
    if (!indexName || !indexName.trim()) {
      message.error('请输入知识库名称');
      return;
    }

    // 验证索引名称格式：只能包含小写字母、数字、下划线和连字符
    const indexNamePattern = /^[a-z0-9_-]+$/;
    if (!indexNamePattern.test(indexName.trim())) {
      message.error('知识库名称只能包含小写字母、数字、下划线(_)和连字符(-)');
      return;
    }

    // 验证是否选择了文件
    if (fileList.length === 0) {
      message.error('请选择要上传的文件');
      return;
    }

    // 获取文件对象，可能是originFileObj或者直接就是File
    const fileItem = fileList[0];
    const file = (fileItem.originFileObj || fileItem) as File;
    
    if (!file || !(file instanceof File)) {
      message.error('文件格式错误');
      console.error('File object:', file);
      return;
    }

    setUploading(true);
    try {
      const result = await uploadProductFile(file, indexName.trim());
      message.success(
        `上传成功！处理了 ${result.result.processed} 个商品，耗时 ${result.result.elapsed_time_seconds.toFixed(2)} 秒`
      );
      // 清空文件列表和索引名称
      setFileList([]);
      setIndexName('');
      // 关闭弹框
      setIsModalVisible(false);
      // 刷新索引列表
      await fetchIndices();
      if (onUploadSuccess) {
        onUploadSuccess();
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || '上传失败');
    } finally {
      setUploading(false);
    }
  };

  const handleModalCancel = () => {
    if (!uploading) {
      setIsModalVisible(false);
      setFileList([]);
      setIndexName('');
    }
  };

  const uploadProps: UploadProps = {
    name: 'file',
    accept: '.json',
    multiple: false,
    fileList,
    onRemove: () => {
      setFileList([]);
      return true;
    },
    beforeUpload: (file) => {
      // 检查文件类型
      const isJson = file.name.endsWith('.json');
      if (!isJson) {
        message.error('只能上传 JSON 文件！');
        return false;
      }

      // 检查文件大小（限制50MB）
      const isLt50M = file.size / 1024 / 1024 < 50;
      if (!isLt50M) {
        message.error('文件大小不能超过 50MB！');
        return false;
      }

      // 只更新文件列表，不立即上传
      setFileList([file as UploadFile]);
      return false; // 阻止默认上传行为
    },
  };

  const columns: ColumnsType<IndexInfo> = [
    {
      title: '知识库名称',
      dataIndex: 'name',
      key: 'name',
      width: 300,
      ellipsis: true,
      render: (name) => (
        <Space>
          <DatabaseOutlined style={{ color: '#1890ff' }} />
          <span style={{ fontWeight: 500 }}>{name}</span>
        </Space>
      ),
    },
    {
      title: '文档数量',
      dataIndex: 'docs_count',
      key: 'docs_count',
      width: 120,
      align: 'right',
      sorter: (a, b) => a.docs_count - b.docs_count,
      render: (count) => (
        <Tag color={count > 0 ? 'blue' : 'default'}>
          {count.toLocaleString()}
        </Tag>
      ),
    },
    {
      title: '存储大小',
      dataIndex: 'store_size',
      key: 'store_size',
      width: 120,
      align: 'right',
    },
    {
      title: '健康状态',
      dataIndex: 'health',
      key: 'health',
      width: 100,
      align: 'center',
      render: (health) => {
        const colorMap: Record<string, string> = {
          green: 'success',
          yellow: 'warning',
          red: 'error',
        };
        return (
          <Tag color={colorMap[health] || 'default'}>
            {health.toUpperCase()}
          </Tag>
        );
      },
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      align: 'center',
      render: (status) => (
        <Tag color={status === 'open' ? 'green' : 'default'}>
          {status.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      ellipsis: true,
      render: (time) => time || '-',
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      fixed: 'right',
      render: (_, record) => (
        <Space>
          {onIndexSelected && (
            <Button
              type="link"
              size="small"
              onClick={() => onIndexSelected(record.name)}
            >
              选择
            </Button>
          )}
          <Popconfirm
            title="确定要删除此知识库吗？"
            description={`知识库 ${record.name} 及其所有数据将被永久删除！`}
            onConfirm={() => handleDeleteIndex(record.name)}
            okText="确定"
            cancelText="取消"
            okButtonProps={{ danger: true }}
          >
            <Button
              type="link"
              danger
              size="small"
              icon={<DeleteOutlined />}
              loading={deletingIndex === record.name}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <>
      {/* 上传弹框 */}
      <Modal
        title="新建商品知识库"
        open={isModalVisible}
        onCancel={handleModalCancel}
        onOk={handleSave}
        okText="保存"
        cancelText="取消"
        width={600}
        maskClosable={!uploading}
        closable={!uploading}
        confirmLoading={uploading}
      >
        {/* 索引名称输入框 */}
        <div style={{ marginBottom: 16 }}>
          <Space direction="vertical" style={{ width: '100%' }}>
            <div style={{ 
              fontSize: '13px', 
              fontWeight: 500,
              color: '#262626',
              marginBottom: 4
            }}>
              知识库名称 <span style={{ color: '#ff4d4f' }}>*</span>
            </div>
            <Input
              placeholder="请输入知识库名称，例如: product_rag_test"
              value={indexName}
              onChange={(e) => setIndexName(e.target.value)}
              disabled={uploading}
              size="large"
              style={{
                borderRadius: '8px',
                fontSize: '14px',
              }}
            />
            <div style={{ 
              fontSize: '12px', 
              color: '#8c8c8c',
              fontStyle: 'italic'
            }}>
              💡 知识库名称只能包含小写字母、数字、下划线(_)和连字符(-)，不能包含中文和大写字母
            </div>
          </Space>
        </div>

        {/* 文件上传区域 */}
        <Dragger {...uploadProps} disabled={uploading} style={{
          background: 'linear-gradient(145deg, #f0f5ff 0%, #f9f0ff 100%)',
          border: '2px dashed #1890ff',
          borderRadius: '12px',
        }}>
          <p className="ant-upload-drag-icon">
            <InboxOutlined style={{ fontSize: '48px', color: '#1890ff' }} />
          </p>
          <p className="ant-upload-text" style={{ 
            fontSize: '15px',
            fontWeight: 600,
            color: '#1890ff'
          }}>
            点击或拖拽 JSON 文件到此区域上传
          </p>
          <p className="ant-upload-hint" style={{ 
            fontSize: '12px',
            color: '#8c8c8c'
          }}>
            支持单个商品对象或商品数组格式，文件大小不超过 50MB
          </p>
        </Dragger>
      </Modal>

      {/* 索引列表卡片 */}
      <Card
        title={
          <Space>
            <DatabaseOutlined style={{ fontSize: '18px', color: '#1890ff' }} />
            <span>商品知识库列表</span>
            <Tag color="blue">{indices.length} 个知识库</Tag>
          </Space>
        }
        extra={
          <Space>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setIsModalVisible(true)}
            >
              新建商品知识库
            </Button>
            <Tooltip title="刷新知识库列表">
              <Button
                icon={<ReloadOutlined />}
                onClick={fetchIndices}
                loading={loading}
              >
                刷新
              </Button>
            </Tooltip>
          </Space>
        }
        style={{ height: '100%', display: 'flex', flexDirection: 'column' }}
        bodyStyle={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}
      >
        <div style={{ marginBottom: 16, color: '#666', fontSize: '13px' }}>
          💡 提示: 这里显示所有商品知识库及其状态信息。您可以查看知识库详情、选择知识库进行查询测试或删除不需要的知识库。
        </div>

        <div style={{ flex: 1, overflow: 'auto' }}>
          <Table
            columns={columns}
            dataSource={indices}
            rowKey="name"
            loading={loading}
            pagination={{
              pageSize: 10,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total) => `共 ${total} 个知识库`,
            }}
            scroll={{ x: 1200 }}
            bordered
            size="small"
          />
        </div>
      </Card>
    </>
  );
};

export default IndexManagement;

