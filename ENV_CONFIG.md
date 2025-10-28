# 前端环境变量配置说明

## 概述

本项目使用环境变量来配置前端应用，支持开发和生产两种模式。

## 文件说明

1. **项目根目录 `.env.example`** - Docker Compose 环境变量模板
2. **`frontend/.env.example`** - 前端 Vite 环境变量模板
3. **`frontend/.env`** - 本地开发环境变量（不提交到 Git）

## 快速开始

### 1. 本地开发（不使用 Docker）

复制并配置前端环境变量：
```bash
cd frontend
cp .env.example .env
```

默认配置已经可以直接使用：
```bash
npm run dev
```

访问: http://localhost:9101

### 2. Docker 开发环境

复制根目录的环境变量文件：
```bash
cp .env.example .env
```

启动开发环境：
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

访问: http://localhost:3000

### 3. Docker 生产环境

复制并编辑环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件，设置生产环境的配置
```

构建并启动：
```bash
docker-compose up --build
```

访问: http://localhost

## 环境变量说明

### 前端 Vite 环境变量（frontend/.env）

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `VITE_PORT` | 9101 | 开发服务器端口 |
| `VITE_HOST` | 0.0.0.0 | 开发服务器监听地址 |
| `VITE_API_PROXY_TARGET` | http://localhost:8000 | API 代理目标（开发模式） |
| `VITE_API_URL` | 空 | API URL（生产模式，留空使用相对路径） |

### Docker Compose 环境变量（根目录 .env）

#### 前端相关
- `FRONTEND_PORT` - 前端服务端口（默认: 80）
- `VITE_API_URL` - 生产构建时的 API URL（留空使用相对路径）
- `VITE_PORT` - Vite 开发服务器端口（默认: 9101）
- `VITE_HOST` - Vite 开发服务器地址（默认: 0.0.0.0）
- `VITE_DEV_PORT` - 开发容器映射到宿主机的端口（默认: 3000）
- `VITE_API_PROXY_TARGET` - 开发模式 API 代理（默认: http://localhost:8000）

#### 后端相关
- `BACKEND_PORT` - 后端服务端口（默认: 8000）
- `POSTGRES_DB` - 数据库名称
- `POSTGRES_USER` - 数据库用户名
- `POSTGRES_PASSWORD` - 数据库密码
- `SECRET_KEY` - JWT 密钥
- `OPENAI_API_KEY` - OpenAI API 密钥
- 等等...

## 工作原理

### 开发模式
1. Vite 从 `frontend/.env` 读取环境变量
2. 使用代理将 `/api` 请求转发到后端
3. 代码支持热重载

### 生产模式
1. Docker 构建时从根目录 `.env` 读取变量
2. 通过 `docker-compose.yml` 的 `build.args` 传递给 Dockerfile
3. Vite 构建时将环境变量编译到静态文件中
4. Nginx 提供静态文件服务，API 请求通过相对路径访问

## 注意事项

1. **不要提交 `.env` 文件到 Git**（已在 .gitignore 中配置）
2. **生产环境必须修改默认密钥**（SECRET_KEY 等）
3. **Vite 环境变量必须以 `VITE_` 开头**才能在客户端代码中使用
4. **生产环境建议使用相对路径**（VITE_API_URL 留空）
5. **开发环境使用代理避免 CORS 问题**

## 故障排除

### 环境变量不生效
1. 确认变量名以 `VITE_` 开头
2. 修改 `.env` 后需要重启开发服务器
3. Docker 环境需要重新构建：`docker-compose up --build`

### API 请求失败
1. 检查 `VITE_API_PROXY_TARGET` 配置是否正确
2. 确认后端服务是否正常运行
3. 查看浏览器控制台的网络请求

### Docker 构建失败
1. 确认根目录 `.env` 文件存在
2. 检查环境变量格式是否正确
3. 尝试清理并重新构建：`docker-compose down -v && docker-compose up --build`

