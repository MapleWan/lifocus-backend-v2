from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
import redis
from celery import Celery

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
redis_client = redis.Redis()
celery_app = Celery('lifocus')