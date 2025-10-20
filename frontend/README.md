# 前端应用 (React + TypeScript + Ant Design X) 启动指南

## 📋 简介

基于 React 18、TypeScript、Ant Design X 的现代化 AI 聊天前端应用。

## 🚀 快速启动

### 方式一：使用启动脚本（推荐）

**Windows**:
```cmd
start-frontend.bat
```

**Linux/Mac**:
```bash
chmod +x start-frontend.sh
./start-frontend.sh
```

### 方式二：手动启动

#### 1. 安装依赖

```bash
npm install
```

**如果遇到 PowerShell 执行策略问题**:

```powershell
# 方案 1: 临时允许
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
npm install

# 方案 2: 使用 CMD 而不是 PowerShell

# 方案 3: 管理员身份运行 PowerShell
Set-ExecutionPolicy RemoteSigned
```

#### 2. 启动开发服务器

```bash
npm run dev
```

#### 3. 构建生产版本

```bash
npm run build
```

#### 4. 预览生产构建

```bash
npm run preview
```

## 🌐 访问地址

服务启动后访问：

- **开发环境**: http://localhost:3000
- **或**: http://localhost:5173 (Vite 默认端口)

## 📦 项目结构

```
frontend/
├── src/
│   ├── components/        # React 组件
│   │   ├── Auth/         # 认证组件
│   │   │   ├── Login.tsx
│   │   │   └── Register.tsx
│   │   ├── Chat/         # 聊天组件
│   │   │   ├── ChatWindowX.tsx    # Ant Design X 对话组件
│   │   │   ├── MessageList.tsx
│   │   │   └── MessageInput.tsx
│   │   ├── Layout/       # 布局组件
│   │   │   └── MainLayout.tsx
│   │   └── Sidebar/      # 侧边栏组件
│   │       └── ConversationList.tsx
│   ├── services/         # API 服务
│   │   ├── api.ts        # Axios 配置
│   │   ├── auth.ts       # 认证服务
│   │   ├── conversation.ts
│   │   ├── message.ts    # 支持流式响应
│   │   └── provider.ts
│   ├── store/            # Zustand 状态管理
│   │   ├── authStore.ts
│   │   └── conversationStore.ts
│   ├── pages/            # 页面组件
│   │   └── ChatPage.tsx
│   ├── App.tsx           # 应用入口（路由配置）
│   ├── main.tsx          # React 入口
│   └── index.css         # 全局样式
├── public/               # 静态资源
├── index.html           # HTML 模板
├── package.json         # 依赖配置
├── tsconfig.json        # TypeScript 配置
├── vite.config.ts       # Vite 配置
└── README.md           # 本文件
```

## 🎨 核心功能

### UI 组件
- ✅ **Ant Design X** - 专业的 AI 对话组件
- ✅ **Ant Design** - 企业级 UI 组件库
- ✅ 响应式布局设计
- ✅ 流畅的动画效果

### 核心功能
- ✅ 用户认证（登录/注册）
- ✅ 多会话管理
- ✅ 实时流式消息显示
- ✅ **Stop 停止功能** ⭐新增
- ✅ Markdown 消息渲染
- ✅ AI 提供商和模型选择

### 路由管理
- ✅ React Router v6 嵌套路由
- ✅ URL 包含会话 ID
- ✅ 支持直接访问和分享
- ✅ 浏览器前进/后退支持

## 🛠️ 技术栈

### 核心依赖

```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "react-router-dom": "^6.20.0",
  "antd": "^5.12.0",
  "@ant-design/x": "^1.0.0",
  "@ant-design/icons": "^5.2.6",
  "axios": "^1.6.2",
  "zustand": "^4.4.7",
  "react-markdown": "^9.0.1",
  "remark-gfm": "^4.0.0"
}
```

### 开发依赖

```json
{
  "@vitejs/plugin-react": "^4.2.1",
  "typescript": "^5.3.3",
  "vite": "^5.0.8"
}
```

## 🔧 开发命令

```bash
# 启动开发服务器（热重载）
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview

# 类型检查
tsc --noEmit

# 清除缓存
npm cache clean --force
```

## ⚙️ 配置说明

### Vite 配置 (vite.config.ts)

```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
```

### TypeScript 配置

项目使用严格的 TypeScript 配置：
- 严格模式启用
- 完整的类型检查
- 未使用变量和参数检查

### API 代理

开发环境中，`/api` 请求会自动代理到后端服务 `http://localhost:8000`。

## 🎯 路由结构

```
/                          → 重定向到 /chat
/login                     → 登录页面
/register                  → 注册页面
/chat                      → 聊天页面（无会话）
/chat/:conversationId      → 指定会话的聊天页面
```

### 路由特性

- ✅ 嵌套路由设计
- ✅ URL 包含会话 ID
- ✅ 认证守卫
- ✅ 支持浏览器历史

## 🔑 主要特性详解

### 1. Ant Design X 对话界面

使用 Ant Design 专门为 AI 场景设计的对话组件：

```typescript
import { Conversations } from '@ant-design/x';

<Conversations
  items={messages}
  placeholder={{
    value: content,
    onChange: setContent,
    onSubmit: handleSend,
  }}
/>
```

### 2. Stop 停止功能

用户可以随时停止 AI 生成：

```typescript
const handleStop = async () => {
  await fetch(`/api/conversations/${id}/messages/stop/${msgId}`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  });
};
```

### 3. 流式响应处理

实时接收和显示 AI 响应：

```typescript
await messageService.sendMessageStream(
  conversationId,
  message,
  (event) => {
    if (event.type === 'content') {
      // 实时更新消息内容
    }
  }
);
```

### 4. 状态管理 (Zustand)

轻量级状态管理：

```typescript
// authStore.ts
export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem('token'),
  setAuth: (token, user) => {
    localStorage.setItem('token', token);
    set({ token, user });
  }
}));
```

## 🔍 开发技巧

### 热重载

- ✅ 代码修改自动刷新
- ✅ 保持应用状态（HMR）
- ✅ 快速开发体验

### 调试

**浏览器开发者工具**:
```
F12 → Console
F12 → Network (查看 API 请求)
F12 → React DevTools (需要安装扩展)
```

**代码中添加日志**:
```typescript
console.log('Debug:', data);
console.error('Error:', error);
```

### 状态调试

使用 React DevTools 查看组件状态和 props：
```
Components → 选择组件 → 查看 hooks 状态
```

## 🐛 常见问题

### 问题 1: npm install 失败

**PowerShell 执行策略错误**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

**或使用 CMD**:
```cmd
npm install
```

### 问题 2: 端口被占用

**Windows**:
```cmd
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

**Linux/Mac**:
```bash
lsof -i :3000
kill -9 <PID>
```

### 问题 3: 依赖冲突

```bash
# 删除并重新安装
rm -rf node_modules package-lock.json
npm install
```

### 问题 4: 构建失败

```bash
# 清除缓存
npm cache clean --force

# 删除构建产物
rm -rf dist

# 重新构建
npm run build
```

### 问题 5: API 请求失败

检查：
1. 后端服务是否运行（http://localhost:8000/health）
2. Vite 代理配置是否正确
3. 浏览器控制台 Network 标签查看请求详情

## 🎨 样式定制

### Ant Design 主题

在 `App.tsx` 中配置主题：

```typescript
<ConfigProvider
  theme={{
    token: {
      colorPrimary: '#1890ff',
      borderRadius: 6,
    }
  }}
>
  <App />
</ConfigProvider>
```

### 全局样式

编辑 `src/index.css` 添加全局样式。

## 📱 响应式设计

应用支持多种屏幕尺寸：
- 桌面端（>1200px）
- 平板端（768px - 1200px）
- 移动端（<768px）

## 🧪 测试

### 手动测试清单

- [ ] 登录功能
- [ ] 注册功能
- [ ] 创建会话
- [ ] 发送消息
- [ ] Stop 停止功能
- [ ] 切换会话
- [ ] 删除会话
- [ ] 切换 AI 模型
- [ ] 浏览器前进/后退
- [ ] 页面刷新保持状态

## 🚀 生产构建

### 构建应用

```bash
npm run build
```

构建产物位于 `dist/` 目录。

### 预览构建

```bash
npm run preview
```

### 部署到 Nginx

```nginx
server {
    listen 80;
    root /path/to/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
    }
}
```

## 🐳 Docker 部署

### 构建镜像

```bash
docker build -t chatai-frontend .
```

### 运行容器

```bash
docker run -d -p 80:80 chatai-frontend
```

### 使用 Docker Compose

```bash
# 在项目根目录
docker-compose up -d
```

## 📊 性能优化

### 已实施的优化

- ✅ Vite 快速冷启动
- ✅ 代码分割（路由级别）
- ✅ 懒加载组件
- ✅ 生产构建压缩
- ✅ Tree-shaking

### 进一步优化建议

- 图片懒加载
- 虚拟滚动（长列表）
- Service Worker（PWA）
- CDN 加速

## 📖 相关文档

- **项目总体说明**: [../README.md](../README.md)
- **完整开发指南**: [../DEV_SETUP.md](../DEV_SETUP.md)
- **快速启动指南**: [../START_DEV_GUIDE.md](../START_DEV_GUIDE.md)
- **升级说明**: [../UPGRADE_NOTES.md](../UPGRADE_NOTES.md)
- **Ant Design X 文档**: https://x.ant.design/

## 🎓 学习资源

- [React 官方文档](https://react.dev/)
- [TypeScript 文档](https://www.typescriptlang.org/)
- [Ant Design 文档](https://ant.design/)
- [Ant Design X 文档](https://x.ant.design/)
- [Vite 文档](https://vitejs.dev/)
- [Zustand 文档](https://zustand-demo.pmnd.rs/)

## 🆘 获取帮助

- 查看项目 README: [../README.md](../README.md)
- 查看后端 API: http://localhost:8000/docs
- 提交 Issue: GitHub Issues

## 📄 许可证

MIT License - 详见 [../LICENSE](../LICENSE)

---

**前端应用版本**: v1.1.0  
**React 版本**: 18.2.0  
**Node.js 要求**: 18+  
**包管理器**: npm

