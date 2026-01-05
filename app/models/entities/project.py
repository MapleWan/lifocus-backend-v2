import uuid
from datetime import datetime
from app.extension import db
from app.utils import format_datetime_to_string
class Project(db.Model):
    __tablename__ = 'project'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False, comment='用户 ID')
    type = db.Column(db.String(64), nullable=False, comment='项目类型')
    name = db.Column(db.String(64), nullable=False, comment='项目名称')
    icon = db.Column(db.String(255), nullable=True, comment='项目图标')
    description = db.Column(db.String(255), nullable=True, comment='项目描述')
    folder = db.Column(db.String(255), nullable=True, comment='项目文件存储文件夹')
    status = db.Column(db.String(64), nullable=False, default='ACTIVE', comment='项目状态')
    is_deleted = db.Column(db.Boolean, nullable=False, default=False, comment='是否删除项目')
    delete_time = db.Column(db.DateTime, nullable=True, comment='删除时间')
    create_time = db.Column(db.DateTime, default=datetime.now(), comment='创建时间')
    update_time = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now(), comment='更新时间')
    
    # 一个用户有多个项目
    user = db.relationship('User', back_populates='projects', lazy=True)

    # 打印项目信息
    def dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'name': self.name,
            'icon': self.icon,
            'description': self.description,
            'folder': self.folder,
            'status': self.status,
            'is_deleted': self.is_deleted,
            'create_time': format_datetime_to_string(self.create_time),
            'update_time': format_datetime_to_string(self.update_time),
            # 'user': self.user.dict()
        }
    
    # 新增项目
    def add_project(self):
        db.session.add(self)
        db.session.commit()
        return self

    # 更新项目
    def update_project(self):
        db.session.add(self)
        db.session.commit()
        return self

    # 删除项目
    def delete_project(self):
        db.session.delete(self)
        db.session.commit()
        return self

    # 根据项目id获取项目信息
    @staticmethod
    def get_project_by_id(project_id):
        return Project.query.filter_by(id=project_id, is_deleted=False).first()
    
    # 根据项目名称获取用户下的项目信息
    @staticmethod
    def get_project_by_name(user_id, project_name, is_filter_deleted=True):
        if is_filter_deleted:
            return Project.query.filter_by(user_id=user_id, name=project_name, is_deleted=False).first()
        else:
            return Project.query.filter_by(user_id=user_id, name=project_name).first()

    # 获取用户下的项目，带查询条件（分页接口）
    '''
    根据用户ID获取项目列表（分页）
    :param user_id: 用户 ID
    :param query_condition: 查询条件 
        {
            "type": "NOTE",
			"name": "project-3",
            "status": "ACTIVE",
			"create_start_time": "2025-12-17 00:00:00",
			"create_end_time": "2025-12-17 00:00:00",
			"update_start_time": "2025-12-17 00:00:00",
			"update_end_time: "2025-12-17 00:00:00",
            "is_query_page": true, # 是否使用分页查询
            "page_no": 1, # page: 页码
            "page_size": 10, # 每页数量
            "order_by": "name", # 排序字段: name, create_time, update_time
            "order_direction": "asc" # 排序方向: asc, desc
		}
    :return: 包含项目列表、总数和总页数的字典
    '''
    @staticmethod
    def get_projects_by_user_id(user_id, query_condition = None):
        query = Project.query.filter_by(user_id=user_id, is_deleted=False)
        exact_match_fields = ['type', 'status']
        fuzzy_match_fields = ['name']
        start_scope_match_fields = ['create_start_time', 'update_start_time']
        end_scope_match_fields = ['create_end_time', 'update_end_time']

        if query_condition:
            for field in query_condition:
                if not query_condition[field]: continue
                if field in exact_match_fields:
                    query = query.filter(getattr(Project, field) == query_condition[field])
                elif field in fuzzy_match_fields:
                    query = query.filter(getattr(Project, field).like(f'%{query_condition[field]}%'))
                elif field in start_scope_match_fields:
                    query = query.filter(getattr(Project, field.replace('start_time', 'time')) >= query_condition[field])
                elif field in end_scope_match_fields:
                    query = query.filter(getattr(Project, field.replace('end_time', 'time')) <= query_condition[field])

        # 添加排序功能
        if query_condition and query_condition.get('order_by') is not None and query_condition.get('order_direction') is not None:
            order_by = query_condition.get('order_by', 'update_time')  # 默认按更新时间排序
            order_direction = query_condition.get('order_direction', 'desc')  # 默认降序
            
            # 验证排序字段是否有效
            valid_order_fields = ['name', 'create_time', 'update_time']
            if order_by in valid_order_fields:
                print(order_by)
                order_attr = getattr(Project, order_by)
                if order_direction.lower() == 'desc':
                    query = query.order_by(order_attr.desc())
                else:
                    query = query.order_by(order_attr.asc())
        
        # 添加分页功能
        if query_condition and query_condition.get('is_query_page'):
            page_no = query_condition.get('page_no', 1)
            page_size = query_condition.get('page_size', 10)
            query = query.paginate(page=page_no, per_page=page_size, error_out=False)
            projects = query.items
            total = query.total
            pages = query.pages
            return {
                'data': projects,
                'total': total,
                'pages': pages
            }
        else:
            return query.all()
