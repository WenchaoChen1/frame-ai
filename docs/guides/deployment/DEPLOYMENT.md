# 部署指南

本文档提供详细的部署说明和生产环境配置建议。

## 生产环境部署

### 1. 服务器要求

- **操作系统**: Linux (Ubuntu 20.04+ 推荐)
- **内存**: 最低 2GB，推荐 4GB+
- **存储**: 最低 10GB，推荐 20GB+
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

### 2. 安全配置

#### 修改默认密码

编辑 `docker-compose.yml`：

```yaml
environment:
  # 修改数据库密码
  POSTGRES_PASSWORD: your-strong-password-here
  
  # 修改JWT密钥
  SECRET_KEY: your-random-secret-key-here
```

生成强密码的方法：

```bash
# 生成随机密钥
openssl rand -hex 32
```

#### 配置HTTPS

生产环境建议使用HTTPS。可以使用以下方案：

1. **使用Nginx反向代理 + Let's Encrypt**

创建 `nginx-proxy.conf`：

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

2. **使用Cloudflare**

如果域名托管在Cloudflare，可以直接启用Cloudflare的SSL/TLS功能。

### 3. 环境变量配置

创建生产环境的 `.env` 文件：

```env
# AI Provider API Keys
OPENAI_API_KEY=sk-your-real-openai-key
ANTHROPIC_API_KEY=sk-ant-your-real-anthropic-key
OLLAMA_BASE_URL=http://ollama-server:11434

# Database
POSTGRES_DB=chatai
POSTGRES_USER=chatai_user
POSTGRES_PASSWORD=your-strong-db-password

# Backend Security
SECRET_KEY=your-generated-secret-key-from-openssl
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# CORS (添加你的域名)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 4. 数据备份

#### 备份PostgreSQL数据库

```bash
# 手动备份
docker-compose exec db pg_dump -U postgres chatai > backup_$(date +%Y%m%d).sql

# 恢复备份
docker-compose exec -T db psql -U postgres chatai < backup_20231215.sql
```

#### 自动备份脚本

创建 `backup.sh`：

```bash
#!/bin/bash
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="chatai_backup_$DATE.sql"

docker-compose exec -T db pg_dump -U postgres chatai > "$BACKUP_DIR/$FILENAME"

# 保留最近7天的备份
find "$BACKUP_DIR" -name "chatai_backup_*.sql" -mtime +7 -delete

echo "Backup completed: $FILENAME"
```

添加到crontab（每天凌晨2点备份）：

```bash
crontab -e
0 2 * * * /path/to/backup.sh
```

### 5. 性能优化

#### PostgreSQL优化

编辑 `docker-compose.yml`，添加PostgreSQL配置：

```yaml
db:
  image: postgres:15-alpine
  command:
    - "postgres"
    - "-c"
    - "shared_buffers=256MB"
    - "-c"
    - "max_connections=200"
    - "-c"
    - "effective_cache_size=1GB"
```

#### 后端优化

增加uvicorn worker数量：

```yaml
backend:
  command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 6. 监控和日志

#### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

#### 日志轮转

编辑 `docker-compose.yml`，添加日志配置：

```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 7. 更新部署

```bash
# 拉取最新代码
git pull

# 重新构建并启动服务
docker-compose up -d --build

# 查看服务状态
docker-compose ps
```

### 8. 健康检查

访问以下端点检查服务状态：

- 后端健康检查: `http://your-domain/api/health`
- 数据库连接测试: 检查后端日志

### 9. 故障排查

#### 服务无法启动

```bash
# 查看服务状态
docker-compose ps

# 查看详细日志
docker-compose logs backend
docker-compose logs db
```

#### 数据库连接失败

```bash
# 进入数据库容器
docker-compose exec db psql -U postgres chatai

# 测试连接
docker-compose exec backend python -c "from app.core.database import engine; print(engine.connect())"
```

#### 重置所有服务

```bash
# 停止并删除所有容器和数据
docker-compose down -v

# 重新启动
docker-compose up -d
```

## 本地开发环境

### 快速启动

```bash
# 安装依赖
cd backend && pip install -r requirements.txt
cd ../frontend && npm install

# 启动数据库
docker-compose up -d db

# 启动后端
cd backend
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/chatai"
uvicorn app.main:app --reload

# 启动前端
cd frontend
npm run dev
```

### 开发环境变量

创建 `backend/.env.dev`：

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/chatai
SECRET_KEY=dev-secret-key-not-for-production
OPENAI_API_KEY=your-dev-key
ANTHROPIC_API_KEY=your-dev-key
OLLAMA_BASE_URL=http://localhost:11434
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## Docker镜像构建

### 构建自定义镜像

```bash
# 构建后端镜像
docker build -t chatai-backend:latest ./backend

# 构建前端镜像
docker build -t chatai-frontend:latest ./frontend

# 推送到私有仓库
docker tag chatai-backend:latest your-registry/chatai-backend:latest
docker push your-registry/chatai-backend:latest
```

### 使用私有镜像

修改 `docker-compose.yml`：

```yaml
services:
  backend:
    image: your-registry/chatai-backend:latest
    # 移除 build: ./backend

  frontend:
    image: your-registry/chatai-frontend:latest
    # 移除 build: ./frontend
```

## 性能基准

推荐配置下的性能指标：

- **并发用户**: 100+
- **响应时间**: < 200ms (不含AI响应)
- **AI流式响应延迟**: < 1s (首字节)
- **数据库查询**: < 50ms

## 安全建议

1. ✅ 使用强密码和随机密钥
2. ✅ 启用HTTPS
3. ✅ 定期备份数据
4. ✅ 限制API访问频率
5. ✅ 更新依赖包
6. ✅ 监控异常访问
7. ✅ 使用防火墙限制端口访问
8. ✅ 定期审计日志

## 扩展性

### 水平扩展

可以通过增加backend服务实例来扩展：

```yaml
backend:
  deploy:
    replicas: 3
```

### 负载均衡

使用Nginx或HAProxy作为负载均衡器：

```nginx
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    location /api {
        proxy_pass http://backend;
    }
}
```

## 支持

遇到问题？

1. 查看 [README.md](./README.md) 中的常见问题
2. 查看 [Issues](https://github.com/your-repo/issues)
3. 提交新的Issue

