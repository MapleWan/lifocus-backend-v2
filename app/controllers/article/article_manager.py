from flask import request
from flask_restx import Resource, reqparse
from app.models import Article, User, Project
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers import article_ns
from app.utils import check_enum, rename_article, del_article_from_disk, save_article_to_disk
from .article_api_model import article_with_content_response_model, article_no_content_response_model
from datetime import datetime
import os

from app.enums import ARTICLE_ERROR_MESSAGE, ARTICLE_SUCCESS_MESSAGE, ARTICLE_TYPE, ARTICLE_STATUS
class ArticleResource(Resource):
    @jwt_required()
    @article_ns.doc(description='获取文章详情')
    @article_ns.marshal_with(article_with_content_response_model)
    def get(self, article_id):
        try:
            article = Article.get_article_by_id(article_id)
            if not article:
                return {'code': 404, 'message': ARTICLE_ERROR_MESSAGE['NOT_FOUND']}, 404
            return {'code': 200, 'message': ARTICLE_SUCCESS_MESSAGE['DETAIL_SUCCESS'], 'data': article}, 200
        except Exception as e:
            return {'code': 500, 'message': ARTICLE_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500

    @jwt_required()
    @article_ns.doc(description='更新文章详情')
    @article_ns.marshal_with(article_with_content_response_model)
    def put(self, article_id):
        try:
            project_id = request.headers.get('X-Project-Id')
            user_id = get_jwt_identity()
            current_project = Project.get_project_by_id(project_id)
            current_user = User.get_user_by_id(user_id)
            article = Article.get_article_by_id(article_id)
            if not article:
                return {'code': 404, 'message': ARTICLE_ERROR_MESSAGE['NOT_FOUND']}, 404
            parser = reqparse.RequestParser()
            parser.add_argument('category_id', type=int, required=True)
            parser.add_argument('category_full_path', type=str, required=True)
            parser.add_argument('type', type=str, required=False)
            parser.add_argument('title', type=str, required=False)
            parser.add_argument('content', type=str, required=False)
            parser.add_argument('status', type=str, required=False)
            parser.add_argument('is_shared', type=bool, required=False)
            parser.add_argument('share_password', type=str, required=False)
            try:
                args = parser.parse_args()
            except Exception as e:
                return {'code': 400, 'message': ARTICLE_ERROR_MESSAGE['PARAM_ERROR']}, 400
            if not check_enum([args['type'], args['status']], [ARTICLE_TYPE, ARTICLE_STATUS]):
                return {'code': 400, 'message': ARTICLE_ERROR_MESSAGE['TYPE_STATUS_ERROR']}, 400
            
            existing_article = Article.get_article_by_title_and_category_id(args['title'], args['category_id'])
            if existing_article:
                return {'code': 400, 'message': ARTICLE_ERROR_MESSAGE['ALREADY_TITLE_EXIST']}, 400

            origin_article_title = article.title
            update_fields = ['category_id', 'category_full_path', 'type', 'title', 'content', 'status', 'is_shared', 'share_password']
            for field in update_fields:
                if field in args:
                    setattr(article, field, args[field])
            article.update_time = datetime.now()
            is_success, res = article.update_article()
            if is_success:
                del_article_from_disk(current_user.username, current_project.name, args['category_full_path'], origin_article_title)
                save_article_to_disk(current_user.username, current_project.name, args['category_full_path'], args['title'], args['content'])
                return {'code': 200, 'message': ARTICLE_SUCCESS_MESSAGE['UPDATE_SUCCESS'], 'data': article}, 200
            else:
                return {'code': 400, 'message': res}, 400
        except Exception as e:
            return {'code': 500, 'message': ARTICLE_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500
    
    @jwt_required()
    @article_ns.doc(description='删除文章')
    def delete(self, article_id):
        try:
            project_id = request.headers.get('X-Project-Id')
            user_id = get_jwt_identity()
            current_project = Project.get_project_by_id(project_id)
            current_user = User.get_user_by_id(user_id)
            article = Article.get_article_by_id(article_id)
            if not article:
                return {'code': 404, 'message': ARTICLE_ERROR_MESSAGE['NOT_FOUND']}, 404
            parser = reqparse.RequestParser()
            parser.add_argument('category_full_path', type=str, required=True)
            try:
                args = parser.parse_args()
            except Exception as e:
                raise Exception(ARTICLE_ERROR_MESSAGE['PARAM_ERROR'])
            is_success, res = article.soft_delete_article()
            if is_success:
                del_article_from_disk(current_user.username, current_project.name, args['category_full_path'], article.title)
                return {'code': 200, 'message': ARTICLE_SUCCESS_MESSAGE['DELETE_SUCCESS']}, 200
            else:
                return {'code': 400, 'message': res}, 400
        except Exception as e:
            return {'code': 500, 'message': ARTICLE_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500

class AddArticleResource(Resource):
    @jwt_required()
    @article_ns.doc(description='新建文章')
    @article_ns.marshal_with(article_with_content_response_model)
    def post(self):
        """
        新增文章
        :params: category_id, category_full_path(用于创建存储本地文件使用), type, title, content, status
        """
        try:
            try:
                project_id = request.headers.get('X-Project-Id')
                user_id = get_jwt_identity()
                current_project = Project.get_project_by_id(project_id)
                current_user = User.get_user_by_id(user_id)
                parser = reqparse.RequestParser()
                parser.add_argument('category_id', type=int, required=True)
                parser.add_argument('category_full_path', type=str, required=True)
                parser.add_argument('type', type=str, default='NOTE', required=True)
                parser.add_argument('title', type=str, required=True)
                parser.add_argument('content', type=str, required=True)
                parser.add_argument('status', type=str, default='ACTIVE', required=True)
                args = parser.parse_args()
            except Exception as e:
                raise Exception(ARTICLE_ERROR_MESSAGE['PARAM_ERROR'])
            if not check_enum([args['type'], args['status']], [ARTICLE_TYPE, ARTICLE_STATUS]):
                return {'code': 400, 'message': ARTICLE_ERROR_MESSAGE['TYPE_STATUS_ERROR']}, 400
            if not args['title']:
                return {'code': 400, 'message': ARTICLE_ERROR_MESSAGE['TITLE_EMPTY_ERROR']}, 400
            if not args['content']:
                return {'code': 400, 'message': ARTICLE_ERROR_MESSAGE['CONTENT_EMPTY_ERROR']}, 400
            article = Article(category_id=args['category_id'], type=args['type'], title=args['title'], content=args['content'], status=args['status'])
            is_success, res = article.add_article()
            if is_success: 
                save_article_to_disk(current_user.username, current_project.name, args['category_full_path'], args['title'], args['content'])    
                return {'code': 200, 'message': ARTICLE_SUCCESS_MESSAGE['CREATE_SUCCESS'], 'data': article}, 200
            else:
                return {'code': 400, 'message': res}, 400
        except Exception as e:
            return {'code': 500, 'message': ARTICLE_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500
