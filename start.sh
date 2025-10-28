#!/bin/bash

# ChatAI 快速启动脚本
# 用于快速启动和管理 Docker 服务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 显示欢迎信息
show_welcome() {
    echo -e "${GREEN}"
    cat << "EOF"
╔═══════════════════════════════════════╗
║                                       ║
║        ChatAI Docker 启动脚本         ║
║                                       ║
╚═══════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# 检查 Docker 是否安装
check_docker() {
    log_step "检查 Docker 环境..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    log_info "Docker 环境检查通过"
}

# 检查环境变量文件
check_env_file() {
    log_step "检查环境变量配置..."
    
    if [ ! -f .env ]; then
        log_warn ".env 文件不存在，需要创建"
        
        cat > .env << 'EOF'
# 数据库配置
POSTGRES_DB=chatai
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# 端口配置
BACKEND_PORT=8000
FRONTEND_PORT=80

# 安全配置（生产环境必须修改）
SECRET_KEY=change-this-to-a-random-secret-key-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# OpenAI 配置
OPENAI_API_KEY=
OPENAI_API_BASE=https://api.openai.com/v1

# Anthropic 配置
ANTHROPIC_API_KEY=

# Ollama 配置
OLLAMA_BASE_URL=http://host.docker.internal:11434

# Elasticsearch 配置
ELASTICSEARCH_URL=http://elasticsearch:9200

# CORS 配置
CORS_ORIGINS=http://localhost:3000,http://localhost:80,http://localhost

# 应用配置
ENVIRONMENT=production
LOG_LEVEL=INFO
EOF
        
        log_info ".env 文件已创建，请根据需要修改配置"
    else
        log_info ".env 文件已存在"
    fi
}

# 构建镜像
build_images() {
    log_step "构建 Docker 镜像..."
    docker-compose build
    log_info "镜像构建完成"
}

# 启动服务
start_services() {
    log_step "启动服务..."
    
    if [ "$1" == "full" ]; then
        log_info "启动所有服务（包括 Elasticsearch）..."
        docker-compose --profile full up -d
    else
        log_info "启动基础服务..."
        docker-compose up -d
    fi
    
    log_info "服务启动完成"
}

# 等待服务就绪
wait_for_services() {
    log_step "等待服务就绪..."
    
    local max_attempts=30
    local attempt=0
    
    # 等待数据库
    log_info "等待数据库服务..."
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose exec -T db pg_isready -U postgres &> /dev/null; then
            log_info "数据库服务已就绪"
            break
        fi
        attempt=$((attempt + 1))
        sleep 2
    done
    
    if [ $attempt -eq $max_attempts ]; then
        log_error "数据库服务启动超时"
        return 1
    fi
    
    # 等待后端
    log_info "等待后端服务..."
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://localhost:${BACKEND_PORT:-8000}/api/health &> /dev/null; then
            log_info "后端服务已就绪"
            break
        fi
        attempt=$((attempt + 1))
        sleep 2
    done
    
    if [ $attempt -eq $max_attempts ]; then
        log_warn "后端服务启动超时，请检查日志"
    fi
    
    log_info "所有服务已就绪"
}

# 显示服务信息
show_services_info() {
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════${NC}"
    echo -e "${GREEN}           服务已启动成功！            ${NC}"
    echo -e "${GREEN}═══════════════════════════════════════${NC}"
    echo ""
    echo -e "前端访问地址: ${BLUE}http://localhost:${FRONTEND_PORT:-80}${NC}"
    echo -e "后端 API 地址: ${BLUE}http://localhost:${BACKEND_PORT:-8000}${NC}"
    echo -e "API 文档地址: ${BLUE}http://localhost:${BACKEND_PORT:-8000}/docs${NC}"
    echo ""
    echo -e "常用命令:"
    echo -e "  查看日志: ${YELLOW}docker-compose logs -f${NC}"
    echo -e "  停止服务: ${YELLOW}docker-compose down${NC}"
    echo -e "  重启服务: ${YELLOW}docker-compose restart${NC}"
    echo -e "  查看状态: ${YELLOW}docker-compose ps${NC}"
    echo ""
    echo -e "使用 Makefile 命令:"
    echo -e "  ${YELLOW}make help${NC}  - 查看所有可用命令"
    echo ""
}

# 主函数
main() {
    show_welcome
    
    # 检查环境
    check_docker
    check_env_file
    
    # 询问是否需要构建镜像
    read -p "是否需要构建镜像? (y/n, 默认: y): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        build_images
    fi
    
    # 询问是否启动 Elasticsearch
    read -p "是否启动 Elasticsearch (用于 RAG 功能)? (y/n, 默认: n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        start_services "full"
    else
        start_services
    fi
    
    # 等待服务就绪
    wait_for_services
    
    # 显示服务信息
    show_services_info
}

# 处理脚本参数
case "${1:-}" in
    start)
        main
        ;;
    stop)
        log_info "停止所有服务..."
        docker-compose down
        log_info "服务已停止"
        ;;
    restart)
        log_info "重启所有服务..."
        docker-compose restart
        log_info "服务已重启"
        ;;
    logs)
        docker-compose logs -f
        ;;
    status)
        docker-compose ps
        ;;
    *)
        main
        ;;
esac

