from typing import AsyncGenerator, List, Dict
from anthropic import AsyncAnthropic
from .ai_provider import AIProvider
from ...core.config import settings


class ClaudeService(AIProvider):
    """Anthropic Claude服务"""
    
    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY) if settings.ANTHROPIC_API_KEY else None
    
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        model: str = "claude-3-sonnet-20240229",
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式聊天响应"""
        if not self.client:
            raise ValueError("Anthropic API密钥未配置")
        
        # 提取系统消息
        system_message = ""
        formatted_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                formatted_messages.append(msg)
        
        # 如果没有系统消息，使用默认的
        if not system_message:
            system_message = "You are a helpful assistant."
        
        async with self.client.messages.stream(
            model=model,
            messages=formatted_messages,
            system=system_message,
            max_tokens=4096,
            **kwargs
        ) as stream:
            async for text in stream.text_stream:
                yield text
    
    def get_available_models(self) -> List[str]:
        """获取可用的模型列表"""
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-3-5-sonnet-20241022"
        ]
    
    def is_available(self) -> bool:
        """检查服务是否可用"""
        # 始终返回 True，即使没有配置 API key，也显示在列表中
        # 实际使用时如果没有 API key 会报错提示用户配置
        return True

