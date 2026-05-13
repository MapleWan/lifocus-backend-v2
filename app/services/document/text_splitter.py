import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.services.ai_config import AIConfig

logger = logging.getLogger(__name__)


class TextSplitterService:
    """文本分块服务，封装 LangChain RecursiveCharacterTextSplitter"""

    @staticmethod
    def split_text(text: str, chunk_size: int = None, chunk_overlap: int = None) -> list[dict]:
        """
        将文本分块，返回 chunk 列表。
        每个 chunk 包含: content, chunk_index, start_char, end_char, content_length
        """
        chunk_size = chunk_size or AIConfig.CHUNK_SIZE
        chunk_overlap = chunk_overlap or AIConfig.CHUNK_OVERLAP

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", "；", ";", "，", ",", " ", ""],
        )

        documents = splitter.create_documents([text])

        chunks = []
        current_pos = 0
        for idx, doc in enumerate(documents):
            chunk_content = doc.page_content
            # 定位块在原文中的起始位置
            start_char = text.find(chunk_content, current_pos)
            if start_char == -1:
                start_char = current_pos
            end_char = start_char + len(chunk_content)
            current_pos = start_char + 1

            chunks.append({
                'chunk_index': idx,
                'content': chunk_content,
                'content_length': len(chunk_content),
                'start_char': start_char,
                'end_char': end_char,
            })

        logger.info(f"文本分块完成: 原文 {len(text)} 字符 -> {len(chunks)} 个块 (chunk_size={chunk_size}, overlap={chunk_overlap})")
        return chunks
