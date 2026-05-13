import logging
import chardet
from bs4 import BeautifulSoup
from .base_parser import BaseParser, ParseResult

logger = logging.getLogger(__name__)


class HtmlParser(BaseParser):
    """HTML 文件解析器"""

    def parse(self, file_path: str) -> ParseResult:
        with open(file_path, 'rb') as f:
            raw_data = f.read()

        detected = chardet.detect(raw_data)
        encoding = detected.get('encoding', 'utf-8') or 'utf-8'

        try:
            html_content = raw_data.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            html_content = raw_data.decode('utf-8', errors='replace')

        soup = BeautifulSoup(html_content, 'html.parser')

        # 移除 script 和 style 标签
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()

        # 提取标题
        import os
        title = os.path.splitext(os.path.basename(file_path))[0]
        title_tag = soup.find('title')
        if title_tag and title_tag.string:
            title = title_tag.string.strip()

        # 提取正文
        content = soup.get_text(separator='\n', strip=True)

        return ParseResult(
            content=content,
            title=title,
            metadata={'encoding': encoding, 'format': 'html'}
        )

    def supported_extensions(self) -> list:
        return ['.html', '.htm']
