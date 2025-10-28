# Docker 部署指南

本项目使用 Docker 和 Docker Compose 进行容器化部署，包含前端、后端和数据库服务。

## 目录结构

```
.
├── backend/
│   ├── Dockerfile              # 后端 Docker 镜像构建文件
│   └── .dockerignore          # 后端 Docker 忽略文件
├── frontend/
│   ├── Dockerfile              # 前端 Docker 镜像构建文件
│   └── .dockerignore          # 前端 Docker 忽略文件
├── docker-compose.yml          # Docker Compose 配置文件
└── .env.example               # 环境变量示例文件
```

## 快速开始

### 1. 准备环境变量

复制环境变量示例文件并根据实际情况修改：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置必要的环境变量：

```bash
# 必须修改的配置
SECRET_KEY=your-very-long-random-secret-key-here
POSTGRES_PASSWORD=your-secure-password

# 如果使用 AI 功能，配置 API 密钥
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### 2. 启动所有服务

使用 Docker Compose 启动所有服务（不包括 Elasticsearch）：

```bash
docker-compose up -d
```

启动所有服务（包括 Elasticsearch）：

```bash
docker-compose --profile full up -d
```

### 3. 查看服务状态

```bash
docker-compose ps
```

### 4. 查看日志

查看所有服务日志：

```bash
docker-compose logs -f
```

查看特定服务日志：

```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### 5. 停止服务

```bash
docker-compose down
```

停止服务并删除数据卷：

```bash
docker-compose down -v
```

## 服务说明

### 数据库 (PostgreSQL)

- **容器名称**: `chatai-db`
- **端口**: `5432:5432`
- **默认配置**:
  - 数据库名: `chatai`
  - 用户名: `postgres`
  - 密码: `postgres`（生产环境请修改）
- **数据持久化**: 使用 Docker volume `postgres_data`

### 后端 (FastAPI)

- **容器名称**: `chatai-backend`
- **端口**: `8000:8000`
- **功能**:
  - RESTful API 服务
  - AI 对话功能
  - 数据库交互
  - 知识库管理
- **健康检查**: `http://localhost:8000/api/health`

### 前端 (React + Nginx)

- **容器名称**: `chatai-frontend`
- **端口**: `80:80`
- **功能**:
  - Web UI 界面
  - API 代理到后端
  - 静态资源服务
- **访问地址**: `http://localhost`

### Elasticsearch (可选)

- **容器名称**: `chatai-elasticsearch`
- **端口**: `9200:9200`
- **功能**: RAG 向量检索
- **启动方式**: 使用 `--profile full` 参数

## 构建镜像

### 构建所有镜像

```bash
docker-compose build
```

### 构建特定服务镜像

```bash
docker-compose build backend
docker-compose build frontend
```

### 使用镜像标签

```bash
docker-compose build --build-arg VERSION=1.0.0
```

## 数据库初始化

首次启动时，数据库会自动初始化。如果需要手动运行迁移：

```bash
# 进入后端容器
docker-compose exec backend bash

# 运行数据库迁移
python -m alembic upgrade head
```

## 生产环境部署建议

### 1. 安全配置

- 修改默认密码和密钥
- 使用 HTTPS（配置 SSL 证书）
- 限制数据库端口访问（不暴露 5432 端口）
- 配置防火墙规则

### 2. 性能优化

修改 `backend/Dockerfile` 中的 workers 数量：

```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 3. 资源限制

在 `docker-compose.yml` 中添加资源限制：

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### 4. 日志管理

配置日志驱动：

```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 5. 备份策略

备份数据库：

```bash
# 备份
docker-compose exec db pg_dump -U postgres chatai > backup.sql

# 恢复
docker-compose exec -T db psql -U postgres chatai < backup.sql
```

## 开发模式

如果在开发模式下需要热重载，可以取消 `docker-compose.yml` 中的卷挂载注释：

```yaml
backend:
  volumes:
    - ./backend:/app
```

## 故障排查

### 容器无法启动

```bash
# 查看容器日志
docker-compose logs backend

# 检查容器状态
docker-compose ps

# 重新构建镜像
docker-compose build --no-cache backend
```

### 数据库连接失败

```bash
# 检查数据库是否就绪
docker-compose exec db pg_isready -U postgres

# 查看数据库日志
docker-compose logs db
```

### 端口被占用

修改 `.env` 文件中的端口配置：

```bash
BACKEND_PORT=8001
FRONTEND_PORT=8080
```

## 监控和维护

### 查看资源使用情况

```bash
docker stats
```

### 清理未使用的资源

```bash
# 清理未使用的容器、网络、镜像
docker system prune -a

# 清理未使用的卷
docker volume prune
```

## 常用命令

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f

# 进入容器
docker-compose exec backend bash
docker-compose exec frontend sh

# 重新构建并启动
docker-compose up -d --build

# 查看服务状态
docker-compose ps

# 更新镜像
docker-compose pull
```

## 环境变量说明

### 数据库相关

- `POSTGRES_DB`: 数据库名称
- `POSTGRES_USER`: 数据库用户名
- `POSTGRES_PASSWORD`: 数据库密码

### 应用相关

- `SECRET_KEY`: JWT 密钥（必须修改）
- `ALGORITHM`: 加密算法（默认 HS256）
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token 过期时间

### AI 模型相关

- `OPENAI_API_KEY`: OpenAI API 密钥
- `OPENAI_API_BASE`: OpenAI API 地址
- `ANTHROPIC_API_KEY`: Anthropic API 密钥
- `OLLAMA_BASE_URL`: Ollama 服务地址

### 其他配置

- `CORS_ORIGINS`: CORS 允许的源
- `ENVIRONMENT`: 运行环境（development/production）
- `LOG_LEVEL`: 日志级别（DEBUG/INFO/WARNING/ERROR）

## 技术支持

如果遇到问题，请查看：

1. 容器日志: `docker-compose logs -f`
2. 应用文档: `docs/`
3. GitHub Issues

## 更新日志

- 2024-01-01: 初始版本，支持基础的前后端容器化部署
- 添加 Elasticsearch 可选服务支持
- 优化 Dockerfile 和 docker-compose 配置

