from datetime import datetime
import uuid
from app.extension import db
from app.utils import format_datetime_to_string
from app.enums.timeline_enum import TIMELINE_ERROR_MESSAGE


class Timeline(db.Model):
    __tablename__ = 'timeline'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment='主键，事件ID')
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False, comment='用户ID')
    title = db.Column(db.String(255), nullable=False, comment='事件标题')
    type = db.Column(db.String(64), nullable=False, comment='事件类型')
    content = db.Column(db.Text, nullable=True, comment='事件内容')
    status = db.Column(db.String(64), nullable=False, default='ACTIVE', comment='事件状态')
    description = db.Column(db.String(500), nullable=True, comment='事件描述')
    importance = db.Column(db.Integer, nullable=False, default=1, comment='事件重要级别（1-4级，1为最低，4为最高）')
    is_summaried = db.Column(db.Boolean, nullable=False, default=False, comment='是否总结为日常')
    start_time = db.Column(db.DateTime, nullable=True, comment='事件开始时间')
    end_time = db.Column(db.DateTime, nullable=True, comment='事件结束时间')
    create_time = db.Column(db.DateTime, default=datetime.now(), comment='创建时间')
    update_time = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now(), comment='更新时间')

    # 打印时间线信息
    def dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'type': self.type,
            'content': self.content,
            'status': self.status,
            'description': self.description,
            'importance': self.importance,
            'is_summaried': self.is_summaried,
            'start_time': format_datetime_to_string(self.start_time) if self.start_time else None,
            'end_time': format_datetime_to_string(self.end_time) if self.end_time else None,
            'create_time': format_datetime_to_string(self.create_time),
            'update_time': format_datetime_to_string(self.update_time)
        }

    # 添加时间线事件
    def add_timeline(self):
        db.session.add(self)
        db.session.commit()
        return True, self

    # 更新时间线事件
    def update_timeline(self):
        db.session.add(self)
        db.session.commit()
        return True, self

    # 删除时间线事件
    def soft_delete_timeline(self):
        db.session.delete(self)
        db.session.commit()
        return True, self

    # 根据ID获取时间线事件
    @staticmethod
    def get_timeline_by_id(timeline_id):
        return Timeline.query.filter_by(id=timeline_id).first()

    # 根据用户ID获取时间线事件列表
    @staticmethod
    def get_timelines_by_user_id(user_id):
        return Timeline.query.filter_by(user_id=user_id).all()

    # 根据用户ID和类型获取时间线事件列表
    @staticmethod
    def get_timelines_by_user_and_type(user_id, type):
        return Timeline.query.filter_by(user_id=user_id, type=type).all()

    # 根据用户ID和状态获取时间线事件列表
    @staticmethod
    def get_timelines_by_user_and_status(user_id, status):
        return Timeline.query.filter_by(user_id=user_id, status=status).all()

    # 获取时间线事件列表，带查询条件（分页接口）
    '''
    :param query_condition: 查询条件 
        {
            "title": "event title",
            "type": "WORK",
            "status": "ACTIVE",
            "importance": 3,
            "is_summaried": false,
            "start_time": "2025-12-17 00:00:00",
            "end_time": "2025-12-17 00:00:00",
            "create_start_time": "2025-12-17 00:00:00",
            "create_end_time": "2025-12-17 00:00:00",
            "update_start_time": "2025-12-17 00:00:00",
            "update_end_time: "2025-12-17 00:00:00",
            "is_query_page": true, # 是否使用分页查询
            "page_no": 1, # 页码
            "page_size": 10, # 每页数量
            "order_by": "start_time", # 排序字段: title, type, status, importance, start_time, create_time, update_time
            "order_direction": "asc" # 排序方向: asc, desc
        }
    :return 包含时间线事件列表、总数和总页数的字典
    '''
    @classmethod
    def get_timelines_by_condition(cls, user_id, query_condition=None):
        query = cls.query.filter_by(user_id=user_id)
        
        exact_match_fields = ['type', 'status', 'importance', 'is_summaried']
        fuzzy_match_fields = ['title']
        start_scope_match_fields = ['start_time', 'create_start_time', 'update_start_time']
        end_scope_match_fields = ['end_time', 'create_end_time', 'update_end_time']
        print(query_condition, "查询条件")
        if query_condition:
            for field in query_condition:
                if query_condition[field] is None: continue
                if field in exact_match_fields:
                    query = query.filter(getattr(cls, field) == query_condition[field])
                elif field in fuzzy_match_fields:
                    query = query.filter(getattr(cls, field).like(f'%{query_condition[field]}%'))
                elif field in start_scope_match_fields:
                    tmp_field = field
                    if field != 'start_time':
                        tmp_field = field.replace('start_time', 'time')
                    print("开始时间范围查询字段", tmp_field, query_condition[field])
                    query = query.filter(getattr(cls, tmp_field) >= query_condition[field])
                elif field in end_scope_match_fields:
                    tmp_field = field
                    if field != 'end_time':
                        tmp_field = field.replace('end_time', 'time')
                    print("结束时间范围查询字段", tmp_field, query_condition[field])
                    query = query.filter(getattr(cls, tmp_field) <= query_condition[field])

        # 添加排序功能
        if query_condition and query_condition.get('order_by') is not None and query_condition.get('order_direction') is not None:
            order_by = query_condition.get('order_by', 'create_time')  # 默认按创建时间排序
            order_direction = query_condition.get('order_direction', 'desc')  # 默认降序
            # 验证排序字段是否有效
            valid_order_fields = ['title', 'importance', 'start_time', 'create_time', 'update_time']
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
            timelines = query.items
            total = query.total
            pages = query.pages
            return {
                'data': timelines,
                'total': total,
                'pages': pages
            }
        else:
            return query.all()