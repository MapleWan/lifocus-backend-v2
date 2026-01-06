from flask import request
from flask_restx import Resource, reqparse
from app.models import Dict, User
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers import dict_ns
from app.utils import check_enum
from .dict_api_model import dict_response_model, dict_list_response_model, dict_page_response_model, add_dict_model, update_dict_model
from datetime import datetime
from app.enums import DICT_ERROR_MESSAGE, DICT_SUCCESS_MESSAGE


class SingleDictResource(Resource):
    '''
    根据字典 id 获取字典信息
    '''
    @jwt_required()
    @dict_ns.doc(description='根据字典 id 获取字典信息')
    @dict_ns.marshal_with(dict_response_model)
    def get(self, dict_id):
        try:
            if dict_id:
                current_user_id = get_jwt_identity()
                dict_item = Dict.get_dict_by_id(dict_id)
                if dict_item and dict_item.user_id == current_user_id:
                    return {'code': 200, 'message': DICT_SUCCESS_MESSAGE['DICT_DETAIL_SUCCESS'], 'data': dict_item.dict()}, 200
                else:
                    return {'code': 404, 'message': DICT_ERROR_MESSAGE['DICT_NOT_FOUND']}, 404
            else:
                return {'code': 404, 'message': DICT_ERROR_MESSAGE['DICT_ID_EMPTY_ERROR']}, 404
        except Exception as e:
            return {'code': 500, 'message': DICT_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500

    '''
    根据字典 id 更新字典信息
    '''
    @jwt_required()
    @dict_ns.doc(description='根据字典 id 更新字典')
    @dict_ns.expect(update_dict_model)
    @dict_ns.marshal_with(dict_response_model)
    def put(self, dict_id):
        try:
            if dict_id:
                current_user_id = get_jwt_identity()
                current_user = User.get_user_by_id(current_user_id)
                
                try:
                    parser = reqparse.RequestParser()
                    parser.add_argument('type', type=str, required=False)
                    parser.add_argument('code', type=str, required=False)
                    parser.add_argument('value', type=str, required=False)
                    parser.add_argument('description', type=str, required=False)

                    args = parser.parse_args()
                except:
                    return {'code': 400, 'message': DICT_ERROR_MESSAGE['DICT_PARAM_ERROR']}, 400

                dict_item = Dict.get_dict_by_id(dict_id)
                if dict_item and dict_item.user_id == current_user_id:
                    # 检查是否有重复的编码
                    if args['code'] and args['code'] != dict_item.code:
                        existing_dict = Dict.get_dict_by_user_type_code(current_user_id, dict_item.type, args['code'])
                        if existing_dict:
                            return {'code': 400, 'message': DICT_ERROR_MESSAGE['DICT_CODE_EXIST_ERROR']}, 400

                    # 更新字典信息
                    update_fields = ['type', 'code', 'value', 'description']
                    for field in update_fields:
                        if args[field] is not None:
                            setattr(dict_item, field, args[field])

                    dict_item.update_time = datetime.now()
                    dict_item.update_dict()

                    return {'code': 200, 'message': DICT_SUCCESS_MESSAGE['DICT_UPDATE_SUCCESS'], 'data': dict_item.dict()}, 200
                else:
                    return {'code': 404, 'message': DICT_ERROR_MESSAGE['DICT_NOT_FOUND']}, 404
            else:
                return {'code': 404, 'message': DICT_ERROR_MESSAGE['DICT_ID_EMPTY_ERROR']}, 404
        except Exception as e:
            return {'code': 500, 'message': DICT_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500

    '''
    根据字典 id 删除字典
    '''
    @jwt_required()
    @dict_ns.doc(description='根据字典 id 删除字典')
    def delete(self, dict_id):
        try:
            if dict_id:
                current_user_id = get_jwt_identity()
                dict_item = Dict.get_dict_by_id(dict_id)
                if dict_item and dict_item.user_id == current_user_id:
                    dict_item.delete_dict()
                    return {'code': 200, 'message': DICT_SUCCESS_MESSAGE['DICT_DELETE_SUCCESS']}, 200
                else:
                    return {'code': 404, 'message': DICT_ERROR_MESSAGE['DICT_NOT_FOUND']}, 404
            else:
                return {'code': 404, 'message': DICT_ERROR_MESSAGE['DICT_ID_EMPTY_ERROR']}, 404
        except Exception as e:
            return {'code': 500, 'message': DICT_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500


class AddDictResource(Resource):
    '''
    添加字典
    '''
    @jwt_required()
    @dict_ns.expect(add_dict_model)
    @dict_ns.marshal_with(dict_response_model)
    @dict_ns.doc(description='添加字典')
    def post(self):
        try:
            current_user_id = get_jwt_identity()
            current_user = User.get_user_by_id(current_user_id)
            
            try:
                parser = reqparse.RequestParser()
                parser.add_argument('type', type=str, required=True)
                parser.add_argument('code', type=str, required=True)
                parser.add_argument('value', type=str, required=True)
                parser.add_argument('description', type=str, required=False)
                args = parser.parse_args()
            except Exception as e:
                return {'code': 400, 'message': DICT_ERROR_MESSAGE['DICT_PARAM_ERROR']}, 400

            # 检查编码是否已存在
            existing_dict = Dict.get_dict_by_user_type_code(current_user_id, args['type'], args['code'])
            if existing_dict:
                return {'code': 400, 'message': DICT_ERROR_MESSAGE['DICT_CODE_EXIST_ERROR']}, 400

            dict_item = Dict(
                user_id=current_user_id,
                type=args['type'],
                code=args['code'],
                value=args['value'],
                description=args['description']
            )

            success, result = dict_item.add_dict()
            if success:
                return {'code': 200, 'message': DICT_SUCCESS_MESSAGE['DICT_ADD_SUCCESS'], 'data': result.dict()}, 200
            else:
                return {'code': 400, 'message': result}, 400
        except Exception as e:
            return {'code': 500, 'message': DICT_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500


class UserDictResource(Resource):

    '''
    获取用户字典列表
    '''
    @jwt_required()
    @dict_ns.doc(description='获取用户字典列表')
    @dict_ns.marshal_with(dict_list_response_model)
    def get(self):
        try:
            current_user_id = get_jwt_identity()
            try:
                parser = reqparse.RequestParser()
                parser.add_argument('type', type=str, required=False, help='字典类型')
                args = parser.parse_args()
            except Exception as e:
                return {'code': 400, 'message': DICT_ERROR_MESSAGE['DICT_PARAM_ERROR']}, 400
            args['order_by'] = 'value'
            args['order_direction'] = 'asc'
            print(args)
            dicts = Dict.get_dicts_by_condition(current_user_id, args)
            dict_list = [dict_item.dict() for dict_item in dicts]
            return {'code': 200, 'message': DICT_SUCCESS_MESSAGE['DICT_LIST_SUCCESS'], 'data': dict_list}, 200
        except Exception as e:
            return {'code': 500, 'message': DICT_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500
    
    '''
    获取用户字典列表
    '''
    @jwt_required()
    @dict_ns.doc(description='获取用户字典列表【分页，带查询条件】')
    @dict_ns.marshal_with(dict_page_response_model)
    def post(self):
        try:
            current_user_id = get_jwt_identity()
            try:
                parse = reqparse.RequestParser()
                parse.add_argument('type', type=str, required=False, help='字典类型')
                parse.add_argument('code', type=str, required=False, help='字典编码')
                parse.add_argument('value', type=str, required=False, help='字典值')
                parse.add_argument('description', type=str, required=False, help='字典描述')
                parse.add_argument('create_start_time', type=str, required=False, help='创建开始时间')
                parse.add_argument('create_end_time', type=str, required=False, help='创建结束时间')
                parse.add_argument('update_start_time', type=str, required=False, help='更新开始时间')
                parse.add_argument('update_end_time', type=str, required=False, help='更新结束时间')
                # parse.add_argument('is_query_page', type=bool, required=False, help='是否分页查询')
                parse.add_argument('page_no', type=int, required=False, default=1, help='页码')
                parse.add_argument('page_size', type=int, required=False, default=10, help='每页数量')
                parse.add_argument('order_by', type=str, required=False, help='排序字段')
                parse.add_argument('order_direction', type=str, required=False, help='排序方向')
                
                args = parse.parse_args()
            except Exception as e:
                return {'code': 400, 'message': DICT_ERROR_MESSAGE['DICT_PARAM_ERROR']}, 400

            # query_condition = {}
            # for arg in args:
            #     if args[arg] is not None:
            #         query_condition[arg] = args[arg]
            args['is_query_page'] = True
            page_res = Dict.get_dicts_by_condition(current_user_id, args)
            return {'code': 200, 'message': DICT_SUCCESS_MESSAGE['DICT_LIST_SUCCESS'], 'data': {
                'page_no': args['page_no'],
                'page_size': args['page_size'],
                'total': page_res['total'],
                'pages': page_res['pages'],
                'data': page_res['data']
            }}, 200
        except Exception as e:
            return {'code': 500, 'message': DICT_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500
