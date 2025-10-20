"""
文档加载器模块
支持多种文档格式的文本提取
"""
from .base import DocumentLoader
from .txt_loader import TxtLoader
from .pdf_loader import PdfLoader
from .docx_loader import DocxLoader
from .json_loader import JsonLoader

__all__ = ["DocumentLoader", "TxtLoader", "PdfLoader", "DocxLoader", "JsonLoader", "DocumentLoaderFactory"]


class DocumentLoaderFactory:
    """文档加载器工厂"""
    
    _loaders = {
        '.txt': TxtLoader(),
        '.pdf': PdfLoader(),
        '.docx': DocxLoader(),
        '.json': JsonLoader(),
    }
    
    @classmethod
    def get_loader(cls, file_type: str) -> DocumentLoader:
        """
        根据文件类型获取对应的加载器
        
        Args:
            file_type: 文件类型（扩展名，如 .txt）
            
        Returns:
            文档加载器实例
            
        Raises:
            ValueError: 不支持的文件类型
        """
        file_type = file_type.lower()
        if not file_type.startswith('.'):
            file_type = f'.{file_type}'
        
        loader = cls._loaders.get(file_type)
        if loader is None:
            raise ValueError(f"不支持的文件类型: {file_type}")
        
        return loader
    
    @classmethod
    def supports_file_type(cls, file_type: str) -> bool:
        """检查是否支持该文件类型"""
        file_type = file_type.lower()
        if not file_type.startswith('.'):
            file_type = f'.{file_type}'
        return file_type in cls._loaders

