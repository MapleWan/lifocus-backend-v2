import uuid
from datetime import datetime
from app.extension import db
from app.utils import format_datetime_to_string


class KnowledgeBase(db.Model):
    """知识库主表"""
    __tablename__ = 'knowledge_base'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False, index=True, comment='创建者ID')
    project_id = db.Column(db.String(36), db.ForeignKey('project.id'), nullable=True, index=True, comment='所属项目ID')

    # 基本信息
    name = db.Column(db.String(255), nullable=False, comment='知识库名称')
    description = db.Column(db.Text, nullable=True, comment='知识库描述')
    icon = db.Column(db.String(255), nullable=True, comment='知识库图标URL')

    # AI 配置
    embedding_model = db.Column(db.String(64), default='bge-large-zh-v1.5', comment='Embedding模型')
    llm_model = db.Column(db.String(64), default='glm-4-flash', comment='默认对话模型')
    vector_collection = db.Column(db.String(64), nullable=False, unique=True, comment='向量库Collection名称')

    # 处理配置
    chunk_size = db.Column(db.Integer, default=500, comment='文本分块大小')
    chunk_overlap = db.Column(db.Integer, default=50, comment='文本分块重叠大小')

    # 统计信息
    document_count = db.Column(db.Integer, default=0, comment='文档数量')
    total_chunks = db.Column(db.Integer, default=0, comment='总块数')

    # 状态管理
    status = db.Column(db.String(32), default='ACTIVE', comment='状态: ACTIVE/ARCHIVED')
    is_public = db.Column(db.Boolean, default=False, comment='是否公开分享')
    is_deleted = db.Column(db.Boolean, default=False, comment='是否删除')
    delete_time = db.Column(db.DateTime, nullable=True, comment='删除时间')

    # 时间戳
    create_time = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关联关系
    user = db.relationship('User', backref='knowledge_bases')
    project = db.relationship('Project', backref='knowledge_bases')
    documents = db.relationship('Document', backref='knowledge_base', lazy='dynamic', cascade='all, delete-orphan')
    chat_sessions = db.relationship('ChatSession', backref='knowledge_base', lazy='dynamic')

    __table_args__ = (
        db.Index('idx_kb_user_project', 'user_id', 'project_id'),
        db.Index('idx_kb_status', 'status'),
    )

    def dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'project_id': self.project_id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'embedding_model': self.embedding_model,
            'llm_model': self.llm_model,
            'vector_collection': self.vector_collection,
            'chunk_size': self.chunk_size,
            'chunk_overlap': self.chunk_overlap,
            'document_count': self.document_count,
            'total_chunks': self.total_chunks,
            'status': self.status,
            'is_public': self.is_public,
            'create_time': format_datetime_to_string(self.create_time),
            'update_time': format_datetime_to_string(self.update_time),
        }

    def add_knowledge_base(self):
        db.session.add(self)
        db.session.commit()
        return self

    def update_knowledge_base(self):
        db.session.add(self)
        db.session.commit()
        return self

    def soft_delete(self):
        self.is_deleted = True
        self.delete_time = datetime.now()
        db.session.commit()
        return self

    @staticmethod
    def get_by_id(kb_id):
        return KnowledgeBase.query.filter_by(id=kb_id, is_deleted=False).first()

    @staticmethod
    def get_by_name(user_id, name):
        return KnowledgeBase.query.filter_by(user_id=user_id, name=name, is_deleted=False).first()

    @staticmethod
    def get_by_user_id(user_id, query_condition=None):
        query = KnowledgeBase.query.filter_by(user_id=user_id, is_deleted=False)

        exact_match_fields = ['status']
        fuzzy_match_fields = ['name']
        start_scope_match_fields = ['create_start_time', 'update_start_time']
        end_scope_match_fields = ['create_end_time', 'update_end_time']

        if query_condition:
            for field in query_condition:
                if not query_condition[field]:
                    continue
                if field in exact_match_fields:
                    query = query.filter(getattr(KnowledgeBase, field) == query_condition[field])
                elif field in fuzzy_match_fields:
                    query = query.filter(getattr(KnowledgeBase, field).like(f'%{query_condition[field]}%'))
                elif field in start_scope_match_fields:
                    query = query.filter(getattr(KnowledgeBase, field.replace('start_time', 'time')) >= query_condition[field])
                elif field in end_scope_match_fields:
                    query = query.filter(getattr(KnowledgeBase, field.replace('end_time', 'time')) <= query_condition[field])

            # 排序
            if query_condition.get('order_by') and query_condition.get('order_direction'):
                order_by = query_condition.get('order_by', 'update_time')
                order_direction = query_condition.get('order_direction', 'desc')
                valid_order_fields = ['name', 'create_time', 'update_time', 'document_count']
                if order_by in valid_order_fields:
                    order_attr = getattr(KnowledgeBase, order_by)
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
