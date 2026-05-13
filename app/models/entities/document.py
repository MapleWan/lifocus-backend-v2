import uuid
from datetime import datetime
from app.extension import db
from app.utils import format_datetime_to_string


class Document(db.Model):
    """知识库文档表"""
    __tablename__ = 'document'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    knowledge_base_id = db.Column(db.String(36), db.ForeignKey('knowledge_base.id'), nullable=False, index=True, comment='所属知识库ID')

    # 来源信息
    source_type = db.Column(db.String(32), nullable=False, comment='来源类型: FILE/ARTICLE/URL/NOTE')
    source_id = db.Column(db.String(36), nullable=True, comment='关联来源ID')
    source_url = db.Column(db.String(2048), nullable=True, comment='原始URL')

    # 文件信息
    file_type = db.Column(db.String(32), nullable=False, comment='文件类型: PDF/DOCX/PPTX/XLSX/MD/TXT/HTML')
    file_name = db.Column(db.String(255), nullable=False, comment='原始文件名')
    file_path = db.Column(db.String(512), nullable=True, comment='文件存储路径')
    file_size = db.Column(db.BigInteger, default=0, comment='文件大小(字节)')
    file_hash = db.Column(db.String(64), nullable=True, index=True, comment='文件MD5哈希')

    # 内容信息
    title = db.Column(db.String(512), nullable=True, comment='文档标题')
    content_preview = db.Column(db.Text, nullable=True, comment='内容预览')
    content_length = db.Column(db.Integer, default=0, comment='内容总字符数')

    # 处理状态
    embed_status = db.Column(db.String(32), default='PENDING', comment='向量化状态: PENDING/PROCESSING/COMPLETED/FAILED')
    process_error = db.Column(db.Text, nullable=True, comment='处理错误信息')
    chunk_count = db.Column(db.Integer, default=0, comment='分块数量')

    # 元数据
    meta_data = db.Column(db.JSON, nullable=True, comment='额外元数据')
    tags = db.Column(db.JSON, nullable=True, comment='标签列表')

    # 状态管理
    is_deleted = db.Column(db.Boolean, default=False, comment='是否删除')
    delete_time = db.Column(db.DateTime, nullable=True, comment='删除时间')

    # 时间戳
    create_time = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    process_time = db.Column(db.DateTime, nullable=True, comment='处理完成时间')

    # 关联关系
    chunks = db.relationship('DocumentChunk', backref='document', lazy='dynamic', cascade='all, delete-orphan')

    __table_args__ = (
        db.Index('idx_doc_kb_status', 'knowledge_base_id', 'embed_status'),
        db.Index('idx_doc_source', 'source_type', 'source_id'),
    )

    def dict(self):
        return {
            'id': self.id,
            'knowledge_base_id': self.knowledge_base_id,
            'source_type': self.source_type,
            'source_id': self.source_id,
            'source_url': self.source_url,
            'file_type': self.file_type,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'title': self.title,
            'content_preview': self.content_preview,
            'content_length': self.content_length,
            'embed_status': self.embed_status,
            'process_error': self.process_error,
            'chunk_count': self.chunk_count,
            'meta_data': self.meta_data,
            'tags': self.tags,
            'create_time': format_datetime_to_string(self.create_time),
            'update_time': format_datetime_to_string(self.update_time),
            'process_time': format_datetime_to_string(self.process_time) if self.process_time else None,
        }

    def add_document(self):
        db.session.add(self)
        db.session.commit()
        return self

    def update_document(self):
        db.session.add(self)
        db.session.commit()
        return self

    def soft_delete(self):
        self.is_deleted = True
        self.delete_time = datetime.now()
        db.session.commit()
        return self

    @staticmethod
    def get_by_id(doc_id):
        return Document.query.filter_by(id=doc_id, is_deleted=False).first()

    @staticmethod
    def get_by_hash(knowledge_base_id, file_hash):
        return Document.query.filter_by(
            knowledge_base_id=knowledge_base_id,
            file_hash=file_hash,
            is_deleted=False
        ).first()

    @staticmethod
    def get_by_knowledge_base_id(knowledge_base_id, query_condition=None):
        query = Document.query.filter_by(knowledge_base_id=knowledge_base_id, is_deleted=False)

        exact_match_fields = ['embed_status', 'file_type', 'source_type']
        fuzzy_match_fields = ['file_name', 'title']

        if query_condition:
            for field in query_condition:
                if not query_condition[field]:
                    continue
                if field in exact_match_fields:
                    query = query.filter(getattr(Document, field) == query_condition[field])
                elif field in fuzzy_match_fields:
                    query = query.filter(getattr(Document, field).like(f'%{query_condition[field]}%'))

            # 排序
            if query_condition.get('order_by') and query_condition.get('order_direction'):
                order_by = query_condition.get('order_by', 'create_time')
                order_direction = query_condition.get('order_direction', 'desc')
                valid_order_fields = ['file_name', 'create_time', 'update_time', 'file_size']
                if order_by in valid_order_fields:
                    order_attr = getattr(Document, order_by)
                    if order_direction.lower() == 'desc':
                        query = query.order_by(order_attr.desc())
                    else:
                        query = query.order_by(order_attr.asc())

            # 分页
            if query_condition.get('is_query_page'):
                page_no = query_condition.get('page_no', 1)
                page_size = query_condition.get('page_size', 10)
                query = query.paginate(page=page_no, per_page=page_size, error_out=False)
                return {
                    'data': query.items,
                    'total': query.total,
                    'pages': query.pages
                }

        return query.all()
