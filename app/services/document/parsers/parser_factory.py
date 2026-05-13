import os
import logging
from .base_parser import BaseParser, ParseResult
from .txt_parser import TxtParser
from .md_parser import MarkdownParser
from .html_parser import HtmlParser
from .pdf_parser import PdfParser
from .docx_parser import DocxParser
from .pptx_parser import PptxParser
from .xlsx_parser import XlsxParser

logger = logging.getLogger(__name__)

# 注册所有解析器
_PARSERS: list[BaseParser] = [
    TxtParser(),
    MarkdownParser(),
    HtmlParser(),
    PdfParser(),
    DocxParser(),
    PptxParser(),
    XlsxParser(),
]

# 构建扩展名 -> 解析器映射
_EXTENSION_MAP: dict[str, BaseParser] = {}
for parser in _PARSERS:
    for ext in parser.supported_extensions():
        _EXTENSION_MAP[ext.lower()] = parser


class ParserFactory:
    """文档解析器工厂"""

    @staticmethod
    def get_parser(file_path: str) -> BaseParser:
        """根据文件扩展名获取对应解析器"""
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        parser = _EXTENSION_MAP.get(ext)
        if not parser:
            raise ValueError(f"不支持的文件类型: {ext}")
        return parser

    @staticmethod
    def parse(file_path: str) -> ParseResult:
        """解析文件，返回 ParseResult"""
        parser = ParserFactory.get_parser(file_path)
        logger.info(f"使用 {parser.__class__.__name__} 解析文件: {file_path}")
        return parser.parse(file_path)

    @staticmethod
    def is_supported(file_path: str) -> bool:
        """检查文件类型是否支持"""
        _, ext = os.path.splitext(file_path)
        return ext.lower() in _EXTENSION_MAP

    @staticmethod
    def supported_extensions() -> list:
        """返回所有支持的扩展名"""
        return list(_EXTENSION_MAP.keys())
