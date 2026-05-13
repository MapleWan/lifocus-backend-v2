import uuid
from datetime import datetime
from app.extension import db
from app.utils import format_datetime_to_string


class ChatMessage(db.Model):
    """对话消息表"""
    __tablename__ = 'chat_message'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = db.Column(db.String(36), db.ForeignKey('chat_session.id'), nullable=False, index=True, comment='所属会话ID')
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False, index=True, comment='用户ID')

    # 消息内容
    role = db.Column(db.String(16), nullable=False, comment='角色: user/assistant/system')
    content = db.Column(db.Text, nullable=False, comment='消息内容')
    content_type = db.Column(db.String(32), default='TEXT', comment='内容类型: TEXT/MARKDOWN')

    # 引用来源
    sources = db.Column(db.JSON, nullable=True, comment='引用来源列表')

    # Token 消耗
    prompt_tokens = db.Column(db.Integer, default=0, comment='输入Token数')
    completion_tokens = db.Column(db.Integer, default=0, comment='输出Token数')
    total_tokens = db.Column(db.Integer, default=0, comment='总Token数')

    # 性能指标
    response_time = db.Column(db.Integer, nullable=True, comment='响应时间(ms)')

    # 反馈
    feedback = db.Column(db.String(16), nullable=True, comment='用户反馈: like/dislike')

    # 时间戳
    create_time = db.Column(db.DateTime, default=datetime.now, comment='创建时间')

    __table_args__ = (
        db.Index('idx_msg_session', 'session_id', 'create_time'),
    )

    def dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'role': self.role,
            'content': self.content,
            'content_type': self.content_type,
            'sources': self.sources,
            'prompt_tokens': self.prompt_tokens,
            'completion_tokens': self.completion_tokens,
            'total_tokens': self.total_tokens,
            'response_time': self.response_time,
            'feedback': self.feedback,
            'create_time': format_datetime_to_string(self.create_time),
        }
