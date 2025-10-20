/**
 * 路由配置文件
 */
import { 
  MessageOutlined, 
  TeamOutlined,
  ToolOutlined,
  SettingOutlined,
  AuditOutlined,
  UserOutlined,
  RobotOutlined,
  BookOutlined
} from '@ant-design/icons';
import { Outlet } from 'react-router-dom';
import { RouteConfig } from '../types/route';
import Login from '../components/Auth/Login';
import Register from '../components/Auth/Register';
import MainLayout from '../components/Layout/MainLayout';
import ChatPage from '../pages/ChatPage';
import UserManagement from '../pages/UserManagement';
import ToolManagement from '../pages/ToolManagement';
import ProfilePage from '../pages/ProfilePage';
import LoginAudit from '../pages/LoginAudit';
import RobotManagement from '../pages/RobotManagement';
import KnowledgeBaseManagement from '../pages/KnowledgeBaseManagement';
import KnowledgeBaseDetail from '../pages/KnowledgeBaseDetail';

/**
 * 路由配置
 * - 支持嵌套路由
 * - 支持路由元数据
 * - 支持权限控制
 * - 支持动态路由
 */
export const routes: RouteConfig[] = [
  // 公开路由（无需登录）
  {
    path: '/login',
    name: 'Login',
    element: <Login />,
    meta: {
      title: '登录',
      requireAuth: false,
      hideInMenu: true,
    },
  },
  {
    path: '/register',
    name: 'Register',
    element: <Register />,
    meta: {
      title: '注册',
      requireAuth: false,
      hideInMenu: true,
    },
  },
  
  // 主应用路由（需要登录）
  {
    path: '/',
    name: 'Root',
    element: <MainLayout />,
    meta: {
      requireAuth: true,
    },
    children: [
      // 默认重定向到聊天页面
      {
        path: '',
        redirect: '/chat',
      },
      // 聊天页面
      {
        path: 'chat',
        name: 'Chat',
        element: <ChatPage />,
        meta: {
          title: 'Chat对话',
          icon: <MessageOutlined />,
          requireAuth: true,
          breadcrumb: true,
        },
      },
      {
        path: 'chat/:conversationId',
        name: 'ChatDetail',
        element: <ChatPage />,
        meta: {
          title: '对话详情',
          requireAuth: true,
          hideInMenu: true,
          breadcrumb: true,
        },
      },
      
      // 个人中心
      {
        path: 'profile',
        name: 'Profile',
        element: <ProfilePage />,
        meta: {
          title: '个人中心',
          icon: <UserOutlined />,
          requireAuth: true,
          hideInMenu: true, // 不在侧边栏显示，通过用户下拉菜单访问
          breadcrumb: true,
        },
      },
      
      // 系统管理（管理菜单组）
      {
        path: 'system',
        name: 'System',
        element: <Outlet />,
        meta: {
          title: '系统管理',
          icon: <SettingOutlined />,
          requireAuth: true,
          breadcrumb: true,
        },
        children: [
          // 默认重定向到用户管理
          {
            path: '',
            redirect: '/system/users',
          },
          // 用户管理（仅管理员可见）
          {
            path: 'users',
            name: 'SystemUsers',
            element: <UserManagement />,
            meta: {
              title: '用户管理',
              icon: <TeamOutlined />,
              requireAuth: true,
              roles: ['admin'], // 仅管理员可访问
              breadcrumb: true,
            },
          },
          // 工具管理
          {
            path: 'tools',
            name: 'SystemTools',
            element: <ToolManagement />,
            meta: {
              title: '工具管理',
              icon: <ToolOutlined />,
              requireAuth: true,
              breadcrumb: true,
            },
          },
          // 登录审计
          {
            path: 'login-audit',
            name: 'LoginAudit',
            element: <LoginAudit />,
            meta: {
              title: '登录审计',
              icon: <AuditOutlined />,
              requireAuth: true,
              breadcrumb: true,
            },
          },
          // 机器人管理
          {
            path: 'robots',
            name: 'SystemRobots',
            element: <RobotManagement />,
            meta: {
              title: '机器人管理',
              icon: <RobotOutlined />,
              requireAuth: true,
              breadcrumb: true,
            },
          },
          // 知识库管理
          {
            path: 'knowledge-bases',
            name: 'SystemKnowledgeBases',
            element: <KnowledgeBaseManagement />,
            meta: {
              title: '知识库管理',
              icon: <BookOutlined />,
              requireAuth: true,
              breadcrumb: true,
            },
          },
          // 知识库详情
          {
            path: 'knowledge-bases/:id',
            name: 'KnowledgeBaseDetail',
            element: <KnowledgeBaseDetail />,
            meta: {
              title: '知识库详情',
              requireAuth: true,
              hideInMenu: true,
              breadcrumb: true,
            },
          },
        ],
      },
    ],
  },
  
  // 404 页面（预留）
  {
    path: '*',
    name: 'NotFound',
    redirect: '/chat',
    meta: {
      hideInMenu: true,
    },
  },
];

/**
 * 获取所有需要鉴权的路由路径
 */
export const getAuthRoutes = (): string[] => {
  const authRoutes: string[] = [];
  
  const traverse = (routes: RouteConfig[], parentPath = '') => {
    routes.forEach(route => {
      const fullPath = parentPath + route.path;
      if (route.meta?.requireAuth) {
        authRoutes.push(fullPath);
      }
      if (route.children) {
        traverse(route.children, fullPath === '/' ? '' : fullPath);
      }
    });
  };
  
  traverse(routes);
  return authRoutes;
};

/**
 * 根据角色过滤路由
 */
export const filterRoutesByRole = (
  routes: RouteConfig[], 
  userRole?: string
): RouteConfig[] => {
  return routes
    .filter(route => {
      // 如果路由配置了角色限制
      if (route.meta?.roles && route.meta.roles.length > 0) {
        // 检查用户角色是否在允许列表中
        return userRole && route.meta.roles.includes(userRole);
      }
      // 没有角色限制的路由默认允许访问
      return true;
    })
    .map(route => {
      // 递归过滤子路由
      if (route.children) {
        return {
          ...route,
          children: filterRoutesByRole(route.children, userRole),
        };
      }
      return route;
    });
};

/**
 * 获取菜单项（过滤掉 hideInMenu 的路由）
 */
export const getMenuRoutes = (routes: RouteConfig[]): RouteConfig[] => {
  return routes
    .filter(route => !route.meta?.hideInMenu)
    .map(route => {
      if (route.children) {
        return {
          ...route,
          children: getMenuRoutes(route.children),
        };
      }
      return route;
    });
};

