import os
import datetime
from flask_restx import Resource, reqparse
from sqlalchemy.engine import default
from app.controllers import project_ns
from app.models import Project, User

from app.enums import PROJECT_ERROR_MESSAGE, PROJECT_SUCCESS_MESSAGE, PROJECT_TYPE, PROJECT_STATUS
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils import del_user_project_dir, make_user_project_dir
from app.utils.enum_check import check_enum

from .project_api_model import add_project_model, project_list_response_model, project_page_response_model, update_project_model, project_response_model

class SingleProjectResource(Resource):

    '''
    根据项目 id 获取项目信息
    '''
    @jwt_required()
    @project_ns.doc(description='根据项目 id 获取项目信息')
    @project_ns.marshal_with(project_response_model)
    def get(self, project_id):
        try:
            if project_id:
                project = Project.get_project_by_id(project_id)
                if project:
                    return {'code': 200, 'message': '查询成功', 'data': project.dict()}, 200
                else:
                    return {'code': 404, 'message': PROJECT_ERROR_MESSAGE['PROJECT_NOT_FOUND']}, 404
            else:
                return {'code': 404, 'message': PROJECT_ERROR_MESSAGE['PROJECT_ID_EMPTY_ERROR']}, 404
        except Exception as e:
            return {'code': 500, 'message': PROJECT_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500

    '''
    根据项目 id 更新项目信息
    '''
    @jwt_required()
    @project_ns.doc(description='根据项目 id 更新项目')
    @project_ns.expect(update_project_model)
    @project_ns.marshal_with(project_response_model)
    def put(self, project_id):
        try:
            if project_id:
                current_user_id = get_jwt_identity()
                try:
                    parser = reqparse.RequestParser()
                    parser.add_argument('type', type=str, required=False)
                    parser.add_argument('name', type=str, required=False)
                    parser.add_argument('icon', type=str, required=False)
                    parser.add_argument('description', type=str, required=False)
                    parser.add_argument('folder', type=str, required=False)
                    parser.add_argument('status', type=str, required=False)

                    args = parser.parse_args()
                except:
                    raise Exception(PROJECT_ERROR_MESSAGE['PROJECT_PARAM_ERROR'])

                if not check_enum([args['type'], args['status']], [PROJECT_TYPE, PROJECT_STATUS]):
                    return {'code': 400, 'message': PROJECT_ERROR_MESSAGE['PROJECT_TYPE_STATUS_ERROR']}, 400
                repeat_project = Project.get_project_by_name(current_user_id, args['name'], is_filter_deleted=False)
                if repeat_project and repeat_project.id != project_id:
                    return {'code': 400, 'message': PROJECT_ERROR_MESSAGE['PROJECT_NAME_EXIST_ERROR']}, 400
                project = Project.get_project_by_id(project_id)
                if project:
                    origin_project_name = project.name
                    # 简化更新逻辑，使用循环更新属性
                    update_fields = ['type', 'name', 'icon',
                                     'description', 'folder', 'status']
                    for field in update_fields:
                        if args[field]:  # 只有当参数存在且非空时才更新
                            setattr(project, field, args[field])
                    project.update_time = datetime.datetime.now()
                    project.update_project()

                    user = User.get_user_by_id(current_user_id)
                    make_user_project_dir(user.username, origin_project_name, project.name)
                    return {'code': 200, 'message': PROJECT_SUCCESS_MESSAGE['PROJECT_UPDATE_SUCCESS'], 'data': project.dict()}, 200
                else:
                    return {'code': 404, 'message': PROJECT_ERROR_MESSAGE['PROJECT_NOT_FOUND']}, 404
            else:
                return {'code': 404, 'message': PROJECT_ERROR_MESSAGE['PROJECT_ID_EMPTY_ERROR']}, 404
        except Exception as e:
            return {'code': 500, 'message': PROJECT_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500

    '''
    根据项目 id 删除项目
    '''
    @jwt_required()
    @project_ns.doc(description='根据项目 id 删除项目')
    def delete(self, project_id):
        try:
            if project_id:
                project = Project.get_project_by_id(project_id)
                if project:
                    # project.delete_project()
                    project.is_deleted = True
                    project.delete_time = datetime.datetime.now()
                    project.update_project()
                    user = User.get_user_by_id(get_jwt_identity())
                    del_user_project_dir(user.username, project.name)
                    return {'code': 200, 'message': PROJECT_SUCCESS_MESSAGE['PROJECT_DELETE_SUCCESS']}, 200
                else:
                    return {'code': 404, 'message': PROJECT_ERROR_MESSAGE['PROJECT_NOT_FOUND']}, 404
            else:
                return {'code': 404, 'message': PROJECT_ERROR_MESSAGE['PROJECT_ID_EMPTY_ERROR']}, 404
        except Exception as e:
            return {'code': 500, 'message': PROJECT_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500

class AddProjectResource(Resource):
    '''
    添加项目
    '''
    @jwt_required()
    @project_ns.expect(add_project_model)
    @project_ns.marshal_with(project_response_model)
    @project_ns.doc(description='添加项目')
    def post(self):
        try:
            current_user_id = get_jwt_identity()
            user = User.get_user_by_id(current_user_id)
            try:
                parser = reqparse.RequestParser()
                parser.add_argument('type', type=str, required=True)
                parser.add_argument('name', type=str, required=True)
                parser.add_argument('icon', type=str, required=False)
                parser.add_argument('description', type=str, required=False)
                # parser.add_argument('folder', type=str, required=False)
                parser.add_argument('status', type=str, required=True)
                args = parser.parse_args()
            except Exception as e:
                raise Exception(PROJECT_ERROR_MESSAGE['PROJECT_PARAM_ERROR'])
            if not check_enum([args['type'], args['status']], [PROJECT_TYPE, PROJECT_STATUS]):
                return {'code': 400, 'message': PROJECT_ERROR_MESSAGE['PROJECT_TYPE_STATUS_ERROR']}, 400
            if Project.get_project_by_name(current_user_id, args['name'], is_filter_deleted=False):
                return {'code': 400, 'message': PROJECT_ERROR_MESSAGE['PROJECT_NAME_EXIST_ERROR']}, 400
            project = Project(
                user_id=current_user_id,
                type=args['type'],
                name=args['name'],
                icon=args['icon'],
                description=args['description'],
                folder= os.path.join(os.path.expanduser('~'), 'lifocus_data', user.username, args['name']),
                status=args['status']
            )
            project.add_project()
            make_user_project_dir(user.username, '', project.name)
            return {'code': 200, 'message': PROJECT_SUCCESS_MESSAGE['PROJECT_ADD_SUCCESS'], 'data': project}, 200
        except Exception as e:
            return {'code': 500, 'message': PROJECT_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500

class UserProjectResource(Resource):
    '''
    获取用户所有项目，未分页
    '''
    @jwt_required()
    @project_ns.doc(description='获取用户所有项目【未分页，带查询条件】')
    @project_ns.marshal_with(project_list_response_model)
    def get(self):
        try:
            current_user_id = get_jwt_identity()
            try:
                parse = reqparse.RequestParser()
                parse.add_argument('type', type=str, required=False, help='项目类型')
                parse.add_argument('name', type=str, required=False, help='项目名称')
                parse.add_argument('status', type=str, required=False, help='项目状态')
                parse.add_argument('create_start_time', type=str, required=False, help='项目创建开始时间')
                parse.add_argument('create_end_time', type=str, required=False, help='项目创建结束时间')
                parse.add_argument('update_start_time', type=str, required=False, help='项目更新开始时间')
                parse.add_argument('update_end_time', type=str, required=False, help='项目更新结束时间')
                parse.add_argument('order_by', type=str, default='update_time', required=False, help='项目排序字段')
                parse.add_argument('order_direction', type=str, default='desc', required=False, help='项目排序方向')
                args = parse.parse_args()
            except Exception as e:
                raise Exception(PROJECT_ERROR_MESSAGE['PROJECT_PARAM_ERROR'])
            print(args)
            projects = Project.get_projects_by_user_id(current_user_id, args)
            return {'code': 200, 'message': '查询成功', 'data': projects}, 200
        except Exception as e:
            return {'code': 500, 'message': PROJECT_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500
    
    '''
    获取用户项目列表
    '''
    @jwt_required()
    @project_ns.doc(description='获取用户项目列表【分页，带查询条件】')
    @project_ns.marshal_with(project_page_response_model)
    def post(self):
        try:
            current_user_id = get_jwt_identity()
            try:
                parse = reqparse.RequestParser()
                parse.add_argument('type', type=str, required=False, help='项目类型')
                parse.add_argument('name', type=str, required=False, help='项目名称')
                parse.add_argument('status', type=str, required=False, help='项目状态')
                parse.add_argument('create_start_time', type=str, required=False, help='项目创建开始时间')
                parse.add_argument('create_end_time', type=str, required=False, help='项目创建结束时间')
                parse.add_argument('update_start_time', type=str, required=False, help='项目更新开始时间')
                parse.add_argument('update_end_time', type=str, required=False, help='项目更新结束时间')
                parse.add_argument('page_no', type=int, default=1, required=True, help='页码')
                parse.add_argument('page_size', type=int, default=10, required=True, help='页大小')
                parse.add_argument('order_by', type=str, default='update_time', required=False, help='项目排序字段')
                parse.add_argument('order_direction', type=str, default='desc', required=False, help='项目排序方向')
                args = parse.parse_args()
                args['is_query_page'] = True
            except Exception as e:
                raise Exception(PROJECT_ERROR_MESSAGE['PROJECT_PARAM_ERROR'])
            page_res = Project.get_projects_by_user_id(current_user_id, args)
            return {
                'code': 200, 'message': '查询成功', 
                'data': {
                    'page_no': args['page_no'],
                    'page_size': args['page_size'],
                    'pages': page_res['pages'],
                    'total': page_res['total'],
                    'data': page_res['data']
                }
            }, 200
        except Exception as e:
            return {'code': 500, 'message': PROJECT_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500
