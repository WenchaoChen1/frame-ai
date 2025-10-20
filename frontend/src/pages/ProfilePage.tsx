import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Form, 
  Input, 
  Button, 
  message, 
  Space,
  Divider,
  Avatar,
  Table,
  Tag,
  Anchor,
  Row,
  Col
} from 'antd';
import { 
  UserOutlined, 
  LockOutlined, 
  MailOutlined,
  SafetyOutlined,
  AuditOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ReloadOutlined,
  IdcardOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { useAuthStore } from '../store/authStore';

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

const ProfilePage: React.FC = () => {
  const { user, updateUser } = useAuthStore();
  const [profileForm] = Form.useForm();
  const [passwordForm] = Form.useForm();
  const [loadingProfile, setLoadingProfile] = useState(false);
  const [loadingPassword, setLoadingPassword] = useState(false);
  const [audits, setAudits] = useState<LoginAuditRecord[]>([]);
  const [loadingAudits, setLoadingAudits] = useState(false);

  // 初始化表单数据
  useEffect(() => {
    if (user) {
      profileForm.setFieldsValue({
        username: user.username,
        email: user.email,
      });
    }
  }, [user, profileForm]);

  // 获取个人登录审计记录
  const fetchMyAudits = async () => {
    setLoadingAudits(true);
    try {
      const { loginAuditService } = await import('../services/loginAudit');
      const response = await loginAuditService.getMyLoginAudits(0, 20);
      setAudits(response);
    } catch (error: any) {
      console.error('获取登录审计失败:', error);
      message.error('获取登录记录失败');
    } finally {
      setLoadingAudits(false);
    }
  };

  // 初始化时加载登录审计
  useEffect(() => {
    fetchMyAudits();
  }, []);

  // 提交个人资料
  const handleProfileSubmit = async () => {
    try {
      setLoadingProfile(true);
      const values = await profileForm.validateFields();
      const { userService } = await import('../services/user');
      
      const updatedUser = await userService.updateProfile(values);
      updateUser(updatedUser);
      message.success('个人资料更新成功');
    } catch (error: any) {
      if (error.errorFields) {
        // 表单验证错误
        return;
      }
      message.error(error.response?.data?.detail || '更新失败');
    } finally {
      setLoadingProfile(false);
    }
  };

  // 提交修改密码
  const handlePasswordSubmit = async () => {
    try {
      setLoadingPassword(true);
      const values = await passwordForm.validateFields();
      const { userService } = await import('../services/user');
      
      await userService.changePassword(values);
      message.success('密码修改成功，请重新登录');
      passwordForm.resetFields();
      
      // 可以选择自动登出或让用户继续使用
    } catch (error: any) {
      if (error.errorFields) {
        // 表单验证错误
        return;
      }
      message.error(error.response?.data?.detail || '密码修改失败');
    } finally {
      setLoadingPassword(false);
    }
  };

  return (
    <div style={{ 
      padding: 24, 
      height: '100%', 
      overflow: 'auto',
      background: '#f5f7fa'
    }}>
      <div style={{ maxWidth: 1200, margin: '0 auto' }}>
        <Row gutter={24}>
          {/* 左侧导航 */}
          <Col xs={0} md={6}>
            <div style={{ position: 'sticky', top: 24 }}>
              <Card 
                title={
                  <span style={{ 
                    fontSize: 16, 
                    fontWeight: 600,
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text'
                  }}>
                    快速导航
                  </span>
                }
                style={{ 
                  borderRadius: 12,
                  boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
                  border: '1px solid rgba(102, 126, 234, 0.1)',
                  overflow: 'hidden'
                }}
                styles={{ body: { padding: '8px 0' } }}
              >
                <style>
                  {`
                    .profile-nav-anchor .ant-anchor-link {
                      padding: 12px 24px;
                      border-left: 3px solid transparent;
                      transition: all 0.3s ease;
                    }
                    .profile-nav-anchor .ant-anchor-link:hover {
                      background: rgba(102, 126, 234, 0.08);
                      border-left-color: #667eea;
                    }
                    .profile-nav-anchor .ant-anchor-link-active {
                      background: linear-gradient(90deg, rgba(102, 126, 234, 0.12) 0%, rgba(102, 126, 234, 0.02) 100%);
                      border-left-color: #667eea;
                    }
                    .profile-nav-anchor .ant-anchor-link-title {
                      display: flex;
                      align-items: center;
                      gap: 8px;
                      color: #333;
                      font-size: 14px;
                      font-weight: 500;
                    }
                    .profile-nav-anchor .ant-anchor-link-active .ant-anchor-link-title {
                      color: #667eea;
                    }
                    .profile-nav-anchor .ant-anchor-link-title:hover {
                      color: #667eea;
                    }
                    .profile-nav-anchor .ant-anchor-ink {
                      display: none;
                    }
                  `}
                </style>
                <Anchor
                  className="profile-nav-anchor"
                  affix={false}
                  offsetTop={100}
                  targetOffset={100}
                  onClick={(e, link) => {
                    e.preventDefault();
                    const targetId = link.href.replace('#', '');
                    const element = document.getElementById(targetId);
                    if (element) {
                      // 获取元素位置
                      const elementPosition = element.getBoundingClientRect().top;
                      const offsetPosition = elementPosition + window.pageYOffset - 100;
                      
                      // 平滑滚动
                      window.scrollTo({
                        top: offsetPosition,
                        behavior: 'smooth'
                      });
                      
                      // 添加高亮动画效果
                      element.style.transition = 'box-shadow 0.3s ease';
                      element.style.boxShadow = '0 0 0 3px rgba(102, 126, 234, 0.3)';
                      setTimeout(() => {
                        element.style.boxShadow = '';
                      }, 1000);
                    }
                  }}
                  items={[
                    {
                      key: 'user-info',
                      href: '#user-info',
                      title: (
                        <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <IdcardOutlined style={{ fontSize: 16 }} />
                          <span>用户信息</span>
                        </span>
                      ),
                    },
                    {
                      key: 'profile',
                      href: '#profile',
                      title: (
                        <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <UserOutlined style={{ fontSize: 16 }} />
                          <span>个人资料</span>
                        </span>
                      ),
                    },
                    {
                      key: 'password',
                      href: '#password',
                      title: (
                        <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <LockOutlined style={{ fontSize: 16 }} />
                          <span>修改密码</span>
                        </span>
                      ),
                    },
                    {
                      key: 'login-audit',
                      href: '#login-audit',
                      title: (
                        <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <AuditOutlined style={{ fontSize: 16 }} />
                          <span>登录记录</span>
                        </span>
                      ),
                    },
                  ]}
                />
              </Card>
            </div>
          </Col>

          {/* 右侧内容 */}
          <Col xs={24} md={18}>
            {/* 用户信息卡片 */}
            <Card 
              id="user-info"
              style={{ marginBottom: 24 }}
              styles={{ 
                body: { 
                  display: 'flex', 
                  alignItems: 'center',
                  padding: 32
                } 
              }}
            >
          <Avatar 
            size={80} 
            icon={<UserOutlined />}
            style={{ 
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              marginRight: 24
            }}
          />
          <div>
            <h2 style={{ margin: 0, marginBottom: 8 }}>{user?.username}</h2>
            <p style={{ margin: 0, color: '#666', fontSize: 14 }}>
              {user?.email}
            </p>
            <p style={{ 
              margin: '8px 0 0 0', 
              fontSize: 12,
              color: '#fff',
              display: 'inline-block',
              padding: '4px 12px',
              borderRadius: 4,
              background: user?.role === 'admin' 
                ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' 
                : 'linear-gradient(135deg, #52c41a 0%, #73d13d 100%)'
            }}>
              {user?.role === 'admin' ? '管理员' : '普通用户'}
            </p>
          </div>
        </Card>

            {/* 个人资料编辑卡片 */}
            <Card 
              id="profile"
              title={
                <Space>
                  <UserOutlined />
                  <span>个人资料</span>
                </Space>
              }
              style={{ marginBottom: 24 }}
            >
          <Form
            form={profileForm}
            layout="vertical"
            onFinish={handleProfileSubmit}
          >
            <Form.Item
              label="用户名"
              name="username"
              rules={[
                { required: true, message: '请输入用户名' },
                { min: 3, message: '用户名至少3个字符' },
              ]}
            >
              <Input 
                prefix={<UserOutlined />} 
                placeholder="请输入用户名" 
                size="large"
              />
            </Form.Item>

            <Form.Item
              label="邮箱"
              name="email"
              rules={[
                { required: true, message: '请输入邮箱' },
                { type: 'email', message: '请输入有效的邮箱地址' },
              ]}
            >
              <Input 
                prefix={<MailOutlined />} 
                placeholder="请输入邮箱" 
                size="large"
              />
            </Form.Item>

            <Form.Item>
              <Button 
                type="primary" 
                htmlType="submit"
                loading={loadingProfile}
                size="large"
              >
                保存修改
              </Button>
            </Form.Item>
          </Form>
        </Card>

            {/* 修改密码卡片 */}
            <Card 
              id="password"
              title={
                <Space>
                  <LockOutlined />
                  <span>修改密码</span>
                </Space>
              }
              style={{ marginBottom: 24 }}
            >
          <Form
            form={passwordForm}
            layout="vertical"
            onFinish={handlePasswordSubmit}
          >
            <Form.Item
              label="旧密码"
              name="old_password"
              rules={[
                { required: true, message: '请输入旧密码' },
              ]}
            >
              <Input.Password 
                prefix={<LockOutlined />} 
                placeholder="请输入旧密码" 
                size="large"
              />
            </Form.Item>

            <Form.Item
              label="新密码"
              name="new_password"
              rules={[
                { required: true, message: '请输入新密码' },
                { min: 6, message: '密码至少6个字符' },
              ]}
            >
              <Input.Password 
                prefix={<SafetyOutlined />} 
                placeholder="请输入新密码" 
                size="large"
              />
            </Form.Item>

            <Form.Item
              label="确认新密码"
              name="confirm_password"
              dependencies={['new_password']}
              rules={[
                { required: true, message: '请确认新密码' },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue('new_password') === value) {
                      return Promise.resolve();
                    }
                    return Promise.reject(new Error('两次输入的密码不一致'));
                  },
                }),
              ]}
            >
              <Input.Password 
                prefix={<SafetyOutlined />} 
                placeholder="请再次输入新密码" 
                size="large"
              />
            </Form.Item>

            <Form.Item>
              <Space>
                <Button 
                  type="primary" 
                  htmlType="submit"
                  loading={loadingPassword}
                  size="large"
                  danger
                >
                  修改密码
                </Button>
                <Button 
                  onClick={() => passwordForm.resetFields()}
                  size="large"
                >
                  重置
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Card>

            {/* 登录审计卡片 */}
            <Card 
              id="login-audit"
              title={
                <Space>
                  <AuditOutlined />
                  <span>登录记录</span>
                </Space>
              }
              extra={
                <Button 
                  icon={<ReloadOutlined />}
                  onClick={fetchMyAudits}
                  loading={loadingAudits}
                >
                  刷新
                </Button>
              }
            >
          <Table
            columns={[
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
                render: (device: string) => device || '-',
              },
            ]}
            dataSource={audits}
            rowKey="id"
            loading={loadingAudits}
            pagination={{
              pageSize: 10,
              showSizeChanger: false,
              showTotal: (total) => `共 ${total} 条记录`,
            }}
            size="small"
          />
            </Card>
          </Col>
        </Row>
      </div>
    </div>
  );
};

export default ProfilePage;

