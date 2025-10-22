import React, { useState } from 'react';
import { Layout, Menu, Button, Avatar, Dropdown } from 'antd';
import { 
  LogoutOutlined, 
  UserOutlined, 
  MessageOutlined,
  TeamOutlined,
  ToolOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  SettingOutlined,
  AuditOutlined,
  ProfileOutlined,
  RobotOutlined,
  BookOutlined,
  ExperimentOutlined
} from '@ant-design/icons';
import { useNavigate, Outlet, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import type { MenuProps } from 'antd';

const { Sider, Content } = Layout;

const MainLayout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const [collapsed, setCollapsed] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // 用户下拉菜单
  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <ProfileOutlined />,
      label: '个人中心',
      onClick: () => navigate('/profile'),
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: handleLogout,
    },
  ];

  // 菜单项配置 - 使用嵌套结构
  const menuItems: MenuProps['items'] = [
    {
      key: '/chat',
      icon: <MessageOutlined />,
      label: 'Chat对话',
      onClick: () => navigate('/chat'),
    },
    {
      key: '/system/robots',
      icon: <RobotOutlined />,
      label: '机器人管理',
      onClick: () => navigate('/system/robots'),
    },
    {
      key: '/system/knowledge-bases',
      icon: <BookOutlined />,
      label: '知识库管理',
      onClick: () => navigate('/system/knowledge-bases'),
    },
    {
      key: '/system/product-rag',
      icon: <ExperimentOutlined />,
      label: '商品测试',
      onClick: () => navigate('/system/product-rag'),
    },
    {
      key: '/system',
      icon: <SettingOutlined />,
      label: '系统管理',
      children: [
        // 用户管理 - 只有管理员可见
        ...(user?.role === 'admin' ? [{
          key: '/system/users',
          icon: <TeamOutlined />,
          label: '用户管理',
          onClick: () => navigate('/system/users'),
        }] : []),
        {
          key: '/system/tools',
          icon: <ToolOutlined />,
          label: '工具管理',
          onClick: () => navigate('/system/tools'),
        },
        {
          key: '/system/login-audit',
          icon: <AuditOutlined />,
          label: '登录审计',
          onClick: () => navigate('/system/login-audit'),
        },
      ],
    },
  ];

  // 获取当前选中的菜单和打开的子菜单
  const getSelectedKey = () => {
    const path = location.pathname;
    if (path.startsWith('/chat')) return '/chat';
    if (path.startsWith('/system/users')) return '/system/users';
    if (path.startsWith('/system/robots')) return '/system/robots';
    if (path.startsWith('/system/tools')) return '/system/tools';
    if (path.startsWith('/system/login-audit')) return '/system/login-audit';
    if (path.startsWith('/system/knowledge-bases')) return '/system/knowledge-bases'; // 包括详情页
    if (path.startsWith('/system/product-rag')) return '/system/product-rag';
    if (path.startsWith('/profile')) return '/profile';
    return '/chat';
  };

  const getOpenKeys = () => {
    const path = location.pathname;
    if (path.startsWith('/system')) return ['/system'];
    return [];
  };

  return (
    <Layout style={{ height: '100vh' }}>
      {/* 侧边栏 */}
      <Sider 
        trigger={null} 
        collapsible 
        collapsed={collapsed}
        style={{
          height: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
          background: 'linear-gradient(180deg, #f5f7fa 0%, #ffffff 100%)',
          boxShadow: '2px 0 8px rgba(0, 0, 0, 0.06)',
          overflow: 'hidden',
          borderRight: '1px solid rgba(0, 0, 0, 0.06)'
        }}
      >
        <div style={{
          height: '100%',
          display: 'flex',
          flexDirection: 'column'
        }}>
          {/* Logo区域 */}
          <div style={{ 
            height: 64, 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'space-between',
            padding: '0 16px',
            borderBottom: '1px solid rgba(0, 0, 0, 0.06)',
            flexShrink: 0,
            transition: 'all 0.2s ease'
          }}>
            <div style={{
              fontSize: 22,
              fontWeight: 'bold',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              flex: 1,
              overflow: 'hidden',
              whiteSpace: 'nowrap',
              transition: 'all 0.2s ease'
            }}>
              AI
            </div>
            <Button
              type="text"
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => setCollapsed(!collapsed)}
              style={{ 
                fontSize: 16, 
                width: 32, 
                height: 32,
                color: '#666',
                flexShrink: 0,
                transition: 'all 0.2s ease'
              }}
            />
          </div>

          {/* 菜单区域 */}
          <div style={{ 
            flex: 1, 
            overflow: 'auto',
            overflowX: 'hidden',
            paddingBottom: 8
          }}>
            <Menu
              mode="inline"
              selectedKeys={[getSelectedKey()]}
              defaultOpenKeys={getOpenKeys()}
              items={menuItems}
              style={{ 
                background: 'transparent', 
                border: 'none',
                fontSize: 14
              }}
              theme="light"
            />
          </div>

          {/* 底部用户信息 */}
          <div style={{
            borderTop: '1px solid rgba(0, 0, 0, 0.06)',
            padding: '16px',
            background: 'rgba(102, 126, 234, 0.04)',
            flexShrink: 0,
            position: 'relative',
            zIndex: 10,
            transition: 'all 0.2s ease'
          }}>
          <Dropdown 
            menu={{ items: userMenuItems }} 
            placement="topLeft"
            trigger={['click']}
          >
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: collapsed ? 0 : 12,
              color: '#333',
              cursor: 'pointer',
              padding: '8px',
              borderRadius: 8,
              transition: 'all 0.2s ease',
              background: 'transparent',
              justifyContent: collapsed ? 'center' : 'flex-start'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(102, 126, 234, 0.08)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent';
            }}
            >
              <Avatar 
                icon={<UserOutlined />}
                size={40}
                style={{ 
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  flexShrink: 0,
                  boxShadow: '0 2px 8px rgba(102, 126, 234, 0.4)',
                  transition: 'all 0.2s ease'
                }}
              />
              {!collapsed && (
                <div style={{ 
                  flex: 1, 
                  minWidth: 0,
                  opacity: collapsed ? 0 : 1,
                  transition: 'opacity 0.2s ease'
                }}>
                  <div style={{ 
                    fontSize: 14, 
                    fontWeight: 600,
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                    marginBottom: 2
                  }}>
                    {user?.username}
                  </div>
                  <div style={{ 
                    fontSize: 11, 
                    color: '#fff',
                    display: 'inline-block',
                    padding: '2px 8px',
                    borderRadius: 4,
                    background: user?.role === 'admin' 
                      ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' 
                      : 'linear-gradient(135deg, #52c41a 0%, #73d13d 100%)',
                    fontWeight: 500
                  }}>
                    {user?.role === 'admin' ? '管理员' : '用户'}
                  </div>
                </div>
              )}
            </div>
          </Dropdown>
          </div>
        </div>
      </Sider>

      {/* 主内容区 */}
      <Layout style={{ marginLeft: collapsed ? 80 : 200, transition: 'all 0.2s' }}>
        {/* 内容区域 */}
        <Content style={{ 
          padding: 0,
          height: '100vh',
          overflow: 'hidden'
        }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;

