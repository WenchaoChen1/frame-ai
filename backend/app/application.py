"""
应用启动类
负责初始化和配置 FastAPI 应用
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Optional

from app.core.config import settings
from app.core.database import Base, engine
from app.core.logger import get_logger
from app.routers import auth, conversations, messages, providers, users, login_audit, robots, database_config, knowledge_bases
from app.playground.product_rag import router as product_rag_router
from app.swagger import swagger_config, tags_metadata

# 获取logger实例
logger = get_logger(__name__)


class Application:
    """
    应用启动类
    
    封装 FastAPI 应用的初始化、配置和启动逻辑
    """
    
    def __init__(self):
        """初始化应用启动器"""
        self.app: Optional[FastAPI] = None
        self._initialized = False
    
    def _create_app(self) -> FastAPI:
        """
        创建 FastAPI 应用实例
        
        Returns:
            FastAPI: 配置好的 FastAPI 应用实例
        """
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            """应用生命周期管理"""
            # 启动时执行
            logger.info("应用启动中...")
            self._init_database()
            logger.info("数据库初始化完成")
            yield
            # 关闭时执行
            logger.info("应用关闭中...")
        
        app = FastAPI(
            title=swagger_config["title"],
            description=swagger_config["description"],
            version=swagger_config["version"],
            docs_url=swagger_config["docs_url"],
            redoc_url=swagger_config["redoc_url"],
            lifespan=lifespan,
            openapi_tags=tags_metadata,
            contact=swagger_config["contact"],
            license_info=swagger_config["license_info"]
        )
        
        logger.info(f"FastAPI 应用创建成功 - 版本: {app.version}")
        return app
    
    def _init_database(self):
        """初始化数据库表"""
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("数据库表创建成功")
        except Exception as e:
            logger.error(f"数据库初始化失败: {str(e)}")
            raise
    
    def _setup_middleware(self):
        """配置中间件"""
        if self.app is None:
            raise RuntimeError("应用未初始化，请先调用 initialize()")
        
        # 配置 CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins_list,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        logger.info(f"CORS 中间件配置完成 - 允许的源: {settings.cors_origins_list}")
    
    def _register_routers(self):
        """注册路由"""
        if self.app is None:
            raise RuntimeError("应用未初始化，请先调用 initialize()")
        
        # 注册各个模块的路由
        self.app.include_router(auth.router)
        self.app.include_router(conversations.router)
        self.app.include_router(messages.router)
        self.app.include_router(providers.router)
        self.app.include_router(users.router)
        self.app.include_router(login_audit.router)
        self.app.include_router(robots.router)
        self.app.include_router(database_config.router)
        self.app.include_router(knowledge_bases.router)
        self.app.include_router(product_rag_router.router)
        
        logger.info("路由注册完成")
    
    def _register_system_routes(self):
        """注册系统路由"""
        if self.app is None:
            raise RuntimeError("应用未初始化，请先调用 initialize()")
        
        @self.app.get("/", tags=["系统"])
        def root():
            """
            API 根路径
            
            返回API基本信息和文档链接。
            """
            # 测试日志输出 - 使用正确的logger实例
            logger.info("✅ 根路径被访问 - logging正常工作")
            
            # 测试print输出 - 需要flush确保立即输出
            print("✅ 根路径被访问 - print正常工作", flush=True)
            
            return {
                "message": "AI聊天对话系统API",
                "version": "1.1.0",
                "docs": "/docs",
                "redoc": "/redoc",
                "features": [
                    "多AI提供商支持（OpenAI、Claude、Ollama）",
                    "流式响应",
                    "Stop停止功能",
                    "会话管理",
                    "用户认证"
                ]
            }
        
        @self.app.get("/health", tags=["系统"])
        def health_check():
            """
            健康检查
            
            检查API服务是否正常运行。
            """
            return {
                "status": "healthy",
                "version": "1.1.0",
                "database": "connected"
            }
        
        logger.info("系统路由注册完成")
    
    def initialize(self) -> FastAPI:
        """
        初始化应用
        
        按照顺序执行：
        1. 创建 FastAPI 实例
        2. 配置中间件
        3. 注册路由
        4. 注册系统路由
        
        Returns:
            FastAPI: 完全配置好的 FastAPI 应用实例
        """
        if self._initialized:
            logger.warning("应用已经初始化，跳过重复初始化")
            return self.app
        
        logger.info("开始初始化应用...")
        
        # 创建应用
        self.app = self._create_app()
        
        # 配置中间件
        self._setup_middleware()
        
        # 注册路由
        self._register_routers()
        
        # 注册系统路由
        self._register_system_routes()
        
        self._initialized = True
        logger.info("应用初始化完成！")
        
        return self.app
    
    def get_app(self) -> FastAPI:
        """
        获取应用实例
        
        如果应用未初始化，会自动进行初始化。
        
        Returns:
            FastAPI: FastAPI 应用实例
        """
        if not self._initialized:
            return self.initialize()
        return self.app


# 创建全局应用实例
application = Application()


def create_app() -> FastAPI:
    """
    创建并返回配置好的 FastAPI 应用
    
    这是应用的主入口函数。
    
    Returns:
        FastAPI: 完全配置好的 FastAPI 应用实例
    
    Example:
        >>> app = create_app()
        >>> # 使用 uvicorn 运行
        >>> # uvicorn app.application:create_app --factory
    """
    return application.initialize()

