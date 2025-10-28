#!/bin/bash

# Docker 镜像构建脚本
# 用于构建和推送 Docker 镜像到镜像仓库

set -e

# 配置
VERSION=${VERSION:-"latest"}
REGISTRY=${REGISTRY:-""}  # 例如: registry.example.com
PROJECT_NAME="chatai"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# 构建镜像
build_image() {
    local service=$1
    local dockerfile=$2
    local context=$3
    
    log_info "构建 ${service} 镜像..."
    
    if [ -n "$REGISTRY" ]; then
        IMAGE_NAME="${REGISTRY}/${PROJECT_NAME}-${service}:${VERSION}"
    else
        IMAGE_NAME="${PROJECT_NAME}-${service}:${VERSION}"
    fi
    
    docker build -t "${IMAGE_NAME}" -f "${dockerfile}" "${context}"
    
    # 同时打 latest 标签
    if [ "$VERSION" != "latest" ]; then
        if [ -n "$REGISTRY" ]; then
            docker tag "${IMAGE_NAME}" "${REGISTRY}/${PROJECT_NAME}-${service}:latest"
        else
            docker tag "${IMAGE_NAME}" "${PROJECT_NAME}-${service}:latest"
        fi
    fi
    
    log_info "${service} 镜像构建完成: ${IMAGE_NAME}"
}

# 推送镜像
push_image() {
    local service=$1
    
    if [ -z "$REGISTRY" ]; then
        log_warn "未配置镜像仓库地址，跳过推送"
        return
    fi
    
    log_info "推送 ${service} 镜像到仓库..."
    
    docker push "${REGISTRY}/${PROJECT_NAME}-${service}:${VERSION}"
    
    if [ "$VERSION" != "latest" ]; then
        docker push "${REGISTRY}/${PROJECT_NAME}-${service}:latest"
    fi
    
    log_info "${service} 镜像推送完成"
}

# 主函数
main() {
    log_info "开始构建 Docker 镜像..."
    log_info "版本: ${VERSION}"
    
    # 构建后端镜像
    build_image "backend" "./backend/Dockerfile" "./backend"
    
    # 构建前端镜像
    build_image "frontend" "./frontend/Dockerfile" "./frontend"
    
    log_info "所有镜像构建完成！"
    
    # 如果配置了镜像仓库，询问是否推送
    if [ -n "$REGISTRY" ]; then
        read -p "是否推送镜像到仓库? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            push_image "backend"
            push_image "frontend"
            log_info "所有镜像推送完成！"
        fi
    fi
}

# 显示帮助信息
show_help() {
    cat << EOF
Docker 镜像构建脚本

用法:
    ./build-images.sh [选项]

选项:
    -h, --help              显示帮助信息
    -v, --version VERSION   指定镜像版本 (默认: latest)
    -r, --registry URL      指定镜像仓库地址
    -p, --push              构建后自动推送

示例:
    # 构建 latest 版本
    ./build-images.sh

    # 构建指定版本
    ./build-images.sh -v 1.0.0

    # 构建并推送到镜像仓库
    ./build-images.sh -v 1.0.0 -r registry.example.com -p

环境变量:
    VERSION     镜像版本
    REGISTRY    镜像仓库地址

EOF
}

# 解析命令行参数
AUTO_PUSH=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        -r|--registry)
            REGISTRY="$2"
            shift 2
            ;;
        -p|--push)
            AUTO_PUSH=true
            shift
            ;;
        *)
            log_error "未知参数: $1"
            show_help
            exit 1
            ;;
    esac
done

# 执行主函数
main

# 自动推送（如果指定了 -p 参数）
if [ "$AUTO_PUSH" = true ] && [ -n "$REGISTRY" ]; then
    push_image "backend"
    push_image "frontend"
    log_info "所有镜像推送完成！"
fi

