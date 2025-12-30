from dotenv import load_dotenv

load_dotenv() # 加载环境变量
# print(os.environ.get("FLASK_ENV"))
from app import app

if __name__ == '__main__':
    app.run(app.config['FLASK_RUN_HOST'], app.config['FLASK_RUN_PORT'], app.config['DEBUG'])

# 启动项目
# flask -e .env.develop run
# flask -e .env.production run

# 初始化数据库
# flask -e .env.develop db init
# 更新数据库
# flask -e .env.develop db migrate -m '新增<项目>表'
# flask -e .env.develop db upgrade