import uuid
import os
from datetime import datetime

from flask import request, send_file
from flask_restx import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.controllers import attachment_ns
from app.models.entities.attachment import Attachment
from app.models.entities.user import User
from app.models.entities.project import Project
from app.models.entities.category import Category
from app.enums.attachment_enum import (
    ATTACHMENT_SUCCESS_MESSAGE,
    ATTACHMENT_ERROR_MESSAGE,
    get_kind_by_ext,
    PREVIEWABLE_KINDS,
)
from app.utils import save_attachment_to_disk, del_attachment_from_disk, get_attachment_abs_path


class AttachmentResource(Resource):
    @jwt_required()
    @attachment_ns.doc(description='上传附件')
    def post(self):
        """
        上传附件
        :form file: 文件
        :form project_id: 项目ID
        :form category_id: 目录ID（可选）
        :form category_full_path: 目录完整路径（可选，用于落盘）
        """
        try:
            user_id = get_jwt_identity()
            current_user = User.get_user_by_id(user_id)
            if not current_user:
                return {'code': 401, 'message': '用户不存在'}, 401

            # 检查文件
            if 'file' not in request.files:
                return {'code': 400, 'message': ATTACHMENT_ERROR_MESSAGE['NO_FILE']}, 400
            file = request.files['file']
            if file.filename == '':
                return {'code': 400, 'message': ATTACHMENT_ERROR_MESSAGE['NO_FILE']}, 400

            # 获取参数
            project_id = request.form.get('project_id') or request.headers.get('X-Project-Id')
            if not project_id:
                return {'code': 400, 'message': ATTACHMENT_ERROR_MESSAGE['PROJECT_ID_EMPTY']}, 400
            
            category_id = request.form.get('category_id', type=int)
            category_full_path = request.form.get('category_full_path', '')

            current_project = Project.get_project_by_id(project_id)
            if not current_project:
                return {'code': 404, 'message': '项目不存在'}, 404

            # 验证扩展名
            ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
            kind = get_kind_by_ext(ext)
            if not kind:
                return {'code': 400, 'message': ATTACHMENT_ERROR_MESSAGE['UNSUPPORTED_TYPE']}, 400

            # 生成存储文件名
            stored_name = f"{uuid.uuid4().hex}.{ext}"

            # 保存文件到磁盘
            abs_path, rel_path = save_attachment_to_disk(
                current_user.username,
                current_project.name,
                category_full_path,
                stored_name,
                file
            )

            # 获取文件大小
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)

            # 创建数据库记录
            attachment = Attachment(
                user_id=user_id,
                project_id=project_id,
                category_id=category_id,
                name=file.filename,
                stored_name=stored_name,
                ext=ext,
                mime_type=file.content_type or '',
                size=file_size,
                kind=kind,
                storage_path=rel_path,
            )
            attachment.add_attachment()

            return {
                'code': 200,
                'message': ATTACHMENT_SUCCESS_MESSAGE['UPLOAD_SUCCESS'],
                'data': attachment.dict()
            }, 200

        except Exception as e:
            return {'code': 500, 'message': ATTACHMENT_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500

    @jwt_required()
    @attachment_ns.doc(description='获取附件列表')
    def get(self):
        """
        获取附件列表
        :query project_id: 项目ID（优先从 header 读取）
        :query category_id: 目录ID（可选）
        :query kind: 附件类型（可选）
        :query keyword: 搜索关键词（可选）
        :query page: 页码
        :query page_size: 每页数量
        """
        try:
            project_id = request.args.get('project_id') or request.headers.get('X-Project-Id')
            if not project_id:
                return {'code': 400, 'message': ATTACHMENT_ERROR_MESSAGE['PROJECT_ID_EMPTY']}, 400

            category_id = request.args.get('category_id', type=int)
            kind = request.args.get('kind')
            keyword = request.args.get('keyword')
            page = request.args.get('page', 1, type=int)
            page_size = request.args.get('page_size', 20, type=int)

            query = Attachment.query.filter_by(
                project_id=project_id,
                is_deleted=False
            )

            if category_id:
                query = query.filter_by(category_id=category_id)
            if kind:
                query = query.filter_by(kind=kind)
            if keyword:
                query = query.filter(Attachment.name.like(f'%{keyword}%'))

            query = query.order_by(Attachment.create_time.desc())

            total = query.count()
            attachments = query.offset((page - 1) * page_size).limit(page_size).all()

            return {
                'code': 200,
                'message': ATTACHMENT_SUCCESS_MESSAGE['LIST_SUCCESS'],
                'data': {
                    'page': page,
                    'page_size': page_size,
                    'total': total,
                    'pages': (total + page_size - 1) // page_size,
                    'data': [att.dict() for att in attachments]
                }
            }, 200

        except Exception as e:
            return {'code': 500, 'message': ATTACHMENT_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500


class SingleAttachmentResource(Resource):
    @jwt_required()
    @attachment_ns.doc(description='获取附件详情')
    def get(self, attachment_id):
        try:
            attachment = Attachment.get_attachment_by_id(attachment_id)
            if not attachment or attachment.is_deleted:
                return {'code': 404, 'message': ATTACHMENT_ERROR_MESSAGE['NOT_FOUND']}, 404
            return {
                'code': 200,
                'message': ATTACHMENT_SUCCESS_MESSAGE['DETAIL_SUCCESS'],
                'data': attachment.dict()
            }, 200
        except Exception as e:
            return {'code': 500, 'message': ATTACHMENT_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500

    @jwt_required()
    @attachment_ns.doc(description='删除附件')
    def delete(self, attachment_id):
        try:
            user_id = get_jwt_identity()
            current_user = User.get_user_by_id(user_id)
            current_project = Project.get_project_by_id(request.headers.get('X-Project-Id'))

            attachment = Attachment.get_attachment_by_id(attachment_id)
            if not attachment or attachment.is_deleted:
                return {'code': 404, 'message': ATTACHMENT_ERROR_MESSAGE['NOT_FOUND']}, 404

            # 软删除
            attachment.soft_delete_attachment()

            # 物理删除文件
            category_path = ''
            if attachment.category:
                # 构建目录路径
                def get_category_full_path(cat):
                    parts = []
                    current = cat
                    while current:
                        parts.insert(0, current.name)
                        current = current.parent if current.parent_id else None
                    return '/'.join(parts)
                category_path = get_category_full_path(attachment.category)
            
            abs_path = get_attachment_abs_path(
                current_user.username,
                current_project.name,
                category_path,
                attachment.stored_name
            )
            del_attachment_from_disk(abs_path)

            return {
                'code': 200,
                'message': ATTACHMENT_SUCCESS_MESSAGE['DELETE_SUCCESS']
            }, 200

        except Exception as e:
            return {'code': 500, 'message': ATTACHMENT_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500


class AttachmentDownloadResource(Resource):
    @jwt_required()
    @attachment_ns.doc(description='下载附件')
    def get(self, attachment_id):
        try:
            user_id = get_jwt_identity()
            current_user = User.get_user_by_id(user_id)
            current_project = Project.get_project_by_id(request.headers.get('X-Project-Id'))

            attachment = Attachment.get_attachment_by_id(attachment_id)
            if not attachment or attachment.is_deleted:
                return {'code': 404, 'message': ATTACHMENT_ERROR_MESSAGE['NOT_FOUND']}, 404

            category_path = ''
            if attachment.category:
                def get_category_full_path(cat):
                    parts = []
                    current = cat
                    while current:
                        parts.insert(0, current.name)
                        current = current.parent if current.parent_id else None
                    return '/'.join(parts)
                category_path = get_category_full_path(attachment.category)
            
            abs_path = get_attachment_abs_path(
                current_user.username,
                current_project.name,
                category_path,
                attachment.stored_name
            )

            if not os.path.exists(abs_path):
                return {'code': 404, 'message': '文件不存在'}, 404

            return send_file(
                abs_path,
                as_attachment=True,
                download_name=attachment.name,
                mimetype=attachment.mime_type
            )

        except Exception as e:
            return {'code': 500, 'message': ATTACHMENT_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500


class AttachmentPreviewResource(Resource):
    @jwt_required()
    @attachment_ns.doc(description='预览附件')
    def get(self, attachment_id):
        try:
            user_id = get_jwt_identity()
            current_user = User.get_user_by_id(user_id)
            current_project = Project.get_project_by_id(request.headers.get('X-Project-Id'))

            attachment = Attachment.get_attachment_by_id(attachment_id)
            if not attachment or attachment.is_deleted:
                return {'code': 404, 'message': ATTACHMENT_ERROR_MESSAGE['NOT_FOUND']}, 404

            # 检查是否支持预览
            if attachment.kind not in PREVIEWABLE_KINDS:
                return {'code': 400, 'message': ATTACHMENT_ERROR_MESSAGE['PREVIEW_NOT_SUPPORTED']}, 400

            category_path = ''
            if attachment.category:
                def get_category_full_path(cat):
                    parts = []
                    current = cat
                    while current:
                        parts.insert(0, current.name)
                        current = current.parent if current.parent_id else None
                    return '/'.join(parts)
                category_path = get_category_full_path(attachment.category)
            
            abs_path = get_attachment_abs_path(
                current_user.username,
                current_project.name,
                category_path,
                attachment.stored_name
            )

            if not os.path.exists(abs_path):
                return {'code': 404, 'message': '文件不存在'}, 404

            return send_file(
                abs_path,
                mimetype=attachment.mime_type
            )

        except Exception as e:
            return {'code': 500, 'message': ATTACHMENT_ERROR_MESSAGE['COMMON_ERROR'] + ': ' + str(e)}, 500
