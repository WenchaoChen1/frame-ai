#!/bin/bash

echo "==================================="
echo "  启动前端服务 (React + Vite)"
echo "==================================="
echo ""

# 检查 node_modules 是否存在
if [ ! -d "node_modules" ]; then
    echo "📦 依赖未安装，正在安装..."
    echo ""
    npm install
    if [ $? -ne 0 ]; then
        echo ""
        echo "❌ 依赖安装失败"
        exit 1
    fi
    echo "✅ 依赖安装成功"
    echo ""
fi

echo "🚀 启动前端服务..."
echo ""
echo "访问地址:"
echo "  - 前端应用: http://localhost:3000"
echo "  - 或: http://localhost:5173"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 启动服务
npm run dev

