# Docker 快速启动指南

本指南帮助您快速启动项目的 Docker 环境。

## 🚀 快速启动（推荐）

### Windows 用户

双击运行启动脚本：
```bash
start.bat
```

或在命令行中运行：
```cmd
.\start.bat
```

### Linux/Mac 用户

```bash
chmod +x start.sh
./start.sh
```

## 📦 手动启动步骤

### 1. 准备环境变量（首次使用）

如果没有 `.env` 文件，脚本会自动创建。或者手动复制：

```bash
# Linux/Mac
cp .env.example .env

# Windows
copy .env.example .env
```

然后编辑 `.env` 文件，配置必要的参数（特别是 API 密钥）。

### 2. 构建镜像

```bash
docker-compose build
```

### 3. 启动服务

**基础服务（前端 + 后端 + 数据库）：**
```bash
docker-compose up -d
```

**完整服务（包括 Elasticsearch）：**
```bash
docker-compose --profile full up -d
```

### 4. 检查服务状态

```bash
docker-compose ps
```

### 5. 访问服务

- **前端界面**: http://localhost
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

## 🛠️ 使用 Makefile（推荐）

如果系统支持 `make` 命令，可以使用更简单的方式：

```bash
# 查看所有可用命令
make help

# 构建镜像
make build

# 启动服务
make up

# 查看日志
make logs

# 停止服务
make down

# 进入后端容器
make shell-backend

# 备份数据库
make db-backup
```

## 📝 常用命令

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart backend
```

### 停止服务

```bash
# 停止服务（保留数据）
docker-compose down

# 停止服务并删除数据卷
docker-compose down -v
```

### 进入容器

```bash
# 进入后端容器
docker-compose exec backend bash

# 进入前端容器
docker-compose exec frontend sh

# 进入数据库容器
docker-compose exec db psql -U postgres -d chatai
```

## 🔧 开发模式

如果需要代码热重载，使用开发配置：

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

或使用 Makefile：
```bash
make dev
```

开发模式下：
- 前端运行在 http://localhost:3000
- 后端运行在 http://localhost:8000
- 代码修改会自动重载

## 📊 监控和维护

### 查看资源使用

```bash
docker stats
```

### 健康检查

```bash
# 检查后端健康
curl http://localhost:8000/api/health

# 检查数据库
docker-compose exec db pg_isready -U postgres
```

### 备份数据库

```bash
# 使用 Makefile
make db-backup

# 或手动备份
docker-compose exec -T db pg_dump -U postgres chatai > backup.sql
```

### 恢复数据库

```bash
# 使用 Makefile
make db-restore FILE=backup.sql

# 或手动恢复
docker-compose exec -T db psql -U postgres chatai < backup.sql
```

## 🐛 故障排查

### 端口被占用

修改 `.env` 文件中的端口：
```bash
BACKEND_PORT=8001
FRONTEND_PORT=8080
```

### 镜像构建失败

清理并重新构建：
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 服务无法启动

查看详细日志：
```bash
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db
```

### 数据库连接失败

确保数据库已启动并就绪：
```bash
docker-compose ps
docker-compose logs db
```

### 清理 Docker 资源

```bash
# 清理所有未使用的容器、网络、镜像
docker system prune -a

# 清理未使用的卷
docker volume prune
```

## 🔐 生产环境配置

在生产环境部署前，请务必：

1. **修改默认密码和密钥**
   ```bash
   SECRET_KEY=使用长随机字符串
   POSTGRES_PASSWORD=使用强密码
   ```

2. **配置 HTTPS**（推荐使用 Nginx 反向代理 + Let's Encrypt）

3. **限制数据库端口访问**
   - 注释掉 `docker-compose.yml` 中数据库的 `ports` 配置
   - 数据库仅在内部网络访问

4. **配置日志轮转**
   ```yaml
   logging:
     driver: "json-file"
     options:
       max-size: "10m"
       max-file: "3"
   ```

5. **增加资源限制**
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '2'
         memory: 2G
   ```

## 📚 更多信息

详细部署文档请参考：[DOCKER_DEPLOYMENT.md](./DOCKER_DEPLOYMENT.md)

## 🆘 需要帮助？

如果遇到问题：
1. 查看日志：`docker-compose logs -f`
2. 检查服务状态：`docker-compose ps`
3. 查看文档：`docs/` 目录
4. 提交 Issue 到 GitHub

## 🎯 下一步

服务启动后，您可以：
1. 访问前端界面进行注册登录
2. 在后端配置 AI 模型
3. 创建知识库
4. 开始使用 AI 对话功能

祝您使用愉快！🎉

