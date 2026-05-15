# 附件类型枚举
ATTACHMENT_KIND = {
    'IMAGE': '图片',
    'PDF': 'PDF',
    'WORD': 'Word文档',
    'PPT': 'PPT演示文稿',
    'EXCEL': 'Excel表格',
    'AUDIO': '音频',
    'VIDEO': '视频',
    'MARKDOWN': 'Markdown',
    'TEXT': '纯文本',
}

# 扩展名到附件类型的映射
EXT_TO_KIND = {
    # IMAGE
    'jpg': 'IMAGE', 'jpeg': 'IMAGE', 'png': 'IMAGE', 'gif': 'IMAGE', 'webp': 'IMAGE', 'bmp': 'IMAGE', 'svg': 'IMAGE',
    # PDF
    'pdf': 'PDF',
    # WORD
    'doc': 'WORD', 'docx': 'WORD',
    # PPT
    'ppt': 'PPT', 'pptx': 'PPT',
    # EXCEL
    'xls': 'EXCEL', 'xlsx': 'EXCEL', 'csv': 'EXCEL',
    # AUDIO
    'mp3': 'AUDIO', 'wav': 'AUDIO', 'm4a': 'AUDIO', 'ogg': 'AUDIO', 'flac': 'AUDIO',
    # VIDEO
    'mp4': 'VIDEO', 'webm': 'VIDEO', 'mov': 'VIDEO', 'mkv': 'VIDEO',
    # MARKDOWN
    'md': 'MARKDOWN', 'markdown': 'MARKDOWN',
    # TEXT
    'txt': 'TEXT', 'log': 'TEXT',
}

# MIME类型映射（用于返回给前端预览时使用）
KIND_TO_MIME = {
    'IMAGE': 'image/jpeg',  # 具体类型会在运行时根据扩展名调整
    'PDF': 'application/pdf',
    'WORD': 'application/msword',
    'PPT': 'application/vnd.ms-powerpoint',
    'EXCEL': 'application/vnd.ms-excel',
    'AUDIO': 'audio/mpeg',
    'VIDEO': 'video/mp4',
    'MARKDOWN': 'text/markdown',
    'TEXT': 'text/plain',
}

# 可预览的类型
PREVIEWABLE_KINDS = {'IMAGE', 'PDF', 'AUDIO', 'VIDEO', 'MARKDOWN', 'TEXT'}


def get_kind_by_ext(ext: str) -> str | None:
    """根据文件扩展名获取附件类型"""
    return EXT_TO_KIND.get(ext.lower())


ATTACHMENT_SUCCESS_MESSAGE = {
    'UPLOAD_SUCCESS': '附件上传成功',
    'LIST_SUCCESS': '附件列表获取成功',
    'DETAIL_SUCCESS': '附件详情获取成功',
    'DELETE_SUCCESS': '附件删除成功',
    'DOWNLOAD_SUCCESS': '附件下载成功',
}

ATTACHMENT_ERROR_MESSAGE = {
    'NO_FILE': '未选择文件',
    'UNSUPPORTED_TYPE': '不支持的文件类型',
    'FILE_TOO_LARGE': '文件大小超过100MB限制',
    'NOT_FOUND': '附件不存在或已删除',
    'PROJECT_ID_EMPTY': '项目ID不能为空',
    'PREVIEW_NOT_SUPPORTED': '该文件类型不支持在线预览',
    'COMMON_ERROR': '系统错误',
}
