import uuid
from app.extension import db
from app.utils import format_datetime_to_string
from datetime import datetime
class User(db.Model):
    __tablename__ = 'user' # 数据库表名

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(64), unique=True, nullable=False, comment='用户名')
    nickname = db.Column(db.String(64), nullable=True, comment='昵称')
    email = db.Column(db.String(128), unique=True, nullable=False, comment='邮箱')
    password = db.Column(db.String(255), nullable=False, comment='密码')
    salt = db.Column(db.String(255), nullable=False, comment='盐值')
    description = db.Column(db.Text, nullable=True, comment='用户描述')
    avatar = db.Column(db.String(255), nullable=True, comment='头像URL')
    create_time = db.Column(db.DateTime, nullable=False, default=datetime.now(), comment='创建时间')
    update_time = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now(), comment='更新时间')

    # 打印用户信息
    def dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname,
            'email': self.email,
            'avatar': self.avatar,
            'create_time': format_datetime_to_string(self.create_time),
            'update_time': format_datetime_to_string(self.update_time)
        }

    # 添加用户
    def add_user(self):
        db.session.add(self)
        db.session.commit()
        return self

    # 更新用户
    def update_user(self):
        db.session.add(self)
        db.session.commit()
        return self

    # 删除用户
    def delete_user(self):
        db.session.delete(self)
        db.session.commit()
        return self

    # 根据username查询用户
    @classmethod
    def get_user_by_username(cls, username):
        return User.query.filter_by(username=username).first()

    # 根据username或者email查询用户
    @classmethod
    def get_user_by_username_or_email(cls, username_or_email):
        return User.query.filter(
            db.or_(
                User.username == username_or_email,
                User.email == username_or_email
            )
        ).first()
        # return cls.query.filter((cls.username == username_or_email) | (cls.email == username_or_email)).first()

    # 根据id查询用户
    @classmethod
    def get_user_by_id(cls, user_id):
        return User.query.filter_by(id=user_id).first()
    
    # 查询所有用户
    @classmethod
    def get_all_users(cls):
        return User.query.all()
