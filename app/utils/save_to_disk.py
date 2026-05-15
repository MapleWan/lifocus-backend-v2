import os
import shutil

user_path = os.path.expanduser('~') + '/lifocus_data/'

'''
创建或更新用户项目目录
'''
def make_user_project_dir(user_name, origin_project_name, new_project_name):
    if origin_project_name == new_project_name:
        return False
    origin_project_dir = os.path.join(user_path, user_name,origin_project_name)
    new_project_dir = os.path.join(user_path, user_name, new_project_name)

    if not origin_project_name:
        if os.path.exists(new_project_dir):
            return False
        else:
            os.makedirs(new_project_dir)
            return True
    else:
        shutil.move(origin_project_dir, new_project_dir)
        return True

'''
删除用户项目目录
'''
def del_user_project_dir(user_name, project_name):
    project_dir = os.path.join(user_path, user_name, project_name)
    if os.path.exists(project_dir):
        shutil.rmtree(project_dir)
        return True
    else:
        return False

def rename_project_category(user_name, project_name, old_category_path, new_category_path):
    """
    重命名用户项目下分类对应的目录名
    """
    category_dir = os.path.join(user_path, user_name, project_name, old_category_path)
    if os.path.exists(category_dir):
        new_category_dir = os.path.join(user_path, user_name, project_name, new_category_path)
        shutil.move(category_dir, new_category_dir)
        return True
    else:
        return False

def del_project_category(user_name, project_name, category_path):
    """
    删除用户项目下分类对应的目录
    """
    category_dir = os.path.join(user_path, user_name, project_name, category_path)
    print(category_dir)
    if os.path.exists(category_dir):
        shutil.rmtree(category_dir)
        return True
    else:
        return False

def save_article_to_disk(user_name, project_name, category_path, article_title, article_content):
    """
    保存文章到磁盘
    """
    category_dir = os.path.join(user_path, user_name, project_name, category_path)
    if not os.path.exists(category_dir):
        os.makedirs(category_dir)
    file_path = os.path.join(category_dir, article_title) + '.md'
    # print(file_path, "----保存")
    with open(file_path, 'w') as f:
        f.write(article_content)
    return True

def del_article_from_disk(user_name, project_name, category_path, article_title):
    """
    从磁盘删除文章
    """
    article_path = os.path.join(user_path, user_name, project_name, category_path, article_title) + '.md'
    # print(article_path, "----删除")

    if os.path.exists(article_path):
        os.remove(article_path)
        return True
    else:
        return False

def rename_article(user_name, project_name, category_path, old_article_title, new_article_title):
    """
    重命名用户项目下分类对应的文章
    """
    article_path = os.path.join(user_path, user_name, project_name, category_path, old_article_title) + '.md'
    if os.path.exists(article_path):
        new_article_path = os.path.join(user_path, user_name, project_name, category_path, new_article_title) + '.md'
        shutil.move(article_path, new_article_path)
        return True
    else:
        return False


def get_attachment_base_dir(user_name, project_name, category_path=None):
    """
    获取附件存储的基础目录
    """
    category_segment = category_path if category_path else '_root'
    return os.path.join(user_path, user_name, project_name, category_segment, 'attachments')


def save_attachment_to_disk(user_name, project_name, category_path, stored_name, werkzeug_file):
    """
    保存附件到磁盘
    :param user_name: 用户名
    :param project_name: 项目名
    :param category_path: 目录路径（可空）
    :param stored_name: 存储文件名（uuid.ext）
    :param werkzeug_file: Werkzeug FileStorage 对象
    :return: (absolute_path, relative_path) 绝对路径和相对于 user_path 的相对路径
    """
    base_dir = get_attachment_base_dir(user_name, project_name, category_path)
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    abs_path = os.path.join(base_dir, stored_name)
    werkzeug_file.save(abs_path)
    
    # 相对路径：从 user_path 之后开始
    rel_path = os.path.relpath(abs_path, user_path)
    return abs_path, rel_path


def del_attachment_from_disk(abs_path):
    """
    从磁盘删除附件
    """
    if os.path.exists(abs_path):
        os.remove(abs_path)
        return True
    return False


def get_attachment_abs_path(user_name, project_name, category_path, stored_name):
    """
    获取附件的绝对路径
    """
    base_dir = get_attachment_base_dir(user_name, project_name, category_path)
    return os.path.join(base_dir, stored_name)
