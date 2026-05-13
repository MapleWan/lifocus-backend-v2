import os
import uuid
import hashlib
import datetime
from flask_restx import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from werkzeug.datastructures import FileStorage

from app.controllers import knowledge_ns
from app.models import KnowledgeBase, Document, DocumentChunk
from app.enums import (
    KNOWLEDGE_SUCCESS_MESSAGE, KNOWLEDGE_ERROR_MESSAGE,
    FILE_EXTENSION_MAP, DOCUMENT_FILE_TYPE
)
from app.services.ai_config import AIConfig
from app.utils.vector_store import VectorStoreService
from app.tasks.document_tasks import process_document_task, reprocess_document_task

from .knowledge_api_model import (
    doc_response_model, doc_list_response_model, doc_page_response_model
)


class SingleDocumentResource(Resource):

    @jwt_required()
    @knowledge_ns.doc(description='获取文档详情')
    @knowledge_ns.marshal_with(doc_response_model)
    def get(self, kb_id, doc_id):
        try:
            current_user_id = get_jwt_identity()
            kb = KnowledgeBase.get_by_id(kb_id)
            if not kb or (kb.user_id != current_user_id and not kb.is_public):
                return {'code': 404, 'message': KNOWLEDGE_ERROR_MESSAGE['KB_NOT_FOUND']}, 404

            doc = Document.get_by_id(doc_id)
            if not doc or doc.knowledge_base_id != kb_id:
                return {'code': 404, 'message': KNOWLEDGE_ERROR_MESSAGE['DOC_NOT_FOUND']}, 404

            return {'code': 200, 'message': KNOWLEDGE_SUCCESS_MESSAGE['DOC_DETAIL_SUCCESS'], 'data': doc.dict()}, 200
        except Exception as e:
            return {'code': 500, 'message': KNOWLEDGE_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500

    @jwt_required()
    @knowledge_ns.doc(description='删除文档')
    def delete(self, kb_id, doc_id):
        try:
            current_user_id = get_jwt_identity()
            kb = KnowledgeBase.get_by_id(kb_id)
            if not kb or kb.user_id != current_user_id:
                return {'code': 404, 'message': KNOWLEDGE_ERROR_MESSAGE['KB_NOT_FOUND']}, 404

            doc = Document.get_by_id(doc_id)
            if not doc or doc.knowledge_base_id != kb_id:
                return {'code': 404, 'message': KNOWLEDGE_ERROR_MESSAGE['DOC_NOT_FOUND']}, 404

            # 删除向量数据库中的分块
            chunks = DocumentChunk.query.filter_by(document_id=doc_id).all()
            vector_ids = [c.vector_id for c in chunks if c.vector_id]
            if vector_ids:
                VectorStoreService.delete_by_ids(kb.vector_collection, vector_ids)

            # 删除分块记录
            DocumentChunk.query.filter_by(document_id=doc_id).delete()

            # 软删除文档
            doc.soft_delete()

            # 更新知识库统计
            kb.document_count = Document.query.filter_by(
                knowledge_base_id=kb.id, is_deleted=False
            ).count()
            kb.total_chunks = DocumentChunk.query.filter_by(
                knowledge_base_id=kb.id
            ).count()
            kb.update_knowledge_base()

            return {'code': 200, 'message': KNOWLEDGE_SUCCESS_MESSAGE['DOC_DELETE_SUCCESS']}, 200
        except Exception as e:
            return {'code': 500, 'message': KNOWLEDGE_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500


class UploadDocumentResource(Resource):

    upload_parser = reqparse.RequestParser()
    upload_parser.add_argument('file', type=FileStorage, location='files', required=True, help='上传文件')

    @jwt_required()
    @knowledge_ns.doc(description='上传文档到知识库')
    @knowledge_ns.expect(upload_parser)
    @knowledge_ns.marshal_with(doc_response_model)
    def post(self, kb_id):
        try:
            current_user_id = get_jwt_identity()
            kb = KnowledgeBase.get_by_id(kb_id)
            if not kb or kb.user_id != current_user_id:
                return {'code': 404, 'message': KNOWLEDGE_ERROR_MESSAGE['KB_NOT_FOUND']}, 404

            args = self.upload_parser.parse_args()
            file = args['file']
            if not file or not file.filename:
                return {'code': 400, 'message': KNOWLEDGE_ERROR_MESSAGE['DOC_FILE_EMPTY']}, 400

            # 检查文件类型
            _, ext = os.path.splitext(file.filename)
            ext = ext.lower()
            file_type = FILE_EXTENSION_MAP.get(ext)
            if not file_type:
                return {'code': 400, 'message': KNOWLEDGE_ERROR_MESSAGE['DOC_TYPE_NOT_SUPPORTED']}, 400

            # 读取文件内容用于计算哈希
            file_data = file.read()
            file_size = len(file_data)

            # 检查文件大小
            if file_size > AIConfig.MAX_FILE_SIZE:
                return {'code': 400, 'message': KNOWLEDGE_ERROR_MESSAGE['DOC_FILE_TOO_LARGE']}, 400

            # 计算文件哈希
            file_hash = hashlib.md5(file_data).hexdigest()

            # 检查重复
            existing = Document.get_by_hash(kb_id, file_hash)
            if existing:
                return {'code': 400, 'message': KNOWLEDGE_ERROR_MESSAGE['DOC_DUPLICATE']}, 400

            # 保存文件到磁盘
            upload_dir = os.path.join(AIConfig.UPLOAD_FOLDER, kb_id)
            os.makedirs(upload_dir, exist_ok=True)

            doc_id = str(uuid.uuid4())
            safe_filename = f"{doc_id}{ext}"
            file_path = os.path.join(upload_dir, safe_filename)

            with open(file_path, 'wb') as f:
                f.write(file_data)

            # 创建文档记录
            doc = Document(
                id=doc_id,
                knowledge_base_id=kb_id,
                source_type='FILE',
                file_type=file_type,
                file_name=file.filename,
                file_path=file_path,
                file_size=file_size,
                file_hash=file_hash,
                title=os.path.splitext(file.filename)[0],
                embed_status='PENDING',
            )
            doc.create_time = datetime.datetime.now()
            doc.update_time = datetime.datetime.now()
            doc.add_document()

            # 提交 Celery 异步任务
            process_document_task.delay(doc_id)

            return {'code': 200, 'message': KNOWLEDGE_SUCCESS_MESSAGE['DOC_UPLOAD_SUCCESS'], 'data': doc.dict()}, 200
        except Exception as e:
            return {'code': 500, 'message': KNOWLEDGE_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500


class ReprocessDocumentResource(Resource):

    @jwt_required()
    @knowledge_ns.doc(description='重新处理文档')
    @knowledge_ns.marshal_with(doc_response_model)
    def post(self, kb_id, doc_id):
        try:
            current_user_id = get_jwt_identity()
            kb = KnowledgeBase.get_by_id(kb_id)
            if not kb or kb.user_id != current_user_id:
                return {'code': 404, 'message': KNOWLEDGE_ERROR_MESSAGE['KB_NOT_FOUND']}, 404

            doc = Document.get_by_id(doc_id)
            if not doc or doc.knowledge_base_id != kb_id:
                return {'code': 404, 'message': KNOWLEDGE_ERROR_MESSAGE['DOC_NOT_FOUND']}, 404

            if doc.embed_status == 'PROCESSING':
                return {'code': 400, 'message': KNOWLEDGE_ERROR_MESSAGE['DOC_PROCESSING']}, 400

            # 更新状态为待处理
            doc.embed_status = 'PENDING'
            doc.process_error = None
            doc.update_document()

            # 提交 Celery 异步任务
            reprocess_document_task.delay(doc_id)

            return {'code': 200, 'message': KNOWLEDGE_SUCCESS_MESSAGE['DOC_REPROCESS_SUCCESS'], 'data': doc.dict()}, 200
        except Exception as e:
            return {'code': 500, 'message': KNOWLEDGE_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500


class KBDocumentListResource(Resource):

    @jwt_required()
    @knowledge_ns.doc(description='获取知识库文档列表（不分页）')
    @knowledge_ns.marshal_with(doc_list_response_model)
    def get(self, kb_id):
        try:
            current_user_id = get_jwt_identity()
            kb = KnowledgeBase.get_by_id(kb_id)
            if not kb or (kb.user_id != current_user_id and not kb.is_public):
                return {'code': 404, 'message': KNOWLEDGE_ERROR_MESSAGE['KB_NOT_FOUND']}, 404

            parser = reqparse.RequestParser()
            parser.add_argument('file_name', type=str, required=False)
            parser.add_argument('file_type', type=str, required=False)
            parser.add_argument('embed_status', type=str, required=False)
            parser.add_argument('order_by', type=str, default='create_time', required=False)
            parser.add_argument('order_direction', type=str, default='desc', required=False)
            args = parser.parse_args()

            docs = Document.get_by_knowledge_base_id(kb_id, args)
            return {'code': 200, 'message': KNOWLEDGE_SUCCESS_MESSAGE['DOC_LIST_SUCCESS'], 'data': docs}, 200
        except Exception as e:
            return {'code': 500, 'message': KNOWLEDGE_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500

    @jwt_required()
    @knowledge_ns.doc(description='获取知识库文档列表（分页）')
    @knowledge_ns.marshal_with(doc_page_response_model)
    def post(self, kb_id):
        try:
            current_user_id = get_jwt_identity()
            kb = KnowledgeBase.get_by_id(kb_id)
            if not kb or (kb.user_id != current_user_id and not kb.is_public):
                return {'code': 404, 'message': KNOWLEDGE_ERROR_MESSAGE['KB_NOT_FOUND']}, 404

            parser = reqparse.RequestParser()
            parser.add_argument('file_name', type=str, required=False)
            parser.add_argument('file_type', type=str, required=False)
            parser.add_argument('embed_status', type=str, required=False)
            parser.add_argument('page_no', type=int, default=1, required=True)
            parser.add_argument('page_size', type=int, default=10, required=True)
            parser.add_argument('order_by', type=str, default='create_time', required=False)
            parser.add_argument('order_direction', type=str, default='desc', required=False)
            args = parser.parse_args()
            args['is_query_page'] = True

            page_res = Document.get_by_knowledge_base_id(kb_id, args)
            return {
                'code': 200,
                'message': KNOWLEDGE_SUCCESS_MESSAGE['DOC_LIST_SUCCESS'],
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
