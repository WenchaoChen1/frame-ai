"""
应用主入口
使用启动类初始化应用
"""
from app.application import create_app, application


# 创建应用实例
# 方式1: 直接使用 create_app 函数
app = create_app()

# 方式2: 通过启动类的 get_app 方法
# app = application.get_app()

# 导出 app 实例供 uvicorn 使用
__all__ = ["app"]

if __name__ == "__main__":
    # 方便在开发模式下直接运行：
    # - 命令行: python -m app.main  (需在包含 app 的目录下执行)
    # - PyCharm: Run/Debug 使用 "Module name: app.main"
    import uvicorn
    from app.core.logger import LoggerConfig
    
    # 使用统一的日志配置
    log_config = LoggerConfig.get_uvicorn_log_config()

    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_config=log_config,  # 使用自定义日志配置
        access_log=True
    )
