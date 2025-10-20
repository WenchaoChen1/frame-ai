from abc import ABC, abstractmethod
from typing import AsyncGenerator, List, Dict


class AIProvider(ABC):
    """AI提供商抽象基类"""
    
    @abstractmethod
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        model: str,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式聊天响应"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """获取可用的模型列表"""
        pass

