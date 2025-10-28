#!/bin/bash

# 环境变量配置验证脚本
# 用于验证前端环境变量是否正确配置

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

echo -e "${CYAN}================================================${NC}"
echo -e "${CYAN}  前端环境变量配置验证脚本${NC}"
echo -e "${CYAN}================================================${NC}"
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$ROOT_DIR/frontend"

# 检查项目目录
if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}❌ 错误: 找不到 frontend 目录${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 项目目录: $ROOT_DIR${NC}"
echo ""

# 1. 检查 .env.example 文件
echo -e "${YELLOW}1. 检查 .env.example 文件...${NC}"
if [ -f "$FRONTEND_DIR/.env.example" ]; then
    echo -e "  ${GREEN}✅ frontend/.env.example 存在${NC}"
else
    echo -e "  ${RED}❌ frontend/.env.example 不存在${NC}"
fi

if [ -f "$ROOT_DIR/.env.example" ]; then
    echo -e "  ${GREEN}✅ 根目录/.env.example 存在${NC}"
else
    echo -e "  ${RED}❌ 根目录/.env.example 不存在${NC}"
fi
echo ""

# 2. 检查 .env 文件
echo -e "${YELLOW}2. 检查 .env 文件...${NC}"
if [ -f "$FRONTEND_DIR/.env" ]; then
    echo -e "  ${GREEN}✅ frontend/.env 存在${NC}"
    echo -e "  ${CYAN}📄 内容预览:${NC}"
    while IFS= read -r line; do
        echo -e "     ${GRAY}$line${NC}"
    done < "$FRONTEND_DIR/.env"
else
    echo -e "  ${YELLOW}⚠️  frontend/.env 不存在（本地开发需要）${NC}"
    echo -e "     运行: cd frontend && cp .env.example .env"
fi
echo ""

if [ -f "$ROOT_DIR/.env" ]; then
    echo -e "  ${GREEN}✅ 根目录/.env 存在（Docker 环境需要）${NC}"
else
    echo -e "  ${YELLOW}⚠️  根目录/.env 不存在（Docker 环境需要）${NC}"
    echo -e "     运行: cp .env.example .env"
fi
echo ""

# 3. 检查 vite.config.ts
echo -e "${YELLOW}3. 检查 vite.config.ts 配置...${NC}"
if [ -f "$FRONTEND_DIR/vite.config.ts" ]; then
    if grep -q "loadEnv" "$FRONTEND_DIR/vite.config.ts"; then
        echo -e "  ${GREEN}✅ vite.config.ts 已配置环境变量加载${NC}"
    else
        echo -e "  ${RED}❌ vite.config.ts 未配置 loadEnv${NC}"
    fi
else
    echo -e "  ${RED}❌ vite.config.ts 不存在${NC}"
fi
echo ""

# 4. 检查 Dockerfile
echo -e "${YELLOW}4. 检查 Dockerfile 配置...${NC}"
if [ -f "$FRONTEND_DIR/Dockerfile" ]; then
    if grep -q "ARG VITE_API_URL" "$FRONTEND_DIR/Dockerfile"; then
        echo -e "  ${GREEN}✅ Dockerfile 已配置构建参数${NC}"
    else
        echo -e "  ${RED}❌ Dockerfile 未配置 ARG${NC}"
    fi
else
    echo -e "  ${RED}❌ Dockerfile 不存在${NC}"
fi
echo ""

# 5. 检查 docker-compose.yml
echo -e "${YELLOW}5. 检查 docker-compose.yml 配置...${NC}"
if [ -f "$ROOT_DIR/docker-compose.yml" ]; then
    if grep -q "args:" "$ROOT_DIR/docker-compose.yml"; then
        echo -e "  ${GREEN}✅ docker-compose.yml 已配置 build args${NC}"
    else
        echo -e "  ${RED}❌ docker-compose.yml 未配置 build args${NC}"
    fi
else
    echo -e "  ${RED}❌ docker-compose.yml 不存在${NC}"
fi
echo ""

# 6. 检查端口占用
echo -e "${YELLOW}6. 检查端口占用...${NC}"
for port in 9101 8000 80; do
    if command -v lsof &> /dev/null; then
        if lsof -i :$port &> /dev/null; then
            echo -e "  ${YELLOW}⚠️  端口 $port 已被占用${NC}"
            lsof -i :$port | tail -n +2 | awk '{print "     进程: " $1 " (PID: " $2 ")"}'
        else
            echo -e "  ${GREEN}✅ 端口 $port 可用${NC}"
        fi
    elif command -v netstat &> /dev/null; then
        if netstat -tuln | grep -q ":$port "; then
            echo -e "  ${YELLOW}⚠️  端口 $port 已被占用${NC}"
        else
            echo -e "  ${GREEN}✅ 端口 $port 可用${NC}"
        fi
    else
        echo -e "  ${GRAY}⊗ 无法检查端口 $port（需要 lsof 或 netstat）${NC}"
    fi
done
echo ""

# 7. 检查 Node.js 和 npm
echo -e "${YELLOW}7. 检查开发环境...${NC}"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "  ${GREEN}✅ Node.js: $NODE_VERSION${NC}"
else
    echo -e "  ${RED}❌ Node.js 未安装${NC}"
fi

if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo -e "  ${GREEN}✅ npm: $NPM_VERSION${NC}"
else
    echo -e "  ${RED}❌ npm 未安装${NC}"
fi
echo ""

# 总结
echo -e "${CYAN}================================================${NC}"
echo -e "${CYAN}  验证完成${NC}"
echo -e "${CYAN}================================================${NC}"
echo ""
echo -e "${CYAN}📖 快速开始指南:${NC}"
echo ""
echo -e "1. 本地开发:"
echo -e "   ${GRAY}cd frontend${NC}"
echo -e "   ${GRAY}cp .env.example .env${NC}"
echo -e "   ${GRAY}npm install${NC}"
echo -e "   ${GRAY}npm run dev${NC}"
echo ""
echo -e "2. Docker 环境:"
echo -e "   ${GRAY}cp .env.example .env${NC}"
echo -e "   ${GRAY}docker-compose up --build${NC}"
echo ""
echo -e "${CYAN}📚 详细文档: frontend/ENV_SETUP.md${NC}"
echo ""

