import datetime
from flask_restx import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request

from app.controllers import knowledge_ns
from app.models import KnowledgeBase
from app.enums import KNOWLEDGE_SUCCESS_MESSAGE, KNOWLEDGE_ERROR_MESSAGE, KNOWLEDGE_BASE_STATUS
from app.utils.vector_store import VectorStoreService

from .knowledge_api_model import (
    add_knowledge_base_model, update_knowledge_base_model,
    kb_response_model, kb_list_response_model, kb_page_response_model
)


class SingleKnowledgeBaseResource(Resource):

    @jwt_required()
    @knowledge_ns.doc(description='获取知识库详情')
    @knowledge_ns.marshal_with(kb_response_model)
    def get(self, kb_id):
        try:
            kb = KnowledgeBase.get_by_id(kb_id)
            if not kb:
                return {'code': 404, 'message': KNOWLEDGE_ERROR_MESSAGE['KB_NOT_FOUND']}, 404
            # 验证归属
            current_user_id = get_jwt_identity()
            if kb.user_id != current_user_id and not kb.is_public:
                return {'code': 404, 'message': KNOWLEDGE_ERROR_MESSAGE['KB_NOT_FOUND']}, 404
            return {'code': 200, 'message': KNOWLEDGE_SUCCESS_MESSAGE['KB_DETAIL_SUCCESS'], 'data': kb.dict()}, 200
        except Exception as e:
            return {'code': 500, 'message': KNOWLEDGE_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500

    @jwt_required()
    @knowledge_ns.doc(description='更新知识库')
    @knowledge_ns.expect(update_knowledge_base_model)
    @knowledge_ns.marshal_with(kb_response_model)
    def put(self, kb_id):
        try:
            current_user_id = get_jwt_identity()
            kb = KnowledgeBase.get_by_id(kb_id)
            if not kb:
                return {'code': 404, 'message': KNOWLEDGE_ERROR_MESSAGE['KB_NOT_FOUND']}, 404
            if kb.user_id != current_user_id:
                return {'code': 404, 'message': KNOWLEDGE_ERROR_MESSAGE['KB_NOT_FOUND']}, 404

            parser = reqparse.RequestParser()
            parser.add_argument('name', type=str, required=False)
            parser.add_argument('description', type=str, required=False)
            parser.add_argument('icon', type=str, required=False)
            parser.add_argument('llm_model', type=str, required=False)
            parser.add_argument('status', type=str, required=False)
            parser.add_argument('is_public', type=bool, required=False)
            args = parser.parse_args()

            # 检查名称唯一性
            if args.get('name') and args['name'] != kb.name:
                existing = KnowledgeBase.get_by_name(current_user_id, args['name'])
                if existing:
                    return {'code': 400, 'message': KNOWLEDGE_ERROR_MESSAGE['KB_NAME_EXIST']}, 400

            # 验证状态
            if args.get('status') and args['status'] not in KNOWLEDGE_BASE_STATUS:
                return {'code': 400, 'message': KNOWLEDGE_ERROR_MESSAGE['KB_PARAM_ERROR']}, 400

            update_fields = ['name', 'description', 'icon', 'llm_model', 'status', 'is_public']
            for field in update_fields:
                if args.get(field) is not None:
                    setattr(kb, field, args[field])
            kb.update_time = datetime.datetime.now()
            kb.update_knowledge_base()

            return {'code': 200, 'message': KNOWLEDGE_SUCCESS_MESSAGE['KB_UPDATE_SUCCESS'], 'data': kb.dict()}, 200
        except Exception as e:
            return {'code': 500, 'message': KNOWLEDGE_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500

    @jwt_required()
    @knowledge_ns.doc(description='删除知识库')
    def delete(self, kb_id):
        try:
            current_user_id = get_jwt_identity()
            kb = KnowledgeBase.get_by_id(kb_id)
            if not kb:
                return {'code': 404, 'message': KNOWLEDGE_ERROR_MESSAGE['KB_NOT_FOUND']}, 404
            if kb.user_id != current_user_id:
                return {'code': 404, 'message': KNOWLEDGE_ERROR_MESSAGE['KB_NOT_FOUND']}, 404

            force = request.args.get('force', 'false').lower() == 'true'

            if not force and kb.document_count > 0:
                return {'code': 400, 'message': KNOWLEDGE_ERROR_MESSAGE['KB_HAS_DOCUMENTS']}, 400

            # 删除向量数据库 Collection
            VectorStoreService.delete_collection(kb.vector_collection)

            # 软删除知识库
            kb.soft_delete()

            return {'code': 200, 'message': KNOWLEDGE_SUCCESS_MESSAGE['KB_DELETE_SUCCESS']}, 200
        except Exception as e:
            return {'code': 500, 'message': KNOWLEDGE_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500


class AddKnowledgeBaseResource(Resource):

    @jwt_required()
    @knowledge_ns.doc(description='创建知识库')
    @knowledge_ns.expect(add_knowledge_base_model)
    @knowledge_ns.marshal_with(kb_response_model)
    def post(self):
        try:
            current_user_id = get_jwt_identity()

            parser = reqparse.RequestParser()
            parser.add_argument('name', type=str, required=True, help='知识库名称不能为空')
            parser.add_argument('description', type=str, required=False)
            parser.add_argument('icon', type=str, required=False)
            parser.add_argument('embedding_model', type=str, required=False)
            parser.add_argument('llm_model', type=str, required=False)
            parser.add_argument('chunk_size', type=int, required=False)
            parser.add_argument('chunk_overlap', type=int, required=False)
            parser.add_argument('is_public', type=bool, required=False)
            args = parser.parse_args()

            if not args.get('name'):
                return {'code': 400, 'message': KNOWLEDGE_ERROR_MESSAGE['KB_NAME_EMPTY']}, 400

            # 检查名称唯一性
            if KnowledgeBase.get_by_name(current_user_id, args['name']):
                return {'code': 400, 'message': KNOWLEDGE_ERROR_MESSAGE['KB_NAME_EXIST']}, 400

            # 获取项目ID
            project_id = request.headers.get('X-Project-Id')

            import uuid
            kb_id = str(uuid.uuid4())
            vector_collection = f"kb_{kb_id[:8]}"

            kb = KnowledgeBase(
                id=kb_id,
                user_id=current_user_id,
                project_id=project_id,
                name=args['name'],
                description=args.get('description'),
                icon=args.get('icon'),
                embedding_model=args.get('embedding_model') or 'bge-large-zh-v1.5',
                llm_model=args.get('llm_model') or 'glm-4-flash',
                vector_collection=vector_collection,
                chunk_size=args.get('chunk_size') or 500,
                chunk_overlap=args.get('chunk_overlap') or 50,
                is_public=args.get('is_public') or False,
            )
            kb.create_time = datetime.datetime.now()
            kb.update_time = datetime.datetime.now()
            kb.add_knowledge_base()

            # 创建向量数据库 Collection
            VectorStoreService.get_or_create_collection(vector_collection)

            return {'code': 200, 'message': KNOWLEDGE_SUCCESS_MESSAGE['KB_CREATE_SUCCESS'], 'data': kb.dict()}, 200
        except Exception as e:
            return {'code': 500, 'message': KNOWLEDGE_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500


class UserKnowledgeBaseResource(Resource):

    @jwt_required()
    @knowledge_ns.doc(description='获取用户知识库列表（不分页）')
    @knowledge_ns.marshal_with(kb_list_response_model)
    def get(self):
        try:
            current_user_id = get_jwt_identity()

            parser = reqparse.RequestParser()
            parser.add_argument('name', type=str, required=False, help='知识库名称')
            parser.add_argument('status', type=str, required=False, help='知识库状态')
            parser.add_argument('order_by', type=str, default='update_time', required=False)
            parser.add_argument('order_direction', type=str, default='desc', required=False)
            args = parser.parse_args()

            kbs = KnowledgeBase.get_by_user_id(current_user_id, args)
            return {'code': 200, 'message': KNOWLEDGE_SUCCESS_MESSAGE['KB_LIST_SUCCESS'], 'data': kbs}, 200
        except Exception as e:
            return {'code': 500, 'message': KNOWLEDGE_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500

    @jwt_required()
    @knowledge_ns.doc(description='获取用户知识库列表（分页）')
    @knowledge_ns.marshal_with(kb_page_response_model)
    def post(self):
        try:
            current_user_id = get_jwt_identity()

            parser = reqparse.RequestParser()
            parser.add_argument('name', type=str, required=False, help='知识库名称')
            parser.add_argument('status', type=str, required=False, help='知识库状态')
            parser.add_argument('page_no', type=int, default=1, required=True, help='页码')
            parser.add_argument('page_size', type=int, default=10, required=True, help='每页数量')
            parser.add_argument('order_by', type=str, default='update_time', required=False)
            parser.add_argument('order_direction', type=str, default='desc', required=False)
            args = parser.parse_args()
            args['is_query_page'] = True

            page_res = KnowledgeBase.get_by_user_id(current_user_id, args)
            return {
                'code': 200,
                'message': KNOWLEDGE_SUCCESS_MESSAGE['KB_LIST_SUCCESS'],
                'data': {
                    'page_no': args['page_no'],
                    'page_size': args['page_size'],
                    'pages': page_res['pages'],
                    'total': page_res['total'],
                    'data': page_res['data']
                }
            }, 200
        except Exception as e:
            return {'code': 500, 'message': KNOWLEDGE_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500
