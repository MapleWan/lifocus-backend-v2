import uuid
from datetime import datetime

from app.enums.article_enum import ARTICLE_ERROR_MESSAGE
from app.extension import db
from app.models.entities.category import Category
from app.models.entities.project import Project
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
    share_password = db.Column(db.String(255), nullable=True, comment='共享密码')
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
        if existing_article and existing_article.id == self.id:
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
    
    # 获取项目某一目录下的所有文章列表，带查询条件（分页接口）
    '''
        :param category_id: 目录id
        :param query_condition: 查询条件 
            {
                "title": #文章标题
                "type": "NOTE" #文章类型, NOTE DAILY
                "status": "ACTIVE" # 文章状态 ACTIVE ARCHIVED
                "is_shared": false, # 是否分享
                "create_start_time": "2025-12-17 00:00:00",
                "create_end_time": "2025-12-17 00:00:00",
                "update_start_time": "2025-12-17 00:00:00",
                "update_end_time: "2025-12-17 00:00:00",
                "is_query_page": true, # 是否使用分页查询
                "page_no": 1, # page: 页码
                "page_size": 10, # 每页数量
                "order_by": "title", # 排序字段: title, create_time, update_time
                "order_direction": "asc" # 排序方向: asc, desc
            }
        :return 包含文章列表、总数和总页数的字典
    '''
    @classmethod
    def get_articles_by_category_id(cls, category_id, project_id = None, query_condition = {}):
        if category_id:
            # 只查询当前目录下的文章，没有递归查询子目录下的文章
            # query = cls.query.filter_by(category_id=category_id, is_deleted=False)

            # 获取指定目录及其所有子目录的ID
            def get_all_subcategory_ids(category_id):
                subcategory_ids = [category_id]
                # 获取当前目录的子目录
                children = Category.query.filter_by(parent_id=category_id, is_deleted=False).all()
                for child in children:
                    # 递归获取子目录的子目录
                    subcategory_ids.extend(get_all_subcategory_ids(child.id))
                return subcategory_ids
            # 获取所有相关的目录ID
            all_category_ids = get_all_subcategory_ids(category_id)
            # 查询这些目录下的所有文章
            query = cls.query.filter(cls.category_id.in_(all_category_ids), cls.is_deleted == False)
        
        else:
            query = cls.query.filter_by(is_deleted=False).join(Category, cls.category_id == Category.id).filter(Category.project_id == project_id).filter(Category.is_deleted == False)
            # query = Project.query.filter_by(id=project_id, is_deleted=False).join(Category, Project.id == Category.project_id).filter(Category.is_deleted == False).join(cls, Category.id == cls.category_id).filter(cls.is_deleted == False)
        exact_match_fields = ['type', 'status', 'is_shared']
        fuzzy_match_fields = ['title']
        start_scope_match_fields = ['create_start_time', 'update_start_time']
        end_scope_match_fields = ['create_end_time', 'update_end_time']

        if query_condition:
            for field in query_condition:
                if query_condition[field] == None: continue
                if field in exact_match_fields:
                    query = query.filter(getattr(cls, field) == query_condition[field])
                elif field in fuzzy_match_fields:
                    query = query.filter(getattr(cls, field).like(f'%{query_condition[field]}%'))
                elif field in start_scope_match_fields:
                    query = query.filter(getattr(cls, field.replace('start_time', 'time')) >= query_condition[field])
                elif field in end_scope_match_fields:
                    query = query.filter(getattr(cls, field.replace('end_time', 'time')) <= query_condition[field])

        # 添加排序功能
        if query_condition and query_condition.get('order_by') is not None and query_condition.get('order_direction') is not None:
            order_by = query_condition.get('order_by', 'update_time')  # 默认按更新时间排序
            order_direction = query_condition.get('order_direction', 'desc')  # 默认降序
            
            # 验证排序字段是否有效
            valid_order_fields = ['title', 'create_time', 'update_time']
            if order_by in valid_order_fields:
                order_attr = getattr(cls, order_by)
                if order_direction.lower() == 'desc':
                    query = query.order_by(order_attr.desc())
                else:
                    query = query.order_by(order_attr.asc())
        
        # 添加分页功能
        if query_condition and query_condition.get('is_query_page'):
            page_no = query_condition.get('page_no', 1)
            page_size = query_condition.get('page_size', 10)
            query = query.paginate(page=page_no, per_page=page_size, error_out=False)
            articles = query.items
            total = query.total
            pages = query.pages
            return {
                'data': articles,
                'total': total,
                'pages': pages
            }
        else:
            return query.all()