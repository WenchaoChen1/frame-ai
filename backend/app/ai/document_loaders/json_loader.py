"""
JSON 文档加载器
"""
import json
from typing import BinaryIO

from .base import DocumentLoader
from app.core.logger import get_logger

logger = get_logger(__name__)


class JsonLoader(DocumentLoader):
    """JSON 文档加载器"""
    
    def extract_text(self, file: BinaryIO) -> str:
        """
        从 JSON 文件中提取文本
        将JSON内容格式化为可读的文本形式
        
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
                    json_data = json.loads(content.decode(encoding))
                    
                    # 将JSON转换为格式化的文本
                    text = self._json_to_text(json_data)
                    logger.info(f"成功使用 {encoding} 编码解析 JSON 文件")
                    return text.strip()
                except (UnicodeDecodeError, json.JSONDecodeError, AttributeError):
                    continue
            
            # 如果所有编码都失败，使用 utf-8 并忽略错误
            file.seek(0)
            content = file.read()
            text = content.decode('utf-8', errors='ignore')
            json_data = json.loads(text)
            text = self._json_to_text(json_data)
            logger.warning("使用 utf-8 编码解析 JSON 文件（忽略错误）")
            return text.strip()
            
        except Exception as e:
            logger.error(f"提取 JSON 文本失败: {e}")
            raise
    
    def _json_to_text(self, data, indent=0) -> str:
        """
        递归地将JSON数据转换为可读文本
        
        Args:
            data: JSON数据（dict、list或基本类型）
            indent: 缩进级别
            
        Returns:
            格式化的文本
        """
        lines = []
        prefix = "  " * indent
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    lines.append(f"{prefix}{key}:")
                    lines.append(self._json_to_text(value, indent + 1))
                else:
                    lines.append(f"{prefix}{key}: {value}")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    lines.append(f"{prefix}[{i}]:")
                    lines.append(self._json_to_text(item, indent + 1))
                else:
                    lines.append(f"{prefix}- {item}")
        else:
            lines.append(f"{prefix}{data}")
        
        return "\n".join(lines)
    
    def supports_file_type(self, file_type: str) -> bool:
        """检查是否支持该文件类型"""
        return file_type.lower() in ['.json', 'json']

