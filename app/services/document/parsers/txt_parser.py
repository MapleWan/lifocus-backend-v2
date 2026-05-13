import logging
import chardet
from .base_parser import BaseParser, ParseResult

logger = logging.getLogger(__name__)


class TxtParser(BaseParser):
    """纯文本文件解析器"""

    def parse(self, file_path: str) -> ParseResult:
        # 自动检测编码
        with open(file_path, 'rb') as f:
            raw_data = f.read()

        detected = chardet.detect(raw_data)
        encoding = detected.get('encoding', 'utf-8') or 'utf-8'

        try:
            content = raw_data.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            content = raw_data.decode('utf-8', errors='replace')

        import os
        title = os.path.splitext(os.path.basename(file_path))[0]

        return ParseResult(
            content=content.strip(),
            title=title,
            metadata={'encoding': encoding}
        )

    def supported_extensions(self) -> list:
        return ['.txt', '.text']
