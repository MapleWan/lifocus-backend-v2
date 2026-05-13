import uuid
from datetime import datetime
from app.extension import db


class DocumentChunk(db.Model):
    """文档分块表"""
    __tablename__ = 'document_chunk'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = db.Column(db.String(36), db.ForeignKey('document.id'), nullable=False, index=True, comment='所属文档ID')
    knowledge_base_id = db.Column(db.String(36), db.ForeignKey('knowledge_base.id'), nullable=False, index=True, comment='所属知识库ID')

    # 块内容
    chunk_index = db.Column(db.Integer, nullable=False, comment='块序号')
    content = db.Column(db.Text, nullable=False, comment='块内容')
    content_length = db.Column(db.Integer, default=0, comment='内容长度')
    token_count = db.Column(db.Integer, default=0, comment='Token数量')

    # 位置信息
    page_number = db.Column(db.Integer, nullable=True, comment='页码')
    start_char = db.Column(db.Integer, nullable=True, comment='起始字符位置')
    end_char = db.Column(db.Integer, nullable=True, comment='结束字符位置')

    # 向量ID
    vector_id = db.Column(db.String(64), nullable=True, unique=True, comment='向量数据库中的ID')

    # 时间戳
    create_time = db.Column(db.DateTime, default=datetime.now, comment='创建时间')

    __table_args__ = (
        db.Index('idx_chunk_doc', 'document_id', 'chunk_index'),
        db.Index('idx_chunk_kb', 'knowledge_base_id'),
    )

    def dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'knowledge_base_id': self.knowledge_base_id,
            'chunk_index': self.chunk_index,
            'content': self.content,
            'content_length': self.content_length,
            'page_number': self.page_number,
            'vector_id': self.vector_id,
        }
