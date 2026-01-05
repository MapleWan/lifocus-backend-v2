import uuid
from datetime import datetime

from app.extension import db
from app.utils import format_datetime_to_string

class Article(db.Model):
    __tablename__ = 'article'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    type = db.Column(db.String(64), nullable=False, comment='文章类型')
    title = db.Column(db.String(255), nullable=False, comment='文章标题')
    content = db.Column(db.Text, nullable=False, comment='文章内容')
    folder = db.Column(db.String(255), nullable=True, comment='文件存储文件夹')
    status = db.Column(db.String(64), nullable=False, default='ACTIVE', comment='文章状态')
    is_deleted = db.Column(db.Boolean, nullable=True, default=False, comment='是否删除文章')
    delete_time = db.Column(db.DateTime, nullable=True, comment='删除时间')
    is_shared = db.Column(db.Boolean, nullable=True, default=False, comment='是否共享文章')
    share_password = db.Column(db.String(64), nullable=True, comment='共享密码')
    create_time = db.Column(db.DateTime, default=datetime.now(), nullable=False, comment='创建时间')
    update_time = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now(), nullable=False, comment='更新时间')
    
    # 打印文章信息
    def dict(self):
        return {
            'id': self.id,
            'category_id': self.category_id,
            'type': self.type,
            'title': self.title,
            # 'content': self.content,
            'folder': self.folder,
            'status': self.status,
            'is_deleted': self.is_deleted,
            'delete_time': format_datetime_to_string(self.delete_time),
            'is_shared': self.is_shared,
            # 'share_password': self.share_password,
            'create_time': format_datetime_to_string(self.create_time),
            'update_time': format_datetime_to_string(self.update_time)
        }
    
    # 新增文章
    def add_article(self):
        db.session.add(self)
        db.session.commit()
        return self
    
    # 更新文章
    def update_article(self):
        db.session.add(self)
        db.session.commit()
        return self
    
    # 删除文章
    def delete_article(self):
        db.session.delete(self)
        db.session.commit()
        return self
    
    # 根据文章id获取文章信息
    @staticmethod
    def get_article_by_id(article_id):
        return Article.query.filter_by(id=article_id).first()

    