from app.controllers import dict_ns
from flask_restx import fields

dict_model = dict_ns.model('Dict', {
    'id': fields.Integer(required=True, description='字典ID'),
    'user_id': fields.String(required=True, description='用户ID'),
    'type': fields.String(required=True, description='字典类型'),
    'code': fields.String(required=True, description='字典编码'),
    'value': fields.String(required=True, description='字典值'),
    'description': fields.String(required=False, description='字典描述'),
    'create_time': fields.String(required=True, description='创建时间'),
    'update_time': fields.String(required=True, description='更新时间')
})

dict_page_model = dict_ns.model('DictPage', {
    'page_no': fields.Integer(required=True, description='页码'),
    'page_size': fields.Integer(required=True, description='每页数量'),
    'pages': fields.Integer(required=True, description='总页数'),
    'total': fields.Integer(required=True, description='总数'),
    'data': fields.List(fields.Nested(dict_model), description='字典数据列表', allow_null=True)
})

add_dict_model = dict_ns.model('AddDictModel', {
    'type': fields.String(required=True, description='字典类型'),
    'code': fields.String(required=True, description='字典编码'),
    'value': fields.String(required=True, description='字典值'),
    'description': fields.String(required=False, description='字典描述')
})

update_dict_model = dict_ns.model('UpdateDictModel', {
    'type': fields.String(required=False, description='字典类型'),
    'code': fields.String(required=False, description='字典编码'),
    'value': fields.String(required=False, description='字典值'),
    'description': fields.String(required=False, description='字典描述')
})

dict_response_model = dict_ns.model('DictResponse', {
    'code': fields.Integer(required=True, description='响应码'),
    'message': fields.String(required=True, description='响应信息'),
    'data': fields.Nested(dict_model, description='字典数据', allow_null=True)
})

dict_list_response_model = dict_ns.model('DictListResponse', {
    'code': fields.Integer(required=True, description='响应码'),
    'message': fields.String(required=True, description='响应信息'),
    'data': fields.List(fields.Nested(dict_model), description='字典数据列表', allow_null=True)
})

dict_page_response_model = dict_ns.model('DictPageResponse', {
    'code': fields.Integer(required=True, description='响应码'),
    'message': fields.String(required=True, description='响应信息'),
    'data': fields.Nested(dict_page_model, description='字典分页查询数据', allow_null=True)
})