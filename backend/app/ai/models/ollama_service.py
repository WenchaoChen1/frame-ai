from typing import AsyncGenerator, List, Dict
import httpx

from .ai_provider import AIProvider
from app.core.config import settings


class OllamaService(AIProvider):
    """Ollama本地模型服务"""
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
    
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        model: str = "llama2",
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式聊天响应"""
        url = f"{self.base_url}/api/chat"
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                async with client.stream(
                    "POST",
                    url,
                    json={
                        "model": model,
                        "messages": messages,
                        "stream": True
                    }
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.strip():
                            import json
                            data = json.loads(line)
                            if "message" in data and "content" in data["message"]:
                                yield data["message"]["content"]
            except httpx.RequestError as e:
                raise ValueError(f"无法连接到Ollama服务: {str(e)}")
    
    async def get_available_models_async(self) -> List[str]:
        """异步获取可用的模型列表"""
        url = f"{self.base_url}/api/tags"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
            except httpx.RequestError:
                return []
    
    def get_available_models(self) -> List[str]:
        """获取可用的模型列表（同步版本，返回常见模型）"""
        return [
            "llama2",
            "llama3",
            "mistral",
            "mixtral",
            "codellama",
            "qwen",
            "gemma"
        ]
    
    def is_available(self) -> bool:
        """检查服务是否可用（同步版本，仅检查配置）"""
        # 简单检查配置是否存在，避免在同步上下文中进行异步调用
        return self.base_url is not None and self.base_url != ""
    
    async def is_available_async(self) -> bool:
        """异步检查服务是否真正可用"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except:
            return False

