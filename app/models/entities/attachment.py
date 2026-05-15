import uuid
from datetime import datetime

from app.enums.attachment_enum import ATTACHMENT_ERROR_MESSAGE
from app.extension import db
from app.utils import format_datetime_to_string


class Attachment(db.Model):
    __tablename__ = 'attachment'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False, index=True, comment='上传用户ID')
    project_id = db.Column(db.String(36), db.ForeignKey('project.id'), nullable=False, index=True, comment='所属项目ID')
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True, index=True, comment='所属目录ID（可空）')
    name = db.Column(db.String(512), nullable=False, comment='原始文件名')
    stored_name = db.Column(db.String(128), nullable=False, comment='磁盘存储名（uuid.ext）')
    ext = db.Column(db.String(16), nullable=False, comment='文件扩展名')
    mime_type = db.Column(db.String(128), nullable=True, comment='MIME类型')
    size = db.Column(db.BigInteger, nullable=False, comment='文件大小（字节）')
    kind = db.Column(db.String(32), nullable=False, comment='附件类型：IMAGE/PDF/WORD/PPT/EXCEL/AUDIO/VIDEO/MARKDOWN/TEXT')
    storage_path = db.Column(db.String(512), nullable=False, comment='相对于uploads根的相对路径')
    is_deleted = db.Column(db.Boolean, nullable=True, default=False, comment='是否删除')
    delete_time = db.Column(db.DateTime, nullable=True, comment='删除时间')
    create_time = db.Column(db.DateTime, default=datetime.now, nullable=False, comment='创建时间')
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False, comment='更新时间')

    user = db.relationship('User', backref='attachments', lazy=True)
    project = db.relationship('Project', backref='attachments', lazy=True)
    category = db.relationship('Category', backref='attachments', lazy=True)

    def dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'project_id': self.project_id,
            'category_id': self.category_id,
            'name': self.name,
            'stored_name': self.stored_name,
            'ext': self.ext,
            'mime_type': self.mime_type,
            'size': self.size,
            'kind': self.kind,
            'storage_path': self.storage_path,
            'is_deleted': self.is_deleted,
            'delete_time': format_datetime_to_string(self.delete_time) if self.delete_time else None,
            'create_time': format_datetime_to_string(self.create_time),
            'update_time': format_datetime_to_string(self.update_time),
        }

    @staticmethod
    def get_attachment_by_id(attachment_id):
        return Attachment.query.get(attachment_id)

    def add_attachment(self):
        db.session.add(self)
        db.session.commit()
        return True, self

    def soft_delete_attachment(self):
        self.is_deleted = True
        self.delete_time = datetime.now()
        db.session.add(self)
        db.session.commit()
        return True, self
