# Docker 配置文件总结

本文档总结了项目中所有 Docker 相关的配置文件及其用途。

## 📁 文件清单

### 核心 Docker 配置

#### 1. `docker-compose.yml` ✅ 已优化
主要的 Docker Compose 配置文件，定义了所有服务。

**包含的服务**:
- PostgreSQL 数据库
- Elasticsearch（可选，使用 `--profile full` 启动）
- 后端服务 (FastAPI)
- 前端服务 (React + Nginx)

**主要特性**:
- 环境变量配置支持
- 健康检查
- 依赖关系管理
- 数据持久化
- 网络隔离

#### 2. `docker-compose.dev.yml` ✅ 新建
开发环境的 Docker Compose 配置。

**特性**:
- 代码卷挂载（支持热重载）
- 开发模式启动
- 调试日志级别

**使用方式**:
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### 后端 Docker 配置

#### 3. `backend/Dockerfile` ✅ 已优化
后端服务的 Docker 镜像构建文件。

**优化内容**:
- ✅ 安装必要的系统依赖（gcc, g++, libpq-dev）
- ✅ 创建非 root 用户 (appuser)
- ✅ 添加健康检查
- ✅ 支持多 worker 配置
- ✅ 优化镜像层缓存

**镜像信息**:
- 基础镜像: `python:3.11-slim`
- 暴露端口: 8000
- 运行用户: appuser (UID 1000)

#### 4. `backend/.dockerignore` ✅ 已优化
后端构建时忽略的文件。

**排除内容**:
- Python 缓存文件
- 虚拟环境
- 测试文件
- 文档
- IDE 配置
- 日志文件
- 环境变量文件（.env）

### 前端 Docker 配置

#### 5. `frontend/Dockerfile` ✅ 已优化
前端服务的 Docker 镜像构建文件（多阶段构建）。

**优化内容**:
- ✅ 使用 `npm ci` 替代 `npm install`
- ✅ 多阶段构建（构建阶段 + 运行阶段）
- ✅ 安装 curl 用于健康检查
- ✅ 配置文件权限
- ✅ 添加健康检查

**镜像信息**:
- 构建阶段: `node:18-alpine`
- 运行阶段: `nginx:alpine`
- 暴露端口: 80

#### 6. `frontend/Dockerfile.dev` ✅ 新建
前端开发环境的 Docker 镜像。

**特性**:
- 运行 Vite 开发服务器
- 支持热模块替换 (HMR)
- 端口: 3000

#### 7. `frontend/.dockerignore` ✅ 已优化
前端构建时忽略的文件。

**排除内容**:
- node_modules
- 构建产物 (dist/)
- 测试覆盖率文件
- 文档
- IDE 配置
- 临时文件

#### 8. `frontend/nginx.conf` ✅ 已存在
Nginx 配置文件。

**功能**:
- SPA 路由支持
- API 代理到后端
- Gzip 压缩
- 静态资源缓存
- SSE (Server-Sent Events) 支持

### 根目录配置

#### 9. `.dockerignore` ✅ 新建
根目录的 Docker 忽略文件。

**用途**: 在构建 Docker 上下文时排除不必要的文件。

### 脚本和工具

#### 10. `scripts/build-images.sh` ✅ 新建
Linux/Mac 的镜像构建脚本。

**功能**:
- 构建前后端镜像
- 支持版本标签
- 推送到镜像仓库
- 彩色输出和日志
- 参数化配置

**使用示例**:
```bash
./scripts/build-images.sh -v 1.0.0 -r registry.example.com -p
```

#### 11. `scripts/build-images.bat` ✅ 新建
Windows 的镜像构建脚本。

**功能**: 与 shell 脚本相同，但适配 Windows 环境。

#### 12. `start.sh` ✅ 新建
Linux/Mac 的快速启动脚本。

**功能**:
- 检查 Docker 环境
- 创建 .env 文件
- 构建镜像
- 启动服务
- 等待服务就绪
- 显示访问信息
- 彩色界面

#### 13. `start.bat` ✅ 新建
Windows 的快速启动脚本。

**功能**: 与 shell 脚本相同，但适配 Windows 环境。

#### 14. `Makefile` ✅ 新建
Make 命令集合，简化 Docker 操作。

**可用命令**:
```bash
make help           # 显示帮助
make build          # 构建镜像
make up             # 启动服务
make up-full        # 启动所有服务（含 ES）
make down           # 停止服务
make logs           # 查看日志
make ps             # 查看状态
make clean          # 清理资源
make shell-backend  # 进入后端容器
make db-backup      # 备份数据库
make dev            # 启动开发环境
```

### 文档

#### 15. `DOCKER_DEPLOYMENT.md` ✅ 新建
详细的 Docker 部署文档。

**内容**:
- 服务说明
- 启动步骤
- 常用命令
- 生产环境配置
- 故障排查
- 监控维护
- 环境变量说明

#### 16. `DOCKER_QUICK_START.md` ✅ 新建
快速启动指南。

**内容**:
- 快速启动方法
- 手动启动步骤
- 常用命令速查
- 故障排查
- 开发模式说明

#### 17. `BUILD_GUIDE.md` ✅ 新建
构建和部署指南。

**内容**:
- 镜像构建方法
- 推送到镜像仓库
- 生产环境部署
- CI/CD 集成示例
- 安全最佳实践
- 监控和日志

## 🎯 使用场景

### 场景 1: 快速开始（推荐新手）

**Windows**:
```cmd
.\start.bat
```

**Linux/Mac**:
```bash
./start.sh
```

### 场景 2: 使用 Makefile（推荐开发者）

```bash
make build    # 构建镜像
make up       # 启动服务
make logs     # 查看日志
```

### 场景 3: 使用 Docker Compose（标准方式）

```bash
docker-compose build
docker-compose up -d
docker-compose logs -f
```

### 场景 4: 开发模式

```bash
# 方式一
make dev

# 方式二
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### 场景 5: 生产部署

```bash
# 1. 配置环境变量
cp .env.example .env
nano .env

# 2. 构建镜像
docker-compose build

# 3. 启动服务
docker-compose up -d

# 4. 查看状态
docker-compose ps
```

## 📋 服务端口

| 服务 | 内部端口 | 外部端口 | 说明 |
|------|---------|---------|------|
| 前端 | 80 | 80 (可配置) | Web 界面 |
| 后端 | 8000 | 8000 (可配置) | API 服务 |
| 数据库 | 5432 | 5432 (可关闭) | PostgreSQL |
| Elasticsearch | 9200 | 9200 (可选) | 搜索引擎 |

## 🔧 环境变量

环境变量通过 `.env` 文件配置，关键变量包括：

### 必须配置
- `SECRET_KEY`: JWT 密钥（必须修改）
- `POSTGRES_PASSWORD`: 数据库密码（生产环境必须修改）

### AI 功能
- `OPENAI_API_KEY`: OpenAI API 密钥
- `ANTHROPIC_API_KEY`: Anthropic API 密钥
- `OLLAMA_BASE_URL`: Ollama 服务地址

### 可选配置
- `BACKEND_PORT`: 后端端口（默认 8000）
- `FRONTEND_PORT`: 前端端口（默认 80）
- `LOG_LEVEL`: 日志级别（默认 INFO）

详细说明见 `.env.example` 文件。

## 🚀 部署流程

### 开发环境
1. 克隆代码
2. 运行 `start.sh` 或 `start.bat`
3. 访问 http://localhost

### 测试环境
1. 配置 `.env` 文件
2. 运行 `docker-compose up -d`
3. 运行集成测试

### 生产环境
1. 准备服务器（Linux + Docker）
2. 配置 `.env`（修改密码和密钥）
3. 构建镜像：`docker-compose build`
4. 启动服务：`docker-compose up -d`
5. 配置 Nginx + SSL（推荐）
6. 设置自动重启和监控

详细步骤见 `BUILD_GUIDE.md`。

## 📊 资源需求

### 最小配置
- CPU: 2 核
- 内存: 2GB
- 磁盘: 20GB

### 推荐配置
- CPU: 4 核
- 内存: 4GB
- 磁盘: 50GB

### 生产环境
- CPU: 8 核
- 内存: 8GB
- 磁盘: 100GB (含 Elasticsearch)

## 🔒 安全检查清单

在生产环境部署前，请确保：

- [ ] 修改了 `SECRET_KEY`
- [ ] 修改了 `POSTGRES_PASSWORD`
- [ ] 配置了 HTTPS (SSL)
- [ ] 关闭了数据库的外部端口访问
- [ ] 配置了防火墙规则
- [ ] 设置了日志轮转
- [ ] 配置了资源限制
- [ ] 设置了自动备份
- [ ] 配置了监控告警
- [ ] 更新了 CORS 配置

## 📚 相关文档

- [DOCKER_QUICK_START.md](./DOCKER_QUICK_START.md) - 快速启动指南
- [DOCKER_DEPLOYMENT.md](./DOCKER_DEPLOYMENT.md) - 详细部署文档
- [BUILD_GUIDE.md](./BUILD_GUIDE.md) - 构建和部署指南
- [README.md](./README.md) - 项目总览

## 🆘 获取帮助

如果遇到问题：
1. 查看快速启动指南: `DOCKER_QUICK_START.md`
2. 查看详细文档: `DOCKER_DEPLOYMENT.md`
3. 查看日志: `docker-compose logs -f`
4. 检查服务状态: `docker-compose ps`
5. 提交 Issue

## ✅ 完成状态

所有 Docker 配置文件已完成并优化：

- ✅ Docker Compose 配置（生产 + 开发）
- ✅ Dockerfile（前端 + 后端）
- ✅ .dockerignore 文件
- ✅ 构建脚本（Linux + Windows）
- ✅ 启动脚本（Linux + Windows）
- ✅ Makefile 工具集
- ✅ 完整文档

您现在可以：
- 使用 `start.sh` 或 `start.bat` 快速启动
- 使用 `make` 命令管理服务
- 部署到生产环境

祝您使用愉快！🎉

