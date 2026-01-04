from app.controllers import project_ns
from flask_restx import fields

project_model = project_ns.model('Project', {
    'id': fields.String(required=True, description='项目ID'),
    'type': fields.String(required=True, description='项目类型'),
    'name': fields.String(required=True, description='项目名称'),
    'icon': fields.String(required=True, description='项目图标'),
    'description': fields.String(required=True, description='项目描述'),
    'status': fields.String(required=True, description='项目状态'),
    'create_time': fields.String(required=True, description='项目创建时间'),
    'update_time': fields.String(required=True, description='项目更新时间')
})

project_page_model = project_ns.model('ProjectPage', {
    'page_no': fields.Integer(required=True, description='页码'),
    'page_size': fields.Integer(required=True, description='每页数量'),
    'pages': fields.Integer(required=True, description='总页数'),
    'total': fields.Integer(required=True, description='总数'),
    'data': fields.List(fields.Nested(project_model), description='项目数据列表', allow_null=True)
})

add_project_model = project_ns.model('AddProjectModel', {
    'type': fields.String(required=True, description='项目类型'),
    'name': fields.String(required=True, description='项目名称'),
    'icon': fields.String(required=False, description='项目图标'),
    'description': fields.String(required=False, description='项目描述'),
    'status': fields.String(required=True, description='项目状态')
})

update_project_model = project_ns.model('UpdateProjectModel', {
    'type': fields.String(required=False, description='项目类型'),
    'name': fields.String(required=False, description='项目名称'),
    'icon': fields.String(required=False, description='项目图标'),
    'description': fields.String(required=False, description='项目描述'),
    'status': fields.String(required=False, description='项目状态')
})

project_response_model = project_ns.model('ProjectResponse', {
    'code': fields.Integer(required=True, description='响应码'),
    'message': fields.String(required=True, description='响应信息'),
    'data': fields.Nested(project_model, description='项目数据', allow_null=True)
})

project_list_response_model = project_ns.model('ProjectListResponse', {
    'code': fields.Integer(required=True, description='响应码'),
    'message': fields.String(required=True, description='响应信息'),
    'data': fields.List(fields.Nested(project_model), description='项目数据列表', allow_null=True)
})

project_page_response_model = project_ns.model('ProjectPageResponse', {
    'code': fields.Integer(required=True, description='响应码'),
    'message': fields.String(required=True, description='响应信息'),
    'data': fields.Nested(project_page_model, description='项目分页查询数据', allow_null=True)
})
