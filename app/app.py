import os
from flask import Flask
from flask_cors import CORS
from .config import config
import redis
from .extension import db, migrate, jwt, redis_client
from .controllers import api_blueprint
def register_JWT_hooks(jwt):
    # 注册JWT钩子函数，用于检查token是否在黑名单中
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        token_in_redis = redis_client.get(jti)
        return token_in_redis is not None

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV') or 'develop'
        
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    app.register_blueprint(api_blueprint) # 注册API蓝图
    
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    register_JWT_hooks(jwt) # 注册JWT钩子函数

    redis_client.connection_pool = redis.ConnectionPool(host=app.config['REDIS_HOST'],
                                port=app.config['REDIS_PORT'],
                                db=app.config['REDIS_DB'],
                                password=app.config['REDIS_PASSWORD'])
    
    CORS(app)
    return app

app = create_app(os.getenv('FLASK_ENV'))
