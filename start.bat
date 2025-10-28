@echo off
REM ChatAI 快速启动脚本 (Windows)
REM 用于快速启动和管理 Docker 服务

setlocal enabledelayedexpansion

REM 颜色显示（Windows 10+）
echo.
echo =======================================
echo        ChatAI Docker 启动脚本
echo =======================================
echo.

REM 检查 Docker 是否安装
echo [STEP] 检查 Docker 环境...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker 未安装，请先安装 Docker
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose 未安装，请先安装 Docker Compose
    pause
    exit /b 1
)

echo [INFO] Docker 环境检查通过
echo.

REM 检查 .env 文件
echo [STEP] 检查环境变量配置...
if not exist .env (
    echo [WARN] .env 文件不存在，正在创建...
    
    (
        echo # 数据库配置
        echo POSTGRES_DB=chatai
        echo POSTGRES_USER=postgres
        echo POSTGRES_PASSWORD=postgres
        echo.
        echo # 端口配置
        echo BACKEND_PORT=8000
        echo FRONTEND_PORT=80
        echo.
        echo # 安全配置（生产环境必须修改）
        echo SECRET_KEY=change-this-to-a-random-secret-key-in-production
        echo ALGORITHM=HS256
        echo ACCESS_TOKEN_EXPIRE_MINUTES=10080
        echo.
        echo # OpenAI 配置
        echo OPENAI_API_KEY=
        echo OPENAI_API_BASE=https://api.openai.com/v1
        echo.
        echo # Anthropic 配置
        echo ANTHROPIC_API_KEY=
        echo.
        echo # Ollama 配置
        echo OLLAMA_BASE_URL=http://host.docker.internal:11434
        echo.
        echo # Elasticsearch 配置
        echo ELASTICSEARCH_URL=http://elasticsearch:9200
        echo.
        echo # CORS 配置
        echo CORS_ORIGINS=http://localhost:3000,http://localhost:80,http://localhost
        echo.
        echo # 应用配置
        echo ENVIRONMENT=production
        echo LOG_LEVEL=INFO
    ) > .env
    
    echo [INFO] .env 文件已创建，请根据需要修改配置
) else (
    echo [INFO] .env 文件已存在
)
echo.

REM 询问是否构建镜像
set /p BUILD="是否需要构建镜像? (Y/N, 默认: Y): "
if "%BUILD%"=="" set BUILD=Y

if /i "%BUILD%"=="Y" (
    echo.
    echo [STEP] 构建 Docker 镜像...
    docker-compose build
    if errorlevel 1 (
        echo [ERROR] 镜像构建失败
        pause
        exit /b 1
    )
    echo [INFO] 镜像构建完成
)
echo.

REM 询问是否启动 Elasticsearch
set /p ES="是否启动 Elasticsearch (用于 RAG 功能)? (Y/N, 默认: N): "
if "%ES%"=="" set ES=N

echo.
echo [STEP] 启动服务...
if /i "%ES%"=="Y" (
    echo [INFO] 启动所有服务（包括 Elasticsearch）...
    docker-compose --profile full up -d
) else (
    echo [INFO] 启动基础服务...
    docker-compose up -d
)

if errorlevel 1 (
    echo [ERROR] 服务启动失败
    pause
    exit /b 1
)
echo [INFO] 服务启动完成
echo.

REM 等待服务就绪
echo [STEP] 等待服务就绪...
timeout /t 5 /nobreak >nul

REM 显示服务信息
echo.
echo =======================================
echo           服务已启动成功！
echo =======================================
echo.
echo 前端访问地址: http://localhost:80
echo 后端 API 地址: http://localhost:8000
echo API 文档地址: http://localhost:8000/docs
echo.
echo 常用命令:
echo   查看日志: docker-compose logs -f
echo   停止服务: docker-compose down
echo   重启服务: docker-compose restart
echo   查看状态: docker-compose ps
echo.
echo 按任意键查看日志，或关闭窗口...
pause >nul

REM 显示日志
docker-compose logs -f

