from typing import AsyncGenerator, List, Dict
from .openai_service import OpenAIService
from .claude_service import ClaudeService
from .ollama_service import OllamaService


class AIManager:
    """AI服务管理器"""
    
    def __init__(self):
        self.providers = {
            "openai": OpenAIService(),
            "claude": ClaudeService(),
            "ollama": OllamaService()
        }
    
    async def chat_stream(
        self,
        provider: str,
        messages: List[Dict[str, str]],
        model: str,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式聊天响应"""
        if provider not in self.providers:
            raise ValueError(f"不支持的AI提供商: {provider}")
        
        service = self.providers[provider]
        async for chunk in service.chat_stream(messages, model, **kwargs):
            yield chunk
    
    def get_available_providers(self) -> Dict[str, List[str]]:
        """获取所有可用的提供商和模型"""
        result = {}
        for name, service in self.providers.items():
            # 检查服务是否可用
            if hasattr(service, 'is_available') and callable(service.is_available):
                try:
                    if not service.is_available():
                        continue
                except Exception:
                    # 如果检查失败，跳过该服务
                    continue
            
            result[name] = service.get_available_models()
        
        return result


# 全局AI管理器实例
ai_manager = AIManager()

