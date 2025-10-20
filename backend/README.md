# 后端服务 (FastAPI) 启动指南

## 📋 简介

基于 FastAPI 的 AI 聊天系统后端服务，支持多个 AI 提供商（OpenAI、Claude、Ollama）。

## 🚀 快速启动

### 方式一：使用启动脚本（推荐）

**Windows**:
```cmd
start-backend.bat
```

**Linux/Mac**:
```bash
chmod +x start-backend.sh
./start-backend.sh
```

### 方式二：手动启动

#### 1. 创建并激活虚拟环境

**Windows (PowerShell)**:
```powershell
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 如果遇到执行策略错误
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\Activate.ps1
```

**Windows (CMD)**:
```cmd
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate.bat
```

**Linux/Mac**:
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate
```

#### 2. 安装依赖

```bash
# 确保虚拟环境已激活（看到 (venv) 前缀）
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3. 配置环境变量

创建 `.env` 文件（或复制 `.env.example`）：

```env
# 数据库配置
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/chatai

# JWT 配置
SECRET_KEY=your-secret-key-use-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# AI 提供商配置（至少配置一个）
OPENAI_API_KEY=sk-your-openai-api-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key
OLLAMA_BASE_URL=http://localhost:11434

# CORS 配置
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

**生成安全的 SECRET_KEY**:
```bash
# 使用 Python
python -c "import secrets; print(secrets.token_hex(32))"

# 或使用 OpenSSL
openssl rand -hex 32
```

#### 4. 启动服务

```bash
# 开发模式（自动重载）
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🌐 访问地址

服务启动后访问：

- **API 根路径**: http://localhost:8000/
- **健康检查**: http://localhost:8000/health
- **Swagger UI**: http://localhost:8000/docs ⭐
- **ReDoc**: http://localhost:8000/redoc

## 📚 API 文档

### Swagger 交互式文档

访问 http://localhost:8000/docs 可以：
- 查看所有 API 接口
- 在线测试接口
- 查看请求/响应示例
- 配置认证 Token

### 使用 Swagger 测试

1. 访问 http://localhost:8000/docs
2. 点击 **POST /api/auth/login** 登录获取 token
3. 点击右上角 **Authorize** 按钮
4. 输入 `Bearer <your_token>`
5. 开始测试其他接口

## 🗄️ 数据库配置

### 1. 安装 PostgreSQL

下载并安装 PostgreSQL 15+

### 2. 创建数据库

```bash
# 连接到 PostgreSQL
psql -U postgres

# 创建数据库
CREATE DATABASE chatai;
CREATE USER chatai_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE chatai TO chatai_user;

# 退出
\q
```

### 3. 测试连接

```bash
psql -U postgres -d chatai -c "SELECT version();"
```

## 📦 项目结构

```
backend/
├── app/
│   ├── core/              # 核心配置
│   │   ├── config.py      # 配置管理
│   │   ├── database.py    # 数据库连接
│   │   └── security.py    # JWT 和密码加密
│   ├── models/            # SQLAlchemy 数据模型
│   │   ├── user.py
│   │   ├── conversation.py
│   │   └── message.py
│   ├── schemas/           # Pydantic 验证模式
│   ├── routers/           # API 路由
│   │   ├── auth.py        # 认证接口
│   │   ├── conversations.py
│   │   ├── messages.py    # 含 Stop 功能
│   │   └── providers.py
│   ├── services/          # AI 服务
│   │   ├── openai_service.py
│   │   ├── claude_service.py
│   │   └── ollama_service.py
│   └── main.py           # 应用入口
├── requirements.txt      # Python 依赖
├── .env                 # 环境变量配置
├── Dockerfile           # Docker 构建文件
└── README.md           # 本文件
```

## 🔑 主要功能

### 认证系统
- JWT token 认证
- 用户注册和登录
- 密码 bcrypt 加密

### AI 服务集成
- **OpenAI**: GPT-3.5/GPT-4/GPT-4o
- **Anthropic**: Claude-3 系列
- **Ollama**: 本地模型支持

### 核心功能
- ✅ 流式响应（SSE）
- ✅ Stop 停止功能 ⭐新增
- ✅ 会话管理
- ✅ 消息持久化
- ✅ 上下文记忆

## 🛠️ 开发命令

```bash
# 启动开发服务器（自动重载）
uvicorn app.main:app --reload

# 运行测试
pytest

# 代码格式化
black app/

# 类型检查
mypy app/

# 查看所有路由
uvicorn app.main:app --reload --log-level debug
```

## 🔍 常见问题

### 问题 1: 虚拟环境激活失败

**Windows PowerShell 执行策略错误**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

### 问题 2: 数据库连接失败

检查：
1. PostgreSQL 服务是否运行
2. `.env` 中的 `DATABASE_URL` 是否正确
3. 数据库和用户是否已创建

### 问题 3: 端口被占用

**Windows**:
```cmd
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Linux/Mac**:
```bash
lsof -i :8000
kill -9 <PID>
```

### 问题 4: 模块找不到

确保虚拟环境已激活，重新安装依赖：
```bash
pip install -r requirements.txt
```

## 📊 性能配置

### 开发环境
```bash
# 单进程，自动重载
uvicorn app.main:app --reload
```

### 生产环境
```bash
# 多进程，无自动重载
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Worker 数量计算
```python
workers = (CPU 核心数 × 2) + 1
```

## 🔐 安全建议

1. **生产环境必须修改**:
   - `SECRET_KEY`: 使用强随机字符串
   - 数据库密码
   - 禁用调试模式

2. **API 密钥保护**:
   - 不要提交 `.env` 到版本控制
   - 使用环境变量或密钥管理服务

3. **CORS 配置**:
   - 生产环境限制允许的源
   - 不要使用 `*` 通配符

## 🐳 Docker 部署

### 构建镜像
```bash
docker build -t chatai-backend .
```

### 运行容器
```bash
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  -e OPENAI_API_KEY="sk-..." \
  chatai-backend
```

### 使用 Docker Compose
```bash
# 在项目根目录
docker-compose up -d
```

## 📝 环境变量说明

| 变量名 | 必需 | 说明 | 示例 |
|-------|------|------|------|
| `DATABASE_URL` | ✅ | PostgreSQL 连接字符串 | `postgresql://user:pass@host:5432/db` |
| `SECRET_KEY` | ✅ | JWT 签名密钥 | 使用 `openssl rand -hex 32` 生成 |
| `OPENAI_API_KEY` | ❌ | OpenAI API 密钥 | `sk-...` |
| `ANTHROPIC_API_KEY` | ❌ | Anthropic API 密钥 | `sk-ant-...` |
| `OLLAMA_BASE_URL` | ❌ | Ollama 服务地址 | `http://localhost:11434` |
| `CORS_ORIGINS` | ❌ | 允许的跨域源 | `http://localhost:3000` |

## 🧪 API 测试示例

### 使用 curl

```bash
# 健康检查
curl http://localhost:8000/health

# 注册用户
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"password123"}'

# 登录
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"password123"}'

# 获取当前用户（需要 token）
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <your_token>"
```

### 使用 Python

```python
import requests

# 登录
response = requests.post('http://localhost:8000/api/auth/login', json={
    'username': 'test',
    'password': 'password123'
})
token = response.json()['access_token']

# 获取会话列表
headers = {'Authorization': f'Bearer {token}'}
response = requests.get('http://localhost:8000/api/conversations', headers=headers)
print(response.json())
```

## 📖 相关文档

- **项目总体说明**: [../README.md](../README.md)
- **完整开发指南**: [../DEV_SETUP.md](../DEV_SETUP.md)
- **API 详细文档**: [../API.md](../API.md)
- **升级说明**: [../UPGRADE_NOTES.md](../UPGRADE_NOTES.md)

## 🆘 获取帮助

- 查看 Swagger 文档: http://localhost:8000/docs
- 查看项目 README: [../README.md](../README.md)
- 提交 Issue: GitHub Issues

## 📄 许可证

MIT License - 详见 [../LICENSE](../LICENSE)

---

**后端服务版本**: v1.1.0  
**FastAPI 版本**: 0.104.1  
**Python 要求**: 3.11+

