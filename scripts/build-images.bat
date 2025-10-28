@echo off
REM Docker 镜像构建脚本 (Windows)
REM 用于构建和推送 Docker 镜像到镜像仓库

setlocal enabledelayedexpansion

REM 配置
set VERSION=%1
if "%VERSION%"=="" set VERSION=latest

set REGISTRY=%2
set PROJECT_NAME=chatai

echo ======================================
echo Docker 镜像构建脚本
echo ======================================
echo 版本: %VERSION%
if not "%REGISTRY%"=="" (
    echo 镜像仓库: %REGISTRY%
)
echo ======================================
echo.

REM 构建后端镜像
echo [INFO] 构建后端镜像...
if not "%REGISTRY%"=="" (
    set BACKEND_IMAGE=%REGISTRY%/%PROJECT_NAME%-backend:%VERSION%
) else (
    set BACKEND_IMAGE=%PROJECT_NAME%-backend:%VERSION%
)

docker build -t "%BACKEND_IMAGE%" -f backend/Dockerfile backend
if errorlevel 1 (
    echo [ERROR] 后端镜像构建失败
    exit /b 1
)

REM 打 latest 标签
if not "%VERSION%"=="latest" (
    if not "%REGISTRY%"=="" (
        docker tag "%BACKEND_IMAGE%" "%REGISTRY%/%PROJECT_NAME%-backend:latest"
    ) else (
        docker tag "%BACKEND_IMAGE%" "%PROJECT_NAME%-backend:latest"
    )
)

echo [INFO] 后端镜像构建完成: %BACKEND_IMAGE%
echo.

REM 构建前端镜像
echo [INFO] 构建前端镜像...
if not "%REGISTRY%"=="" (
    set FRONTEND_IMAGE=%REGISTRY%/%PROJECT_NAME%-frontend:%VERSION%
) else (
    set FRONTEND_IMAGE=%PROJECT_NAME%-frontend:%VERSION%
)

docker build -t "%FRONTEND_IMAGE%" -f frontend/Dockerfile frontend
if errorlevel 1 (
    echo [ERROR] 前端镜像构建失败
    exit /b 1
)

REM 打 latest 标签
if not "%VERSION%"=="latest" (
    if not "%REGISTRY%"=="" (
        docker tag "%FRONTEND_IMAGE%" "%REGISTRY%/%PROJECT_NAME%-frontend:latest"
    ) else (
        docker tag "%FRONTEND_IMAGE%" "%PROJECT_NAME%-frontend:latest"
    )
)

echo [INFO] 前端镜像构建完成: %FRONTEND_IMAGE%
echo.

echo [INFO] 所有镜像构建完成！
echo.

REM 推送镜像
if not "%REGISTRY%"=="" (
    set /p PUSH="是否推送镜像到仓库? (Y/N): "
    if /i "!PUSH!"=="Y" (
        echo.
        echo [INFO] 推送后端镜像...
        docker push "%REGISTRY%/%PROJECT_NAME%-backend:%VERSION%"
        if not "%VERSION%"=="latest" (
            docker push "%REGISTRY%/%PROJECT_NAME%-backend:latest"
        )
        
        echo [INFO] 推送前端镜像...
        docker push "%REGISTRY%/%PROJECT_NAME%-frontend:%VERSION%"
        if not "%VERSION%"=="latest" (
            docker push "%REGISTRY%/%PROJECT_NAME%-frontend:latest"
        )
        
        echo [INFO] 所有镜像推送完成！
    )
)

echo.
echo 完成！
pause

