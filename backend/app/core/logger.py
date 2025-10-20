"""
统一的日志配置中心
所有模块应该从这里获取logger实例
"""
import logging
import sys
from typing import Optional


class LoggerConfig:
    """日志配置管理器"""
    
    _initialized = False
    _loggers = {}
    
    # 统一的日志格式
    DEFAULT_FORMAT = '%(asctime)s - [%(levelname)s] - %(name)s - %(message)s'
    
    @classmethod
    def setup(cls, level: int = logging.DEBUG, format_string: Optional[str] = None):
        """
        初始化日志配置
        
        Args:
            level: 日志级别，默认DEBUG（显示所有级别日志）
            format_string: 自定义日志格式
        """
        if cls._initialized:
            return
        
        # 默认日志格式
        if format_string is None:
            format_string = cls.DEFAULT_FORMAT
        
        # 配置根日志器
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        
        # 移除所有现有的handlers（避免重复输出）
        # for handler in root_logger.handlers[:]:
        #     root_logger.removeHandler(handler)
        
        # 创建控制台handler - 确保输出到stdout
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        # 设置格式
        formatter = logging.Formatter(format_string)
        console_handler.setFormatter(formatter)
        
        # 添加handler到根日志器
        root_logger.addHandler(console_handler)
        
        # 设置第三方库的日志级别（避免过多输出）
        # 注意：这些设置可能会被uvicorn的log_config覆盖
        logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
        logging.getLogger('uvicorn.error').setLevel(logging.DEBUG)
        
        # 确保stdout不被缓冲
        sys.stdout.flush()
        
        cls._initialized = True
        logging.info("=" * 60)
        logging.info("✅ 日志系统初始化完成")
        logging.info(f"📊 日志级别: {logging.getLevelName(level)}")
        logging.info(f"📝 日志格式: {format_string}")
        logging.info(f"💡 提示: 使用 logger.info/debug/warning/error 输出日志")
        logging.info(f"💡 提示: print需要添加 flush=True 确保立即输出")
        logging.info("=" * 60)
        sys.stdout.flush()
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        获取指定名称的logger实例
        
        Args:
            name: logger名称，通常使用 __name__
            
        Returns:
            logging.Logger: logger实例
        """
        if not cls._initialized:
            cls.setup()
        
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            cls._loggers[name] = logger
        
        return cls._loggers[name]
    
    @classmethod
    def get_uvicorn_log_config(cls) -> dict:
        """
        生成 Uvicorn 服务器的日志配置字典
        
        该方法返回一个符合 Python logging dictConfig 格式的配置字典，用于配置 Uvicorn 的日志行为。
        主要功能：
        1. 使用统一的日志格式（与应用程序日志格式保持一致）
        2. 将所有日志输出到标准输出（stdout）
        3. 配置 uvicorn 和 uvicorn.access 日志记录器的级别和处理器
        4. 禁用清除现有日志记录器，以保留应用程序自定义的日志配置
        
        配置说明：
        - formatters.default: 使用类的 DEFAULT_FORMAT 格式化日志消息
        - formatters.access: HTTP 访问日志专用格式，突出显示客户端地址、请求行和状态码
        - handlers.default: 将日志输出到 sys.stdout，使用 default 格式化器
        - handlers.access: 将 HTTP 访问日志输出到 sys.stdout，使用 access 格式化器
        - loggers.uvicorn: Uvicorn 主日志器，级别为 INFO，不向上传播
        - loggers.uvicorn.error: Uvicorn 错误日志器，级别为 INFO，使用 default 处理器
        - loggers.uvicorn.access: HTTP 访问日志器，级别为 INFO，使用 access 处理器记录所有请求
        
        Returns:
            dict: 符合 Python logging.config.dictConfig 规范的配置字典
            
        Example:
            uvicorn.run(
                app,
                host="0.0.0.0",
                port=8000,
                log_config=LoggerConfig.get_uvicorn_log_config()
            )
        """
        return {
            "version": 1,
            "disable_existing_loggers": False,  # 保留自定义的 logger
            "formatters": {
                "default": {
                    "format": cls.DEFAULT_FORMAT,
                },
                "access": {
                    # HTTP 访问日志专用格式：更简洁，突出请求信息
                    "format": cls.DEFAULT_FORMAT,
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
                "access": {
                    "formatter": "access",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "loggers": {
                "uvicorn": {
                    "handlers": ["default"],
                    "level": "INFO",
                    "propagate": False,
                },
                "uvicorn.error": {
                    "handlers": ["default"],
                    "level": "INFO",
                    "propagate": False,
                },
                "uvicorn.access": {
                    "handlers": ["access"],  # 使用专门的访问日志处理器
                    "level": "DEBUG",
                    "propagate": False,
                },
            },
        }


# 便捷函数
def get_logger(name: str) -> logging.Logger:
    """
    获取logger实例的便捷函数
    
    Usage:
        from app.core.logger import get_logger
        logger = get_logger(__name__)
        logger.info("这是一条日志")
    
    Args:
        name: logger名称，通常使用 __name__
        
    Returns:
        logging.Logger: logger实例
    """
    return LoggerConfig.get_logger(name)


# 在模块导入时初始化日志配置
LoggerConfig.setup()

