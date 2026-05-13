KNOWLEDGE_SUCCESS_MESSAGE = {
    'KB_CREATE_SUCCESS': '知识库创建成功',
    'KB_UPDATE_SUCCESS': '知识库更新成功',
    'KB_DELETE_SUCCESS': '知识库删除成功',
    'KB_DETAIL_SUCCESS': '知识库详情获取成功',
    'KB_LIST_SUCCESS': '知识库列表获取成功',
    'DOC_UPLOAD_SUCCESS': '文档上传成功，正在处理中',
    'DOC_DELETE_SUCCESS': '文档删除成功',
    'DOC_DETAIL_SUCCESS': '文档详情获取成功',
    'DOC_LIST_SUCCESS': '文档列表获取成功',
    'DOC_REPROCESS_SUCCESS': '文档已加入重新处理队列',
}

KNOWLEDGE_ERROR_MESSAGE = {
    'KB_NOT_FOUND': '知识库不存在或已删除',
    'KB_NAME_EXIST': '知识库名称已存在',
    'KB_NAME_EMPTY': '知识库名称不能为空',
    'KB_PARAM_ERROR': '知识库参数错误',
    'KB_HAS_DOCUMENTS': '知识库包含文档，请使用强制删除',
    'DOC_NOT_FOUND': '文档不存在或已删除',
    'DOC_FILE_EMPTY': '上传文件不能为空',
    'DOC_TYPE_NOT_SUPPORTED': '不支持的文件类型',
    'DOC_FILE_TOO_LARGE': '文件大小超过限制',
    'DOC_DUPLICATE': '文档已存在（文件哈希重复）',
    'DOC_PROCESSING': '文档正在处理中',
    'COMMON_ERROR': '系统错误',
}

# 知识库状态
KNOWLEDGE_BASE_STATUS = {
    'ACTIVE': '活跃',
    'ARCHIVED': '已归档',
}

# 文档来源类型
DOCUMENT_SOURCE_TYPE = {
    'FILE': '文件上传',
    'ARTICLE': '文章导入',
    'URL': '网页抓取',
    'NOTE': '手动笔记',
}

# 文档文件类型
DOCUMENT_FILE_TYPE = {
    'PDF': 'PDF',
    'DOCX': 'Word',
    'PPTX': 'PPT',
    'XLSX': 'Excel',
    'MD': 'Markdown',
    'TXT': '纯文本',
    'HTML': '网页',
}

# 向量化状态
EMBED_STATUS = {
    'PENDING': '待处理',
    'PROCESSING': '处理中',
    'COMPLETED': '已完成',
    'FAILED': '处理失败',
}

# 文件扩展名到文件类型的映射
FILE_EXTENSION_MAP = {
    '.pdf': 'PDF',
    '.docx': 'DOCX',
    '.doc': 'DOCX',
    '.pptx': 'PPTX',
    '.ppt': 'PPTX',
    '.xlsx': 'XLSX',
    '.xls': 'XLSX',
    '.md': 'MD',
    '.markdown': 'MD',
    '.txt': 'TXT',
    '.text': 'TXT',
    '.html': 'HTML',
    '.htm': 'HTML',
}
