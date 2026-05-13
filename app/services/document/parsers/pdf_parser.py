import logging
import fitz  # PyMuPDF
from .base_parser import BaseParser, ParseResult

logger = logging.getLogger(__name__)


class PdfParser(BaseParser):
    """PDF 文件解析器，使用 PyMuPDF"""

    def parse(self, file_path: str) -> ParseResult:
        doc = fitz.open(file_path)
        pages_text = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text('text')
            if text.strip():
                pages_text.append(text)

        content = '\n\n'.join(pages_text)

        # 提取元数据
        metadata = doc.metadata or {}
        title = metadata.get('title', '')
        if not title:
            import os
            title = os.path.splitext(os.path.basename(file_path))[0]

        doc.close()

        return ParseResult(
            content=content.strip(),
            title=title,
            metadata={
                'page_count': len(doc) if hasattr(doc, '__len__') else 0,
                'author': metadata.get('author', ''),
                'format': 'pdf',
            }
        )

    def supported_extensions(self) -> list:
        return ['.pdf']
