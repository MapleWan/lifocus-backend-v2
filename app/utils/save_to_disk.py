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
