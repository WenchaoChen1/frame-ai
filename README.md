# AI聊天对话系统

一个功能完整的AI聊天对话系统，支持多个AI提供商（OpenAI、Claude、Ollama），包含用户认证、多会话管理、聊天历史持久化和流式输出。

## 功能特性

### 核心功能
- 🤖 **多AI提供商支持**：OpenAI GPT、Anthropic Claude、Ollama本地模型
- 💬 **多会话管理**：创建、切换、删除多个对话会话
- 💾 **历史记录持久化**：所有对话历史保存在PostgreSQL数据库
- 🔐 **用户认证系统**：JWT token认证，注册/登录功能
- ⚡ **流式输出**：实时流式显示AI响应内容
- 🛑 **Stop停止功能**：随时停止AI生成，已生成内容自动保存
- 🎨 **Ant Design X界面**：专业的AI对话UI组件
- 🗺️ **完善的路由管理**：支持URL导航和浏览器历史
- 📚 **Swagger文档**：完整的API交互式文档
- 🐳 **Docker部署**：一键部署，支持独立运行

### 高级功能
- 🤖 **智能机器人管理** - [功能文档](docs/features/robot/ROBOT_FEATURE.md)
- 📚 **RAG 知识库系统** - [功能文档](docs/features/rag/)
- 💬 **Text-to-SQL 自然语言查询** - [功能文档](docs/features/text-to-sql/TEXT_TO_SQL_IMPLEMENTATION.md)
- 🗄️ **多数据库连接支持** - [功能文档](docs/features/DATABASE_FEATURE.md)
- 🧠 **知识库高级配置** - [功能文档](docs/features/knowledge-base/KNOWLEDGE_BASE_ADVANCED_CONFIG.md)

## 技术栈

### 后端
- **FastAPI** - 现代化的Python Web框架
- **SQLAlchemy** - ORM数据库工具
- **PostgreSQL** - 关系型数据库
- **OpenAI SDK** - OpenAI API集成
- **Anthropic SDK** - Claude API集成
- **JWT** - 用户认证

### 前端
- **React 18** - UI框架
- **TypeScript** - 类型安全
- **Ant Design** - UI组件库
- **Ant Design X** - AI对话专用组件
- **React Router v6** - 路由管理
- **Zustand** - 状态管理
- **Vite** - 构建工具
- **React Markdown** - Markdown渲染

## 快速开始

### 环境要求

- Docker & Docker Compose
- （可选）Node.js 18+ 和 Python 3.11+ （本地开发）

### 1. 克隆项目

```bash
git clone <repository-url>
cd fangying-ai
```

### 2. 配置环境变量

复制环境变量模板并配置：

```bash
# 在项目根目录创建 .env 文件
cp .env.example .env
```

编辑 `.env` 文件，填入你的API密钥：

```env
# OpenAI API密钥（如果使用OpenAI）
OPENAI_API_KEY=sk-your-openai-api-key

# Anthropic API密钥（如果使用Claude）
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key

# Ollama地址（如果使用本地Ollama）
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

### 3. 启动服务

使用Docker Compose一键启动所有服务：

```bash
docker-compose up -d
```

等待服务启动完成，可以通过以下命令查看日志：

```bash
docker-compose logs -f
```

### 4. 访问应用

- **前端应用**: http://localhost
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

### 5. 注册账号

首次使用需要注册账号：
1. 访问 http://localhost
2. 点击"注册账号"
3. 填写用户名、邮箱和密码
4. 注册成功后自动登录

## 本地开发

### 三种启动方式

#### 🐳 方式 1: Docker Compose（推荐，生产环境）

```bash
docker-compose up -d --build
```

#### 🚀 方式 2: 使用启动脚本（开发环境）

**后端启动** - 详见 [backend/README.md](backend/README.md)
```bash
cd backend
# Windows: start-backend.bat
# Linux/Mac: ./start-backend.sh
```

**前端启动** - 详见 [frontend/README.md](frontend/README.md)
```bash
cd frontend
# Windows: start-frontend.bat
# Linux/Mac: ./start-frontend.sh
```

#### 🔧 方式 3: 手动启动

**后端开发**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**前端开发**:
```bash
cd frontend
npm install
npm run dev
```

### 📚 详细文档

- **后端启动指南**: [backend/README.md](backend/README.md)
- **前端启动指南**: [frontend/README.md](frontend/README.md)
- **完整开发配置**: [docs/development/setup/DEV_SETUP.md](docs/development/setup/DEV_SETUP.md)
- **快速启动指南**: [docs/guides/quickstart/](docs/guides/quickstart/)
- **完整文档目录**: [docs/README.md](docs/README.md) ⭐

### 访问地址

- **前端应用**: http://localhost:3000
- **后端 API**: http://localhost:8000
- **Swagger 文档**: http://localhost:8000/docs ⭐

## 使用说明

### 1. 创建对话

点击左侧边栏的"新建对话"按钮创建新的对话会话。

### 2. 选择AI提供商

在消息输入框上方：
- 选择AI提供商（OpenAI、Claude、Ollama）
- 选择具体的模型（如 gpt-4, claude-3-sonnet等）

### 3. 发送消息

- 在输入框中输入消息
- 按 `Enter` 发送
- 按 `Shift+Enter` 换行
- 点击"停止"按钮可随时停止AI生成

### 4. 管理会话

- 点击会话可以切换当前对话
- 点击删除按钮可以删除会话
- 会话按最后更新时间排序

## AI提供商配置

### OpenAI

1. 访问 https://platform.openai.com/api-keys
2. 创建API密钥
3. 在 `.env` 文件中配置 `OPENAI_API_KEY`

### Claude (Anthropic)

1. 访问 https://console.anthropic.com/
2. 创建API密钥
3. 在 `.env` 文件中配置 `ANTHROPIC_API_KEY`

### Ollama（本地模型）

1. 安装Ollama: https://ollama.ai/
2. 下载模型: `ollama pull llama2`
3. 确保Ollama服务运行在默认端口 11434

## 项目结构

```
fangying-ai/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic模式
│   │   ├── routers/        # API路由
│   │   ├── services/       # 业务服务
│   │   ├── ai/             # AI 模块
│   │   │   ├── agent/      # 智能体 (RAG, Text-to-SQL)
│   │   │   ├── models/     # AI 模型服务
│   │   │   ├── embeddings/ # 嵌入模型
│   │   │   ├── vector_stores/ # 向量存储
│   │   │   └── document_loaders/ # 文档加载器
│   │   ├── playground/     # 实验功能
│   │   └── main.py         # 应用入口
│   ├── migrations/         # 数据库迁移
│   ├── requirements.txt    # Python依赖
│   └── Dockerfile
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── components/    # React组件
│   │   ├── services/      # API服务
│   │   ├── pages/         # 页面组件
│   │   ├── store/         # 状态管理
│   │   ├── playground/    # 实验功能
│   │   ├── App.tsx        # 应用入口
│   │   └── main.tsx
│   ├── package.json       # Node依赖
│   ├── Dockerfile
│   └── nginx.conf         # Nginx配置
├── docs/                   # 📚 项目文档
│   ├── features/          # 功能文档
│   ├── guides/            # 使用指南
│   ├── development/       # 开发文档
│   └── archived/          # 历史文档
├── docker-compose.yml     # Docker编排
├── LICENSE
└── README.md
```

**详细目录结构**：
- [后端目录结构](backend/DIRECTORY_STRUCTURE.md)
- [前端目录结构](frontend/DIRECTORY_STRUCTURE.md)

## API文档

启动服务后，访问 http://localhost:8000/docs 查看完整的API文档（Swagger UI）。

### Swagger 交互式文档

- **Swagger UI**: http://localhost:8000/docs - 在线测试API
- **ReDoc**: http://localhost:8000/redoc - 美观的文档展示
- **详细 API 文档**: [docs/development/api/API.md](docs/development/api/API.md)

主要API端点：

- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/me` - 获取当前用户
- `GET /api/conversations` - 获取会话列表
- `POST /api/conversations` - 创建会话
- `GET /api/conversations/{id}` - 获取会话详情
- `DELETE /api/conversations/{id}` - 删除会话
- `POST /api/conversations/{id}/messages/stream` - 发送消息（流式）
- `POST /api/conversations/{id}/messages/stop/{message_id}` - 停止生成
- `GET /api/providers` - 获取可用的AI提供商
- `GET /api/robots` - 获取机器人列表
- `GET /api/knowledge-bases` - 获取知识库列表

## 常见问题

### 1. 无法连接到Ollama

确保Ollama服务正在运行，并且可以通过 `http://host.docker.internal:11434` 访问（Docker环境）。

### 2. API密钥无效

检查 `.env` 文件中的API密钥是否正确配置，重启服务使配置生效：

```bash
docker-compose restart backend
```

### 3. 数据库连接失败

确保PostgreSQL容器正常运行：

```bash
docker-compose ps
docker-compose logs db
```

### 4. 前端无法连接后端

检查nginx配置和后端服务是否正常运行，查看日志：

```bash
docker-compose logs backend
docker-compose logs frontend
```

## 停止服务

```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷（会删除所有数据）
docker-compose down -v
```

## 许可证

MIT License

## 📖 文档导航

### 快速入门
- [项目概览](PROJECT_OVERVIEW.md)
- [使用指南](USAGE_GUIDE.md)
- [快速开始](docs/guides/quickstart/)

### 功能文档
- [RAG 知识库系统](docs/features/rag/)
- [Text-to-SQL 查询](docs/features/text-to-sql/)
- [机器人管理](docs/features/robot/)
- [知识库高级配置](docs/features/knowledge-base/)
- [商品 RAG 示例](docs/features/product-rag/)

### 开发指南
- [开发环境搭建](docs/development/setup/)
- [API 文档](docs/development/api/)
- [贡献指南](docs/development/contributing/)

### 部署和配置
- [部署指南](docs/guides/deployment/)
- [配置说明](docs/guides/configuration/)

**完整文档目录**: [docs/README.md](docs/README.md)

## 贡献

欢迎提交Issue和Pull Request！请查看 [贡献指南](docs/development/contributing/CONTRIBUTING.md)。

## 变更日志

查看 [CHANGELOG](docs/development/contributing/CHANGELOG.md) 了解版本更新信息。

## 联系方式

如有问题，请提交Issue或联系项目维护者。

