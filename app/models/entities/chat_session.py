import uuid
from datetime import datetime
from app.extension import db
from app.utils import format_datetime_to_string


class ChatSession(db.Model):
    """对话会话表"""
    __tablename__ = 'chat_session'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False, index=True, comment='用户ID')
    knowledge_base_id = db.Column(db.String(36), db.ForeignKey('knowledge_base.id'), nullable=True, index=True, comment='关联知识库ID')

    # 会话信息
    title = db.Column(db.String(255), nullable=True, comment='会话标题')
    session_type = db.Column(db.String(32), default='KNOWLEDGE', comment='会话类型: KNOWLEDGE/WEB_SEARCH/CHAT')

    # 配置
    llm_model = db.Column(db.String(64), nullable=True, comment='使用的模型')
    temperature = db.Column(db.Float, default=0.7, comment='温度参数')

    # 统计
    message_count = db.Column(db.Integer, default=0, comment='消息数量')
    total_tokens = db.Column(db.BigInteger, default=0, comment='总Token消耗')

    # 状态
    is_pinned = db.Column(db.Boolean, default=False, comment='是否置顶')
    status = db.Column(db.String(32), default='ACTIVE', comment='状态: ACTIVE/ARCHIVED')
    is_deleted = db.Column(db.Boolean, default=False, comment='是否删除')
    delete_time = db.Column(db.DateTime, nullable=True, comment='删除时间')

    # 时间戳
    create_time = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关联关系
    messages = db.relationship('ChatMessage', backref='session', lazy='dynamic', cascade='all, delete-orphan')

    __table_args__ = (
        db.Index('idx_session_user', 'user_id', 'update_time'),
        db.Index('idx_session_kb', 'knowledge_base_id'),
    )

    def dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'knowledge_base_id': self.knowledge_base_id,
            'title': self.title,
            'session_type': self.session_type,
            'llm_model': self.llm_model,
            'temperature': self.temperature,
            'message_count': self.message_count,
            'total_tokens': self.total_tokens,
            'is_pinned': self.is_pinned,
            'status': self.status,
            'create_time': format_datetime_to_string(self.create_time),
            'update_time': format_datetime_to_string(self.update_time),
        }
