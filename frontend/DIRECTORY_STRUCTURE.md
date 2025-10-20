# 前端目录结构规范

## 项目概述

本项目采用 **React 18 + TypeScript + Vite** 架构，是一个现代化的单页应用（SPA），提供AI对话、机器人管理等功能。

### 技术栈
- **框架**: React 18.3.1
- **语言**: TypeScript 5.x
- **构建工具**: Vite 5.x
- **状态管理**: Zustand
- **路由**: React Router 6.x
- **HTTP客户端**: Axios
- **UI组件**: Ant Design 5.x
- **样式**: CSS Modules / Tailwind CSS

---

## 目录结构树

```
frontend/
├── public/                      # 静态资源
│   ├── vite.svg                # 网站图标
│   ├── debug-auth.html         # 调试页面
│   ├── debug-conversation.html
│   └── test-api.html
│
├── src/                        # 源代码目录
│   ├── main.tsx                # 应用入口
│   ├── App.tsx                 # 根组件
│   ├── index.css               # 全局样式
│   ├── vite-env.d.ts          # Vite类型声明
│   │
│   ├── components/             # 组件目录（按功能分类）
│   │   ├── Auth/              # 认证相关组件
│   │   │   ├── Login.tsx
│   │   │   ├── Login.css
│   │   │   └── Register.tsx
│   │   ├── Chat/              # 聊天相关组件
│   │   │   ├── ChatWindow.tsx
│   │   │   ├── ChatWindowX.tsx
│   │   │   ├── MessageInput.tsx
│   │   │   └── MessageList.tsx
│   │   ├── Robot/             # 机器人管理组件
│   │   │   ├── CreateRobotModal.tsx
│   │   │   ├── RobotEditForm.tsx
│   │   │   ├── RobotDetailModal.tsx
│   │   │   └── DatabaseConfig.tsx
│   │   ├── Sidebar/           # 侧边栏组件
│   │   │   └── ConversationList.tsx
│   │   ├── Layout/            # 布局组件
│   │   │   └── MainLayout.tsx
│   │   └── Common/            # 通用组件
│   │       └── Breadcrumb.tsx
│   │
│   ├── pages/                 # 页面组件
│   │   ├── ChatPage.tsx
│   │   ├── RobotManagement.tsx
│   │   ├── UserManagement.tsx
│   │   ├── LoginAudit.tsx
│   │   ├── ProfilePage.tsx
│   │   └── ToolManagement.tsx
│   │
│   ├── router/                # 路由配置
│   │   ├── index.tsx          # 路由配置主文件
│   │   ├── routes.tsx         # 路由定义
│   │   └── RouteGuard.tsx     # 路由守卫
│   │
│   ├── services/              # API服务层
│   │   ├── api.ts             # Axios实例配置
│   │   ├── auth.ts            # 认证相关API
│   │   ├── user.ts            # 用户相关API
│   │   ├── conversation.ts    # 会话相关API
│   │   ├── message.ts         # 消息相关API
│   │   ├── robot.ts           # 机器人相关API
│   │   ├── provider.ts        # AI提供商API
│   │   └── loginAudit.ts      # 登录审计API
│   │
│   ├── store/                 # 状态管理
│   │   ├── authStore.ts       # 认证状态
│   │   └── conversationStore.ts # 会话状态
│   │
│   ├── hooks/                 # 自定义Hooks
│   │   ├── useRouteAuth.ts    # 路由权限Hook
│   │   └── useBreadcrumb.ts   # 面包屑Hook
│   │
│   └── types/                 # TypeScript类型定义
│       └── route.ts           # 路由类型
│
├── index.html                 # HTML入口
├── vite.config.ts            # Vite配置
├── tsconfig.json             # TypeScript配置
├── tsconfig.node.json        # Node TypeScript配置
├── package.json              # 项目依赖
├── Dockerfile                # Docker配置
├── nginx.conf                # Nginx配置
└── README.md                 # 项目说明
```

---

## 目录详细说明

### 1. `src/` - 源代码目录
应用的核心代码，所有TypeScript/TSX文件都在这里。

#### 关键文件
- **`main.tsx`**: 应用入口，渲染根组件到DOM
- **`App.tsx`**: 根组件，包含路由配置
- **`index.css`**: 全局样式，包含基础样式和主题变量
- **`vite-env.d.ts`**: Vite的TypeScript类型声明

### 2. `src/components/` - 组件目录
可复用的React组件，按功能模块分类。

#### 组织原则
- **按功能分类**: 每个功能一个文件夹（如 `Auth/`, `Chat/`, `Robot/`）
- **相关文件放一起**: 组件及其样式、测试放在同一目录
- **避免过深嵌套**: 最多3层目录结构

#### 子目录说明

**`Auth/` - 认证组件**
- `Login.tsx`: 登录表单
- `Register.tsx`: 注册表单
- `Login.css`: 登录相关样式

**`Chat/` - 聊天组件**
- `ChatWindow.tsx`: 聊天窗口主容器
- `MessageList.tsx`: 消息列表展示
- `MessageInput.tsx`: 消息输入框

**`Robot/` - 机器人管理组件**
- `CreateRobotModal.tsx`: 创建机器人弹窗
- `RobotEditForm.tsx`: 机器人编辑表单
- `RobotDetailModal.tsx`: 机器人详情弹窗
- `DatabaseConfig.tsx`: 数据库配置组件

**`Layout/` - 布局组件**
- `MainLayout.tsx`: 主布局（包含侧边栏、顶栏等）

**`Common/` - 通用组件**
- `Breadcrumb.tsx`: 面包屑导航
- 其他可复用的通用组件

**`Sidebar/` - 侧边栏组件**
- `ConversationList.tsx`: 会话列表

### 3. `src/pages/` - 页面组件
页面级组件，通常对应一个路由。

#### 命名规范
- 文件名：大驼峰 + `Page` 后缀，如 `ChatPage.tsx`
- 组件名：与文件名一致

#### 页面职责
- 组合多个组件
- 处理页面级状态
- 连接路由参数
- 调用API服务

#### 示例结构
```tsx
// pages/ChatPage.tsx
import React from 'react';
import ChatWindow from '../components/Chat/ChatWindow';
import ConversationList from '../components/Sidebar/ConversationList';

const ChatPage: React.FC = () => {
  return (
    <div className="chat-page">
      <ConversationList />
      <ChatWindow />
    </div>
  );
};

export default ChatPage;
```

### 4. `src/router/` - 路由配置
React Router的路由定义和配置。

- **`index.tsx`**: 路由器主文件，导出配置好的路由
- **`routes.tsx`**: 路由表定义（路径、组件、权限等）
- **`RouteGuard.tsx`**: 路由守卫，处理认证和权限

#### 路由定义示例
```tsx
// router/routes.tsx
import { RouteObject } from 'react-router-dom';
import ChatPage from '../pages/ChatPage';
import RobotManagement from '../pages/RobotManagement';

export const routes: RouteObject[] = [
  {
    path: '/chat',
    element: <ChatPage />,
    meta: { requiresAuth: true }
  },
  {
    path: '/robots',
    element: <RobotManagement />,
    meta: { requiresAuth: true, roles: ['admin'] }
  }
];
```

### 5. `src/services/` - API服务层
封装所有的HTTP请求，与后端API交互。

#### 文件组织
- **`api.ts`**: Axios实例配置，请求/响应拦截器
- 其他文件：按资源分类，如 `user.ts`, `conversation.ts`

#### 命名规范
- 文件名：小写，与后端资源对应
- 函数名：动词 + 名词，如 `getUsers`, `createConversation`

#### 示例结构
```typescript
// services/user.ts
import api from './api';

export interface User {
  id: number;
  username: string;
  email: string;
}

// 获取用户列表
export const getUsers = async (): Promise<User[]> => {
  const response = await api.get('/api/users');
  return response.data;
};

// 获取单个用户
export const getUserById = async (id: number): Promise<User> => {
  const response = await api.get(`/api/users/${id}`);
  return response.data;
};

// 创建用户
export const createUser = async (data: Omit<User, 'id'>): Promise<User> => {
  const response = await api.post('/api/users', data);
  return response.data;
};
```

### 6. `src/store/` - 状态管理
使用Zustand管理全局状态。

#### 状态划分原则
- 按功能领域划分store
- 每个store一个文件
- 避免过度使用全局状态

#### 示例结构
```typescript
// store/authStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      isAuthenticated: false,
      login: (token, user) => 
        set({ token, user, isAuthenticated: true }),
      logout: () => 
        set({ token: null, user: null, isAuthenticated: false }),
    }),
    {
      name: 'auth-storage',
    }
  )
);
```

### 7. `src/hooks/` - 自定义Hooks
封装可复用的逻辑为自定义Hooks。

#### 命名规范
- 文件名：`use` + 功能描述，如 `useAuth.ts`
- Hook函数名：与文件名一致

#### 使用场景
- 复用的状态逻辑
- 复杂的副作用管理
- 表单处理
- 数据获取

#### 示例
```typescript
// hooks/useRouteAuth.ts
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

export const useRouteAuth = (requiresAuth: boolean = true) => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();

  useEffect(() => {
    if (requiresAuth && !isAuthenticated) {
      navigate('/login');
    }
  }, [requiresAuth, isAuthenticated, navigate]);
};
```

### 8. `src/types/` - TypeScript类型定义
共享的TypeScript类型和接口。

#### 组织原则
- 按功能模块分文件
- 导出类型供其他模块使用
- 避免与组件耦合的类型（放在组件文件内）

#### 示例
```typescript
// types/route.ts
export interface RouteMetaType {
  requiresAuth?: boolean;
  roles?: string[];
  title?: string;
  icon?: string;
}

export interface AppRouteObject {
  path: string;
  element: React.ReactNode;
  meta?: RouteMetaType;
  children?: AppRouteObject[];
}
```

### 9. `public/` - 静态资源
不需要经过构建处理的静态文件。

- 图标、图片
- 调试HTML页面
- 其他静态资源

---

## 命名规范

### 文件命名

**组件文件**
- 格式：大驼峰（PascalCase）
- 示例：`ChatWindow.tsx`, `UserProfile.tsx`

**非组件文件**
- 格式：小驼峰（camelCase）
- 示例：`authStore.ts`, `useAuth.ts`, `api.ts`

**样式文件**
- 格式：与组件同名或 `index.css`
- 示例：`Login.css`, `ChatWindow.module.css`

### 组件命名

**函数组件**
```tsx
// ✅ 推荐
const UserProfile: React.FC<UserProfileProps> = (props) => {
  return <div>...</div>;
};

export default UserProfile;
```

**Props接口**
```tsx
// 命名：组件名 + Props
interface UserProfileProps {
  userId: number;
  onUpdate?: () => void;
}
```

### 变量命名

- **普通变量**: 小驼峰，如 `userName`, `isLoading`
- **常量**: 全大写+下划线，如 `API_BASE_URL`, `MAX_RETRY`
- **布尔值**: is/has/should前缀，如 `isVisible`, `hasPermission`
- **事件处理**: handle前缀，如 `handleClick`, `handleSubmit`

---

## 组件开发规范

### 1. 组件结构模板

```tsx
// components/Example/ExampleComponent.tsx
import React, { useState, useEffect } from 'react';
import './ExampleComponent.css';

// 1. 类型定义
interface ExampleComponentProps {
  title: string;
  onSave?: (data: any) => void;
}

// 2. 组件定义
const ExampleComponent: React.FC<ExampleComponentProps> = ({ 
  title, 
  onSave 
}) => {
  // 3. Hooks
  const [data, setData] = useState<any>(null);
  
  useEffect(() => {
    // 副作用逻辑
  }, []);

  // 4. 事件处理函数
  const handleClick = () => {
    // 处理逻辑
  };

  // 5. 渲染
  return (
    <div className="example-component">
      <h1>{title}</h1>
      {/* JSX内容 */}
    </div>
  );
};

// 6. 导出
export default ExampleComponent;
```

### 2. Props传递原则

- 使用解构接收props
- 提供默认值
- 使用TypeScript接口定义类型

```tsx
interface ButtonProps {
  text: string;
  type?: 'primary' | 'secondary';
  onClick?: () => void;
  disabled?: boolean;
}

const Button: React.FC<ButtonProps> = ({ 
  text, 
  type = 'primary',
  onClick,
  disabled = false 
}) => {
  // ...
};
```

### 3. 状态管理原则

- **本地状态**: 使用 `useState`
- **全局状态**: 使用Zustand store
- **服务端状态**: 考虑使用React Query（未来）

```tsx
// 本地状态
const [isOpen, setIsOpen] = useState(false);

// 全局状态
const { user, login } = useAuthStore();
```

### 4. 副作用处理

```tsx
useEffect(() => {
  // 数据获取
  const fetchData = async () => {
    const data = await getUsers();
    setUsers(data);
  };
  
  fetchData();
  
  // 清理函数
  return () => {
    // 清理逻辑
  };
}, [dependencies]);
```

---

## 样式规范

### 1. CSS组织方式

**全局样式** (`index.css`)
- 重置样式
- 主题变量
- 通用工具类

**组件样式**
- 每个组件一个CSS文件
- 使用BEM命名或CSS Modules
- 避免全局污染

### 2. 样式命名（BEM）

```css
/* components/Chat/ChatWindow.css */
.chat-window {
  /* 块 */
}

.chat-window__header {
  /* 元素 */
}

.chat-window__header--active {
  /* 修饰符 */
}
```

### 3. CSS变量使用

```css
/* index.css */
:root {
  --primary-color: #1890ff;
  --text-color: #333;
  --border-radius: 4px;
}

/* 组件中使用 */
.button {
  background-color: var(--primary-color);
  border-radius: var(--border-radius);
}
```

---

## API调用规范

### 1. 错误处理

```typescript
// services/user.ts
import api from './api';

export const getUsers = async () => {
  try {
    const response = await api.get('/api/users');
    return response.data;
  } catch (error: any) {
    console.error('获取用户列表失败:', error);
    throw error;
  }
};
```

### 2. 在组件中使用

```tsx
import { useEffect, useState } from 'react';
import { getUsers } from '../services/user';

const UserList = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUsers = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getUsers();
        setUsers(data);
      } catch (err: any) {
        setError(err.message || '加载失败');
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, []);

  if (loading) return <div>加载中...</div>;
  if (error) return <div>错误: {error}</div>;

  return <div>{/* 渲染用户列表 */}</div>;
};
```

---

## 新增功能指南

### 添加新页面
1. 在 `pages/` 创建页面组件，如 `NewPage.tsx`
2. 在 `router/routes.tsx` 添加路由配置
3. 如需权限控制，在路由meta中配置

### 添加新组件
1. 在 `components/` 相应分类下创建组件文件
2. 如果是新功能模块，创建新的子目录
3. 添加组件样式文件（如需要）
4. 导出组件供其他模块使用

### 添加新的API服务
1. 在 `services/` 创建服务文件，如 `product.ts`
2. 定义接口类型
3. 封装API调用函数
4. 在组件中导入使用

### 添加新的全局状态
1. 在 `store/` 创建store文件，如 `productStore.ts`
2. 使用Zustand的create方法创建store
3. 导出hook供组件使用

---

## 最佳实践

### 1. 组件设计原则

**单一职责**
- 每个组件只做一件事
- 大组件拆分成小组件
- 提取可复用逻辑为Hooks

**Props接口清晰**
- 使用TypeScript定义Props
- 避免传递过多props（考虑组合）
- 使用可选props提供默认值

**避免prop drilling**
- 使用Context或Zustand传递深层数据
- 不要层层传递props

### 2. 性能优化

**使用React.memo**
```tsx
const ExpensiveComponent = React.memo<Props>(({ data }) => {
  // 渲染逻辑
});
```

**使用useCallback和useMemo**
```tsx
const handleClick = useCallback(() => {
  // 处理逻辑
}, [dependencies]);

const computedValue = useMemo(() => {
  return expensiveCalculation(data);
}, [data]);
```

**懒加载**
```tsx
import { lazy, Suspense } from 'react';

const HeavyComponent = lazy(() => import('./HeavyComponent'));

<Suspense fallback={<div>加载中...</div>}>
  <HeavyComponent />
</Suspense>
```

### 3. 代码分割

```tsx
// router/routes.tsx
import { lazy } from 'react';

const ChatPage = lazy(() => import('../pages/ChatPage'));
const RobotManagement = lazy(() => import('../pages/RobotManagement'));
```

### 4. 错误边界

```tsx
// components/Common/ErrorBoundary.tsx
class ErrorBoundary extends React.Component<Props, State> {
  componentDidCatch(error, errorInfo) {
    console.error('错误:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <h1>出错了</h1>;
    }
    return this.props.children;
  }
}
```

---

## 开发工具配置

### ESLint配置建议
```json
{
  "extends": [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:@typescript-eslint/recommended"
  ],
  "rules": {
    "react/react-in-jsx-scope": "off",
    "@typescript-eslint/explicit-module-boundary-types": "off"
  }
}
```

### Prettier配置建议
```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5"
}
```

---

## 常见问题

**Q: 什么时候使用Context vs Zustand？**  
A: 简单的主题、语言等用Context；复杂状态管理用Zustand。

**Q: 组件太大怎么办？**  
A: 按功能拆分成小组件，提取逻辑到Hooks。

**Q: 如何组织大型表单？**  
A: 使用表单库（如react-hook-form），按区域拆分子组件。

**Q: API调用应该放在哪里？**  
A: 封装在services层，在组件中通过Hook调用。

---

## 参考资源

- [React官方文档](https://react.dev/)
- [TypeScript官方文档](https://www.typescriptlang.org/)
- [Vite官方文档](https://vitejs.dev/)
- [Zustand文档](https://zustand-demo.pmnd.rs/)
- [Ant Design文档](https://ant.design/)
- [项目根目录README.md](../README.md)

