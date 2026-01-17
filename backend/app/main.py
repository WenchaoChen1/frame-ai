"""
应用主入口
使用启动类初始化应用
"""
import time
import sys
import io

# 设置 stdout 编码为 utf-8，避免 Windows 上的编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 记录模块导入开始时间
_import_start = time.time()
print(f"⏱️  开始导入应用模块...", flush=True)

from app.application import create_app, application

_import_time = time.time() - _import_start
print(f"✅ 模块导入完成 - 耗时: {_import_time:.3f}秒", flush=True)

# 创建应用实例
# 方式1: 直接使用 create_app 函数
print(f"⏱️  开始创建应用实例...", flush=True)
_app_create_start = time.time()
app = create_app()
_app_create_time = time.time() - _app_create_start
print(f"✅ 应用实例创建完成 - 耗时: {_app_create_time:.3f}秒", flush=True)

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
        reload=False,
        log_config=log_config,  # 使用自定义日志配置
        access_log=True
    )
