"""
文档加载器基类
"""
from abc import ABC, abstractmethod
from typing import BinaryIO


class DocumentLoader(ABC):
    """文档加载器抽象基类"""
    
    @abstractmethod
    def extract_text(self, file: BinaryIO) -> str:
        """
        从文件中提取文本
        
        Args:
            file: 文件对象
            
        Returns:
            提取的文本内容
        """
        pass
    
    @abstractmethod
    def supports_file_type(self, file_type: str) -> bool:
        """
        检查是否支持该文件类型
        
        Args:
            file_type: 文件类型（扩展名）
            
        Returns:
            是否支持
        """
        pass

