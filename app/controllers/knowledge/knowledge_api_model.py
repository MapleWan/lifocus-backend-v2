from app.controllers import knowledge_ns
from flask_restx import fields

# ==================== 知识库模型 ====================

knowledge_base_model = knowledge_ns.model('KnowledgeBase', {
    'id': fields.String(description='知识库ID'),
    'user_id': fields.String(description='创建者ID'),
    'project_id': fields.String(description='所属项目ID'),
    'name': fields.String(description='知识库名称'),
    'description': fields.String(description='知识库描述'),
    'icon': fields.String(description='知识库图标'),
    'embedding_model': fields.String(description='Embedding模型'),
    'llm_model': fields.String(description='默认LLM模型'),
    'vector_collection': fields.String(description='向量Collection名称'),
    'chunk_size': fields.Integer(description='分块大小'),
    'chunk_overlap': fields.Integer(description='分块重叠'),
    'document_count': fields.Integer(description='文档数量'),
    'total_chunks': fields.Integer(description='总块数'),
    'status': fields.String(description='状态'),
    'is_public': fields.Boolean(description='是否公开'),
    'create_time': fields.String(description='创建时间'),
    'update_time': fields.String(description='更新时间'),
})

add_knowledge_base_model = knowledge_ns.model('AddKnowledgeBase', {
    'name': fields.String(required=True, description='知识库名称'),
    'description': fields.String(required=False, description='知识库描述'),
    'icon': fields.String(required=False, description='知识库图标'),
    'embedding_model': fields.String(required=False, description='Embedding模型'),
    'llm_model': fields.String(required=False, description='默认LLM模型'),
    'chunk_size': fields.Integer(required=False, description='分块大小'),
    'chunk_overlap': fields.Integer(required=False, description='分块重叠'),
    'is_public': fields.Boolean(required=False, description='是否公开'),
})

update_knowledge_base_model = knowledge_ns.model('UpdateKnowledgeBase', {
    'name': fields.String(required=False, description='知识库名称'),
    'description': fields.String(required=False, description='知识库描述'),
    'icon': fields.String(required=False, description='知识库图标'),
    'llm_model': fields.String(required=False, description='默认LLM模型'),
    'status': fields.String(required=False, description='状态'),
    'is_public': fields.Boolean(required=False, description='是否公开'),
})

kb_response_model = knowledge_ns.model('KBResponse', {
    'code': fields.Integer(description='响应码'),
    'message': fields.String(description='响应信息'),
    'data': fields.Nested(knowledge_base_model, description='知识库数据', allow_null=True),
})

kb_list_response_model = knowledge_ns.model('KBListResponse', {
    'code': fields.Integer(description='响应码'),
    'message': fields.String(description='响应信息'),
    'data': fields.List(fields.Nested(knowledge_base_model), description='知识库列表', allow_null=True),
})

kb_page_model = knowledge_ns.model('KBPage', {
    'page_no': fields.Integer(description='页码'),
    'page_size': fields.Integer(description='每页数量'),
    'pages': fields.Integer(description='总页数'),
    'total': fields.Integer(description='总数'),
    'data': fields.List(fields.Nested(knowledge_base_model), description='知识库列表', allow_null=True),
})

kb_page_response_model = knowledge_ns.model('KBPageResponse', {
    'code': fields.Integer(description='响应码'),
    'message': fields.String(description='响应信息'),
    'data': fields.Nested(kb_page_model, description='分页数据', allow_null=True),
})

# ==================== 文档模型 ====================

document_model = knowledge_ns.model('Document', {
    'id': fields.String(description='文档ID'),
    'knowledge_base_id': fields.String(description='所属知识库ID'),
    'source_type': fields.String(description='来源类型'),
    'source_id': fields.String(description='关联来源ID'),
    'source_url': fields.String(description='原始URL'),
    'file_type': fields.String(description='文件类型'),
    'file_name': fields.String(description='文件名'),
    'file_size': fields.Integer(description='文件大小'),
    'title': fields.String(description='文档标题'),
    'content_preview': fields.String(description='内容预览'),
    'content_length': fields.Integer(description='内容长度'),
    'embed_status': fields.String(description='向量化状态'),
    'process_error': fields.String(description='处理错误'),
    'chunk_count': fields.Integer(description='分块数量'),
    'meta_data': fields.Raw(description='元数据'),
    'tags': fields.Raw(description='标签'),
    'create_time': fields.String(description='创建时间'),
    'update_time': fields.String(description='更新时间'),
    'process_time': fields.String(description='处理完成时间'),
})

doc_response_model = knowledge_ns.model('DocResponse', {
    'code': fields.Integer(description='响应码'),
    'message': fields.String(description='响应信息'),
    'data': fields.Nested(document_model, description='文档数据', allow_null=True),
})

doc_list_response_model = knowledge_ns.model('DocListResponse', {
    'code': fields.Integer(description='响应码'),
    'message': fields.String(description='响应信息'),
    'data': fields.List(fields.Nested(document_model), description='文档列表', allow_null=True),
})

doc_page_model = knowledge_ns.model('DocPage', {
    'page_no': fields.Integer(description='页码'),
    'page_size': fields.Integer(description='每页数量'),
    'pages': fields.Integer(description='总页数'),
    'total': fields.Integer(description='总数'),
    'data': fields.List(fields.Nested(document_model), description='文档列表', allow_null=True),
})

doc_page_response_model = knowledge_ns.model('DocPageResponse', {
    'code': fields.Integer(description='响应码'),
    'message': fields.String(description='响应信息'),
    'data': fields.Nested(doc_page_model, description='分页数据', allow_null=True),
})
