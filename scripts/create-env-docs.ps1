# Create UTF-8 encoded documentation files
# This script ensures all documentation files are created with UTF-8 encoding (without BOM)

$utf8NoBom = New-Object System.Text.UTF8Encoding $false

$envConfigContent = @'
# 前端环境变量配置说明

## 概述

本项目使用环境变量来配置前端应用，支持开发和生产两种模式。

## 文件说明

1. **项目根目录 .env.example** - Docker Compose 环境变量模板
2. **frontend/.env.example** - 前端 Vite 环境变量模板
3. **frontend/.env** - 本地开发环境变量（不提交到 Git）

## 快速开始

### 1. 本地开发（不使用 Docker）

```bash
cd frontend
cp .env.example .env
npm run dev
```

访问: http://localhost:9101

### 2. Docker 开发环境

```bash
cp .env.example .env
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

访问: http://localhost:3000

### 3. Docker 生产环境

```bash
cp .env.example .env
docker-compose up --build
```

访问: http://localhost

## 环境变量说明

### 前端 Vite 环境变量（frontend/.env）

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| VITE_PORT | 9101 | 开发服务器端口 |
| VITE_HOST | 0.0.0.0 | 开发服务器监听地址 |
| VITE_API_PROXY_TARGET | http://localhost:8000 | API 代理目标（开发模式） |
| VITE_API_URL | 空 | API URL（生产模式，留空使用相对路径） |

## 工作原理

### 开发模式
1. Vite 从 frontend/.env 读取环境变量
2. 使用代理将 /api 请求转发到后端
3. 代码支持热重载

### 生产模式
1. Docker 构建时从根目录 .env 读取变量
2. 通过 docker-compose.yml 的 build.args 传递给 Dockerfile
3. Vite 构建时将环境变量编译到静态文件中
4. Nginx 提供静态文件服务，API 请求通过相对路径访问

## 注意事项

1. 不要提交 .env 文件到 Git（已在 .gitignore 中配置）
2. 生产环境必须修改默认密钥（SECRET_KEY 等）
3. Vite 环境变量必须以 VITE_ 开头才能在客户端代码中使用
4. 生产环境建议使用相对路径（VITE_API_URL 留空）
5. 开发环境使用代理避免 CORS 问题

## 故障排除

### 环境变量不生效
1. 确认变量名以 VITE_ 开头
2. 修改 .env 后需要重启开发服务器
3. Docker 环境需要重新构建：docker-compose up --build

### API 请求失败
1. 检查 VITE_API_PROXY_TARGET 配置是否正确
2. 确认后端服务是否正常运行
3. 查看浏览器控制台的网络请求

### Docker 构建失败
1. 确认根目录 .env 文件存在
2. 检查环境变量格式是否正确
3. 尝试清理并重新构建：docker-compose down -v && docker-compose up --build
'@

$frontendFixContent = @'
# 前端环境变量配置修复总结

## 问题描述

前端的 .env 配置没有生效，主要问题包括：
1. 缺少 .env 和 .env.example 文件
2. vite.config.ts 没有读取环境变量
3. robot.ts 使用了未定义的环境变量
4. Docker 构建时没有传递环境变量

## 修复内容

### 1. 创建环境变量文件

#### 根目录 .env.example
包含 Docker Compose 所需的所有环境变量配置

#### frontend/.env.example 和 frontend/.env
包含 Vite 开发服务器所需的环境变量

### 2. 更新 frontend/vite.config.ts

添加 loadEnv 支持，从 .env 文件读取配置

### 3. 更新 frontend/src/services/robot.ts

修正 API_URL 配置为空字符串（使用相对路径）

### 4. 更新 frontend/Dockerfile

添加构建时环境变量支持：
- ARG VITE_API_URL
- ARG VITE_PORT
- ARG VITE_HOST

### 5. 更新 frontend/Dockerfile.dev

添加运行时环境变量

### 6. 更新 docker-compose.yml

添加构建参数传递

### 7. 更新 docker-compose.dev.yml

更新开发环境配置

## 使用方法

### 本地开发

```bash
cd frontend
cp .env.example .env
npm run dev
```

访问：http://localhost:9101

### Docker 开发环境

```bash
cp .env.example .env
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

访问：http://localhost:3000

### Docker 生产环境

```bash
cp .env.example .env
docker-compose up --build
```

访问：http://localhost

## 环境变量说明

### 前端 Vite 变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| VITE_PORT | 9101 | 开发服务器端口 |
| VITE_HOST | 0.0.0.0 | 开发服务器地址 |
| VITE_API_PROXY_TARGET | http://localhost:8000 | API 代理目标（开发） |
| VITE_API_URL | 空 | API URL（生产，留空用相对路径） |

### Docker Compose 前端变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| FRONTEND_PORT | 80 | 前端服务端口 |
| VITE_DEV_PORT | 3000 | 开发容器映射端口 |

## 注意事项

1. 环境变量文件已配置在 .gitignore 和 .dockerignore 中
2. .env.example 文件会包含在 Docker 镜像中
3. 生产环境使用相对路径（VITE_API_URL 留空）
4. 开发环境使用代理避免 CORS 问题
5. 修改环境变量后需要重启服务
6. Docker 环境修改后需要重新构建

## 验证

### 本地开发验证
```bash
cd frontend
npm run dev
# 检查输出中的端口号是否正确
```

### Docker 构建验证
```bash
docker-compose build frontend
docker-compose up frontend
```

### 环境变量验证
在浏览器控制台输入：
```javascript
console.log(import.meta.env)
```

## 相关文档

- **完整配置说明**：ENV_CONFIG.md
- **快速设置指南**：frontend/ENV_SETUP.md
- **验证脚本**：scripts/verify-env.ps1 或 scripts/verify-env.sh
'@

# Write files with UTF-8 encoding (no BOM)
$rootDir = Split-Path -Parent $PSScriptRoot
[System.IO.File]::WriteAllLines((Join-Path $rootDir "ENV_CONFIG.md"), $envConfigContent, $utf8NoBom)
[System.IO.File]::WriteAllLines((Join-Path $rootDir "FRONTEND_ENV_FIX.md"), $frontendFixContent, $utf8NoBom)

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Documentation files created with UTF-8 encoding" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[OK] ENV_CONFIG.md" -ForegroundColor Green
Write-Host "[OK] FRONTEND_ENV_FIX.md" -ForegroundColor Green
Write-Host ""
Write-Host "All files are encoded in UTF-8 (without BOM)" -ForegroundColor Green
Write-Host ""
