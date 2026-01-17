"""
文档分块服务
使用 LangChain 的 TextSplitter 进行文本分块
"""
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class ChunkingService:
    """文档分块服务"""
    
    @staticmethod
    def create_text_splitter(chunk_size: int = None, chunk_overlap: int = None) -> RecursiveCharacterTextSplitter:
        """
        创建文本分块器
        
        Args:
            chunk_size: 块大小
            chunk_overlap: 块重叠大小
            
        Returns:
            文本分块器实例
        """
        chunk_size = chunk_size or settings.CHUNK_SIZE
        chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        
        # 使用递归字符分割器，按段落、句子、字符的优先级分割
        return RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""],
            keep_separator=True
        )
    
    @staticmethod
    def chunk_text(
        text: str,
        chunk_size: int = None,
        chunk_overlap: int = None,
        metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        将文本分块
        
        Args:
            text: 要分块的文本
            chunk_size: 块大小
            chunk_overlap: 块重叠大小
            metadata: 元数据（会附加到每个块）
            
        Returns:
            分块结果列表，每个元素包含 content 和 metadata
        """
        if not text or not text.strip():
            logger.warning("文本为空，无法分块")
            return []
        
        try:
            # 创建分块器
            text_splitter = ChunkingService.create_text_splitter(chunk_size, chunk_overlap)
            
            # 分块
            chunks = text_splitter.split_text(text)
            
            # 构建结果
            result = []
            base_metadata = metadata or {}
            
            for i, chunk_text in enumerate(chunks):
                chunk_metadata = base_metadata.copy()
                chunk_metadata["chunk_index"] = i
                chunk_metadata["total_chunks"] = len(chunks)
                
                result.append({
                    "content": chunk_text.strip(),
                    "metadata": chunk_metadata
                })
            
            logger.info(f"文本分块完成，共生成 {len(result)} 个块")
            return result
            
        except Exception as e:
            logger.error(f"文本分块失败: {e}")
            raise
    
    @staticmethod
    def chunk_documents(
        documents: List[Dict[str, Any]],
        chunk_size: int = None,
        chunk_overlap: int = None
    ) -> List[Dict[str, Any]]:
        """
        批量分块多个文档
        
        Args:
            documents: 文档列表，每个文档包含 content 和 metadata
            chunk_size: 块大小
            chunk_overlap: 块重叠大小
            
        Returns:
            所有文档的分块结果
        """
        all_chunks = []
        
        for doc in documents:
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            
            chunks = ChunkingService.chunk_text(
                text=content,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                metadata=metadata
            )
            all_chunks.extend(chunks)
        
        logger.info(f"批量分块完成，共处理 {len(documents)} 个文档，生成 {len(all_chunks)} 个块")
        return all_chunks

