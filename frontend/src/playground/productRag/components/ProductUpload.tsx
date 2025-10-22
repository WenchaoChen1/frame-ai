/**
 * 商品上传组件
 */
import React, { useState } from 'react';
import { Upload, Button, message, Card, Space, Input } from 'antd';
import { UploadOutlined, InboxOutlined } from '@ant-design/icons';
import type { UploadProps, UploadFile } from 'antd';
import { uploadProductFile } from '../services/productRagApi';

const { Dragger } = Upload;

interface ProductUploadProps {
  indexName?: string;
  onIndexNameChange?: (name: string) => void;
  onUploadSuccess?: () => void;
}

const ProductUpload: React.FC<ProductUploadProps> = ({ 
  indexName: propIndexName,
  onIndexNameChange,
  onUploadSuccess 
}) => {
  const [uploading, setUploading] = useState(false);
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [localIndexName, setLocalIndexName] = useState(propIndexName || '');

  const handleUpload = async (file: File) => {
    // 验证索引名称
    const currentIndexName = propIndexName || localIndexName;
    if (!currentIndexName || !currentIndexName.trim()) {
      message.error('请输入知识库名称');
      return;
    }

    setUploading(true);
    try {
      const result = await uploadProductFile(file, currentIndexName.trim());
      message.success(
        `上传成功！处理了 ${result.result.processed} 个商品，耗时 ${result.result.elapsed_time_seconds.toFixed(2)} 秒`
      );
      // 清空文件列表
      setFileList([]);
      if (onUploadSuccess) {
        onUploadSuccess();
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || '上传失败');
    } finally {
      setUploading(false);
    }
  };

  const handleIndexNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setLocalIndexName(value);
    if (onIndexNameChange) {
      onIndexNameChange(value);
    }
  };

  const uploadProps: UploadProps = {
    name: 'file',
    accept: '.json',
    multiple: false,
    fileList,
    onRemove: () => {
      setFileList([]);
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

      // 更新文件列表
      setFileList([file as UploadFile]);
      handleUpload(file);
      return false; // 阻止默认上传行为
    },
  };

  return (
    <Card 
      title="上传商品数据"
      size="small"
      style={{
        background: 'linear-gradient(145deg, #ffffff 0%, #f8f9ff 100%)',
        borderRadius: '12px',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
        border: '1px solid rgba(24, 144, 255, 0.1)',
      }}
      headStyle={{
        fontSize: '16px',
        fontWeight: 600,
        background: 'linear-gradient(90deg, #1890ff 0%, #722ed1 100%)',
        backgroundClip: 'text',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        padding: '8px 16px',
      }}
      bodyStyle={{
        padding: '12px 16px',
      }}
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
            目标知识库名称 <span style={{ color: '#ff4d4f' }}>*</span>
          </div>
          <Input
            placeholder="请输入知识库名称，例如: product_rag_test"
            value={propIndexName !== undefined ? propIndexName : localIndexName}
            onChange={handleIndexNameChange}
            disabled={uploading || propIndexName !== undefined}
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
            💡 知识库名称用于区分不同的商品数据集，建议使用英文字母、数字和下划线
          </div>
        </Space>
      </div>

      <style>
        {`
          .custom-dragger {
            background: linear-gradient(145deg, #f0f5ff 0%, #f9f0ff 100%) !important;
            border: 2px dashed #1890ff !important;
            border-radius: 12px !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            position: relative !important;
            overflow: hidden !important;
          }
          
          .custom-dragger::before {
            content: '';
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            background: linear-gradient(45deg, #1890ff, #722ed1, #eb2f96, #1890ff);
            background-size: 300% 300%;
            border-radius: 12px;
            opacity: 0;
            transition: opacity 0.3s ease;
            z-index: -1;
            animation: gradient-rotate 3s ease infinite;
          }
          
          @keyframes gradient-rotate {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
          }
          
          .custom-dragger:hover {
            border-color: #722ed1 !important;
            box-shadow: 0 8px 24px rgba(24, 144, 255, 0.3), 
                        0 0 0 4px rgba(24, 144, 255, 0.1) !important;
            transform: translateY(-2px) !important;
            background: linear-gradient(145deg, #e6f7ff 0%, #f9f0ff 100%) !important;
          }
          
          .custom-dragger:hover::before {
            opacity: 1;
          }
          
          .custom-dragger .ant-upload-drag-icon {
            margin-bottom: 12px;
          }
          
          .custom-dragger .ant-upload-drag-icon .anticon {
            font-size: 48px !important;
            background: linear-gradient(135deg, #1890ff 0%, #722ed1 100%);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: icon-pulse 2s ease-in-out infinite;
          }
          
          .custom-dragger .ant-upload {
            padding: 16px !important;
          }
          
          @keyframes icon-pulse {
            0%, 100% {
              transform: scale(1);
              filter: drop-shadow(0 0 0 rgba(24, 144, 255, 0));
            }
            50% {
              transform: scale(1.05);
              filter: drop-shadow(0 0 20px rgba(24, 144, 255, 0.4));
            }
          }
          
          .custom-dragger:hover .ant-upload-drag-icon .anticon {
            animation: icon-bounce 0.6s ease;
          }
          
          @keyframes icon-bounce {
            0%, 100% { transform: scale(1) rotate(0deg); }
            25% { transform: scale(1.1) rotate(-5deg); }
            75% { transform: scale(1.1) rotate(5deg); }
          }
          
          .custom-dragger .ant-upload-text {
            font-size: 15px !important;
            font-weight: 600 !important;
            background: linear-gradient(90deg, #1890ff 0%, #722ed1 100%);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 6px !important;
          }
          
          .custom-dragger .ant-upload-hint {
            font-size: 12px !important;
            color: #8c8c8c !important;
            font-weight: 500 !important;
          }
        `}
      </style>
      <Dragger {...uploadProps} disabled={uploading} className="custom-dragger">
        <p className="ant-upload-drag-icon">
          <InboxOutlined />
        </p>
        <p className="ant-upload-text">点击或拖拽 JSON 文件到此区域上传</p>
        <p className="ant-upload-hint">
          支持单个商品对象或商品数组格式，文件大小不超过 50MB
        </p>
      </Dragger>
    </Card>
  );
};

export default ProductUpload;

