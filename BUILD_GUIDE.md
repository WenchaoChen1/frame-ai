# 构建和部署指南

本文档详细说明如何构建 Docker 镜像并部署到生产环境。

## 📋 目录

- [镜像构建](#镜像构建)
- [推送到镜像仓库](#推送到镜像仓库)
- [生产环境部署](#生产环境部署)
- [CI/CD 集成](#cicd-集成)

## 🏗️ 镜像构建

### 方式一：使用 Docker Compose（推荐）

```bash
# 构建所有镜像
docker-compose build

# 构建特定服务
docker-compose build backend
docker-compose build frontend

# 不使用缓存构建
docker-compose build --no-cache
```

### 方式二：使用构建脚本

**Linux/Mac:**
```bash
# 构建 latest 版本
./scripts/build-images.sh

# 构建指定版本
./scripts/build-images.sh -v 1.0.0

# 构建并推送到镜像仓库
./scripts/build-images.sh -v 1.0.0 -r registry.example.com -p
```

**Windows:**
```cmd
REM 构建 latest 版本
.\scripts\build-images.bat

REM 构建指定版本
.\scripts\build-images.bat 1.0.0

REM 构建并推送到镜像仓库
.\scripts\build-images.bat 1.0.0 registry.example.com
```

### 方式三：手动构建

```bash
# 构建后端镜像
cd backend
docker build -t chatai-backend:latest .

# 构建前端镜像
cd frontend
docker build -t chatai-frontend:latest .
```

## 📦 镜像说明

### 后端镜像 (chatai-backend)

**基础镜像**: `python:3.11-slim`

**特性**:
- 安装了必要的系统依赖（gcc, g++, libpq-dev）
- 使用非 root 用户运行（appuser）
- 包含健康检查
- 支持多 worker 模式

**环境变量**:
- `DATABASE_URL`: 数据库连接地址
- `SECRET_KEY`: JWT 密钥
- `OPENAI_API_KEY`: OpenAI API 密钥
- 更多见 `.env.example`

### 前端镜像 (chatai-frontend)

**基础镜像**: `node:18-alpine` (构建) + `nginx:alpine` (运行)

**特性**:
- 多阶段构建，最终镜像体积小
- 使用 Nginx 提供静态文件服务
- 包含 API 代理配置
- 支持 SPA 路由
- 包含健康检查

**Nginx 配置**:
- Gzip 压缩
- 静态资源缓存
- API 代理到后端
- SSE 支持

## 🚀 推送到镜像仓库

### 配置镜像仓库

在构建脚本中设置环境变量：

```bash
export REGISTRY="registry.example.com"
export VERSION="1.0.0"
```

或在 `docker-compose.yml` 中配置：

```yaml
services:
  backend:
    image: registry.example.com/chatai-backend:1.0.0
    build:
      context: ./backend
      dockerfile: Dockerfile
```

### 登录镜像仓库

```bash
# Docker Hub
docker login

# 私有镜像仓库
docker login registry.example.com
```

### 推送镜像

```bash
# 标记镜像
docker tag chatai-backend:latest registry.example.com/chatai-backend:1.0.0
docker tag chatai-frontend:latest registry.example.com/chatai-frontend:1.0.0

# 推送镜像
docker push registry.example.com/chatai-backend:1.0.0
docker push registry.example.com/chatai-frontend:1.0.0
```

## 🌐 生产环境部署

### 1. 准备服务器

**系统要求**:
- Linux 服务器（推荐 Ubuntu 20.04+）
- Docker 20.10+
- Docker Compose 2.0+
- 至少 2GB 内存
- 至少 20GB 磁盘空间

**安装 Docker**:
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

**安装 Docker Compose**:
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. 部署应用

**克隆代码或拉取镜像**:
```bash
# 方式一：从代码构建
git clone <repository-url>
cd fangying-ai

# 方式二：直接使用镜像（修改 docker-compose.yml）
# 将 build 改为 image
```

**配置环境变量**:
```bash
cp .env.example .env
nano .env  # 编辑配置
```

**关键配置**:
```bash
# 必须修改的配置
SECRET_KEY=使用随机生成的长字符串
POSTGRES_PASSWORD=使用强密码
OPENAI_API_KEY=你的OpenAI密钥

# 端口配置（可选）
BACKEND_PORT=8000
FRONTEND_PORT=80
```

**启动服务**:
```bash
docker-compose up -d
```

### 3. 配置 Nginx 反向代理（可选但推荐）

在服务器上安装 Nginx 并配置 HTTPS：

```nginx
# /etc/nginx/sites-available/chatai
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        
        # SSE 支持
        proxy_buffering off;
        proxy_cache off;
    }
}
```

### 4. 配置 SSL 证书（推荐使用 Let's Encrypt）

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### 5. 设置自动重启

创建 systemd 服务：

```bash
# /etc/systemd/system/chatai.service
[Unit]
Description=ChatAI Docker Compose
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/fangying-ai
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

启用服务：
```bash
sudo systemctl enable chatai
sudo systemctl start chatai
```

## 🔄 CI/CD 集成

### GitHub Actions 示例

创建 `.github/workflows/docker-build.yml`:

```yaml
name: Build and Push Docker Images

on:
  push:
    branches: [ main, master ]
    tags: [ 'v*' ]

env:
  REGISTRY: ghcr.io
  IMAGE_PREFIX: ${{ github.repository }}

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Log in to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata (tags, labels)
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}

      - name: Build and push Backend
        uses: docker/build-push-action@v4
        with:
          context: ./backend
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}-backend:latest
          cache-from: type=registry,ref=${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}-backend:buildcache
          cache-to: type=registry,ref=${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}-backend:buildcache,mode=max

      - name: Build and push Frontend
        uses: docker/build-push-action@v4
        with:
          context: ./frontend
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}-frontend:latest
          cache-from: type=registry,ref=${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}-frontend:buildcache
          cache-to: type=registry,ref=${{ env.REGISTRY }}/${{ env.IMAGE_PREFIX }}-frontend:buildcache,mode=max
```

### GitLab CI 示例

创建 `.gitlab-ci.yml`:

```yaml
stages:
  - build
  - deploy

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: "/certs"

build-backend:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t $CI_REGISTRY_IMAGE/backend:$CI_COMMIT_REF_NAME ./backend
    - docker push $CI_REGISTRY_IMAGE/backend:$CI_COMMIT_REF_NAME

build-frontend:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t $CI_REGISTRY_IMAGE/frontend:$CI_COMMIT_REF_NAME ./frontend
    - docker push $CI_REGISTRY_IMAGE/frontend:$CI_COMMIT_REF_NAME

deploy:
  stage: deploy
  only:
    - main
  script:
    - ssh user@server "cd /path/to/app && docker-compose pull && docker-compose up -d"
```

## 📊 监控和日志

### 日志收集

使用 Docker 日志驱动：

```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

或集成外部日志系统（如 ELK、Loki）。

### 监控指标

推荐使用 Prometheus + Grafana 进行监控。

## 🔐 安全最佳实践

1. **使用非 root 用户运行容器**（已在 Dockerfile 中配置）
2. **定期更新基础镜像**
3. **扫描镜像漏洞**：使用 `docker scan` 或 Trivy
4. **限制容器资源**：设置 CPU 和内存限制
5. **使用 secrets 管理敏感信息**
6. **启用容器只读文件系统**（可选）
7. **配置网络隔离**

## 📝 版本管理

推荐使用语义化版本：

- `major.minor.patch` (例如: 1.0.0)
- `latest` 标签指向最新稳定版本
- `dev` 标签用于开发版本

## 🆘 故障排查

查看构建日志：
```bash
docker-compose build --progress=plain
```

查看容器日志：
```bash
docker-compose logs -f backend
```

进入容器调试：
```bash
docker-compose exec backend bash
```

## 📚 参考资料

- [Docker 官方文档](https://docs.docker.com/)
- [Docker Compose 文档](https://docs.docker.com/compose/)
- [Nginx 配置指南](https://nginx.org/en/docs/)
- [Let's Encrypt 文档](https://letsencrypt.org/docs/)

