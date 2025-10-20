import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Table, 
  Tag, 
  Space,
  Button,
  DatePicker,
  Select
} from 'antd';
import { 
  AuditOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { useAuthStore } from '../store/authStore';

const { RangePicker } = DatePicker;

interface LoginAuditRecord {
  id: number;
  user_id?: number;
  username: string;
  login_time: string;
  login_status: string;
  ip_address?: string;
  user_agent?: string;
  device_info?: string;
  location?: string;
}

const LoginAudit: React.FC = () => {
  const { user } = useAuthStore();
  const [audits, setAudits] = useState<LoginAuditRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string>('all');

  // 获取登录审计列表
  const fetchAudits = async () => {
    setLoading(true);
    try {
      const { loginAuditService } = await import('../services/loginAudit');
      let response;
      
      if (user?.role === 'admin') {
        // 管理员查看所有记录
        response = await loginAuditService.getAllLoginAudits();
      } else {
        // 普通用户只能查看自己的记录
        response = await loginAuditService.getMyLoginAudits();
      }
      
      setAudits(response);
    } catch (error: any) {
      console.error('获取登录审计失败:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAudits();
  }, [user]);

  // 过滤数据
  const filteredAudits = statusFilter === 'all' 
    ? audits 
    : audits.filter(audit => audit.login_status === statusFilter);

  // 表格列定义
  const columns: ColumnsType<LoginAuditRecord> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
      width: 150,
    },
    {
      title: '登录状态',
      dataIndex: 'login_status',
      key: 'login_status',
      width: 120,
      render: (status: string) => (
        <Tag 
          icon={status === 'success' ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
          color={status === 'success' ? 'success' : 'error'}
        >
          {status === 'success' ? '成功' : '失败'}
        </Tag>
      ),
    },
    {
      title: '登录时间',
      dataIndex: 'login_time',
      key: 'login_time',
      width: 180,
      render: (time: string) => new Date(time).toLocaleString('zh-CN'),
      sorter: (a, b) => new Date(a.login_time).getTime() - new Date(b.login_time).getTime(),
      defaultSortOrder: 'descend',
    },
    {
      title: 'IP地址',
      dataIndex: 'ip_address',
      key: 'ip_address',
      width: 150,
      render: (ip: string) => ip || '-',
    },
    {
      title: '设备信息',
      dataIndex: 'device_info',
      key: 'device_info',
      width: 180,
      render: (device: string) => device || '-',
    },
    {
      title: '浏览器',
      dataIndex: 'user_agent',
      key: 'user_agent',
      ellipsis: true,
      render: (agent: string) => agent || '-',
    },
  ];

  // 如果是管理员，添加用户ID列
  if (user?.role === 'admin') {
    columns.splice(2, 0, {
      title: '用户ID',
      dataIndex: 'user_id',
      key: 'user_id',
      width: 100,
      render: (id: number) => id || '-',
    });
  }

  return (
    <div style={{ padding: 24, height: '100%', overflow: 'auto' }}>
      <Card 
        title={
          <Space>
            <AuditOutlined />
            <span>登录审计</span>
          </Space>
        }
        extra={
          <Space>
            <Select
              value={statusFilter}
              onChange={setStatusFilter}
              style={{ width: 120 }}
              options={[
                { label: '全部', value: 'all' },
                { label: '成功', value: 'success' },
                { label: '失败', value: 'failed' },
              ]}
            />
            <Button 
              icon={<ReloadOutlined />}
              onClick={fetchAudits}
            >
              刷新
            </Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={filteredAudits}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条`,
            defaultPageSize: 20,
            pageSizeOptions: ['10', '20', '50', '100'],
          }}
          scroll={{ x: 1200 }}
        />
      </Card>
    </div>
  );
};

export default LoginAudit;

