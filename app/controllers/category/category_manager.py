
from flask_restx import Resource, reqparse
from app.models import Category, User, Project, Article
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers import category_ns
from flask import request
from app.enums import CATEGORY_ERROR_MESSAGE, CATEGORY_SUCCESS_MESSAGE

class CategoryResource(Resource):
    @jwt_required()
    @category_ns.doc(description='获取目录列表')
    def get(self, category_id):
        """
        获取目录列表
        :return: JSON 格式目录列表
        """
        try:
            category = Category.get_category_by_id(category_id)
            return {'code': 200, 'message': CATEGORY_SUCCESS_MESSAGE['CATEGORY_LIST_SUCCESS'], 'data': category.dict() if category else None}, 200
        except Exception as e:
            return {'code': 500, 'message': CATEGORY_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500

    @jwt_required()
    @category_ns.doc(description='编辑目录')
    def put(self, category_id):
        """
        编辑目录
        :return: JSON 格式目录信息
        """
        
        try:
            current_user_id = get_jwt_identity()
            user = User.get_user_by_id(current_user_id)
            try:
                project_id = request.headers.get('X-Project-Id')
                if not project_id:
                    raise Exception(CATEGORY_ERROR_MESSAGE['PROJECT_ID_NOT_FOUND_ERROR'])
                project = Project.get_project_by_id(project_id)
                parser = reqparse.RequestParser()
                parser.add_argument('parent_id', type=str, required=False, help='父目录ID')
                parser.add_argument('name', type=str, required=False, help='目录名称')
                parser.add_argument('icon', type=str, required=False, help='目录图标')
                parser.add_argument('description', type=str, required=False, help='目录描述')
                args = parser.parse_args()
            except Exception as e:
                return {'code': 400, 'message': CATEGORY_ERROR_MESSAGE['CATEGORY_PARAM_ERROR'] + ': ' + str(e)}, 400
            
            # if not args['name']:
            #     raise Exception(CATEGORY_ERROR_MESSAGE['CATEGORY_NAME_EMPTY_ERROR'])
            category = Category.get_category_by_id(category_id)
            if not category:
                return {'code': 400, 'message': CATEGORY_ERROR_MESSAGE['CATEGORY_NOT_FOUND']}, 400
            is_success, data = category.update_category(args['name'], args['parent_id'], args['icon'], args['description'])
            if is_success:
                return {'code': 200, 'message': CATEGORY_SUCCESS_MESSAGE['CATEGORY_UPDATE_SUCCESS'], 'data': data.dict()}, 200
            else:
                return {'code': 400, 'message': CATEGORY_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + data}, 400
        except Exception as e:
            return {'code': 500, 'message': CATEGORY_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500

    @jwt_required()
    @category_ns.doc(description='删除目录')
    def delete(self, category_id):
        """
        删除目录
        """
        try:
            category = Category.get_category_by_id(category_id)
            if not category:
                return {'code': 400, 'message': CATEGORY_ERROR_MESSAGE['CATEGORY_NOT_FOUND']}, 400
            is_success, data = category.soft_delete()
            if is_success:
                return {'code': 200, 'message': CATEGORY_SUCCESS_MESSAGE['CATEGORY_DELETE_SUCCESS'], 'data': data.dict()}, 200
            else:
                return {'code': 400, 'message': CATEGORY_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + data}, 400
        except Exception as e:
            return {'code': 500, 'message': CATEGORY_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500

class AddCategoruResource(Resource):
    @jwt_required()
    @category_ns.doc(description='获取目录列表')
    def get(self):
        """
        获取目录列表
        :return: JSON 格式目录列表
        """
        try:
            project_id = request.headers.get('X-Project-Id')
            if not project_id:
                return {'code': 400, 'message': CATEGORY_ERROR_MESSAGE['PROJECT_ID_NOT_FOUND_ERROR']}, 400
            
            # categories = Category.get_tree(project_id)
            categories = Category.get_all(project_id)
            return {'code': 200, 'message': CATEGORY_SUCCESS_MESSAGE['CATEGORY_LIST_SUCCESS'], 'data': categories}, 200
        except Exception as e:
            return {'code': 500, 'message': CATEGORY_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500
        
    @jwt_required()
    @category_ns.doc(description='创建')
    def post(self):
        """
        创建目录
        :return: JSON 格式目录信息
        """
        try:
            current_user_id = get_jwt_identity()
            user = User.get_user_by_id(current_user_id)
            try:
                project_id = request.headers.get('X-Project-Id')
                if not project_id:
                    raise Exception(CATEGORY_ERROR_MESSAGE['PROJECT_ID_NOT_FOUND_ERROR'])
                project = Project.get_project_by_id(project_id)
                parser = reqparse.RequestParser()
                parser.add_argument('parent_id', type=str, required=False, help='父目录ID')
                parser.add_argument('name', type=str, required=True, help='目录名称')
                parser.add_argument('icon', type=str, required=False, help='目录图标')
                parser.add_argument('description', type=str, required=False, help='目录描述')
                args = parser.parse_args()
            except Exception as e:
                return {'code': 400, 'message': CATEGORY_ERROR_MESSAGE['CATEGORY_PARAM_ERROR'] + ': ' + str(e)}, 400
            if not args['parent_id']:
                args['parent_id'] = None
            category, msg = Category.add_category(
                project_id, args['name'], args['parent_id'], args['icon'], args['description'])
            if category:
                return {'code': 200, 'message': CATEGORY_SUCCESS_MESSAGE['CATEGORY_ADD_SUCCESS'], 'data': category.dict()}, 200
            else:
                return {'code': 400, 'message': CATEGORY_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + msg}, 400
        except Exception as e:
            return {'code': 500, 'message': CATEGORY_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500
