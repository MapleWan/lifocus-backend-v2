from flask import Blueprint
from flask_restx import Api, Namespace

api_blueprint = Blueprint('api', __name__, url_prefix='/api')
api = Api(
    api_blueprint,
    version='1.0',
    title='LiFocus API',
    doc='/docs/',
    description='LiFocus API',

    authorizations={
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'JWT Token格式: Bearer <token>'
        }
    },
    security='Bearer'
)


auth_ns = Namespace('auth', description='认证相关接口', path='/auth')

# 登录注册
from .auth import LoginResource, RegisterResource, LogoutResource
auth_ns.add_resource(LoginResource, '/login')
auth_ns.add_resource(RegisterResource, '/register')
auth_ns.add_resource(LogoutResource, '/logout')

api.add_namespace(auth_ns)

# 项目
project_ns = Namespace('project', description='项目相关接口', path='/project')
from .project import SingleProjectResource, AddProjectResource, UserProjectResource
project_ns.add_resource(SingleProjectResource, '/<string:project_id>')
project_ns.add_resource(AddProjectResource, '')
project_ns.add_resource(UserProjectResource, '/user-project')

api.add_namespace(project_ns)
