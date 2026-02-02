from flask import request
from flask_restx import Resource, reqparse
from app.models import Timeline, User
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.controllers import timeline_ns
from app.utils import check_enum
from .timeline_api_model import timeline_response_model, timeline_list_response_model, timeline_page_response_model, add_timeline_model, update_timeline_model
from datetime import datetime
from app.enums import TIMELINE_ERROR_MESSAGE, TIMELINE_SUCCESS_MESSAGE, TIMELINE_TYPE, TIMELINE_STATUS


class SingleTimelineResource(Resource):
    '''
    根据时间线 id 获取时间线事件信息
    '''
    @jwt_required()
    @timeline_ns.doc(description='根据时间线 id 获取时间线事件信息')
    @timeline_ns.marshal_with(timeline_response_model)
    def get(self, timeline_id):
        try:
            if timeline_id:
                current_user_id = get_jwt_identity()
                timeline_item = Timeline.get_timeline_by_id(timeline_id)
                if timeline_item and timeline_item.user_id == current_user_id:
                    return {'code': 200, 'message': TIMELINE_SUCCESS_MESSAGE['TIMELINE_DETAIL_SUCCESS'], 'data': timeline_item.dict()}, 200
                else:
                    return {'code': 404, 'message': TIMELINE_ERROR_MESSAGE['TIMELINE_NOT_FOUND']}, 404
            else:
                return {'code': 404, 'message': TIMELINE_ERROR_MESSAGE['TIMELINE_ID_EMPTY_ERROR']}, 404
        except Exception as e:
            return {'code': 500, 'message': TIMELINE_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500

    '''
    根据时间线 id 更新时间线事件信息
    '''
    @jwt_required()
    @timeline_ns.doc(description='根据时间线 id 更新时间线事件')
    @timeline_ns.expect(update_timeline_model)
    @timeline_ns.marshal_with(timeline_response_model)
    def put(self, timeline_id):
        try:
            if timeline_id:
                current_user_id = get_jwt_identity()
                current_user = User.get_user_by_id(current_user_id)
                
                try:
                    parser = reqparse.RequestParser()
                    parser.add_argument('title', type=str, required=False)
                    parser.add_argument('type', type=str, required=False)
                    parser.add_argument('content', type=str, required=False)
                    parser.add_argument('status', type=str, required=False)
                    parser.add_argument('description', type=str, required=False)
                    parser.add_argument('importance', type=int, required=False)
                    parser.add_argument('is_summaried', type=bool, required=False)
                    parser.add_argument('start_time', type=str, required=False)
                    parser.add_argument('end_time', type=str, required=False)

                    args = parser.parse_args()
                except:
                    return {'code': 400, 'message': TIMELINE_ERROR_MESSAGE['TIMELINE_PARAM_ERROR']}, 400

                # 检查类型和状态是否合法
                if args['type'] and not check_enum(args['type'], TIMELINE_TYPE):
                    return {'code': 400, 'message': TIMELINE_ERROR_MESSAGE['TIMELINE_PARAM_ERROR']}, 400
                if args['status'] and not check_enum(args['status'], TIMELINE_STATUS):
                    return {'code': 400, 'message': TIMELINE_ERROR_MESSAGE['TIMELINE_PARAM_ERROR']}, 400

                # 检查重要级别范围
                if args['importance'] is not None and (args['importance'] < 1 or args['importance'] > 5):
                    return {'code': 400, 'message': TIMELINE_ERROR_MESSAGE['TIMELINE_IMPORTANCE_RANGE_ERROR']}, 400

                timeline_item = Timeline.get_timeline_by_id(timeline_id)
                if timeline_item and timeline_item.user_id == current_user_id:
                    # 更新时间线事件信息
                    update_fields = ['title', 'type', 'content', 'status', 'description', 
                                   'importance', 'is_summaried', 'start_time', 'end_time']
                    for field in update_fields:
                        if args[field] is not None:
                            setattr(timeline_item, field, args[field])

                    timeline_item.update_time = datetime.now()
                    timeline_item.update_timeline()

                    return {'code': 200, 'message': TIMELINE_SUCCESS_MESSAGE['TIMELINE_UPDATE_SUCCESS'], 'data': timeline_item.dict()}, 200
                else:
                    return {'code': 404, 'message': TIMELINE_ERROR_MESSAGE['TIMELINE_NOT_FOUND']}, 404
            else:
                return {'code': 404, 'message': TIMELINE_ERROR_MESSAGE['TIMELINE_ID_EMPTY_ERROR']}, 404
        except Exception as e:
            return {'code': 500, 'message': TIMELINE_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500

    '''
    根据时间线 id 删除时间线事件
    '''
    @jwt_required()
    @timeline_ns.doc(description='根据时间线 id 删除时间线事件')
    def delete(self, timeline_id):
        try:
            if timeline_id:
                current_user_id = get_jwt_identity()
                timeline_item = Timeline.get_timeline_by_id(timeline_id)
                if timeline_item and timeline_item.user_id == current_user_id:
                    timeline_item.soft_delete_timeline()
                    return {'code': 200, 'message': TIMELINE_SUCCESS_MESSAGE['TIMELINE_DELETE_SUCCESS']}, 200
                else:
                    return {'code': 404, 'message': TIMELINE_ERROR_MESSAGE['TIMELINE_NOT_FOUND']}, 404
            else:
                return {'code': 404, 'message': TIMELINE_ERROR_MESSAGE['TIMELINE_ID_EMPTY_ERROR']}, 404
        except Exception as e:
            return {'code': 500, 'message': TIMELINE_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500


class AddTimelineResource(Resource):
    '''
    添加时间线事件
    '''
    @jwt_required()
    @timeline_ns.expect(add_timeline_model)
    @timeline_ns.marshal_with(timeline_response_model)
    @timeline_ns.doc(description='添加时间线事件')
    def post(self):
        try:
            current_user_id = get_jwt_identity()
            current_user = User.get_user_by_id(current_user_id)
            
            try:
                parser = reqparse.RequestParser()
                parser.add_argument('title', type=str, required=True, help='事件标题不能为空')
                parser.add_argument('type', type=str, required=True, help='事件类型不能为空')
                parser.add_argument('content', type=str, required=False)
                parser.add_argument('status', type=str, default='PROGRESSING', required=False)
                parser.add_argument('description', type=str, required=False)
                parser.add_argument('importance', type=int, default = 1, required=False)
                parser.add_argument('is_summaried', type=bool, default= False, required=False)
                parser.add_argument('start_time', type=str, required=False)
                parser.add_argument('end_time', type=str, required=False)
                args = parser.parse_args()
            except Exception as e:
                return {'code': 400, 'message': TIMELINE_ERROR_MESSAGE['TIMELINE_PARAM_ERROR']}, 400

            # 检查标题和类型是否为空
            if not args['title']:
                return {'code': 400, 'message': TIMELINE_ERROR_MESSAGE['TIMELINE_TITLE_EMPTY_ERROR']}, 400
            if not args['type']:
                return {'code': 400, 'message': TIMELINE_ERROR_MESSAGE['TIMELINE_TYPE_EMPTY_ERROR']}, 400

            # 检查类型和状态是否合法
            if not check_enum(args['type'], TIMELINE_TYPE):
                return {'code': 400, 'message': TIMELINE_ERROR_MESSAGE['TYPE_STATUS_ERROR']}, 400
            if args['status'] and not check_enum(args['status'], TIMELINE_STATUS):
                return {'code': 400, 'message': TIMELINE_ERROR_MESSAGE['TYPE_STATUS_ERROR']}, 400

            # 检查重要级别范围
            if args['importance'] is not None and (args['importance'] < 1 or args['importance'] > 4):
                return {'code': 400, 'message': TIMELINE_ERROR_MESSAGE['TIMELINE_IMPORTANCE_RANGE_ERROR']}, 400

            # 设置默认值
            if not args['status']:
                args['status'] = 'ACTIVE'
            if args['importance'] is None:
                args['importance'] = 1

            timeline_item = Timeline(
                user_id=current_user_id,
                title=args['title'],
                type=args['type'],
                content=args['content'],
                status=args['status'],
                description=args['description'],
                importance=args['importance'],
                is_summaried=args['is_summaried'] or False,
                start_time=datetime.fromisoformat(args['start_time']) if args['start_time'] else datetime.now(),
                end_time=datetime.fromisoformat(args['end_time']) if args['end_time'] else None
            )
            timeline_item.create_time = datetime.now()
            timeline_item.update_time = datetime.now()
            success, result = timeline_item.add_timeline()
            if success:
                return {'code': 200, 'message': TIMELINE_SUCCESS_MESSAGE['TIMELINE_ADD_SUCCESS'], 'data': result.dict()}, 200
            else:
                return {'code': 400, 'message': str(result)}, 400
        except ValueError as ve:
            return {'code': 400, 'message': '时间格式错误: ' + str(ve)}, 400
        except Exception as e:
            return {'code': 500, 'message': TIMELINE_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500


class UserTimelineResource(Resource):
    '''
    获取用户时间线事件列表
    '''
    @jwt_required()
    @timeline_ns.doc(description='获取用户时间线事件列表')
    @timeline_ns.marshal_with(timeline_list_response_model)
    def get(self):
        try:
            current_user_id = get_jwt_identity()
            try:
                parse = reqparse.RequestParser()
                parse.add_argument('title', type=str, required=False, help='事件标题')
                parse.add_argument('type', type=str, required=False, help='事件类型')
                parse.add_argument('status', type=str, required=False, help='事件状态')
                parse.add_argument('importance', type=int, required=False, help='重要级别')
                parse.add_argument('is_summaried', type=str, required=False, help='是否总结为日常')
                parse.add_argument('start_time', type=str, required=False, help='事件开始时间')
                parse.add_argument('end_time', type=str, required=False, help='事件结束时间')
                parse.add_argument('content', type=str, required=False, help='事件内容')
                parse.add_argument('description', type=str, required=False, help='事件描述')
                parse.add_argument('create_start_time', type=str, required=False, help='创建开始时间')
                parse.add_argument('create_end_time', type=str, required=False, help='创建结束时间')
                parse.add_argument('update_start_time', type=str, required=False, help='更新开始时间')
                parse.add_argument('update_end_time', type=str, required=False, help='更新结束时间')
                parse.add_argument('order_by', type=str, required=False, default='create_time', help='排序字段')
                parse.add_argument('order_direction', type=str, required=False, default='asc', help='排序方向')
                
                args = parse.parse_args()
                if args['is_summaried']:
                    args['is_summaried'] = False if args['is_summaried'] == 'false' else True
                print(args, "查询条件-外部 get")
            except Exception as e:
                return {'code': 400, 'message': TIMELINE_ERROR_MESSAGE['TIMELINE_PARAM_ERROR']}, 400

            timelines = Timeline.get_timelines_by_condition(current_user_id, args)
            return {'code': 200, 'message': TIMELINE_SUCCESS_MESSAGE['TIMELINE_LIST_SUCCESS'], 'data': timelines}, 200
        except Exception as e:
            return {'code': 500, 'message': TIMELINE_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500
    
    '''
    获取用户时间线事件列表
    '''
    @jwt_required()
    @timeline_ns.doc(description='获取用户时间线事件列表【分页，带查询条件】')
    @timeline_ns.marshal_with(timeline_page_response_model)
    def post(self):
        try:
            current_user_id = get_jwt_identity()
            try:
                parse = reqparse.RequestParser()
                parse.add_argument('title', type=str, required=False, help='事件标题')
                parse.add_argument('type', type=str, required=False, help='事件类型')
                parse.add_argument('status', type=str, required=False, help='事件状态')
                parse.add_argument('importance', type=int, required=False, help='重要级别')
                parse.add_argument('is_summaried', type=bool, required=False, help='是否总结为日常')
                parse.add_argument('start_time', type=str, required=False, help='事件开始时间')
                parse.add_argument('end_time', type=str, required=False, help='事件结束时间')
                parse.add_argument('content', type=str, required=False, help='事件内容')
                parse.add_argument('description', type=str, required=False, help='事件描述')
                parse.add_argument('create_start_time', type=str, required=False, help='创建开始时间')
                parse.add_argument('create_end_time', type=str, required=False, help='创建结束时间')
                parse.add_argument('update_start_time', type=str, required=False, help='更新开始时间')
                parse.add_argument('update_end_time', type=str, required=False, help='更新结束时间')
                # parse.add_argument('is_query_page', type=bool, required=False, help='是否分页查询')
                parse.add_argument('page_no', type=int, default=1, required=False, help='页码')
                parse.add_argument('page_size', type=int, default=10, required=False, help='每页数量')
                parse.add_argument('order_by', type=str, required=False, default='create_time', help='排序字段')
                parse.add_argument('order_direction', type=str, required=False, default='asc', help='排序方向')
                
                args = parse.parse_args()
            except Exception as e:
                return {'code': 400, 'message': TIMELINE_ERROR_MESSAGE['TIMELINE_PARAM_ERROR']}, 400
            args['is_query_page'] = True
            # query_condition = {}
            # for arg in args:
            #     if args[arg] is not None:
            #         query_condition[arg] = args[arg]

            page_res = Timeline.get_timelines_by_condition(current_user_id, args)
            return {'code': 200, 'message': TIMELINE_SUCCESS_MESSAGE['TIMELINE_LIST_SUCCESS'], 'data': {
                'page_no': args['page_no'],
                'page_size': args['page_size'],
                'total': page_res['total'],
                'pages': page_res['pages'],
                'data': page_res['data']
            }}, 200
        except Exception as e:
            return {'code': 500, 'message': TIMELINE_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500
