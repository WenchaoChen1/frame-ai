# 开发环境独立启动指南

本文档说明如何在本地开发环境中独立启动前后端项目（不使用 Docker）。

## 📋 前置要求

### 必需软件

- **Python**: 3.11+
- **Node.js**: 18+
- **PostgreSQL**: 15+
- **Git**: 最新版本

### 检查版本

```bash
# 检查 Python 版本
python --version  # 或 python3 --version

# 检查 Node.js 版本
node --version

# 检查 npm 版本
npm --version

# 检查 PostgreSQL 版本
psql --version
```

## 🗄️ 第一步：配置数据库

### 1. 启动 PostgreSQL

**Windows**:
```powershell
# 如果安装为服务，检查是否运行
Get-Service postgresql*

# 如果未运行，启动服务
Start-Service postgresql-x64-15
```

**Linux/Mac**:
```bash
# 启动 PostgreSQL
sudo service postgresql start
# 或
sudo systemctl start postgresql
```

### 2. 创建数据库

```bash
# 连接到 PostgreSQL
psql -U postgres

# 在 psql 中执行
CREATE DATABASE chatai;
CREATE USER chatai_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE chatai TO chatai_user;

# 退出
\q
```

### 3. 验证数据库

```bash
# 测试连接
psql -U postgres -d chatai -c "SELECT version();"
```

## 🐍 第二步：启动后端（Python + FastAPI）

### 1. 进入后端目录

```bash
cd backend
```

### 2. 创建虚拟环境

**Windows (PowerShell)**:
```powershell
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 如果遇到执行策略错误，临时允许脚本执行
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

### 3. 安装依赖

```bash
# 确保虚拟环境已激活（看到 (venv) 前缀）
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. 配置环境变量

创建 `backend/.env` 文件：

```env
# 数据库配置
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/chatai

# JWT 配置
SECRET_KEY=your-secret-key-change-this-in-production-use-openssl-rand-hex-32
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
# 使用 Python 生成
python -c "import secrets; print(secrets.token_hex(32))"

# 或使用 OpenSSL
openssl rand -hex 32
```

### 5. 初始化数据库

```bash
# 在 backend 目录中，虚拟环境激活状态下
# FastAPI 会在首次运行时自动创建表
```

### 6. 启动后端服务

```bash
# 确保在 backend 目录，虚拟环境已激活
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**参数说明**:
- `--host 0.0.0.0`: 允许外部访问
- `--port 8000`: 端口号
- `--reload`: 代码变更自动重载（开发模式）

### 7. 验证后端

打开浏览器访问：
- **API 根路径**: http://localhost:8000/
- **健康检查**: http://localhost:8000/health
- **Swagger 文档**: http://localhost:8000/docs
- **ReDoc 文档**: http://localhost:8000/redoc

如果看到 API 信息，说明后端启动成功！✅

### 8. 后端常用命令

```bash
# 停止服务
Ctrl + C

# 重启服务
uvicorn app.main:app --reload

# 查看日志（已在控制台输出）

# 退出虚拟环境
deactivate
```

## ⚛️ 第三步：启动前端（React + TypeScript）

### 1. 打开新的终端窗口

保持后端服务运行，打开新的终端/PowerShell 窗口。

### 2. 进入前端目录

```bash
cd frontend
```

### 3. 安装依赖

**如果遇到 PowerShell 执行策略问题**:

**方法 1: 临时允许**
```powershell
# 在 PowerShell 中执行
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
npm install
```

**方法 2: 使用 CMD**
```cmd
# 在 CMD 中执行
npm install
```

**方法 3: 修改执行策略（管理员权限）**
```powershell
# 以管理员身份运行 PowerShell
Set-ExecutionPolicy RemoteSigned
# 选择 Y 确认
```

**Linux/Mac (无问题)**:
```bash
npm install
```

### 4. 配置环境（可选）

创建 `frontend/.env` 文件（可选）：

```env
VITE_API_URL=http://localhost:8000
```

> 注意：前端已经在 `vite.config.ts` 中配置了代理，通常不需要额外配置。

### 5. 启动前端服务

```bash
npm run dev
```

### 6. 访问前端

打开浏览器访问：
- **前端应用**: http://localhost:3000
- **或**: http://localhost:5173 (Vite 默认端口)

如果看到登录页面，说明前端启动成功！✅

### 7. 前端常用命令

```bash
# 停止服务
Ctrl + C

# 重启服务
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

## 🎯 完整启动流程总结

### 终端 1 - 后端

```bash
# 1. 进入后端目录
cd backend

# 2. 激活虚拟环境
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# 3. 启动后端
uvicorn app.main:app --reload
```

### 终端 2 - 前端

```bash
# 1. 进入前端目录
cd frontend

# 2. 启动前端
npm run dev
```

## 🔍 验证所有服务

### 1. 检查后端

```bash
# 测试健康检查
curl http://localhost:8000/health

# 或在浏览器打开
http://localhost:8000/docs
```

### 2. 检查前端

```bash
# 在浏览器打开
http://localhost:3000
```

### 3. 测试完整流程

1. 打开 http://localhost:3000
2. 点击"注册账号"
3. 填写信息并注册
4. 创建新对话
5. 发送消息测试

## 🐛 常见问题

### 问题 1: PowerShell 脚本执行被禁止

**错误信息**:
```
无法加载文件，因为在此系统上禁止运行脚本
```

**解决方案**:
```powershell
# 方案 1: 临时允许（推荐）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# 方案 2: 使用 CMD 而不是 PowerShell

# 方案 3: 以管理员身份运行 PowerShell，永久修改
Set-ExecutionPolicy RemoteSigned
```

### 问题 2: 端口被占用

**错误信息**:
```
Error: listen EADDRINUSE: address already in use :::8000
```

**解决方案**:

**Windows**:
```powershell
# 查找占用端口的进程
netstat -ano | findstr :8000

# 结束进程（替换 PID）
taskkill /PID <PID> /F
```

**Linux/Mac**:
```bash
# 查找占用端口的进程
lsof -i :8000

# 结束进程
kill -9 <PID>
```

### 问题 3: 数据库连接失败

**错误信息**:
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**解决方案**:
1. 确认 PostgreSQL 服务正在运行
2. 检查 `.env` 中的 `DATABASE_URL` 配置
3. 验证数据库和用户已创建
4. 测试连接：`psql -U postgres -d chatai`

### 问题 4: 模块找不到

**错误信息**:
```
ModuleNotFoundError: No module named 'fastapi'
```

**解决方案**:
```bash
# 确认虚拟环境已激活（看到 (venv) 前缀）
# 重新安装依赖
pip install -r requirements.txt
```

### 问题 5: npm install 失败

**解决方案**:
```bash
# 清除缓存
npm cache clean --force

# 删除 node_modules 和 package-lock.json
rm -rf node_modules package-lock.json

# 重新安装
npm install
```

### 问题 6: API 请求失败（CORS）

**错误信息**:
```
Access to fetch blocked by CORS policy
```

**解决方案**:
1. 确认后端 `.env` 中 `CORS_ORIGINS` 包含前端地址
2. 重启后端服务

## 📊 开发工具推荐

### VS Code 扩展

**后端开发**:
- Python
- Pylance
- Python Debugger

**前端开发**:
- ES7+ React/Redux/React-Native snippets
- TypeScript Importer
- Prettier - Code formatter
- ESLint

### 数据库工具

- **pgAdmin 4**: PostgreSQL 图形化管理工具
- **DBeaver**: 通用数据库管理工具
- **TablePlus**: 现代化数据库管理工具

## 🔄 热重载说明

### 后端热重载

- ✅ 已启用 `--reload` 参数
- 修改 Python 代码会自动重启服务
- 无需手动重启

### 前端热重载

- ✅ Vite 默认支持 HMR（热模块替换）
- 修改代码浏览器自动刷新
- 保持应用状态

## 🎓 调试技巧

### 后端调试

**在代码中添加断点**:
```python
import pdb; pdb.set_trace()
```

**查看日志**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 前端调试

**浏览器开发者工具**:
- F12 打开开发者工具
- Console 查看日志
- Network 查看 API 请求
- React DevTools 扩展

**在代码中添加日志**:
```typescript
console.log('Debug:', data);
console.error('Error:', error);
```

## 🚀 生产环境部署

开发完成后，推荐使用 Docker Compose 部署：

```bash
# 停止开发服务
# 使用 Docker Compose 部署
docker-compose up -d --build
```

## 📝 快速启动脚本

### Windows (start-dev.bat)

创建 `start-dev.bat` 文件：

```batch
@echo off
echo Starting Backend...
start cmd /k "cd backend && venv\Scripts\activate && uvicorn app.main:app --reload"

timeout /t 3

echo Starting Frontend...
start cmd /k "cd frontend && npm run dev"

echo Services started!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
```

### Linux/Mac (start-dev.sh)

创建 `start-dev.sh` 文件：

```bash
#!/bin/bash

echo "Starting Backend..."
cd backend
source venv/bin/activate
uvicorn app.main:app --reload &
BACKEND_PID=$!

sleep 3

echo "Starting Frontend..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "Services started!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

# 等待用户中断
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
```

```bash
# 添加执行权限
chmod +x start-dev.sh

# 运行
./start-dev.sh
```

## ✅ 检查清单

启动前检查：

- [ ] PostgreSQL 服务正在运行
- [ ] 数据库 `chatai` 已创建
- [ ] 后端 `.env` 文件已配置
- [ ] Python 虚拟环境已创建
- [ ] 后端依赖已安装
- [ ] 前端依赖已安装
- [ ] 至少配置一个 AI API 密钥

启动后验证：

- [ ] 后端：http://localhost:8000/health 返回正常
- [ ] 后端：http://localhost:8000/docs 可访问
- [ ] 前端：http://localhost:3000 可访问
- [ ] 可以注册新用户
- [ ] 可以创建对话
- [ ] 可以发送消息并收到响应

## 🎉 开始开发

现在你已经成功启动了前后端开发环境！

- 🔥 代码热重载已启用
- 🐛 可以使用调试工具
- 📝 可以查看详细日志
- ⚡ 享受快速开发体验

祝开发愉快！🚀

