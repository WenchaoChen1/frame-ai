from typing import AsyncGenerator, List, Dict
from openai import AsyncOpenAI

from .ai_provider import AIProvider
from app.core.config import settings


class OpenAIService(AIProvider):
    """OpenAI服务"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
    
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式聊天响应"""
        if not self.client:
            raise ValueError("OpenAI API密钥未配置")
        
        stream = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
            **kwargs
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def get_available_models(self) -> List[str]:
        """获取可用的模型列表"""
        return [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
            "o1-preview",
            "o1-mini"
        ]
    
    def is_available(self) -> bool:
        """检查服务是否可用"""
        # 始终返回 True，即使没有配置 API key，也显示在列表中
        # 实际使用时如果没有 API key 会报错提示用户配置
        return True

