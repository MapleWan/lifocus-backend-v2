from datetime import datetime
from app.extension import db
from app.utils import format_datetime_to_string
from app.enums.dict_enum import DICT_ERROR_MESSAGE


class Dict(db.Model):
    __tablename__ = 'dict'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='字典ID')
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False, comment='用户ID')
    type = db.Column(db.String(64), nullable=False, comment='字典类型')
    code = db.Column(db.String(64), nullable=False, comment='字典编码')
    value = db.Column(db.Text, nullable=False, comment='字典值')
    description = db.Column(db.String(255), nullable=True, comment='字典描述')
    create_time = db.Column(db.DateTime, default=datetime.now(), comment='创建时间')
    update_time = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now(), comment='更新时间')

    # 打印字典信息
    def dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'code': self.code,
            'value': self.value,
            'description': self.description,
            'create_time': format_datetime_to_string(self.create_time),
            'update_time': format_datetime_to_string(self.update_time)
        }

    # 添加字典
    def add_dict(self):
        existing_dict = Dict.query.filter_by(user_id=self.user_id, type=self.type, code=self.code).first()
        if existing_dict:
            return False, DICT_ERROR_MESSAGE['DICT_CODE_EXIST_ERROR']
        db.session.add(self)
        db.session.commit()
        return True, self

    # 更新字典
    def update_dict(self):
        db.session.add(self)
        db.session.commit()
        return True, self

    # 删除字典
    def delete_dict(self):
        db.session.delete(self)
        db.session.commit()
        return True, self

    # 根据ID获取字典
    @staticmethod
    def get_dict_by_id(dict_id):
        return Dict.query.filter_by(id=dict_id).first()

    # 根据用户ID、类型和编码获取字典
    @staticmethod
    def get_dict_by_user_type_code(user_id, type, code):
        return Dict.query.filter_by(user_id=user_id, type=type, code=code).first()

    # 根据用户ID和类型获取字典列表
    @staticmethod
    def get_dicts_by_user_type(user_id, type):
        return Dict.query.filter_by(user_id=user_id, type=type).all()

    # 根据用户ID获取字典列表
    @staticmethod
    def get_dicts_by_user_id(user_id):
        return Dict.query.filter_by(user_id=user_id).all()

    # 获取字典列表，带查询条件（分页接口）
    '''
    :param query_condition: 查询条件 
        {
            "type": "LANGUAGE",
            "code": "en",
            "value": "English", 
            "description": "description",
            "create_start_time": "2025-12-17 00:00:00",
            "create_end_time": "2025-12-17 00:00:00",
            "update_start_time": "2025-12-17 00:00:00",
            "update_end_time: "2025-12-17 00:00:00",
            "is_query_page": true, # 是否使用分页查询
            "page_no": 1, # page: 页码
            "page_size": 10, # 每页数量
            "order_by": "value", # 排序字段: value, create_time, update_time
            "order_direction": "asc" # 排序方向: asc, desc
        }
    :return 包含字典列表、总数和总页数的字典
    '''
    @classmethod
    def get_dicts_by_condition(cls, user_id, query_condition=None):
        query = cls.query.filter_by(user_id=user_id)
        
        exact_match_fields = ['type', 'code']
        fuzzy_match_fields = ['value', 'description']
        start_scope_match_fields = ['create_start_time', 'update_start_time']
        end_scope_match_fields = ['create_end_time', 'update_end_time']

        if query_condition:
            for field in query_condition:
                if not query_condition[field]: continue
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
            valid_order_fields = ['value', 'create_time', 'update_time']
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
            dicts = query.items
            total = query.total
            pages = query.pages
            print(pages, total)
            return {
                'data': dicts,
                'total': total,
                'pages': pages
            }
        else:
            return query.all()