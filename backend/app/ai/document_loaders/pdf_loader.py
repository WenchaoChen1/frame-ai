"""
PDF 文档加载器
"""
from typing import BinaryIO
from .base import DocumentLoader
from ...core.logger import get_logger
import io

logger = get_logger(__name__)


class PdfLoader(DocumentLoader):
    """PDF 文档加载器"""
    
    def extract_text(self, file: BinaryIO) -> str:
        """
        从 PDF 文件中提取文本
        
        Args:
            file: 文件对象
            
        Returns:
            提取的文本内容
        """
        try:
            # 优先使用 pdfplumber（更准确）
            try:
                import pdfplumber
                file.seek(0)
                
                text_parts = []
                with pdfplumber.open(file) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            text_parts.append(text)
                
                logger.info(f"使用 pdfplumber 成功提取 PDF 文本，共 {len(text_parts)} 页")
                return "\n\n".join(text_parts).strip()
                
            except ImportError:
                logger.warning("pdfplumber 未安装，使用 pypdf")
        
            # 备选方案：使用 pypdf
            try:
                from pypdf import PdfReader
                file.seek(0)
                
                reader = PdfReader(file)
                text_parts = []
                
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
                
                logger.info(f"使用 pypdf 成功提取 PDF 文本，共 {len(text_parts)} 页")
                return "\n\n".join(text_parts).strip()
                
            except ImportError:
                logger.error("pypdf 未安装，无法处理 PDF 文件")
                raise ImportError("需要安装 pdfplumber 或 pypdf 来处理 PDF 文件")
                
        except Exception as e:
            logger.error(f"提取 PDF 文本失败: {e}")
            raise
    
    def supports_file_type(self, file_type: str) -> bool:
        """检查是否支持该文件类型"""
        return file_type.lower() in ['.pdf', 'pdf']

