ARTICLE_SUCCESS_MESSAGE = {
    'LIST_SUCCESS': '文章列表获取成功',
    'DETAIL_SUCCESS': '文章详情获取成功',
    'CREATE_SUCCESS': '文章创建成功',
    'UPDATE_SUCCESS': '文章更新成功',
    'DELETE_SUCCESS': '文章删除成功',
    'SHARE_ACCESS_SUCCESS': '分享文章访问成功',
}

ARTICLE_ERROR_MESSAGE = {
    'ALREADY_TITLE_EXIST': '文章标题已存在',
    'PROJECT_ID_EMPTY_ERROR': '项目ID不能为空',
    'NOT_FOUND': '文章不存在或已删除',
    'TITLE_EMPTY_ERROR': '文章标题不能为空',
    'CONTENT_EMPTY_ERROR': '文章内容不能为空',
    'TYPE_STATUS_ERROR': '文章类型或状态错误',
    'PARAM_ERROR': '文章参数错误',
    'PASSWORD_FORMAT_ERROR': '密码格式错误，必须包含字母和数字，且长度不少于8',
    'COMMON_ERROR': '系统错误',
    'NOT_SHARED': '文章未设置为分享状态',
    'SHARE_PASSWORD_REQUIRED': '需要提供分享密码',
    'SHARE_PASSWORD_INCORRECT': '分享密码错误',
}

# 文章类型
ARTICLE_TYPE = {
    "NOTE": "笔记",
    "DAILY": "日常"
}

# 文章状态
ARTICLE_STATUS = {
    'ACTIVE': '活跃中',
    'ARCHIVED': '已归档',
}
