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

# 目录（属于项目）
category_ns = Namespace('category', description='目录相关接口', path='/category')
from .category import CategoryResource, AddCategoruResource
category_ns.add_resource(CategoryResource, '/<string:category_id>')
category_ns.add_resource(AddCategoruResource, '')

api.add_namespace(category_ns)

# 文章
article_ns = Namespace('article', description='文章相关接口', path='/article')
from .article import ArticleResource, AddArticleResource, CategoryArticleResource
article_ns.add_resource(ArticleResource, '/<string:article_id>')
article_ns.add_resource(AddArticleResource, '')
article_ns.add_resource(CategoryArticleResource, '/category-article')

api.add_namespace(article_ns)

# 字典
dict_ns = Namespace('dict', description='字典相关接口', path='/dict')
from .dict import SingleDictResource, AddDictResource, UserDictResource
dict_ns.add_resource(SingleDictResource, '/<int:dict_id>')
dict_ns.add_resource(AddDictResource, '')
dict_ns.add_resource(UserDictResource, '/user-dict')

api.add_namespace(dict_ns)

# 时间线
timeline_ns = Namespace('timeline', description='时间线相关接口', path='/timeline')
from .timeline import SingleTimelineResource, AddTimelineResource, UserTimelineResource
timeline_ns.add_resource(SingleTimelineResource, '/<string:timeline_id>')
timeline_ns.add_resource(AddTimelineResource, '')
timeline_ns.add_resource(UserTimelineResource, '/user-timeline')

api.add_namespace(timeline_ns)
