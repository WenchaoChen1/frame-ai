# 更新日志

本项目的所有重要更改都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.1.0] - 2024-01-02

### 新增功能

#### 前端
- ✅ 集成 Ant Design X - 专业的 AI 对话组件库
- ✅ 新增 Stop 停止功能 - 可随时停止 AI 生成
- ✅ 完善的 React Router 路由管理
- ✅ URL 支持会话 ID，可直接访问和分享
- ✅ 新增 `ChatWindowX` 组件使用 Ant Design X
- ✅ 新增 `ChatPage` 页面组件
- ✅ 停止按钮在生成时显示

#### 后端
- ✅ 新增 `/api/conversations/{id}/messages/stop/{message_id}` 停止接口
- ✅ 流式生成支持实时检查停止信号
- ✅ 停止后自动保存已生成内容到数据库
- ✅ 已有的 Swagger 文档自动更新

### 改进

#### 前端
- ✅ 改进路由结构，使用嵌套路由
- ✅ 状态管理支持函数式更新
- ✅ 会话列表支持路由导航
- ✅ 更流畅的 UI 交互体验

#### 后端
- ✅ 优化流式响应处理逻辑
- ✅ 添加 `active_streams` 管理活跃流
- ✅ 改进错误处理和清理机制

### 技术栈更新

#### 新增依赖
- `@ant-design/x@^1.0.0` - AI 对话专用组件

### 文档
- ✅ 新增 `UPGRADE_NOTES.md` - 升级说明文档
- ✅ 更新 `README.md` - 添加新功能说明
- ✅ 更新 API 文档说明

## [1.0.0] - 2024-01-01

### 新增功能

#### 后端
- ✅ FastAPI后端框架搭建
- ✅ PostgreSQL数据库集成
- ✅ SQLAlchemy ORM数据模型
- ✅ JWT用户认证系统
- ✅ 用户注册和登录功能
- ✅ OpenAI GPT系列模型集成
- ✅ Anthropic Claude系列模型集成
- ✅ Ollama本地模型集成
- ✅ AI服务统一管理器
- ✅ 流式响应（SSE）支持
- ✅ 会话管理（创建、查询、删除）
- ✅ 消息历史持久化
- ✅ CORS跨域支持
- ✅ API文档（Swagger/ReDoc）

#### 前端
- ✅ React + TypeScript + Vite搭建
- ✅ Ant Design UI组件库
- ✅ Zustand状态管理
- ✅ 用户认证界面（登录/注册）
- ✅ 现代化聊天界面
- ✅ 侧边栏会话列表
- ✅ 实时流式消息显示
- ✅ Markdown消息渲染
- ✅ AI提供商和模型选择
- ✅ 多会话管理
- ✅ 响应式布局设计

#### 部署
- ✅ Docker化后端服务
- ✅ Docker化前端服务（Nginx）
- ✅ Docker Compose编排
- ✅ PostgreSQL容器配置
- ✅ 健康检查配置
- ✅ 数据持久化
- ✅ 环境变量配置
- ✅ 一键启动脚本

#### 文档
- ✅ README.md 项目说明
- ✅ DEPLOYMENT.md 部署指南
- ✅ API.md API接口文档
- ✅ QUICKSTART.md 快速开始
- ✅ CHANGELOG.md 更新日志

### 技术栈

#### 后端
- Python 3.11
- FastAPI 0.104.1
- SQLAlchemy 2.0.23
- PostgreSQL 15
- OpenAI SDK 1.3.5
- Anthropic SDK 0.7.7
- JWT认证

#### 前端
- React 18.2
- TypeScript 5.3
- Ant Design 5.12
- Zustand 4.4
- Vite 5.0
- React Markdown

#### 部署
- Docker
- Docker Compose
- Nginx
- PostgreSQL

### 支持的AI模型

#### OpenAI
- gpt-3.5-turbo
- gpt-4
- gpt-4-turbo-preview
- gpt-4o
- gpt-4o-mini

#### Anthropic Claude
- claude-3-opus-20240229
- claude-3-sonnet-20240229
- claude-3-haiku-20240307
- claude-3-5-sonnet-20241022

#### Ollama（本地）
- llama2
- llama3
- mistral
- mixtral
- codellama
- qwen
- gemma

## [未来计划]

### v1.1.0
- [ ] 会话搜索功能
- [ ] 消息编辑和删除
- [ ] 代码高亮优化
- [ ] 导出对话记录
- [ ] 深色模式
- [ ] 多语言支持

### v1.2.0
- [ ] 文件上传（图片、文档）
- [ ] 语音输入
- [ ] 文字转语音
- [ ] AI绘图集成
- [ ] 知识库管理

### v2.0.0
- [ ] RAG（检索增强生成）
- [ ] 向量数据库集成（Elasticsearch）
- [ ] 文档解析和分割
- [ ] 语义搜索
- [ ] 知识库问答
- [ ] 团队协作功能
- [ ] 角色和权限管理
- [ ] 使用统计和分析

## 贡献者

感谢所有为这个项目做出贡献的开发者！

## 许可证

[MIT License](./LICENSE)

