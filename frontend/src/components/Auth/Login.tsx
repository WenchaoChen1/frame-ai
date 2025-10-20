import React from 'react';
import { Form, Input, Button, message } from 'antd';
import { UserOutlined, LockOutlined, InfoCircleOutlined } from '@ant-design/icons';
import { useNavigate, Link } from 'react-router-dom';
import { authService, LoginData } from '../../services/auth';
import { useAuthStore } from '../../store/authStore';
import './Login.css';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);
  const [loading, setLoading] = React.useState(false);
  const [form] = Form.useForm();

  // 默认账号信息
  const DEFAULT_USERNAME = 'admin';
  const DEFAULT_PASSWORD = 'admin123';

  const onFinish = async (values: LoginData) => {
    setLoading(true);
    try {
      const response = await authService.login(values);
      setAuth(response.access_token, response.user);
      message.success('登录成功！');
      
      // 确保 token 已保存到 localStorage 后再跳转
      // 使用 setTimeout 确保状态完全同步
      setTimeout(() => {
        navigate('/');
      }, 100);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '登录失败，请检查用户名和密码');
    } finally {
      setLoading(false);
    }
  };

  // 使用默认账号填充表单
  const useDefaultAccount = () => {
    form.setFieldsValue({
      username: DEFAULT_USERNAME,
      password: DEFAULT_PASSWORD,
    });
    message.info('已填充默认账号');
  };

  return (
    <div className="login-container">
      {/* 动态背景 */}
      <div className="login-bg">
        <div className="login-bg-gradient"></div>
        <div className="login-bg-pattern"></div>
      </div>

      {/* 粒子效果 */}
      <div className="particles">
        {[...Array(20)].map((_, i) => (
          <div key={i} className="particle" style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            animationDelay: `${Math.random() * 5}s`,
            animationDuration: `${5 + Math.random() * 10}s`
          }}></div>
        ))}
      </div>

      {/* 登录卡片 */}
      <div className="login-card">
        {/* Logo和标题 */}
        <div className="login-header">
          <div className="logo-container">
            <div className="logo-circle">
              <div className="logo-inner"></div>
            </div>
          </div>
          <h1 className="login-title">方盈AI</h1>
          <p className="login-subtitle">智能对话 · 无限可能</p>
        </div>

        {/* 默认账号提示 */}
        <div className="default-account-tip">
          <div className="tip-header">
            <InfoCircleOutlined style={{ marginRight: 8 }} />
            <span>默认测试账号</span>
          </div>
          <div className="tip-content">
            <div className="tip-row">
              <span>用户名：</span>
              <strong>{DEFAULT_USERNAME}</strong>
            </div>
            <div className="tip-row">
              <span>密码：</span>
              <strong>{DEFAULT_PASSWORD}</strong>
            </div>
            <Button 
              type="link" 
              size="small" 
              onClick={useDefaultAccount}
              className="quick-fill-btn"
            >
              快速填充
            </Button>
          </div>
        </div>

        {/* 登录表单 */}
        <Form
          form={form}
          name="login"
          onFinish={onFinish}
          autoComplete="off"
          layout="vertical"
          initialValues={{
            username: DEFAULT_USERNAME,
            password: DEFAULT_PASSWORD,
          }}
          className="login-form"
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: '请输入用户名' }]}
          >
            <Input 
              prefix={<UserOutlined className="input-icon" />} 
              placeholder="用户名" 
              size="large"
              className="cyber-input"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password
              prefix={<LockOutlined className="input-icon" />}
              placeholder="密码"
              size="large"
              className="cyber-input"
            />
          </Form.Item>

          <Form.Item>
            <Button 
              type="primary" 
              htmlType="submit" 
              block 
              size="large"
              loading={loading}
              className="cyber-button"
            >
              <span className="button-text">登录系统</span>
            </Button>
          </Form.Item>
        </Form>

        {/* 底部链接 */}
        <div className="login-footer">
          <span>还没有账号？</span>
          <Link to="/register" className="register-link">立即注册</Link>
        </div>
      </div>
    </div>
  );
};

export default Login;

