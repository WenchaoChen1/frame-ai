"""
应用启动类
负责初始化和配置 FastAPI 应用
"""
import logging
import time
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Optional

from app.core.config import settings
from app.core.database import Base, engine
from app.core.logger import get_logger
# 延迟导入：路由模块在注册时才加载，避免启动时加载所有依赖
# from app.routers import auth, conversations, messages, providers, users, login_audit, robots, database_config, knowledge_bases
# from app.playground.product_rag import router as product_rag_router
from app.swagger import swagger_config, tags_metadata

# 获取logger实例
logger = get_logger(__name__)


async def preload_ai_modules():
    """
    后台预加载 AI 模块
    在应用启动后异步执行，不阻塞启动流程
    """
    try:
        logger.info("🔥 开始后台预热 AI 模块...")
        preload_start = time.time()
        
        # 预加载 RAG Agent
        logger.info("  📦 预加载 RAG Agent...")
        rag_start = time.time()
        from app.ai.agent.rag_agent import create_rag_agent
        logger.info(f"  ✅ RAG Agent 预加载完成 - 耗时: {time.time() - rag_start:.3f}秒")
        
        # 预加载 Text-to-SQL Agent
        logger.info("  📦 预加载 Text-to-SQL Agent...")
        sql_start = time.time()
        from app.ai.agent.text_to_sql_agent import text_to_sql_agent
        logger.info(f"  ✅ Text-to-SQL Agent 预加载完成 - 耗时: {time.time() - sql_start:.3f}秒")
        
        # 预加载 RetrievalService
        logger.info("  📦 预加载 RetrievalService...")
        retrieval_start = time.time()
        from app.ai.retrievers import RetrievalService
        logger.info(f"  ✅ RetrievalService 预加载完成 - 耗时: {time.time() - retrieval_start:.3f}秒")
        
        total_preload_time = time.time() - preload_start
        logger.info("=" * 60)
        logger.info(f"🎉 AI 模块预热完成！总耗时: {total_preload_time:.3f}秒")
        logger.info("💡 提示：现在使用 AI 功能将无延迟")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ AI 模块预热失败: {e}")
        logger.warning("⚠️ 将在首次使用时按需加载")


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
            startup_start = time.time()
            logger.info("=" * 60)
            logger.info("⏰ 应用启动中...")
            logger.info("=" * 60)
            
            # 数据库初始化计时
            db_start = time.time()
            self._init_database()
            db_time = time.time() - db_start
            logger.info(f"✅ 数据库初始化完成 - 耗时: {db_time:.3f}秒")
            
            # 总启动时间
            total_startup_time = time.time() - startup_start
            logger.info("=" * 60)
            logger.info(f"🚀 应用启动完成！总耗时: {total_startup_time:.3f}秒")
            logger.info("=" * 60)
            
            # 启动后台预热任务（不阻塞应用启动）
            if settings.LAZY_LOAD_AI_MODULES:
                logger.info("🔧 启动后台 AI 模块预热任务...")
                asyncio.create_task(preload_ai_modules())
            else:
                logger.info("💡 LAZY_LOAD_AI_MODULES=False，跳过预热")
            
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
            logger.info("  📊 开始检查数据库表...")
            db_check_start = time.time()
            Base.metadata.create_all(bind=engine)
            db_check_time = time.time() - db_check_start
            logger.info(f"  ✅ 数据库表检查完成 - 耗时: {db_check_time:.3f}秒")
        except Exception as e:
            logger.error(f"❌ 数据库初始化失败: {str(e)}")
            raise
    
    def _setup_middleware(self):
        """配置中间件"""
        if self.app is None:
            raise RuntimeError("应用未初始化，请先调用 initialize()")
        
        logger.info("  🔧 配置 CORS 中间件...")
        middleware_start = time.time()
        
        # 配置 CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins_list,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        middleware_time = time.time() - middleware_start
        logger.info(f"  ✅ CORS 中间件配置完成 - 耗时: {middleware_time:.3f}秒")
    
    def _register_routers(self):
        """注册路由"""
        if self.app is None:
            raise RuntimeError("应用未初始化，请先调用 initialize()")
        
        logger.info("  🚦 注册业务路由...")
        router_start = time.time()
        
        # 延迟导入：在注册时才加载路由模块，避免启动时加载所有依赖
        logger.info("  📦 导入路由模块...")
        import_start = time.time()
        from app.routers import (
            auth, conversations, messages, providers, 
            users, login_audit, robots, database_config, knowledge_bases
        )
        from app.playground.product_rag import router as product_rag_router
        import_time = time.time() - import_start
        logger.info(f"  ✅ 路由模块导入完成 - 耗时: {import_time:.3f}秒")
        
        # 注册各个模块的路由
        logger.info("  📌 注册路由端点...")
        register_start = time.time()
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
        register_time = time.time() - register_start
        logger.info(f"  ✅ 路由端点注册完成 - 耗时: {register_time:.3f}秒")
        
        router_time = time.time() - router_start
        logger.info(f"  ✅ 路由注册完成 (10个路由) - 耗时: {router_time:.3f}秒")
    
    def _register_system_routes(self):
        """注册系统路由"""
        if self.app is None:
            raise RuntimeError("应用未初始化，请先调用 initialize()")
        
        logger.info("  🏠 注册系统路由...")
        system_router_start = time.time()
        
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
        
        system_router_time = time.time() - system_router_start
        logger.info(f"  ✅ 系统路由注册完成 - 耗时: {system_router_time:.3f}秒")
    
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
        
        init_start = time.time()
        logger.info("=" * 60)
        logger.info("🔧 开始初始化应用...")
        logger.info("=" * 60)
        
        # 创建应用
        logger.info("📦 步骤 1/4: 创建 FastAPI 实例...")
        app_start = time.time()
        self.app = self._create_app()
        app_time = time.time() - app_start
        logger.info(f"✅ FastAPI 实例创建完成 - 耗时: {app_time:.3f}秒")
        logger.info("")
        
        # 配置中间件
        logger.info("📦 步骤 2/4: 配置中间件...")
        middleware_total_start = time.time()
        self._setup_middleware()
        middleware_total_time = time.time() - middleware_total_start
        logger.info(f"✅ 中间件配置完成 - 总耗时: {middleware_total_time:.3f}秒")
        logger.info("")
        
        # 注册路由
        logger.info("📦 步骤 3/4: 注册业务路由...")
        router_total_start = time.time()
        self._register_routers()
        router_total_time = time.time() - router_total_start
        logger.info(f"✅ 业务路由注册完成 - 总耗时: {router_total_time:.3f}秒")
        logger.info("")
        
        # 注册系统路由
        logger.info("📦 步骤 4/4: 注册系统路由...")
        system_total_start = time.time()
        self._register_system_routes()
        system_total_time = time.time() - system_total_start
        logger.info(f"✅ 系统路由注册完成 - 总耗时: {system_total_time:.3f}秒")
        logger.info("")
        
        self._initialized = True
        total_init_time = time.time() - init_start
        logger.info("=" * 60)
        logger.info(f"🎉 应用初始化完成！总耗时: {total_init_time:.3f}秒")
        logger.info("=" * 60)
        
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

