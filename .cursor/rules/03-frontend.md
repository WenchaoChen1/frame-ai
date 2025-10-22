# 前端开发规范 (React/TypeScript)

## 1. 代码风格规范

### 命名规范
- **组件文件**: 大驼峰（PascalCase），如 `ChatWindow.tsx`
- **非组件文件**: 小驼峰（camelCase），如 `authStore.ts`
- **文件夹**: 小驼峰（camelCase），如 `productRag/`
- **变量**: 小驼峰，如 `userName`
- **常量**: 全大写+下划线，如 `API_BASE_URL`
- **布尔值**: is/has/should 前缀，如 `isVisible`
- **事件处理**: handle 前缀，如 `handleClick`

### 组件结构
```tsx
// 1. 导入
import React, { useState, useEffect } from 'react';
import './ExampleComponent.css';

// 2. 类型定义
interface ExampleComponentProps {
  title: string;
  onSave?: (data: any) => void;
}

// 3. 组件定义
const ExampleComponent: React.FC<ExampleComponentProps> = ({ 
  title, 
  onSave 
}) => {
  // 4. Hooks
  const [data, setData] = useState<any>(null);
  
  useEffect(() => {
    // 副作用逻辑
  }, []);

  // 5. 事件处理函数
  const handleClick = () => {
    // 处理逻辑
  };

  // 6. 渲染
  return (
    <div className="example-component">
      <h1>{title}</h1>
    </div>
  );
};

// 7. 导出
export default ExampleComponent;
```

### API 调用
封装在 services 层，不要在组件中直接使用 axios
```typescript
// services/user.ts
import { message } from 'antd';

export const getUsers = async (): Promise<User[]> => {
  try {
    const response = await api.get('/api/users');
    return response.data;
  } catch (error: any) {
    // 统一错误处理
    const errorMsg = error.response?.data?.detail || '获取用户列表失败';
    message.error(errorMsg);
    throw error;
  }
};
```

### 错误处理规范

**组件错误处理**：
```tsx
const [loading, setLoading] = useState(false);
const [error, setError] = useState<string | null>(null);

const fetchData = async () => {
  setLoading(true);
  setError(null);
  try {
    const data = await getUsers();
    // 处理数据
  } catch (err: any) {
    setError(err.message || '操作失败');
  } finally {
    setLoading(false);
  }
};
```

**统一的用户反馈**：
- 使用 Ant Design 的 `message` 组件显示提示
- 成功操作：`message.success('操作成功')`
- 失败操作：`message.error('操作失败')`
- 警告信息：`message.warning('请先选择数据')`
- 加载状态：使用 `loading` state 或 Spin 组件

### Ant Design X 使用规范
**AI 对话组件必须使用 Ant Design X**

```tsx
import { Bubble } from '@ant-design/x';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

// 消息气泡
<Bubble
  content={
    <ReactMarkdown remarkPlugins={[remarkGfm]}>
      {message.content}
    </ReactMarkdown>
  }
  avatar={
    message.role === 'user' 
      ? <UserOutlined /> 
      : <RobotOutlined />
  }
  placement={message.role === 'user' ? 'end' : 'start'}
  typing={isStreaming}
/>
```

**Ant Design X 最佳实践**：
- 使用 `Bubble` 组件展示对话消息
- 使用 `Prompts` 组件提供快捷输入
- 使用 `Conversations` 组件管理会话列表
- 使用 `Sender` 组件作为输入框

---

## 2. 项目目录结构

```
frontend/
├── src/
│   ├── main.tsx               # 应用入口
│   ├── App.tsx                # 根组件
│   ├── components/            # 组件（按功能分类）
│   │   ├── Auth/              # 认证组件
│   │   ├── Chat/              # 聊天组件（使用 Ant Design X）
│   │   ├── Robot/             # 机器人管理
│   │   ├── KnowledgeBase/     # 知识库组件
│   │   ├── Layout/            # 布局组件
│   │   └── Common/            # 通用组件
│   ├── pages/                 # 页面组件
│   ├── features/              # 功能模块（核心业务）
│   │   └── knowledgeBase/     # 知识库功能
│   ├── playground/            # 实验功能模块
│   │   └── productRag/        # 产品 RAG 示例（camelCase）（可删除）
│   │       ├── components/    # 功能专用组件
│   │       ├── hooks/         # 功能专用 Hooks
│   │       ├── services/      # 功能专用 API
│   │       ├── types/         # 功能专用类型
│   │       └── pages/         # 功能专用页面
│   ├── router/                # 路由配置
│   ├── services/              # API服务层
│   ├── store/                 # 状态管理（Zustand）
│   ├── hooks/                 # 自定义Hooks
│   └── types/                 # TypeScript类型定义
├── tests/                     # 测试目录
│   ├── unit/                  # 单元测试
│   ├── integration/           # 集成测试
│   └── e2e/                   # 端到端测试
├── docs/                      # 前端文档
└── public/                    # 静态资源
```

---

## 3. 开发规范

### 组件开发
- **组件拆分**: 单个组件不超过 300 行
- **可复用性**: 提取通用组件到 `Common/`
- **性能优化**: 使用 React.memo、useCallback、useMemo
- **懒加载**: 使用 React.lazy 和 Suspense
- **AI 组件**: 优先使用 Ant Design X 的 Bubble、Sender 等组件

### 状态管理
```tsx
// 本地状态
const [isOpen, setIsOpen] = useState(false);

// 全局状态（Zustand）
const { user, login } = useAuthStore();
```

### 路径别名配置
```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import path from 'path';

export default defineConfig({
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});

// tsconfig.json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

---

## 4. 测试规范

### 测试框架
- Vitest + React Testing Library
- 文件命名: `*.test.tsx` 或 `*.test.ts`
- 覆盖范围: 组件渲染、用户交互、API调用、Hooks

### 组件测试示例
```tsx
// tests/unit/components/Auth/Login.test.tsx
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import Login from '@/components/Auth/Login';

describe('Login Component', () => {
  it('应该正确渲染登录表单', () => {
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );
    
    expect(screen.getByPlaceholderText('用户名')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '登录' })).toBeInTheDocument();
  });
});
```

### 测试覆盖率要求
- **组件**: 关键组件覆盖率 > 80%
- **工具函数**: 覆盖率 > 90%
- **业务逻辑**: 覆盖率 > 85%

---

## 5. 新增功能指南

### 添加新页面
1. 在 `pages/` 创建页面组件
2. 在 `router/routes.tsx` 添加路由
3. 配置权限和面包屑
4.确保符合规范通用组件放到components,等等

### 添加新实验功能（Playground）
1. 在 `src/playground/` 下创建功能文件夹（如 `productRag/`，camelCase命名）
2. 创建必要文件：
   - `components/`: 功能专用组件（有必要可以用最外层的components...）
   - `hooks/`: 功能专用 Hooks（有必要可以用最外层的hooks...）
   - `services/`: 功能专用 API
   - `types/`: 功能专用类型
   - `pages/`: 功能专用页面
   - `README.md`: 功能说明
3. 在 `router/routes.tsx` 中添加路由
4. 确保后端有对应的实现
### 添加核心功能功能（features）
1. 在 `src/features/` 下创建功能文件夹（如 `productRag/`，camelCase命名）
2. 创建必要文件：
   - `components/`: 功能专用组件（有必要可以用最外层的components...）
   - `hooks/`: 功能专用 Hooks（有必要可以用最外层的hooks...）
   - `services/`: 功能专用 API
   - `types/`: 功能专用类型
   - `pages/`: 功能专用页面
   - `README.md`: 功能说明
3. 在 `router/routes.tsx` 中添加路由
4. 确保后端有对应的实现

**前后端命名对应**：
```tsx
// 后端: backend/app/playground/product_rag/  (snake_case)
// 前端: frontend/src/playground/productRag/  (camelCase)

// 导入示例（使用路径别名）
import ProductRagPage from '@/playground/productRag/pages/ProductRagPage';
import { useProductRag } from '@/playground/productRag/hooks/useProductRag';
```

