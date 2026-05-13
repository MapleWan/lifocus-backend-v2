import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class ParseResult:
    """文档解析结果"""

    def __init__(self, content: str, title: str = '', metadata: dict = None):
        self.content = content
        self.title = title
        self.metadata = metadata or {}

    @property
    def content_length(self):
        return len(self.content) if self.content else 0

    @property
    def preview(self):
        return self.content[:500] if self.content else ''


class BaseParser(ABC):
    """文档解析器基类"""

    @abstractmethod
    def parse(self, file_path: str) -> ParseResult:
        """解析文件并返回文本内容"""
        raise NotImplementedError

    @abstractmethod
    def supported_extensions(self) -> list:
        """返回支持的文件扩展名列表"""
        raise NotImplementedError
