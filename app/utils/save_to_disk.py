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
    print(file_path, "----保存")
    with open(file_path, 'w') as f:
        f.write(article_content)
    return True

def del_article_from_disk(user_name, project_name, category_path, article_title):
    """
    从磁盘删除文章
    """
    article_path = os.path.join(user_path, user_name, project_name, category_path, article_title) + '.md'
    print(article_path, "----删除")

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
