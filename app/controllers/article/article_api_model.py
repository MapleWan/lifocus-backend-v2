from app.controllers import article_ns
from flask_restx import fields

article_with_content_model = article_ns.model('ArticleWithContent', {
    'id': fields.String(description='文章 ID'),
    'category_id': fields.Integer(description='文章分类 ID'),
    'type': fields.String(description='文章类型'),
    'title': fields.String(description='文章标题'),
    'content': fields.String(description='文章内容'),
    'status': fields.String(description='文章状态'),
    'is_shared': fields.Boolean(description='文章是否共享'),
    'is_deleted': fields.Boolean(description='文章是否删除'),
    'create_time': fields.String(description='文章创建时间'),
    'update_time': fields.String(description='文章更新时间'),
})

article_no_content_model = article_ns.model('ArticleNoContent', {
    'id': fields.String(description='文章 ID'),
    'category_id': fields.Integer(description='文章分类 ID'),
    'type': fields.String(description='文章类型'),
    'title': fields.String(description='文章标题'),
    'status': fields.String(description='文章状态'),
    'is_shared': fields.Boolean(description='文章是否共享'),
    'is_deleted': fields.Boolean(description='文章是否删除'),
    'create_time': fields.String(description='文章创建时间'),
    'update_time': fields.String(description='文章更新时间'),
})

article_with_content_response_model = article_ns.model('ArticleWithContentResponse', {
    'code': fields.Integer(description='状态码'),
    'message': fields.String(description='提示信息'),
    'data': fields.Nested(article_with_content_model, allow_null=True)
})

article_no_content_response_model = article_ns.model('ArticleNoContentResponse', {
    'code': fields.Integer(description='状态码'),
    'message': fields.String(description='提示信息'),
    'data': fields.Nested(article_no_content_model, allow_null=True)
})
