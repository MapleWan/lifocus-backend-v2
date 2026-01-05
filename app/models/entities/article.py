import uuid
from datetime import datetime

from app.enums.article_enum import ARTICLE_ERROR_MESSAGE
from app.extension import db
from app.utils import format_datetime_to_string

class Article(db.Model):
    __tablename__ = 'article'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    type = db.Column(db.String(64), nullable=False, comment='文章类型')
    title = db.Column(db.String(255), nullable=False, comment='文章标题')
    content = db.Column(db.Text, nullable=False, comment='文章内容')
    status = db.Column(db.String(64), nullable=False, default='ACTIVE', comment='文章状态')
    is_deleted = db.Column(db.Boolean, nullable=True, default=False, comment='是否删除文章')
    delete_time = db.Column(db.DateTime, nullable=True, comment='删除时间')
    is_shared = db.Column(db.Boolean, nullable=True, default=False, comment='是否共享文章')
    share_password = db.Column(db.String(64), nullable=True, comment='共享密码')
    create_time = db.Column(db.DateTime, default=datetime.now(), nullable=False, comment='创建时间')
    update_time = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now(), nullable=False, comment='更新时间')
    
    category = db.relationship('Category', back_populates='articles', lazy=True)

    # 打印文章信息
    def dict(self):
        return {
            'id': self.id,
            'category_id': self.category_id,
            # 'category': self.category.dict() if self.category else None,
            'type': self.type,
            'title': self.title,
            # 'content': self.content,
            'status': self.status,
            'is_deleted': self.is_deleted,
            'delete_time': format_datetime_to_string(self.delete_time) if self.delete_time else None,
            'is_shared': self.is_shared,
            # 'share_password': self.share_password,
            'create_time': format_datetime_to_string(self.create_time),
            'update_time': format_datetime_to_string(self.update_time)
        }
    
    # 新增文章
    def add_article(self):
        existing_article = Article.query.filter_by(title=self.title, is_deleted=False).first()
        if existing_article:
            return False, ARTICLE_ERROR_MESSAGE['ALREADY_TITLE_EXIST']
        db.session.add(self)
        db.session.commit()
        return True, self
    
    # 更新文章
    def update_article(self):
        db.session.add(self)
        db.session.commit()
        return True, self
    
    # 删除文章
    def soft_delete_article(self):
        # db.session.delete(self)
        self.is_deleted = True
        self.delete_time = datetime.now()
        db.session.add(self)
        db.session.commit()
        return True, self
    
    # 根据文章id获取文章信息
    @staticmethod
    def get_article_by_id(article_id):
        return Article.query.get(article_id)

    # 根据文章标题和目录id获取文章信息
    @staticmethod
    def get_article_by_title_and_category_id(article_title, category_id):
        return Article.query.filter_by(title=article_title, category_id=category_id, is_deleted=False).first()
    