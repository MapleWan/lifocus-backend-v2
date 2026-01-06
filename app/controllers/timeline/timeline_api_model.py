from app.controllers import timeline_ns
from flask_restx import fields

timeline_model = timeline_ns.model('Timeline', {
    'id': fields.String(required=True, description='时间线事件ID'),
    'user_id': fields.String(required=True, description='用户ID'),
    'title': fields.String(required=True, description='事件标题'),
    'type': fields.String(required=True, description='事件类型'),
    'content': fields.String(required=False, description='事件内容'),
    'status': fields.String(required=True, description='事件状态'),
    'description': fields.String(required=False, description='事件描述'),
    'importance': fields.Integer(required=True, description='事件重要级别'),
    'is_summaried': fields.Boolean(required=True, description='是否总结为日常'),
    'start_time': fields.String(required=False, description='事件开始时间'),
    'end_time': fields.String(required=False, description='事件结束时间'),
    'create_time': fields.String(required=True, description='创建时间'),
    'update_time': fields.String(required=True, description='更新时间')
})

timeline_page_model = timeline_ns.model('TimelinePage', {
    'page_no': fields.Integer(required=True, description='页码'),
    'page_size': fields.Integer(required=True, description='每页数量'),
    'pages': fields.Integer(required=True, description='总页数'),
    'total': fields.Integer(required=True, description='总数'),
    'data': fields.List(fields.Nested(timeline_model), description='时间线事件数据列表', allow_null=True)
})

add_timeline_model = timeline_ns.model('AddTimelineModel', {
    'title': fields.String(required=True, description='事件标题'),
    'type': fields.String(required=True, description='事件类型'),
    'content': fields.String(required=False, description='事件内容'),
    'status': fields.String(required=False, description='事件状态'),
    'description': fields.String(required=False, description='事件描述'),
    'importance': fields.Integer(required=False, description='事件重要级别'),
    'is_summaried': fields.Boolean(required=False, description='是否总结为日常'),
    'start_time': fields.String(required=False, description='事件开始时间'),
    'end_time': fields.String(required=False, description='事件结束时间')
})

update_timeline_model = timeline_ns.model('UpdateTimelineModel', {
    'title': fields.String(required=False, description='事件标题'),
    'type': fields.String(required=False, description='事件类型'),
    'content': fields.String(required=False, description='事件内容'),
    'status': fields.String(required=False, description='事件状态'),
    'description': fields.String(required=False, description='事件描述'),
    'importance': fields.Integer(required=False, description='事件重要级别'),
    'is_summaried': fields.Boolean(required=False, description='是否总结为日常'),
    'start_time': fields.String(required=False, description='事件开始时间'),
    'end_time': fields.String(required=False, description='事件结束时间')
})

timeline_response_model = timeline_ns.model('TimelineResponse', {
    'code': fields.Integer(required=True, description='响应码'),
    'message': fields.String(required=True, description='响应信息'),
    'data': fields.Nested(timeline_model, description='时间线事件数据', allow_null=True)
})

timeline_list_response_model = timeline_ns.model('TimelineListResponse', {
    'code': fields.Integer(required=True, description='响应码'),
    'message': fields.String(required=True, description='响应信息'),
    'data': fields.List(fields.Nested(timeline_model), description='时间线事件数据列表', allow_null=True)
})

timeline_page_response_model = timeline_ns.model('TimelinePageResponse', {
    'code': fields.Integer(required=True, description='响应码'),
    'message': fields.String(required=True, description='响应信息'),
    'data': fields.Nested(timeline_page_model, description='时间线事件分页查询数据', allow_null=True)
})