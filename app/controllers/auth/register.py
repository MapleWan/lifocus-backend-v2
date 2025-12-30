from flask_restx import Resource, reqparse
from app.controllers import auth_ns
from app.models import User
from app.enums import REGISTER_ERROR_MESSAGE
from app.utils import hash_password, valid_password, checkEmailFormat

class RegisterResource(Resource):
    @auth_ns.doc(description='用户注册')
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('username', required=True, help='用户不能为空')
            parser.add_argument('email', required=True, help='邮箱不能为空')
            parser.add_argument('password', required=True, help='密码不能为空')
            args = parser.parse_args()

            username = args['username']
            email = args['email']
            password = args['password']

            if not checkEmailFormat(email):
                return {'message': REGISTER_ERROR_MESSAGE["EMAIL_FORMAT_ERROR"]}, 400
            if not valid_password(password):
                return {'message': REGISTER_ERROR_MESSAGE["PASSWORD_FORMAT_ERROR"]}, 400
            if User.get_user_by_username_or_email(username):
                return {'message': REGISTER_ERROR_MESSAGE["USER_REPEATED"]}, 400
            if User.get_user_by_username_or_email(email):
                return {'message': REGISTER_ERROR_MESSAGE["EMAIL_REPEATED"]}, 400
            
            salt, saved_password = hash_password(password)
            user = User(username=username, email=email, salt=salt, password=saved_password)
            user.add_user()
            return {'code' : 200, 'message': '注册成功', 'data': user.dict()}, 200

        except Exception as e:
            return {'message': '{}: {}'.format( REGISTER_ERROR_MESSAGE["COMMON_ERROR"], e)}, 500
