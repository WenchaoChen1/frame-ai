@echo off
echo ========================================
echo 启动 RAG 智能体应用
echo ========================================
echo.

echo 激活虚拟环境...
call venv\Scripts\activate.bat

echo.
echo 启动应用...
echo 访问 http://localhost:8000/docs 查看 API 文档
echo 按 Ctrl+C 停止应用
echo.

python -m app.main

