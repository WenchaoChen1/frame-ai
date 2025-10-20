@echo off
chcp 65001 >nul
echo ===================================
echo   启动前端服务 (React + Vite)
echo ===================================
echo.

REM 检查 node_modules 是否存在
if not exist "node_modules\" (
    echo 📦 依赖未安装，正在安装...
    echo.
    
    REM 尝试设置执行策略（可能需要管理员权限）
    powershell -Command "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process" 2>nul
    
    call npm install
    if errorlevel 1 (
        echo.
        echo ❌ 依赖安装失败
        echo.
        echo 💡 如果遇到执行策略错误，请使用管理员权限运行 PowerShell:
        echo    Set-ExecutionPolicy RemoteSigned
        echo.
        echo 或者使用 CMD 运行此脚本
        pause
        exit /b 1
    )
    echo ✅ 依赖安装成功
    echo.
)

echo 🚀 启动前端服务...
echo.
echo 访问地址:
echo   - 前端应用: http://localhost:3000
echo   - 或: http://localhost:5173
echo.
echo 按 Ctrl+C 停止服务
echo.

REM 启动服务
call npm run dev

