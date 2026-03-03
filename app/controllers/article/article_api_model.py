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
    'share_password': fields.String(description='文章分享密码'),
    'is_deleted': fields.Boolean(description='文章是否删除'),
    'create_time': fields.String(description='文章创建时间'),
    'update_time': fields.String(description='文章更新时间'),
})

category_model = article_ns.model('Category', {
    'id': fields.Integer(description='分类 ID'),
    'name': fields.String(description='分类名称')
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
    'category': fields.Nested(category_model, description='文章分类')
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

article_no_content_page_model = article_ns.model('ArticleNoContentPage', {
    'page_no': fields.Integer(description='页码'),
    'page_size': fields.Integer(description='页大小'),
    'pages': fields.Integer(description='总页数'),
    'total': fields.Integer(description='总记录数'),
    'data': fields.List(fields.Nested(article_no_content_model), description='文章数据列表', allow_null=True)
})

article_no_content_page_response_model = article_ns.model('ArticleNoContentPageResponse', {
    'code': fields.Integer(description='状态码'),
    'message': fields.String(description='提示信息'),
    'data': fields.Nested(article_no_content_page_model, allow_null=True)
})

# 分享文章内容模型（不包含敏感字段如 share_password、category_id）
share_article_model = article_ns.model('ShareArticle', {
    'id': fields.String(description='文章 ID'),
    'title': fields.String(description='文章标题'),
    'content': fields.String(description='文章内容'),
    'type': fields.String(description='文章类型'),
    'create_time': fields.String(description='创建时间'),
    'update_time': fields.String(description='更新时间'),
})

share_article_response_model = article_ns.model('ShareArticleResponse', {
    'code': fields.Integer(description='状态码'),
    'message': fields.String(description='响应消息'),
    'data': fields.Nested(share_article_model, description='分享文章数据', allow_null=True),
})
