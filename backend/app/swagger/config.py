"""
Swagger/OpenAPI 文档配置

集中管理API文档的所有配置信息，包括：
- API基本信息（标题、描述、版本等）
- 标签分类
- 联系信息和许可证
"""

# API基本信息配置
swagger_config = {
    "title": "AI聊天对话系统 API",
    "description": """
## AI聊天对话系统

一个功能完整的AI聊天对话系统，支持多个AI提供商。

### 功能特性

* **多AI提供商**: OpenAI GPT、Anthropic Claude、Ollama本地模型
* **用户认证**: JWT token认证
* **会话管理**: 创建、查询、删除会话
* **流式响应**: 实时流式显示AI响应
* **Stop功能**: 随时停止AI生成 ⭐新增
* **消息持久化**: 所有对话历史保存到数据库

### 使用方法

1. 注册账号或登录获取 token
2. 点击右上角 **Authorize** 按钮
3. 输入 `Bearer <your_token>`
4. 开始测试API

### 技术栈

* FastAPI 0.104.1
* PostgreSQL 15
* SQLAlchemy 2.0
* OpenAI SDK
* Anthropic SDK

### API文档

* **Swagger UI**: `/docs` - 交互式API文档
* **ReDoc**: `/redoc` - 美观的API文档
    """,
    "version": "1.1.0",
    "docs_url": "/docs",
    "redoc_url": "/redoc",
    "contact": {
        "name": "AI Chat System",
        "url": "https://github.com/yourusername/fangying-ai",
    },
    "license_info": {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    }
}

# API标签分类配置
tags_metadata = [
    {
        "name": "认证",
        "description": "用户注册、登录和认证相关接口"
    },
    {
        "name": "会话",
        "description": "会话的创建、查询、更新和删除"
    },
    {
        "name": "消息",
        "description": "消息发送、查询和流式响应（支持停止功能）"
    },
    {
        "name": "AI提供商",
        "description": "获取可用的AI提供商和模型列表"
    },
    {
        "name": "系统",
        "description": "系统健康检查和基本信息"
    }
]

