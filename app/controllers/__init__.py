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

from .auth import LoginResource, RegisterResource, LogoutResource
auth_ns.add_resource(LoginResource, '/login')
auth_ns.add_resource(RegisterResource, '/register')
auth_ns.add_resource(LogoutResource, '/logout')

api.add_namespace(auth_ns)