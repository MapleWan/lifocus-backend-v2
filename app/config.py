import os
from datetime import timedelta

# MySQL数据库相关配置
USERNAME = os.getenv('MYSQL_USER_NAME')
PASSWORD = os.getenv('MYSQL_USER_PASSWORD')
HOSTNAEME = os.getenv('MYSQL_HOSTNAME')
PORT = os.getenv('MYSQL_PORT')
DATABASE = os.getenv('MYSQL_DATABASE')
# MySQL数据库连接字符串
DIALECT = 'mysql'
DRIVER = 'pymysql'

# PostgreSQL数据库相关配置
PG_USERNAME = os.getenv('PG_USER_NAME')
PG_PASSWORD = os.getenv('PG_USER_PASSWORD')
PG_HOSTNAME = os.getenv('PG_HOSTNAME')
PG_PORT = os.getenv('PG_PORT')
PG_DATABASE = os.getenv('PG_DATABASE')
# PostgreSQL数据库连接字符串
PG_DIALECT = 'postgresql'
PG_DRIVER = 'psycopg2'

class Config(object):
    DEBUG = os.getenv('FLASK_DEBUG')
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    FLASK_APP = os.getenv('FLASK_APP')
    FLASK_RUN_HOST = os.getenv('FLASK_RUN_HOST')
    FLASK_RUN_PORT = os.getenv('FLASK_RUN_PORT')
    
    # 数据库类型
    DB_TYPE = os.getenv('DB_TYPE') # mysql postgres
    
    if DB_TYPE == 'mysql':
        # 配置MySQL数据库连接字符串
        SQLALCHEMY_DATABASE_URI = '{}+{}://{}:{}@{}:{}/{}?charset=utf8mb4'.format(DIALECT, DRIVER, USERNAME, PASSWORD, HOSTNAEME, PORT, DATABASE)
    elif DB_TYPE == 'postgres':
        # 配置PostgreSQL数据库连接字符串
        SQLALCHEMY_DATABASE_URI = '{}+{}://{}:{}@{}:{}/{}'.format(PG_DIALECT, PG_DRIVER, PG_USERNAME, PG_PASSWORD, PG_HOSTNAME, PG_PORT, PG_DATABASE)
    else:
        raise ValueError('Invalid DB_TYPE. Supported values are "mysql" and "postgres".')

    #JWT配置
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=6) # 6小时
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=1) # 1天
    # JWT_BLOCKLIST_TOKEN_CHECKS = ['access', 'refresh'] # 检查类型

    # Redis配置
    REDIS_HOST = os.getenv('REDIS_HOST')
    REDIS_PORT = os.getenv('REDIS_PORT')
    REDIS_DB = os.getenv('REDIS_DB')
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
class DevelopmentConfig(Config):
    DEBUG = True

class ProuctionConfig(Config):
    DEBUG = False
    # SQLALCHEMY_DATABASE_URI = ''

config = {
    'develop': DevelopmentConfig,
    'production': ProuctionConfig,
    'default': DevelopmentConfig
}