import logging
import chardet
from .base_parser import BaseParser, ParseResult

logger = logging.getLogger(__name__)


class MarkdownParser(BaseParser):
    """Markdown 文件解析器，保留原始 Markdown 文本"""

    def parse(self, file_path: str) -> ParseResult:
        with open(file_path, 'rb') as f:
            raw_data = f.read()

        detected = chardet.detect(raw_data)
        encoding = detected.get('encoding', 'utf-8') or 'utf-8'

        try:
            content = raw_data.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            content = raw_data.decode('utf-8', errors='replace')

        # 尝试从第一个 # 标题提取标题
        import os
        title = os.path.splitext(os.path.basename(file_path))[0]
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('# ') and not line.startswith('##'):
                title = line.lstrip('# ').strip()
                break

        return ParseResult(
            content=content.strip(),
            title=title,
            metadata={'encoding': encoding, 'format': 'markdown'}
        )

    def supported_extensions(self) -> list:
        return ['.md', '.markdown']
