"""
TXT 文档加载器
"""
from typing import BinaryIO
from .base import DocumentLoader
from ...core.logger import get_logger

logger = get_logger(__name__)


class TxtLoader(DocumentLoader):
    """TXT 文档加载器"""
    
    def extract_text(self, file: BinaryIO) -> str:
        """
        从 TXT 文件中提取文本
        
        Args:
            file: 文件对象
            
        Returns:
            提取的文本内容
        """
        try:
            # 尝试多种编码
            encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
            
            for encoding in encodings:
                try:
                    file.seek(0)
                    content = file.read()
                    text = content.decode(encoding)
                    logger.info(f"成功使用 {encoding} 编码解析 TXT 文件")
                    return text.strip()
                except (UnicodeDecodeError, AttributeError):
                    continue
            
            # 如果所有编码都失败，使用 utf-8 并忽略错误
            file.seek(0)
            content = file.read()
            text = content.decode('utf-8', errors='ignore')
            logger.warning("使用 utf-8 编码解析 TXT 文件（忽略错误）")
            return text.strip()
            
        except Exception as e:
            logger.error(f"提取 TXT 文本失败: {e}")
            raise
    
    def supports_file_type(self, file_type: str) -> bool:
        """检查是否支持该文件类型"""
        return file_type.lower() in ['.txt', 'txt']

